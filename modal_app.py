"""Publiczne demo Sztab-SAR na Modal (T4 GPU + Bielik-4.5B BPE Fix + Gemma-4-E4B)."""
from __future__ import annotations

import gc
import time
from pathlib import Path

import modal

app = modal.App("sztab-sar-demo")
vol = modal.Volume.from_name("kustosz-rodo-models", create_if_missing=True)

MODEL_DIR = Path("/models")
BIELIK_REPO = "speakleash/Bielik-4.5B-v3.0-Instruct-GGUF"
BIELIK_RAW = "Bielik-4.5B-v3.0-Instruct.Q8_0.gguf"
BIELIK_FIX = "Bielik-4.5B-v3.0-Instruct.Q8_0.fix.gguf"

GEMMA_REPO = "unsloth/gemma-4-E4B-it-GGUF"
GEMMA_FILE = "gemma-4-E4B-it-Q6_K.gguf"

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-runtime-ubuntu22.04", add_python="3.12")
    .pip_install(
        "fastapi[standard]",
        "python-multipart",
        "pymupdf",
        "python-docx",
        "huggingface_hub",
    )
    .pip_install(
        "llama-cpp-python",
        extra_index_url="https://abetlen.github.io/llama-cpp-python/whl/cu124",
    )
    .pip_install("gguf")
    .add_local_dir("sar", "/root/sar", ignore=["__pycache__", "*.pyc"])
    .add_local_dir("tools", "/root/tools", ignore=["__pycache__", "*.pyc", "_deck.html"])
    .add_local_dir("ui", "/root/ui")
    .add_local_file("Sztab_SAR_Prezentacja.pdf", "/root/Sztab_SAR_Prezentacja.pdf")
)


@app.cls(
    image=image,
    gpu="T4",
    volumes={"/models": vol},
    scaledown_window=300,
    timeout=300,
)
@modal.concurrent(max_inputs=4)
class SztabService:
    @modal.enter()
    def startup(self):
        self.llm = None
        self.active_key = ""
        self.active_label = ""
        self.ensure_model("bielik")

    def _prepare_bielik_path(self) -> Path:
        from huggingface_hub import hf_hub_download

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        fix_path = MODEL_DIR / BIELIK_FIX
        if fix_path.is_file():
            return fix_path

        raw_path = MODEL_DIR / BIELIK_RAW
        if not raw_path.is_file():
            hf_hub_download(repo_id=BIELIK_REPO, filename=BIELIK_RAW, local_dir=str(MODEL_DIR))
            vol.commit()

        tok_json = MODEL_DIR / "tokenizer_45.json"
        if tok_json.is_file():
            import sys
            sys.path.insert(0, "/root")
            from tools.fix_bielik_tok import fix_bielik_gguf

            fix_bielik_gguf(raw_path, fix_path, tok_json)
            vol.commit()
            return fix_path
        return raw_path

    def _prepare_gemma_path(self) -> Path:
        from huggingface_hub import hf_hub_download

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        g_path = MODEL_DIR / GEMMA_FILE
        if not g_path.is_file():
            hf_hub_download(repo_id=GEMMA_REPO, filename=GEMMA_FILE, local_dir=str(MODEL_DIR))
            vol.commit()
        return g_path

    def ensure_model(self, key: str) -> None:
        from llama_cpp import Llama

        target = "gemma" if key == "gemma" else "bielik"
        if target == self.active_key and self.llm is not None:
            return

        if self.llm is not None:
            del self.llm
            self.llm = None
            gc.collect()

        path = self._prepare_gemma_path() if target == "gemma" else self._prepare_bielik_path()
        self.llm = Llama(
            model_path=str(path),
            n_ctx=4096,
            n_gpu_layers=-1,
            verbose=False,
        )
        self.active_key = target
        self.active_label = path.name

    def classify(self, messages: list[dict], meta: dict):
        import sys
        sys.path.insert(0, "/root")
        from sar.slm_extract import SYSTEM_PROMPT, SlmExtractResult, format_prompt_payload, parse_slm_json

        if self.llm is None:
            self.ensure_model("bielik")

        t0 = time.perf_counter()
        resp = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": format_prompt_payload(messages, meta)},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=520,
        )
        content = resp["choices"][0]["message"]["content"]
        data = parse_slm_json(content)
        ms = int((time.perf_counter() - t0) * 1000)
        return SlmExtractResult(data=data, raw_text=content, latency_ms=ms, ok=bool(data))

    @modal.asgi_app()
    def web(self):
        import sys
        sys.path.insert(0, "/root")
        from sar.web_modal import build_app
        return build_app(self)
