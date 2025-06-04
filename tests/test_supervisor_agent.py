import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
