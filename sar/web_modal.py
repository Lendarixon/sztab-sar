"""FastAPI aplikacja dla publicznego demo Sztab-SAR na Modal (T4 GPU)."""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

from sar.pipeline import build_rozkaz_html, run_sar_analysis
from sar.scenarios import DEMO_SCENARIOS


class AnalyzeReq(BaseModel):
    messages: list[dict] = []
    meta: dict = {}
    use_slm: bool = True
    model: str | None = None


class ModelReq(BaseModel):
    model: str = "bielik"


class ExportReq(BaseModel):
    report: dict = {}
    meta: dict = {}
    messages: list[dict] = []


def build_app(service) -> FastAPI:
    api = FastAPI(title="Sztab-SAR — Taktyczny Koordynator Poszukiwań Offline")
    ui_html = Path("/root/ui/index.html").read_text(encoding="utf-8")
    exports: dict[str, str] = {}

    @api.get("/", response_class=HTMLResponse)
    def index():
        return ui_html

    @api.get("/favicon.ico")
    def favicon():
        return Response(status_code=204)

    @api.get("/prezentacja.pdf")
    def prezentacja_pdf():
        pdf_path = Path("/root/Sztab_SAR_Prezentacja.pdf")
        if not pdf_path.exists():
            raise HTTPException(404, "Brak pliku prezentacji")
        return Response(
            content=pdf_path.read_bytes(),
            media_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="Sztab_SAR_Prezentacja.pdf"'},
        )

    @api.get("/api/status")
    def status():
        return {
            "ok": True,
            "model": service.active_label,
            "active_key": service.active_key,
            "device": "Modal T4 GPU",
            "models_available": ["bielik", "gemma"],
        }

    @api.get("/api/scenarios")
    def scenarios():
        return {"scenarios": DEMO_SCENARIOS}

    @api.post("/api/model")
    def switch_model(req: ModelReq):
        key = "gemma" if req.model == "gemma" else "bielik"
        service.ensure_model(key)
        return {
            "ok": True,
            "model": service.active_label,
            "active_key": service.active_key,
            "device": "Modal T4 GPU",
        }

    @api.post("/api/upload")
    async def upload_txt(file: UploadFile = File(...)):
        raw = await file.read()
        if len(raw) > 2_000_000:
            raise HTTPException(400, "Maksymalny rozmiar pliku to 2 MB")
        text = raw.decode("utf-8", errors="replace")
        msgs = []
        for idx, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            msgs.append({"id": f"M{idx}", "time": "--:--", "source": Path(file.filename or "Plik").name, "text": line})
        return {"messages": msgs[:30]}

    @api.post("/api/analyze")
    def analyze(req: AnalyzeReq):
        if req.use_slm and req.model in ("bielik", "gemma") and req.model != service.active_key:
            service.ensure_model(req.model)
        res = run_sar_analysis(
            req.messages,
            req.meta,
            use_slm=req.use_slm,
            classify_fn=service.classify,
        )
        res["model"] = service.active_label
        return res

    @api.post("/api/export")
    def export_rozkaz(req: ExportReq):
        html_doc = build_rozkaz_html(req.report, req.meta, req.messages)
        eid = uuid.uuid4().hex[:10]
        exports[eid] = html_doc
        return {"download_url": f"/api/download/{eid}", "filename": "Rozkaz_Poszukiwawczy_Sztab_SAR.html"}

    @api.get("/api/download/{eid}")
    def download(eid: str):
        if eid not in exports:
            raise HTTPException(404, "Nie znaleziono dokumentu")
        return Response(
            content=exports[eid].encode("utf-8"),
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="Rozkaz_Poszukiwawczy_Sztab_SAR.html"'},
        )

    return api
