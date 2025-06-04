from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn, os, httpx, asyncio

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
        except Exception as e:
            data = {"error": str(e)}
    return {"delegate": delegate, "agent_response": data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
