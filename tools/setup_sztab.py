"""Instalator Sztab-SAR: pobiera llama.cpp (Windows Vulkan/CPU) oraz model Bielik-4.5B (GGUF) z SHA-256."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BIELIK_FILE = "Bielik-4.5B-v3.0-Instruct.Q8_0.gguf"
BIELIK_URL = f"https://huggingface.co/speakleash/Bielik-4.5B-v3.0-Instruct-GGUF/resolve/main/{BIELIK_FILE}"
BIELIK_SHA = "562f2291de257890adf2b4a914da8b194affe6a7a838a6b7ef3d342f306c1b7f"

GEMMA_REV = "bfc15c382204943c3a8fff0c750b94ae2364d7a3"
GEMMA_FILE = "gemma-4-E4B-it-Q6_K.gguf"
GEMMA_URL = f"https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF/resolve/{GEMMA_REV}/{GEMMA_FILE}"
GEMMA_SHA = "fd83f3ef44d22e00ff0f638753dde9a66a83e8ccf79c11024f47d383c489531b"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_with_resume(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    part = dst.with_name(dst.name + ".part")
    have = part.stat().st_size if part.exists() else 0
    headers = {"User-Agent": "sztab-sar-installer/1.0"}
    if have:
        headers["Range"] = f"bytes={have}-"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        if have and r.status != 206:
            have = 0
        total = have + int(r.headers.get("Content-Length", 0))
        with open(part, "ab" if have else "wb") as f:
            done, last = have, -1
            while True:
                buf = r.read(1 << 20)
                if not buf:
                    break
                f.write(buf)
                done += len(buf)
                pct = int(done * 100 / total) if total else 0
                if pct != last:
                    print(f"\r  {dst.name}: {pct}% ({done >> 20} / {total >> 20} MB)", end="", flush=True)
                    last = pct
    print()
    part.replace(dst)


def ensure_pip_deps() -> None:
    print("[1/3] Sprawdzam zależności Python...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], check=True)


def ensure_llama_windows(bin_dir: Path) -> None:
    if (bin_dir / "llama-server.exe").exists():
        print("[2/3] llama-server.exe już istnieje:", bin_dir)
        return
    if os.name != "nt":
        print("[2/3] System inny niż Windows — zainstaluj llama-server (llama.cpp) do PATH lub ./bin/llama-server")
        return

    print("[2/3] Pobieram llama.cpp (Windows Vulkan/CPU) z GitHub Releases...")
    req = urllib.request.Request(
        "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest",
        headers={"User-Agent": "sztab-sar-installer/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        rel = json.loads(r.read().decode("utf-8"))

    chosen = None
    for pattern in ("win-vulkan-x64.zip", "win-cpu-x64.zip"):
        for a in rel.get("assets", []):
            if a["name"].endswith(pattern):
                chosen = a
                break
        if chosen:
            break
    if not chosen:
        raise RuntimeError("Nie znaleziono paczki Windows w najnowszym wydaniu llama.cpp")

    zip_path = bin_dir / chosen["name"]
    download_with_resume(chosen["browser_download_url"], zip_path)
    print(f"  Rozpakowuję {chosen['name']}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            name = Path(member.filename).name
            if name.endswith((".exe", ".dll")) or name.startswith("LICENSE"):
                (bin_dir / name).write_bytes(zf.read(member))
    zip_path.unlink(missing_ok=True)
    print("  Gotowe:", bin_dir / "llama-server.exe")


def ensure_models(models_dir: Path, with_gemma: bool = False) -> None:
    print("[3/3] Sprawdzam model Bielik-4.5B-v3.0-Instruct...")
    cached_fix = Path.home() / "Desktop" / "LocalDocs" / "models" / "sejf" / "Bielik-4.5B-v3.0-Instruct.Q6_K.fix.gguf"
    if cached_fix.is_file():
        print("  Wykryto lokalny model z naprawionym tokenizerem:", cached_fix)
    else:
        dst = models_dir / BIELIK_FILE
        if dst.exists() and sha256(dst) == BIELIK_SHA:
            print("  OK:", dst)
        else:
            print(f"  Pobieram {BIELIK_FILE} (~4.8 GB, jednorazowo)...")
            download_with_resume(BIELIK_URL, dst)
            if sha256(dst) != BIELIK_SHA:
                dst.unlink(missing_ok=True)
                raise RuntimeError(f"Nieprawidłowa suma SHA-256 dla {BIELIK_FILE}")

    if with_gemma:
        gdst = models_dir / GEMMA_FILE
        if gdst.exists() and sha256(gdst) == GEMMA_SHA:
            print("  OK:", gdst)
        else:
            print(f"  Pobieram {GEMMA_FILE} (~6.7 GB)...")
            download_with_resume(GEMMA_URL, gdst)
            if sha256(gdst) != GEMMA_SHA:
                gdst.unlink(missing_ok=True)
                raise RuntimeError(f"Nieprawidłowa suma SHA-256 dla {GEMMA_FILE}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-gemma", action="store_true", help="Pobierz również opcjonalny model Gemma-4-E4B-it")
    ap.add_argument("--skip-deps", action="store_true")
    args = ap.parse_args()

    data_dir = Path(os.environ.get("SZTAB_DATA", Path(os.environ.get("LOCALAPPDATA", Path.home())) / "SztabSAR"))
    if not args.skip_deps:
        ensure_pip_deps()
    ensure_llama_windows(data_dir / "bin")
    ensure_models(data_dir / "models", with_gemma=args.with_gemma)
    print("\nInstalacja Sztab-SAR zakończona pomyślnie.")


if __name__ == "__main__":
    main()
