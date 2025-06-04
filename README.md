# Multi‑Raspberry‑Pi Agentic AI Starter

_Generated on 2025-05-29._

This repo spins up **three sensor‑powered agents**—one per Raspberry Pi—and a **supervisor** that runs on your laptop.

| Service (Docker)  | Intended host | Role |
|-------------------|---------------|------|
| supervisor_agent  | Laptop        | Delegates tasks to RPIs |
| kitchen_agent     | Kitchen RPi   | Reads BME680, serves data |
| hallway_agent     | Hallway RPi   | Reads BME680, serves data |
| office_agent      | Office RPi    | Reads BME680, serves data |

## Quick start (laptop)

```bash
docker compose build
docker compose up -d
```

Interact with the supervisor by sending a natural language prompt:

```bash
curl -X POST "http://localhost:8000/prompt" \
     -H "Content-Type: application/json" \
     -d '{"prompt":"Get the latest kitchen sensor data"}'
```

The LLM-based supervisor will parse your prompt, delegate the task to the appropriate agent and return the agent response.

## Deploying on each RPi

1. Copy only its agent folder and `requirements.txt` to the Pi.
2. `pip install -r requirements.txt`
3. `python agent.py`  
   (No Docker needed if you prefer bare‑metal.)

Each agent auto‑detects the BME680; if the library or sensor isn’t found it falls back to simulated random readings—handy for dev on non‑Pi hardware.

## Customization

* Extend `SensorReader.read()` in `sensor_reader.py` for more sensors.
* Enhance `route()` in `supervisor_agent.py` for richer delegation (LLM prompt, etc).
* Add secure authentication with an API key header before production use.
* Tune `/llm` parameters like `temperature`, `top_p`, and `max_tokens` via the web UI.
