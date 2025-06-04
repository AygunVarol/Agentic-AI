import os
from typing import Optional

try:
    import torch
except Exception:
    torch = None

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception:
    AutoModelForCausalLM = None
    AutoTokenizer = None

try:
    from llama_cpp import Llama
except Exception:
    Llama = None

BASE_CACHE_DIR = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface"))

LLAMA3_ID = "meta-llama/Llama-3.2-1B-Instruct"

TINY_LLAMA_PATH = os.path.join(
    BASE_CACHE_DIR,
    "models--TheBloke--TinyLlama-1.1B-Chat-v1.0-GGUF",
    "snapshots",
    "52e7645ba7c309695bec7ac98f4f005b139cf465",
    "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
)

PHI3_PATH = os.path.join(
    BASE_CACHE_DIR,
    "models--microsoft--Phi-3-mini-4k-instruct-gguf",
    "snapshots",
    "999f761fe19e26cf1a339a5ec5f9f201301cbb83",
    "Phi-3-mini-4k-instruct-q4.gguf",
)

_llama3_model = None
_llama3_tok = None
_tinyllama = None
_phi3 = None

def _load_llama3():
    global _llama3_model, _llama3_tok
    if _llama3_model is None:
        if AutoModelForCausalLM is None:
            raise RuntimeError("transformers not installed")
        _llama3_tok = AutoTokenizer.from_pretrained(LLAMA3_ID)
        _llama3_model = AutoModelForCausalLM.from_pretrained(LLAMA3_ID)
    return _llama3_model, _llama3_tok


def _load_tinyllama():
    global _tinyllama
    if _tinyllama is None:
        if Llama is None:
            raise RuntimeError("llama-cpp-python not installed")
        _tinyllama = Llama(model_path=TINY_LLAMA_PATH)
    return _tinyllama


def _load_phi3():
    global _phi3
    if _phi3 is None:
        if Llama is None:
            raise RuntimeError("llama-cpp-python not installed")
        _phi3 = Llama(model_path=PHI3_PATH)
    return _phi3


def generate(
    model_name: str,
    prompt: str,
    *,
    max_tokens: int = 128,
    temperature: float = 0.7,
    top_p: float = 0.95,
) -> str:
    """Generate text using the specified model."""
    use_gpu = torch is not None and torch.cuda.is_available()
    if model_name == "llama3":
        model, tok = _load_llama3()
        device = "cuda" if use_gpu else "cpu"
        ids = tok(prompt, return_tensors="pt").input_ids.to(device)
        model = model.to(device)
        out = model.generate(
            ids,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return tok.decode(out[0], skip_special_tokens=True)
    elif model_name == "tinyllama":
        llm = _load_tinyllama()
        res = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n_gpu_layers=-1 if use_gpu else 0,
        )
        return res["choices"][0]["text"]
    elif model_name == "phi3":
        llm = _load_phi3()
        res = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n_gpu_layers=-1 if use_gpu else 0,
        )
        return res["choices"][0]["text"]
    else:
        raise ValueError(f"unknown model {model_name}")

