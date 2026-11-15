"""Lokalny serwer HTTP dla Sztab-SAR (100% offline z llama-server)."""
from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import uuid
import webbrowser
from email.parser import BytesParser
from email.policy import default as email_default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from sar.pipeline import build_rozkaz_html, run_sar_analysis
from sar.scenarios import DEMO_SCENARIOS
from sar.slm_extract import classify_via_llama_http

HERE = Path(__file__).resolve().parent
UI_PATH = HERE / "ui" / "index.html"
DATA_DIR = Path(os.environ.get("SZTAB_DATA", Path(os.environ.get("LOCALAPPDATA", Path.home())) / "SztabSAR"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
CFG_PATH = DATA_DIR / "config.json"

BIELIK_FILES = (
    "Bielik-4.5B-v3.0-Instruct.Q6_K.fix.gguf",
    "Bielik-4.5B-v3.0-Instruct.Q8_0.fix.gguf",
    "Bielik-4.5B-v3.0-Instruct.Q8_0.gguf",
)
GEMMA_FILES = ("gemma-4-E4B-it-Q6_K.gguf",)

HOST = "127.0.0.1"
DEFAULT_PORT = 8793
LLAMA_PORT = 8794

_LLAMA_PROC: subprocess.Popen | None = None
_ACTIVE_MODEL = ""
_DEVICE_LABEL = "CPU"
_EXPORTS: dict[str, str] = {}


def load_cfg() -> dict:
    try:
        return json.loads(CFG_PATH.read_text(encoding="utf-8-sig")) if CFG_PATH.is_file() else {}
    except (OSError, ValueError):
        return {}


def save_cfg(cfg: dict) -> None:
    tmp = CFG_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CFG_PATH)


def current_settings() -> dict:
    cfg = load_cfg()
    return {
        "model": cfg.get("model", "bielik"),
        "gpu": cfg.get("gpu", "auto"),
        "threads": int(cfg.get("threads", min(8, os.cpu_count() or 4))),
        "port": int(cfg.get("port", DEFAULT_PORT)),
    }


def _find_llama() -> Path:
    cfg = load_cfg()
    exe = "llama-server.exe" if os.name == "nt" else "llama-server"
    for c in (
        os.environ.get("SZTAB_LLAMA", ""),
        cfg.get("llama_bin", ""),
        str(HERE / "bin" / exe),
        str(DATA_DIR / "bin" / exe),
        str(Path(os.environ.get("LOCALAPPDATA", Path.home())) / "KustoszRODO" / "bin" / exe),
        str(Path.home() / "Desktop" / "LocalDocs" / "runtime" / "llama" / exe),
        shutil.which(exe) or "",
    ):
        if c and Path(c).is_file():
            return Path(c)
    return HERE / "bin" / exe


def _find_gguf(model_choice: str) -> Path:
    cfg = load_cfg()
    if os.environ.get("SZTAB_GGUF"):
        return Path(os.environ["SZTAB_GGUF"])
    search_dirs = [
        Path(cfg["models_dir"]) if cfg.get("models_dir") else None,
        HERE / "models",
        DATA_DIR / "models",
        Path(os.environ.get("LOCALAPPDATA", Path.home())) / "KustoszRODO" / "models",
        Path.home() / "Desktop" / "LocalDocs" / "models" / "sejf",
    ]
    names = GEMMA_FILES if model_choice == "gemma" else BIELIK_FILES
    for d in search_dirs:
        if d and d.is_dir():
            for n in names:
                p = d / n
                if p.is_file():
                    return p
    return HERE / "models" / names[0]


def stop_llama() -> None:
    global _LLAMA_PROC
    if _LLAMA_PROC and _LLAMA_PROC.poll() is None:
        _LLAMA_PROC.terminate()
        try:
            _LLAMA_PROC.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _LLAMA_PROC.kill()
    _LLAMA_PROC = None


def start_llama() -> None:
    global _LLAMA_PROC, _ACTIVE_MODEL, _DEVICE_LABEL
    st = current_settings()
    llama = _find_llama()
    gguf = _find_gguf(st["model"])
    if not llama.is_file():
        raise FileNotFoundError(f"Brak llama-server ({llama}). Uruchom install.bat / tools/setup_sztab.py")
    if not gguf.is_file():
        raise FileNotFoundError(f"Brak modelu GGUF ({gguf}). Uruchom install.bat / tools/setup_sztab.py")

    ngl = "0" if st["gpu"] == "cpu" else "99"
    cmd = [
        str(llama),
        "-m", str(gguf),
        "--host", HOST,
        "--port", str(LLAMA_PORT),
        "-c", "4096",
        "-ngl", ngl,
        "-t", str(st["threads"]),
    ]
    log_file = open(DATA_DIR / "llama_sztab.log", "w", encoding="utf-8")
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    _LLAMA_PROC = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT, creationflags=flags)

    deadline = time.time() + 90
    while time.time() < deadline:
        if _LLAMA_PROC.poll() is not None:
            raise RuntimeError(f"llama-server zakończył pracę — sprawdź {DATA_DIR / 'llama_sztab.log'}")
        try:
            with urllib.request.urlopen(f"http://{HOST}:{LLAMA_PORT}/health", timeout=2) as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(0.5)
    _ACTIVE_MODEL = gguf.name
    _DEVICE_LABEL = "CPU" if ngl == "0" else "Lokalne GPU / CPU"


atexit.register(stop_llama)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, status: int, ctype: str, body: bytes, extra: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: dict):
        self._send(status, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", UI_PATH.read_bytes())
            return
        if self.path == "/favicon.ico":
            self._send(204, "text/plain", b"")
            return
        if self.path == "/api/status":
            st = current_settings()
            self._json(200, {
                "ok": True,
                "model": _ACTIVE_MODEL,
                "active_key": st["model"],
                "device": _DEVICE_LABEL,
                "settings": st,
                "models_available": ["bielik", "gemma"],
            })
            return
        if self.path == "/api/scenarios":
            self._json(200, {"scenarios": DEMO_SCENARIOS})
            return
        if self.path.startswith("/api/download/"):
            eid = self.path.split("/api/download/", 1)[1]
            if eid in _EXPORTS:
                self._send(
                    200,
                    "text/html; charset=utf-8",
                    _EXPORTS[eid].encode("utf-8"),
                    {"Content-Disposition": 'attachment; filename="Rozkaz_Poszukiwawczy_Sztab_SAR.html"'},
                )
                return
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if self.path == "/api/upload":
            raw_body = self.rfile.read(length)
            ctype = self.headers.get("Content-Type", "")
            msg = BytesParser(policy=email_default).parsebytes(
                b"Content-Type: " + ctype.encode("latin-1") + b"\r\nMIME-Version: 1.0\r\n\r\n" + raw_body
            )
            file_part = next((p for p in msg.iter_parts() if p.get_filename()), None)
            if not file_part:
                self._json(400, {"error": "Brak pliku"})
                return
            fname = Path(file_part.get_filename()).name
            raw_txt = file_part.get_payload(decode=True).decode("utf-8", errors="replace")
            msgs = [
                {"id": f"M{i}", "time": "--:--", "source": fname, "text": ln.strip()}
                for i, ln in enumerate(raw_txt.splitlines(), 1)
                if ln.strip()
            ]
            self._json(200, {"messages": msgs[:30]})
            return

        data = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if self.path in ("/api/settings", "/api/model"):
            cfg = load_cfg()
            changed = False
            if data.get("model") in ("bielik", "gemma") and data["model"] != cfg.get("model"):
                cfg["model"] = data["model"]
                changed = True
            if data.get("gpu") in ("auto", "cpu") and data["gpu"] != cfg.get("gpu"):
                cfg["gpu"] = data["gpu"]
                changed = True
            if isinstance(data.get("threads"), int) and 1 <= data["threads"] <= 64 and data["threads"] != cfg.get("threads"):
                cfg["threads"] = data["threads"]
                changed = True
            save_cfg(cfg)
            if changed:
                stop_llama()
                start_llama()
            st = current_settings()
            self._json(200, {"ok": True, "model": _ACTIVE_MODEL, "active_key": st["model"], "device": _DEVICE_LABEL, "settings": st})
            return

        if self.path == "/api/analyze":
            messages = data.get("messages", [])
            meta = data.get("meta", {})
            use_slm = bool(data.get("use_slm", True))
            res = run_sar_analysis(
                messages,
                meta,
                use_slm=use_slm,
                classify_fn=lambda ms, mt: classify_via_llama_http(ms, mt, f"http://{HOST}:{LLAMA_PORT}/v1/chat/completions"),
            )
            res["model"] = _ACTIVE_MODEL
            self._json(200, res)
            return

        if self.path == "/api/export":
            html_doc = build_rozkaz_html(data.get("report", {}), data.get("meta", {}), data.get("messages", []))
            eid = uuid.uuid4().hex[:10]
            _EXPORTS[eid] = html_doc
            self._json(200, {"download_url": f"/api/download/{eid}"})
            return

        self._json(404, {"error": "Not found"})


def main():
    st = current_settings()
    port = st["port"]
    print(f"[Sztab-SAR] Uruchamiam {_find_gguf(st['model']).name}...")
    start_llama()
    url = f"http://{HOST}:{port}/"
    print(f"[Sztab-SAR] Gotowe ({_DEVICE_LABEL}): {url}")
    if os.environ.get("SZTAB_NO_BROWSER") != "1":
        webbrowser.open(url)
    srv = ThreadingHTTPServer((HOST, port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_llama()


if __name__ == "__main__":
    main()
