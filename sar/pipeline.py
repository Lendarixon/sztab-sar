"""Glowny potok analizy Sztab-SAR: SLM + deterministyczny audytor + eksport rozkazu."""
from __future__ import annotations

import html
from dataclasses import asdict

from sar.rules import TacticalAssessment, ground_and_verify, run_regex_baseline
from sar.slm_extract import SlmExtractResult, classify_via_llama_http


def run_sar_analysis(
    messages: list[dict],
    meta: dict,
    use_slm: bool = True,
    classify_fn=classify_via_llama_http,
) -> dict:
    """Przetwarza meldunki poszukiwawcze przez SLM (lub tryb Regex) oraz weryfikator taktyczny."""
    norm_msgs = []
    for idx, m in enumerate(messages, start=1):
        norm_msgs.append({
            "id": str(m.get("id") or f"M{idx}"),
            "time": str(m.get("time") or "--:--"),
            "source": str(m.get("source") or "Meldunek"),
            "text": str(m.get("text") or "").strip(),
        })
    norm_msgs = [m for m in norm_msgs if m["text"]]

    if not norm_msgs:
        return {
            "mode": "empty",
            "latency_ms": 0,
            "slm_ok": False,
            "assessment": asdict(TacticalAssessment("PODWYŻSZONY", 0, 180, [], [], [])),
            "analysis": {
                "profil_zaginionego": {"osoba": "", "ubior": "", "zdrowie": "", "kierunek": ""},
                "klastry_sladow": [],
                "sprzecznosci": [],
                "os_czasu": [],
                "pytania_do_swiadkow": [],
            },
        }

    if not use_slm:
        cleaned, assessment = run_regex_baseline(norm_msgs, meta)
        return {
            "mode": "regex",
            "latency_ms": 1,
            "slm_ok": True,
            "analysis": cleaned,
            "assessment": asdict(assessment),
        }

    slm_res: SlmExtractResult = classify_fn(norm_msgs, meta)
    cleaned, assessment = ground_and_verify(slm_res.data, norm_msgs, meta)
    return {
        "mode": "slm",
        "latency_ms": slm_res.latency_ms,
        "slm_ok": slm_res.ok,
        "analysis": cleaned,
        "assessment": asdict(assessment),
        "raw_slm": slm_res.raw_text,
    }


def build_rozkaz_html(report: dict, meta: dict, messages: list[dict]) -> str:
    """Generuje gotowa Karte Poszukiwan / Rozkaz dla zespolow OSP/GOPR do wydruku PDF/HTML."""
    a = report.get("analysis", {})
    ass = report.get("assessment", {})
    p = a.get("profil_zaginionego", {})
    sectors = sorted(ass.get("sectors", []), key=lambda s: (s.get("priority", 9), -s.get("raw_score", 0)))

    sec_rows = "".join(
        f"<tr><td><b>{html.escape(s['code'])}</b></td><td>{html.escape(s['name'])}</td>"
        f"<td>{html.escape(s.get('badge',''))}</td><td>{html.escape(s.get('reason',''))}</td></tr>"
        for s in sectors
    )
    conf_rows = "".join(
        f"<li><b>[{html.escape(', '.join(c.get('ids', [])))}] {html.escape(c.get('type', ''))}:</b> "
        f"{html.escape(c.get('description', ''))}</li>"
        for c in a.get("sprzecznosci", [])
    ) or "<li>Brak wykrytych sprzeczności czasowo-terenowych.</li>"
    q_rows = "".join(f"<li>{html.escape(q)}</li>" for q in a.get("pytania_do_swiadkow", []))

    return f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<title>Karta Poszukiwań Sztab-SAR</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;max-width:920px;margin:28px auto;color:#111;line-height:1.45;}}
h1{{margin:0 0 6px;font-size:22px;}} .badge{{display:inline-block;padding:4px 10px;border-radius:6px;background:#b91c1c;color:#fff;font-weight:700;font-size:13px;}}
table{{width:100%;border-collapse:collapse;margin:12px 0;}} th,td{{border:1px solid #ccc;padding:7px 9px;text-align:left;font-size:13.5px;}}
th{{background:#f3f4f6;}} .box{{border:1px solid #d1d5db;border-radius:8px;padding:12px 14px;margin:12px 0;background:#fafafa;}}
</style></head><body>
<h1>Karta Poszukiwań i Rozkaz Operacyjny — Sztab-SAR</h1>
<p><span class="badge">ALARM: {html.escape(ass.get('alarm_level',''))} (Złote okno: {ass.get('golden_window_min', 60)} min)</span>
 &nbsp; Miejsce: <b>{html.escape((meta or {}).get('miejsce',''))}</b> | Warunki: {html.escape((meta or {}).get('pogoda',''))}</p>
<div class="box"><b>Zespolony profil osoby zaginionej:</b><br>
• Osoba: {html.escape(p.get('osoba',''))}<br>
• Ubiór: {html.escape(p.get('ubior',''))}<br>
• Zdrowie / ryzyka: {html.escape(p.get('zdrowie',''))} ({html.escape(', '.join(ass.get('risk_factors', [])))})<br>
• Kierunek: {html.escape(p.get('kierunek',''))}</div>
<h3>Priorytetowe sektory poszukiwań</h3>
<table><tr><th>Sektor</th><th>Teren / Punkt</th><th>Priorytet</th><th>Uzasadnienie</th></tr>{sec_rows}</table>
<h3>Wykryte sprzeczności i anomalie</h3><ul>{conf_rows}</ul>
<h3>Pytania weryfikacyjne dla dyspozytora</h3><ul>{q_rows}</ul>
</body></html>"""
