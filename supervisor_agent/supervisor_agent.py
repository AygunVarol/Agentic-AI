from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
from pathlib import Path
from datetime import datetime
import uvicorn, os, httpx, asyncio
from .llm_models import generate

app = FastAPI(title="Supervisor Agent")
INDEX_FILE = Path(__file__).resolve().parent / "static" / "index.html"

AGENTS = {
    # Internal service URLs for each delegate agent
    # Use service names defined in docker-compose instead of
    # hard-coded IP addresses so the agents can communicate in
    # different deployment environments.
    "kitchen_agent": "http://kitchen_agent:8000/task",
    "hallway_agent": "http://hallway_agent:8000/task",
    "office_agent": "http://office_agent:8000/task",
}

LAST_SEEN = {}

@app.get("/", response_class=HTMLResponse)
async def ui():
    return INDEX_FILE.read_text()

def route(task: dict) -> str:
    # Prefer explicit agent field
    if 'agent' in task:
        return f"{task['agent']}_agent" if not task['agent'].endswith('_agent') else task['agent']
    text = task.get("task", "").lower()
    for key in ("kitchen", "hallway", "office"):
        if key in text:
            return f"{key}_agent"
    # default
    return "office_agent"

async def check_agent(name: str, task_url: str):
    health_url = task_url.rsplit('/', 1)[0] + "/health"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(health_url, timeout=2)
            if resp.status_code == 200:
                ts = datetime.utcnow().isoformat(timespec="seconds")
                LAST_SEEN[name] = ts
                return {"name": name, "online": True, "last_seen": ts}
        except Exception:
            pass
    return {"name": name, "online": False, "last_seen": LAST_SEEN.get(name)}

@app.get("/agents")
async def agents_status():
    return await asyncio.gather(
        *[check_agent(name, url) for name, url in AGENTS.items()]
    )

@app.post("/task")
async def handle_task(task: dict = Body(...)):
    delegate = route(task)
    url = AGENTS.get(delegate)
    if not url:
        return {"error": f"unknown delegate {delegate}"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=task, timeout=60)
            data = resp.json()
            if resp.status_code == 200:
                LAST_SEEN[delegate] = datetime.utcnow().isoformat(timespec="seconds")
        except Exception as e:
            data = {"error": str(e)}
    return {"delegate": delegate, "agent_response": data}


@app.post("/llm")
async def handle_llm(data: dict = Body(...)):
    prompt = data.get("prompt", "")
    model = data.get("model", "llama3")
    max_tokens = int(data.get("max_tokens", 128))
    temperature = float(data.get("temperature", 0.7))
    top_p = float(data.get("top_p", 0.95))
    try:
        text = await asyncio.to_thread(
            generate,
            model,
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return {"model": model, "text": text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
