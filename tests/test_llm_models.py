import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from supervisor_agent.llm_models import generate


def test_invalid_model():
    with pytest.raises(ValueError):
        generate("badmodel", "hello")
