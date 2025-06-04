import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from supervisor_agent.llm_models import generate
from supervisor_agent import llm_models
from unittest import mock


def test_invalid_model():
    with pytest.raises(ValueError):
        generate("badmodel", "hello")


def test_load_tinyllama_uses_hf_hub_download():
    with mock.patch.object(llm_models, "hf_hub_download", return_value="/tmp/x") as dl:
        with mock.patch.object(llm_models, "Llama") as LlamaMock:
            llm_models._tinyllama = None
            llm_models._load_tinyllama()
            dl.assert_called_once_with(
                repo_id=llm_models.TINY_LLAMA_REPO,
                filename=llm_models.TINY_LLAMA_FILE,
                cache_dir=llm_models.BASE_CACHE_DIR,
            )
            LlamaMock.assert_called_once()
