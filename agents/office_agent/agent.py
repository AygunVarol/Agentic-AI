from fastapi import FastAPI, Body
import uvicorn, os, threading, time
from sensor_reader import SensorReader

LOCATION = "office"
reader = SensorReader(LOCATION)
latest = reader.read()

# Background thread to refresh sensor every 2 seconds
def loop():
    global latest
    while True:
        latest = reader.read()
        time.sleep(2)

t = threading.Thread(target=loop, daemon=True)
t.start()

app = FastAPI(title="Office Agent")

@app.post("/task")
async def handle_task(task: dict = Body(...)):
    cmd = task.get("task", "").lower()
    if "sensor" in cmd or "temperature" in cmd or "humidity" in cmd:
        return {"status": "ok", "data": latest}
    # Echo fallback
    return {"status": "ok", "echo": task}

@app.get("/health")
async def health():
    return {"status": "ok", "agent": LOCATION}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
