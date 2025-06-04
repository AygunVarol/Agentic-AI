import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from supervisor_agent import supervisor_agent as sa
from supervisor_agent.supervisor_agent import route


def test_explicit_agent_with_suffix():
    task = {"agent": "kitchen_agent"}
    assert route(task) == "kitchen_agent"


def test_explicit_agent_without_suffix():
    task = {"agent": "hallway"}
    assert route(task) == "hallway_agent"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Clean up the kitchen area", "kitchen_agent"),
        ("Please walk through the HALLWAY", "hallway_agent"),
        ("Meet me in the office soon", "office_agent"),
    ],
)
def test_keyword_detection(text, expected):
    assert route({"task": text}) == expected


def test_default_office_agent():
    task = {"task": "Go outside and check the garden"}
    assert route(task) == "office_agent"


@pytest.mark.asyncio
async def test_handle_prompt(monkeypatch):
    def fake_generate(model, prompt, max_tokens=256, temperature=0.7, top_p=0.95):
        return '[{"task": "Check kitchen sensor"}]'

    async def fake_handle_task(task):
        assert task["task"] == "Check kitchen sensor"
        return {"delegate": "kitchen_agent", "agent_response": {"ok": True}}

    monkeypatch.setattr(sa, "generate", fake_generate)
    monkeypatch.setattr(sa, "handle_task", fake_handle_task)

    result = await sa.handle_prompt({"prompt": "Get kitchen data"})
    assert result["results"][0]["delegate"] == "kitchen_agent"
