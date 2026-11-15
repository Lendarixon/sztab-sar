"""Generuje czytelną, 7-slajdową prezentację PDF (16:9) w stylu Metro UI dla Sztab-SAR."""
from __future__ import annotations

import base64
import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "tools" / "_deck.html"
PDF_PATH = ROOT / "Sztab_SAR_Prezentacja.pdf"
BENCH_PATH = ROOT / "bench" / "eval_report.json"
SCREENS_DIR = ROOT / "tools" / "_screens"
BRAVE = Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe")

GITHUB_URL = "https://github.com/Lendarixon/sztab-sar"
DEMO_URL = "https://ninjagovlad--sztab-sar-demo-sztabservice-web.us-east.modal.run"


def img_uri(filename: str) -> str:
    p = SCREENS_DIR / filename
    if not p.is_file():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def load_bench_data() -> list[dict]:
    if not BENCH_PATH.is_file():
        return []
    return json.loads(BENCH_PATH.read_text(encoding="utf-8")).get("results", [])


def build_bench_bars(results: list[dict]) -> str:
    if not results:
        return "<div class='tile'><p>Brak danych bench/eval_report.json</p></div>"
    metrics = [
        ("Koreferencja synonimów", "coreference_acc"),
        ("Detekcja konfliktów (F1)", "conflict_f1"),
        ("Priorytet sektora Top-1", "sector_top1_acc"),
        ("Klasyfikacja ryzyka med.", "medical_risk_acc"),
    ]
    colors = ["#d97706", "#0078d4", "#008272"]
    blocks = []
    for title, key in metrics:
        rows = []
        for idx, r in enumerate(results):
            val = float(r.get(key, 0.0)) * 100.0
            col = colors[idx % len(colors)]
            short_name = (
                "Regex (bez SLM)" if "Regex" in r["system"]
                else ("Bielik-4.5B BPE Fix" if "Bielik" in r["system"] else "Gemma-4-E4B-it")
            )
            rows.append(
                f"<div class='bar-row'>"
                f"<span class='bar-lbl'>{html.escape(short_name)}</span>"
                f"<div class='bar-track'><div class='bar-fill' style='width:{val:.1f}%;background:{col}'></div></div>"
                f"<span class='bar-val'>{val:.1f}%</span>"
                f"</div>"
            )
        blocks.append(f"<div class='metric-group'><div class='mg-title'>{title}</div>{''.join(rows)}</div>")
    return "".join(blocks)


def build_bench_rows(results: list[dict]) -> str:
    if not results:
        return "<tr><td colspan='5'>Brak bench/eval_report.json</td></tr>"
    out = []
    for r in results:
        cls = "hi-row" if "Bielik" in r["system"] else ""
        short = (
            "Regex Baseline" if "Regex" in r["system"]
            else ("Bielik-4.5B BPE Fix" if "Bielik" in r["system"] else "Gemma-4-E4B-it")
        )
        lat = f"{r['avg_latency_ms']} ms" if r["avg_latency_ms"] < 1000 else f"{r['avg_latency_ms']/1000:.1f} s"
        out.append(
            f"<tr class='{cls}'>"
            f"<td><b>{html.escape(short)}</b></td>"
            f"<td><b>{r['coreference_acc']*100:.1f}%</b></td>"
            f"<td><b>{r['conflict_f1']*100:.1f}%</b></td>"
            f"<td>{r['sector_top1_acc']*100:.1f}%</td>"
            f"<td>{lat}</td>"
            f"</tr>"
        )
    return "\n".join(out)


def build_html() -> str:
    results = load_bench_data()
    bench_bars = build_bench_bars(results)
    bench_rows = build_bench_rows(results)

    s_kpi = img_uri("crop_kpi_bar.png")
    s_col1 = img_uri("crop_bory_col1.png")
    s_bielik = img_uri("crop_bielik_col2.png")
    s_regex = img_uri("crop_regex_col2.png")
    s_tatry = img_uri("crop_tatry_col3.png")
    s_rozkaz = img_uri("crop_rozkaz.png")

    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Sztab-SAR — Prezentacja</title>
<style>
@page {{ size: 1280px 720px; margin: 0; }}
* {{ box-sizing: border-box; border-radius: 0 !important; }}
body {{
  margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
  background: #0d121b; color: #f8fafc;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}}
.slide {{
  width: 1280px; height: 720px; padding: 28px 42px 46px; position: relative;
  overflow: hidden; page-break-after: always; display: flex; flex-direction: column;
  background: #0d121b;
}}
.slide:last-child {{ page-break-after: auto; }}

.hdr {{
  display: flex; align-items: center; justify-content: space-between; gap: 18px;
  border-bottom: 2px solid #243044; padding-bottom: 10px; margin-bottom: 16px; flex-shrink: 0;
}}
.hdr-left {{ display: flex; align-items: center; gap: 14px; min-width: 0; }}
.badge {{
  background: #b91c1c; color: #fff; font-size: 13px; font-weight: 700;
  letter-spacing: .07em; padding: 6px 12px; text-transform: uppercase; white-space: nowrap; flex-shrink: 0;
}}
.badge.blue {{ background: #0078d4; }}
.badge.teal {{ background: #008272; }}
.badge.amber {{ background: #c2410c; }}

h1 {{ font-size: 54px; font-weight: 300; line-height: 1.05; margin: 0 0 10px; letter-spacing: -0.02em; color: #fff; }}
h1 b {{ font-weight: 700; color: #fff; }}
h2 {{ font-size: 27px; font-weight: 600; margin: 0; color: #fff; letter-spacing: -0.01em; line-height: 1.15; }}
.lead {{ font-size: 20px; color: #dbe5f4; line-height: 1.42; margin: 0 0 18px; max-width: 1080px; }}

.tile {{
  background: #151d2b; border: 1px solid #2b3950; padding: 16px 18px;
  display: flex; flex-direction: column; gap: 8px;
}}
.tile.accent-red {{ border-left: 5px solid #dc2626; background: #1e1318; }}
.tile.accent-blue {{ border-left: 5px solid #0078d4; background: #101d2e; }}
.tile.accent-teal {{ border-left: 5px solid #008272; background: #0f2120; }}
.tile.accent-amber {{ border-left: 5px solid #d97706; background: #211a10; }}
.tile h3 {{ margin: 0; font-size: 16px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: .04em; }}
.tile p, .tile li {{ margin: 0; font-size: 16px; color: #e2e8f0; line-height: 1.42; }}
.tile ul {{ margin: 2px 0 0 18px; padding: 0; display: flex; flex-direction: column; gap: 7px; }}

.kpi-solid {{ padding: 14px 16px; color: #fff; display: flex; flex-direction: column; gap: 4px; }}
.kpi-solid.red {{ background: #b91c1c; }}
.kpi-solid.blue {{ background: #0078d4; }}
.kpi-solid.teal {{ background: #008272; }}
.kpi-solid.amber {{ background: #b45309; }}
.kpi-solid.slate {{ background: #1e293b; border: 1px solid #334155; }}
.kpi-solid .lbl {{ font-size: 12px; font-weight: 700; letter-spacing: .07em; opacity: .92; text-transform: uppercase; }}
.kpi-solid .val {{ font-size: 32px; font-weight: 700; line-height: 1.05; }}
.kpi-solid .hint {{ font-size: 14px; opacity: .95; line-height: 1.32; }}

.crop-box {{
  border: 2px solid #2e3e58; background: #0b0e14;
  display: flex; flex-direction: column; overflow: hidden; min-height: 0;
}}
.crop-bar {{
  background: #1b2537; color: #fff; font-size: 13px; font-weight: 700;
  letter-spacing: .04em; padding: 8px 12px; text-transform: uppercase;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid #2e3e58; flex-shrink: 0;
}}
.crop-bar .pill-ok {{ background: #008272; padding: 3px 9px; font-size: 12px; }}
.crop-bar .pill-warn {{ background: #c2410c; padding: 3px 9px; font-size: 12px; }}
.crop-bar .pill-blue {{ background: #0078d4; padding: 3px 9px; font-size: 12px; }}
.crop-img-wrap {{
  flex: 1; min-height: 0; display: flex; align-items: flex-start; justify-content: center;
  overflow: hidden; background: #0d121b; padding: 4px;
}}
.crop-img-wrap.white {{ background: #0d121b; padding: 6px; align-items: center; }}
.crop-img-wrap.white img {{ height: auto; max-height: 100%; border: 1px solid #cbd5e1; }}
.crop-img-wrap img {{ width: 100%; height: 100%; object-fit: contain; object-position: top center; display: block; }}

.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: minmax(0, 1fr); gap: 18px; flex: 1; min-height: 0; }}
.grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; flex-shrink: 0; }}
.col {{ display: flex; flex-direction: column; gap: 12px; min-height: 0; }}

.msg-card {{
  background: #141c29; border: 1px solid #2b3950; border-left: 5px solid #dc2626;
  padding: 11px 14px; font-size: 16px; color: #f1f5f9; line-height: 1.38;
}}
.hl {{ background: #006658; color: #fff; padding: 1px 5px; font-weight: 700; }}
.cf {{ background: #991b1b; color: #fff; padding: 1px 6px; font-weight: 700; }}

.metric-group {{ background: #151d2b; border: 1px solid #2b3950; padding: 13px 16px; }}
.mg-title {{ font-size: 15px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 9px; }}
.bar-row {{ display: grid; grid-template-columns: 165px 1fr 62px; align-items: center; gap: 12px; margin-bottom: 7px; }}
.bar-row:last-child {{ margin-bottom: 0; }}
.bar-lbl {{ font-size: 14px; color: #e2e8f0; font-weight: 600; }}
.bar-track {{ height: 15px; background: #0b0e14; border: 1px solid #283548; }}
.bar-fill {{ height: 100%; }}
.bar-val {{ font-size: 15px; font-weight: 700; color: #fff; text-align: right; }}

table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th, td {{ border: 1px solid #2b3950; padding: 9px 10px; text-align: left; }}
th {{ background: #1c2738; color: #fff; font-size: 13px; text-transform: uppercase; }}
tr.hi-row td {{ background: #10263f; color: #fff; }}

.foot {{
  position: absolute; bottom: 14px; left: 42px; right: 42px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; color: #94a3b8; border-top: 1px solid #1e2838; padding-top: 8px;
}}
a {{ color: #60a5fa; text-decoration: none; font-weight: 700; }}
code {{ background: #1e293b; color: #93c5fd; padding: 2px 6px; font-size: 14px; }}
</style>
</head>
<body>

<!-- SLAJD 1: CZYSTY HERO + 4 KAFLE + PRAWDZIWA BELKA KPI 1:1 -->
<section class="slide" style="justify-content:space-between">
  <div>
    <div class="hdr" style="margin-bottom:22px">
      <div class="hdr-left">
        <span class="badge">Bielik Awards 2026</span>
        <span class="badge blue">Kategoria SLM (&lt;10B)</span>
        <span class="badge teal">100% Offline Ready</span>
      </div>
      <span style="font-size:15px;color:#cbd5e1;font-weight:600">OSP · GOPR · TOPR · WOPR · Policja</span>
    </div>
    <h1><b>Sztab-SAR</b> — Taktyczny Koordynator Poszukiwań</h1>
    <p class="lead">Lokalny model <b>Bielik-4.5B (&lt;10B)</b> scala chaotyczne meldunki z radia, 112 i od świadków w jednoznaczne sektory poszukiwań oraz pytania kontrolne — w wozie sztabowym bez dostępu do internetu.</p>
  </div>

  <div class="grid-4">
    <div class="kpi-solid red"><span class="lbl">Praca bez sieci</span><span class="val">100% Offline</span><span class="hint">W lesie i górach bez LTE · zero RODO w chmurze</span></div>
    <div class="kpi-solid blue"><span class="lbl">Silnik Polski</span><span class="val">Bielik-4.5B</span><span class="hint">Q8_0 BPE Fix + opcja Gemma-4-E4B w UI</span></div>
    <div class="kpi-solid teal"><span class="lbl">Skok jakości SLM</span><span class="val">+68.8 pp</span><span class="hint">75.0% koreferencji vs 6.2% w trybie Regex</span></div>
    <div class="kpi-solid slate"><span class="lbl">Kontrola błędów</span><span class="val">0 Halucynacji</span><span class="hint">Deterministyczny audytor godzin i ryzyka</span></div>
  </div>

  <div class="crop-box" style="margin-top:8px">
    <div class="crop-bar"><span>Wycinek 1:1 górnego panelu na żywo · natychmiastowa ocena priorytetów akcji</span><span class="pill-ok">Bory Tucholskie · Bielik-4.5B</span></div>
    <div class="crop-img-wrap" style="padding:0"><img src="{s_kpi}" alt="Pasek KPI Metro UI" style="height:142px;object-fit:contain"></div>
  </div>

  <div class="foot"><span>Demo live: {DEMO_URL}</span><span>Slajd 1 / 7</span></div>
</section>

<!-- SLAJD 2: PROSTA HISTORIA PROBLEMU (DUZY CZYTELNY TEKST) -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge">Problem Terenowy</span><h2>Dlaczego w pierwszych 30 minutach ginie prawdziwy trop?</h2></div>
  </div>
  <div class="grid-2">
    <div class="col" style="justify-content:space-between">
      <div class="tile" style="border-left:5px solid #475569"><h3>Co służby już posiadają</h3><p>Systemy <b>SWD PSP</b> (dysponowanie), <b>SIRON</b> (ślad GPS tyralier), <b>SARUAV</b> (drony) i <b>RATUNEK</b> (GPS telefonu) świetnie obsługują mapy — <b>ale żaden z nich nie analizuje treści zeznań</b>.</p></div>
      <div class="tile accent-amber" style="flex:1;justify-content:center">
        <h3>Co dzieje się naprawdę w sztabie akcji</h3>
        <ul>
          <li>Przez radio i 112 wpada potok sprzecznych relacji od rodziny, świadków i patroli.</li>
          <li>Świadkowie opisują to samo ubranie różnymi słowami (<b>synonimy potoczne</b>).</li>
          <li>Pomyłki godzinowe odciągają pierwsze patrole w zły kwadrat przed zmrokiem.</li>
        </ul>
      </div>
      <div class="kpi-solid red"><span class="lbl">Bariera chmury</span><span class="val" style="font-size:24px">Brak LTE + Dane Medyczne</span><span class="hint">W górach nie ma zasięgu, a wrażliwe dane nie mogą opuszczać wozu sztabowego.</span></div>
    </div>

    <div class="tile accent-blue" style="justify-content:space-between;gap:10px">
      <h3>Żywy przykład pułapki · Scenariusz Bory Tucholskie</h3>
      <div class="msg-card"><b>M1 (13:30 Rodzina):</b> Wyszedł na grzyby, ma cukrzycę bez insuliny. Miał <span class="hl">czerwoną kurtkę pikowaną</span>.</div>
      <div class="msg-card"><b>M2 (14:15 Rowerzysta):</b> Starszy pan w <span class="hl">bordowym anoraku</span> szedł wolno ku rzece Brdzie (sektor A2).</div>
      <div class="msg-card"><b>M3 (Pasażerka PKS):</b> Widziałam pana w czerwonym stroju na przystanku PKS (B2) już o <span class="cf">13:10</span>!</div>
      <div class="tile accent-teal" style="padding:12px 14px">
        <h3>Decyzja Sztab-SAR</h3>
        <p>SLM łączy <b>kurtkę = anorak (M1↔M2)</b>, oznacza fałszywą godzinę <b>13:10 &lt; 13:30</b> i wysyła patrol #1 nad rzekę (<b>A2</b>), nie na przystanek.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Baza porównawcza: scenariusze terenowe OSP / GOPR / Policji</span><span>Slajd 2 / 7</span></div>
</section>

<!-- SLAJD 3: DOWOD SLM VS REGEX (WYCINKI 1:1 BEZ ZMNIEJSZANIA!) -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge teal">Porównanie 1:1</span><h2>Dlaczego bez SLM (&lt;10B) to nie działa: Zbliżenie panelu syntezy</h2></div>
  </div>
  <div class="grid-2">
    <div class="col">
      <div class="crop-box" style="flex:1">
        <div class="crop-bar"><span>1. Tryb SLM · Bielik-4.5B (BPE Fix)</span><span class="pill-ok">Coref 75.0% · F1 75.0%</span></div>
        <div class="crop-img-wrap"><img src="{s_bielik}" alt="Wycinek 1:1 Bielik Synthesys"></div>
      </div>
      <div class="kpi-solid teal" style="padding:11px 15px">
        <span class="hint" style="font-size:15px"><b>Rozumie sens:</b> łączy <i>czerwoną kurtkę pikowaną ↔ bordowy anorak</i> i wykrywa oba konflikty czasu <b>[M1↔M3, M2↔M3]</b>.</span>
      </div>
    </div>
    <div class="col">
      <div class="crop-box" style="flex:1">
        <div class="crop-bar"><span>2. Tryb Bez SLM · Czysty Regex</span><span class="pill-warn">Coref 6.2% · F1 36.4%</span></div>
        <div class="crop-img-wrap"><img src="{s_regex}" alt="Wycinek 1:1 Regex"></div>
      </div>
      <div class="kpi-solid amber" style="padding:11px 15px">
        <span class="hint" style="font-size:15px"><b>Ślepy na synonimy:</b> wypisuje tylko luźne słowa (<i>kurtkę, kalosze, beret, anoraku</i>) — gubi związek M1↔M2 i konflikt M2↔M3.</span>
      </div>
    </div>
  </div>
  <div class="foot"><span>Wycinki 1:1 bezpośrednio z interfejsu Metro UI — bez pomniejszania czcionki</span><span>Slajd 3 / 7</span></div>
</section>

<!-- SLAJD 4: PODSWIETLENIE W TEKSCIE + WORKFLOW DYZURKI -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge blue">Czytelność w terenie</span><h2>Kolumna meldunków 1:1 — system sam zaznacza ślady i konflikty</h2></div>
  </div>
  <div class="grid-2" style="grid-template-columns: 450px 1fr;">
    <div class="crop-box">
      <div class="crop-bar"><span>Wycinek 1:1 · Dziennik meldunków</span><span class="pill-ok">Odmiana PL + Tagi</span></div>
      <div class="crop-img-wrap"><img src="{s_col1}" alt="Wycinek 1:1 kolumny meldunków z podświetleniem"></div>
    </div>
    <div class="col" style="justify-content:space-between">
      <div class="tile accent-teal">
        <h3>1. Automatyczne podświetlanie synonimów w tekście</h3>
        <p>Mimo polskiej odmiany (<i>"czerwoną kurtkę pikowaną"</i> vs <i>"bordowym anoraku"</i>) interfejs natychmiast zaznacza oba tropy w M1 i M2 tym samym turkusowym kolorem — dyspozytor nie musi czytać wszystkiego od zera.</p>
      </div>
      <div class="tile accent-red">
        <h3>2. Jasne znaczniki [KONFLIKT] i [ŚLAD] przy każdym źródle</h3>
        <p>Każde zgłoszenie od razu ma etykietę ostrzegawczą: M3 ze sprzeczną godziną <b>13:10</b> świeci na czerwono jeszcze przed analizą mapy.</p>
      </div>
      <div class="tile accent-blue">
        <h3>3. Dopisywanie nowych zgłoszeń z radia na żywo</h3>
        <p>Gdy patrol lub świadek odpowie na pytanie weryfikacyjne, dyspozytor dopisuje jeden meldunek pod spodem albo wgrywa plik <code>.txt/.log</code>, a cała siatka sektorów A1–C2 przelicza się automatycznie.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Pełna obsługa polskich końcówek deklinacyjnych w podświetleniu na żywo</span><span>Slajd 4 / 7</span></div>
</section>

<!-- SLAJD 5: ARCHITEKTURA BEZ HALUCYNACJI + TATRY ZACHODNIE 1:1 -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge red">0 Halucynacji · GOPR / TOPR</span><h2>Duet SLM + Audytor Python oraz wycinek 1:1 dla Tatr Zachodnich</h2></div>
  </div>
  <div class="grid-2" style="grid-template-columns: 1fr 460px;">
    <div class="col" style="justify-content:space-between">
      <div class="tile accent-blue">
        <h3>Warstwa 1 · Bielik-4.5B (GGUF BPE Fix)</h3>
        <p>Naprawione rangi BPE zapewniają poprawną polską tokenizację. Model grupuje synonimy (<i>"żółta wiatrówka" = "musztardowa kurtka"</i>) i buduje listę pytań weryfikacyjnych dla świadków.</p>
      </div>
      <div class="tile accent-red">
        <h3>Warstwa 2 · Deterministyczny Audytor Python</h3>
        <ul>
          <li><b>Złote okno medyczne:</b> cukrzyca, brak insuliny, uraz, mróz lub bliskość wody sztywno wymuszają właściwy alarm (45m / 90m).</li>
          <li><b>Audytor chronologii i ID:</b> matematycznie wykrywa godziny sprzed wyjścia i odrzuca zmyślone ID.</li>
          <li><b>Gwarancja pytań:</b> jeśli SLM pominie lukę, reguły dogenerują konkretne pytania kontrolne.</li>
        </ul>
      </div>
      <div class="kpi-solid teal" style="padding:12px 16px">
        <span class="lbl">Zweryfikowano na żywo · Tatry Zachodnie</span>
        <span class="hint" style="font-size:15px">Obok prawdziwy wycinek 1:1 kolumny sektorów i checklisty pytań wygenerowanej przez Modal T4.</span>
      </div>
    </div>
    <div class="crop-box">
      <div class="crop-bar"><span>Wycinek 1:1 · Tatry Zachodnie</span><span class="pill-ok">Sektory + Pytania</span></div>
      <div class="crop-img-wrap"><img src="{s_tatry}" alt="Wycinek 1:1 sektory i pytania Tatry Zachodnie"></div>
    </div>
  </div>
  <div class="foot"><span>Scenariusz tatry_hipotermia · widoczne 2 pytania kontrolne z checkboxami poniżej siatki A1–C2</span><span>Slajd 5 / 7</span></div>
</section>

<!-- SLAJD 6: BENCHMARK 16 SCENARIUSZY (CZYTELNE WYKRESY + KPI) -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge amber">Benchmark · 16 Scenariuszy</span><h2>Pomiar na żywo GPU Tesla T4: Regex vs Bielik-4.5B vs Gemma-4-E4B</h2></div>
  </div>
  <div class="grid-2" style="grid-template-columns: 1.15fr 1fr;">
    <div class="col" style="justify-content:space-between">
      {bench_bars}
    </div>
    <div class="col" style="justify-content:space-between">
      <div class="tile" style="padding:14px 16px">
        <h3>Wyniki zbiorcze (<code>bench/eval_report.json</code>)</h3>
        <table>
          <thead><tr><th>System</th><th>Coref</th><th>Konflikty</th><th>Top-1</th><th>Czas</th></tr></thead>
          <tbody>{bench_rows}</tbody>
        </table>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
        <div class="kpi-solid amber" style="padding:12px"><span class="lbl">Regex</span><span class="val" style="font-size:26px">1 ms</span><span class="hint">Ale Coref tylko 6.2%</span></div>
        <div class="kpi-solid blue" style="padding:12px"><span class="lbl">Bielik-4.5B</span><span class="val" style="font-size:26px">15.7 s</span><span class="hint">75.0% Top-1 · 3× szybciej</span></div>
        <div class="kpi-solid teal" style="padding:12px"><span class="lbl">Gemma-4-E4B</span><span class="val" style="font-size:26px">46.3 s</span><span class="hint">Coref 93.8% · cięższy</span></div>
      </div>
      <div class="tile accent-blue" style="padding:14px 16px">
        <h3>Kluczowy wniosek</h3>
        <p><b>Bielik-4.5B</b> daje skok koreferencji o <b>+68.8 pp</b> względem Regex, najwyższą celność sektora Top-1 (<b>75.0% vs 62.5%</b> dla Gemma) i działa <b>3× szybciej</b> w realiach sztabowych.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Odtwarzalny skrypt benchmarku: python bench/run_bench.py · 16 scenariuszy terenowych</span><span>Slajd 6 / 7</span></div>
</section>

<!-- SLAJD 7: EKSPORT ROZKAZU + LINKI + INSTALATOR -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge blue">Wdrożenie &amp; Weryfikacja</span><h2>Gotowy Rozkaz Poszukiwawczy (.html), instalator offline i linki live</h2></div>
  </div>
  <div class="grid-2" style="grid-template-columns: 1.15fr 1fr;">
    <div class="crop-box">
      <div class="crop-bar"><span>Eksport jednym kliknięciem · Rozkaz dla patroli</span><span class="pill-blue">Druk / PDF</span></div>
      <div class="crop-img-wrap white"><img src="{s_rozkaz}" alt="Karta Poszukiwań i Rozkaz Operacyjny"></div>
    </div>
    <div class="col" style="justify-content:space-between">
      <div class="tile accent-teal">
        <h3>1. Publiczne Demo Live (Modal T4 GPU)</h3>
        <p>Interfejs Metro UI bez logowania, przełącznik <b>Bielik-4.5B / Gemma-4-E4B / Bez SLM (Regex)</b> i eksport Rozkazu:</p>
        <p style="font-size:15px;word-break:break-all"><a href="{DEMO_URL}">{DEMO_URL}</a></p>
      </div>
      <div class="tile accent-blue">
        <h3>2. GitHub, Testy i Instalator Offline</h3>
        <p>Automatyczny <code>install.bat</code> (pobiera <code>llama.cpp</code> Vulkan/CPU + weryfikuje SHA-256 wag Bielika), konfiguracja w <code>%LOCALAPPDATA%\\SztabSAR</code> oraz 5 testów jednostkowych.</p>
        <p style="font-size:15px;word-break:break-all"><a href="{GITHUB_URL}">{GITHUB_URL}</a></p>
      </div>
      <div class="kpi-solid slate" style="padding:13px 16px">
        <span class="lbl">Zgodność Bielik Awards 2026</span>
        <span class="hint" style="font-size:15px">Model <b>Bielik-4.5B (&lt;10B)</b> · Licencja MIT · 100% offline bez telemetrii.</span>
      </div>
    </div>
  </div>
  <div class="foot"><span>Bielik Awards 2026 · Projekt Sztab-SAR</span><span>Slajd 7 / 7</span></div>
</section>

</body>
</html>"""


def main() -> None:
    HTML_PATH.write_text(build_html(), encoding="utf-8")
    subprocess.run(
        [
            str(BRAVE),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_PATH}",
            HTML_PATH.as_uri(),
        ],
        check=True,
    )
    print(f"Wygenerowano {PDF_PATH} ({PDF_PATH.stat().st_size} bajtow)")


if __name__ == "__main__":
    main()
