"""Generuje 7-slajdowa prezentacje PDF w stylu Windows Metro UI (16:9) dla Sztab-SAR."""
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
    data = json.loads(BENCH_PATH.read_text(encoding="utf-8"))
    return data.get("results", [])


def build_bench_bars(results: list[dict]) -> str:
    if not results:
        return "<div class='tile'>Brak danych bench/eval_report.json</div>"
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
        return "<tr><td colspan='6'>Brak bench/eval_report.json</td></tr>"
    out = []
    for idx, r in enumerate(results):
        cls = "hi-row" if "Bielik" in r["system"] else ""
        lat = f"{r['avg_latency_ms']} ms" if r["avg_latency_ms"] < 1000 else f"{r['avg_latency_ms']/1000:.1f} s"
        out.append(
            f"<tr class='{cls}'>"
            f"<td><b>{html.escape(r['system'])}</b></td>"
            f"<td><b>{r['coreference_acc']*100:.1f}%</b></td>"
            f"<td><b>{r['conflict_f1']*100:.1f}%</b></td>"
            f"<td>{r['sector_top1_acc']*100:.1f}%</td>"
            f"<td>{r['medical_risk_acc']*100:.1f}%</td>"
            f"<td>{lat}</td>"
            f"</tr>"
        )
    return "\n".join(out)


def build_html() -> str:
    results = load_bench_data()
    bench_bars = build_bench_bars(results)
    bench_rows = build_bench_rows(results)
    s_bory = img_uri("screen_bory.png")
    s_tatry = img_uri("screen_tatry.png")
    s_regex = img_uri("screen_regex.png")
    s_rozkaz = img_uri("screen_rozkaz.png")

    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Sztab-SAR — Prezentacja Konkursowa</title>
<style>
@page {{ size: 1280px 720px; margin: 0; }}
* {{ box-sizing: border-box; border-radius: 0 !important; }}
body {{
  margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
  background: #0b0e14; color: #f3f6fb;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}}
.slide {{
  width: 1280px; height: 720px; padding: 28px 40px 44px; position: relative;
  overflow: hidden; page-break-after: always; display: flex; flex-direction: column;
  background: #0b0e14;
}}
.slide:last-child {{ page-break-after: auto; }}
.hdr {{
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  border-bottom: 2px solid #222b3a; padding-bottom: 9px; margin-bottom: 14px; flex-shrink: 0;
}}
.hdr-left {{ display: flex; align-items: center; gap: 12px; min-width: 0; }}
.badge {{
  background: #b91c1c; color: #fff; font-size: 11px; font-weight: 700;
  letter-spacing: .07em; padding: 5px 10px; text-transform: uppercase; white-space: nowrap; flex-shrink: 0;
}}
.badge.blue {{ background: #0078d4; }}
.badge.teal {{ background: #008272; }}
.badge.amber {{ background: #c2410c; }}
h1 {{ font-size: 40px; font-weight: 300; line-height: 1.08; margin: 0 0 10px; letter-spacing: -0.02em; }}
h1 b {{ font-weight: 700; color: #fff; }}
h2 {{ font-size: 22px; font-weight: 600; margin: 0; color: #fff; letter-spacing: -0.01em; }}
.subline {{ font-size: 12px; color: #9aa7bd; text-align: right; flex-shrink: 0; max-width: 340px; }}
p.lead {{ font-size: 15px; color: #c7d1e0; line-height: 1.45; margin: 0 0 14px; }}

.tile {{
  background: #141923; border: 1px solid #263042; padding: 13px 15px;
  display: flex; flex-direction: column; gap: 6px;
}}
.tile.accent-red {{ border-left: 4px solid #dc2626; background: #1d1216; }}
.tile.accent-blue {{ border-left: 4px solid #0078d4; background: #101b29; }}
.tile.accent-teal {{ border-left: 4px solid #008272; background: #0f1e1d; }}
.tile.accent-amber {{ border-left: 4px solid #d97706; background: #1e1810; }}
.tile h3 {{ margin: 0; font-size: 14px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: .04em; }}
.tile p, .tile li {{ margin: 0; font-size: 13px; color: #c0cad8; line-height: 1.42; }}
.tile ul {{ margin: 2px 0 0 16px; padding: 0; display: flex; flex-direction: column; gap: 5px; }}

.kpi-solid {{ padding: 11px 13px; color: #fff; display: flex; flex-direction: column; gap: 3px; }}
.kpi-solid.red {{ background: #b91c1c; }}
.kpi-solid.blue {{ background: #0078d4; }}
.kpi-solid.teal {{ background: #008272; }}
.kpi-solid.slate {{ background: #1e293b; border: 1px solid #334155; }}
.kpi-solid .lbl {{ font-size: 10px; font-weight: 700; letter-spacing: .08em; opacity: .9; text-transform: uppercase; }}
.kpi-solid .val {{ font-size: 21px; font-weight: 700; line-height: 1.1; }}
.kpi-solid .hint {{ font-size: 11px; opacity: .9; line-height: 1.3; }}

.screen-frame {{
  border: 2px solid #2b374b; background: #090c10; position: relative;
  display: flex; flex-direction: column; overflow: hidden; min-height: 0; height: 100%;
}}
.screen-cap {{
  background: #1b2434; color: #dbe5f4; font-size: 11px; font-weight: 700;
  letter-spacing: .05em; padding: 6px 10px; text-transform: uppercase;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid #2b374b; flex-shrink: 0;
}}
.screen-cap .tag-ok {{ background: #008272; color: #fff; padding: 2px 7px; font-size: 10px; }}
.screen-cap .tag-warn {{ background: #c2410c; color: #fff; padding: 2px 7px; font-size: 10px; }}
.screen-cap .tag-blue {{ background: #0078d4; color: #fff; padding: 2px 7px; font-size: 10px; }}
.screen-frame img {{ width: 100%; flex: 1; min-height: 0; display: block; object-fit: contain; object-position: top center; }}

.grid-hero {{ display: grid; grid-template-columns: 430px 1fr; grid-template-rows: minmax(0, 1fr); gap: 18px; flex: 1; min-height: 0; align-items: stretch; }}
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: minmax(0, 1fr); gap: 16px; flex: 1; min-height: 0; }}
.grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; flex-shrink: 0; }}
.grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; flex-shrink: 0; }}
.col {{ display: flex; flex-direction: column; gap: 10px; min-height: 0; }}

.msg-mini {{
  background: #10151e; border: 1px solid #263042; border-left: 4px solid #dc2626;
  padding: 10px 12px; font-size: 13px; color: #dbe5f4; line-height: 1.42;
}}
.msg-mini b {{ color: #fff; }}
.hl {{ background: #005b4f; color: #ccfbf1; padding: 0 3px; font-weight: 600; }}
.cf {{ background: #7f1d1d; color: #fecaca; padding: 0 4px; font-weight: 700; font-size: 11px; }}

.metric-group {{ background: #141923; border: 1px solid #263042; padding: 10px 12px; }}
.mg-title {{ font-size: 12px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px; }}
.bar-row {{ display: grid; grid-template-columns: 132px 1fr 48px; align-items: center; gap: 8px; margin-bottom: 4px; }}
.bar-row:last-child {{ margin-bottom: 0; }}
.bar-lbl {{ font-size: 11px; color: #c0cad8; }}
.bar-track {{ height: 11px; background: #0a0d12; border: 1px solid #222b3a; }}
.bar-fill {{ height: 100%; }}
.bar-val {{ font-size: 11px; font-weight: 700; color: #fff; text-align: right; }}

table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th, td {{ border: 1px solid #263042; padding: 7px 9px; text-align: left; }}
th {{ background: #1a2230; color: #dbe5f4; font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }}
tr.hi-row td {{ background: #102033; color: #fff; }}

.flow-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
.flow-box {{
  background: #141923; border: 1px solid #263042; border-top: 3px solid #0078d4;
  padding: 10px 12px;
}}
.flow-box.red {{ border-top-color: #dc2626; }}
.flow-box.teal {{ border-top-color: #008272; }}
.flow-box.amber {{ border-top-color: #d97706; }}
.flow-step {{ font-size: 10px; font-weight: 700; color: #60a5fa; letter-spacing: .08em; text-transform: uppercase; }}
.flow-box.red .flow-step {{ color: #f87171; }}
.flow-box.teal .flow-step {{ color: #2dd4bf; }}
.flow-box.amber .flow-step {{ color: #fbbf24; }}
.flow-title {{ font-size: 14px; font-weight: 700; color: #fff; margin: 3px 0 5px; }}
.flow-desc {{ font-size: 12px; color: #c0cad8; line-height: 1.38; }}

.foot {{
  position: absolute; bottom: 14px; left: 40px; right: 40px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px; color: #7e8ba3; border-top: 1px solid #1d2533; padding-top: 7px;
}}
a {{ color: #60a5fa; text-decoration: none; font-weight: 600; }}
code {{ background: #1c2432; color: #93c5fd; padding: 1px 5px; font-size: 11px; }}
</style>
</head>
<body>

<!-- SLAJD 1: HERO + PRAWDZIWY ZRZUT UI -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left">
      <span class="badge">Bielik Awards 2026</span>
      <span class="badge blue">Kategoria SLM (&lt;10B)</span>
      <span class="badge teal">100% Offline Ready</span>
    </div>
    <span class="subline">Koordynator Poszukiwań dla OSP · GOPR · WOPR · Policji</span>
  </div>
  <div class="grid-hero">
    <div class="col" style="justify-content:space-between">
      <div>
        <h1><b>Sztab-SAR</b><br>Taktyczny Koordynator<br>Poszukiwań Offline</h1>
        <p class="lead">Pierwszy lokalny system SLM (&lt;10B) scalający chaotyczne meldunki radiowe, zgłoszenia 112 i zeznania świadków podczas akcji w lesie i górach — bez chmury i bez zasięgu LTE.</p>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div class="kpi-solid red"><span class="lbl">Zasięg / Prywatność</span><span class="val">100% Offline</span><span class="hint">Wóz sztabowy bez LTE · zero RODO w chmurze</span></div>
        <div class="kpi-solid blue"><span class="lbl">Model Językowy</span><span class="val">Bielik-4.5B</span><span class="hint">Q8_0 BPE Fix + opcja Gemma-4-E4B</span></div>
        <div class="kpi-solid teal"><span class="lbl">Koreferencja &amp; Czas</span><span class="val">+68.8 pp</span><span class="hint">75.0% vs 6.2% regex w testach terenowych</span></div>
        <div class="kpi-solid slate"><span class="lbl">Bezpieczeństwo</span><span class="val">0 Halucynacji</span><span class="hint">Deterministyczny audytor ID i medyczny</span></div>
      </div>
      <div class="tile accent-blue">
        <h3>Co rozwiązuje na żywo</h3>
        <p>Łączy różne opisy tego samego obiektu (np. <i>"czerwona kurtka" ↔ "bordowy anorak"</i>), wyłapuje kolizje godzin i wyprowadza gotowe sektory A1–C2 + pytania dla dyspozytora.</p>
      </div>
    </div>
    <div class="screen-frame" style="justify-content:flex-start">
      <div class="screen-cap">
        <span>Widok Live Metro UI · Scenariusz: Bory Tucholskie</span>
        <span class="tag-ok">Bielik-4.5B · Modal T4 GPU</span>
      </div>
      <img src="{s_bory}" alt="Sztab-SAR Metro UI Bory Tucholskie">
    </div>
  </div>
  <div class="foot"><span>Demo live: {DEMO_URL}</span><span>Slajd 1 / 7</span></div>
</section>

<!-- SLAJD 2: LUKA W SLUZBACH + KONKRETNY PRZEPLYW DANYCH -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge">Problem Terenowy</span><h2>Luka między potokiem meldunków a mapami SWD PSP / SIRON / SARUAV</h2></div>
    <span class="subline">Dlaczego istniejące systemy nie analizują sprzecznych zeznań</span>
  </div>
  <div class="grid-4" style="margin-bottom:12px">
    <div class="tile"><h3>SWD PSP / MAPA ST3</h3><p>Dysponowanie zastępów, kartoteka zdarzeń i podkład mapowy — nie analizuje treści zeznań.</p></div>
    <div class="tile"><h3>SIRON</h3><p>Śledzenie GPS tyralier i statusów przeszukanych sektorów — wymaga ręcznego wyboru celu.</p></div>
    <div class="tile"><h3>SARUAV</h3><p>Detekcja sylwetek na zdjęciach z dronów — nie weryfikuje kolizji relacji świadków na ziemi.</p></div>
    <div class="tile"><h3>Aplikacja RATUNEK</h3><p>Przesyła punkt GPS dzwoniącego — nie działa, gdy zaginiony nie ma telefonu lub zasięgu.</p></div>
  </div>
  <div class="grid-2">
    <div class="tile accent-red" style="gap:10px;justify-content:space-between">
      <h3>Wejście: pierwsze 30 minut chaosu na dyżurce / w wozie sztabowym</h3>
      <div class="msg-mini"><b>M1 · 14:40 Rodzina:</b> Wyszedł ok. <b>13:30</b> na grzyby. Cukrzyca typu 1, bez insuliny. Miał <span class="hl">czerwoną kurtkę pikowaną</span>.</div>
      <div class="msg-mini"><b>M2 · 14:52 Rowerzysta:</b> O 14:15 widziałem starszego pana w <span class="hl">bordowym anoraku</span> przy leśniczówce Dębina (B1), szedł ku Brdzie (A2).</div>
      <div class="msg-mini"><b>M3 · 14:58 Pasażerka PKS:</b> Widziałam pana w czerwonym stroju na przystanku PKS (B2) już o <span class="cf">13:10</span>!</div>
      <div class="msg-mini" style="border-left-color:#0078d4"><b>M4 · 15:05 Patrol OSP-2:</b> Przy ambonie nr 4 (A1) porzucony koszyk i świeże ślady butów schodzące do rozlewiska Brdy (A2).</div>
      <div class="kpi-solid slate" style="padding:8px 11px"><span class="lbl">Zagrożenie poznawcze dyspozytora</span><span class="hint">4 źródła na minutę: bez SLM łatwo skierować patrol do B2 na podstawie fałszywego tropu o 13:10.</span></div>
    </div>
    <div class="col">
      <div class="tile accent-teal" style="flex:1">
        <h3>Wyjście Sztab-SAR po 1 kliknięciu (offline):</h3>
        <ul>
          <li><b>Koreferencja M1 ↔ M2:</b> SLM łączy <i>"czerwoną kurtkę pikowaną"</i> z <i>"bordowym anorakiem"</i> jako jedną ścieżkę tropu.</li>
          <li><b>Detekcja kolizji czasu [M1 ↔ M3]:</b> Obserwacja o <b>13:10</b> wyprzedza wyjście z domu o <b>13:30</b> — fałszywy trop na przystanek B2 zostaje oznaczony do weryfikacji.</li>
          <li><b>Priorytet A2 (Rozlewisko Brdy):</b> Złote okno medyczne <b>45 min (ALARM KRYTYCZNY)</b> przez cukrzycę typu 1 + zejście śladów nad wodę.</li>
        </ul>
      </div>
      <div class="tile accent-amber">
        <h3>Dlaczego chmura API odpada w akcji SAR</h3>
        <p>Brak stabilnego LTE w głębokim lesie i Tatrach oraz zakaz przesyłania wrażliwych danych zdrowotnych i operacyjnych na zewnętrzne serwery.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Źródło scenariusza: wbudowany przypadek operacyjny bory_senior</span><span>Slajd 2 / 7</span></div>
</section>

<!-- SLAJD 3: POROWNANIE NA ZYWO SLM VS REGEX -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge teal">Dowód Konieczności SLM</span><h2>Porównanie na żywo: Lokalny SLM (Bielik-4.5B) vs Tryb Bez SLM (Regex)</h2></div>
    <span class="subline">Ten sam zestaw meldunków M1–M4 przetworzony w tym samym interfejsie</span>
  </div>
  <div class="grid-2" style="align-items:stretch">
    <div class="col">
      <div class="screen-frame">
        <div class="screen-cap"><span>1. Tryb SLM · Bielik-4.5B (BPE Fix)</span><span class="tag-ok">Semantyka + Koreferencja</span></div>
        <img src="{s_bory}" alt="Tryb SLM Bielik">
      </div>
      <div class="tile accent-teal">
        <h3>Co widzi Bielik-4.5B</h3>
        <p>Łączy <b>"czerwoną kurtkę" ↔ "bordowym anoraku"</b> (podświetlenie inline w M1 i M2), wykrywa oba konflikty czasu <b>[M1↔M3, M2↔M3]</b> i generuje <b>3 pytania weryfikacyjne</b> dla dyspozytora.</p>
      </div>
    </div>
    <div class="col">
      <div class="screen-frame">
        <div class="screen-cap"><span>2. Tryb Bez SLM · Czysty Regex / Słownik</span><span class="tag-warn">Tylko dosłowne tokeny</span></div>
        <img src="{s_regex}" alt="Tryb Bez SLM Regex">
      </div>
      <div class="tile accent-amber">
        <h3>Gdzie Regex ponosi klęskę</h3>
        <p>Wypisuje puste słowa kluczowe (<i>kurtkę, kalosze, beret, anoraku</i>) bez żadnego powiązania znaczeniowego (<b>Coref 6.2%</b>), gubi konflikt narracji <b>M2↔M3</b> i nie potrafi sformułować pytań do świadków.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Różnica w praktyce: dyspozytor od razu widzi, które zeznania mówią o tym samym ubraniu</span><span>Slajd 3 / 7</span></div>
</section>

<!-- SLAJD 4: ARCHITEKTURA NEURO-SYMBOLICZNA + EKSPORT ROZKAZU -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge blue">Architektura Hybrydowa</span><h2>Duet Neuro-Symboliczny: Semantyka SLM + Deterministyczny Audytor</h2></div>
    <span class="subline">Zero halucynacji w alarmach medycznych, godzinach i identyfikatorach meldunków</span>
  </div>
  <div class="flow-4" style="margin-bottom:14px">
    <div class="flow-box">
      <div class="flow-step">Krok 1 · Wejście</div>
      <div class="flow-title">Dziennik M1..Mn</div>
      <div class="flow-desc">Meldunki z radia, 112 i pliki <code>.txt/.log</code> plus dopisywanie nowych tropów na żywo.</div>
    </div>
    <div class="flow-box teal">
      <div class="flow-step">Krok 2 · Warstwa SLM</div>
      <div class="flow-title">Bielik-4.5B / Gemma-4</div>
      <div class="flow-desc">Ekstrakcja JSON: profil, klastry synonimów, oś czasu, sprzeczności i luki wywiadu.</div>
    </div>
    <div class="flow-box red">
      <div class="flow-step">Krok 3 · Audytor Python</div>
      <div class="flow-title">Twarde Reguły SAR</div>
      <div class="flow-desc">Scoring złotego okna, kontrola chronologii <code>wyjście vs świadek</code>, walidacja ID M1..Mn.</div>
    </div>
    <div class="flow-box amber">
      <div class="flow-step">Krok 4 · Decyzja</div>
      <div class="flow-title">Siatka A1–C2 + Rozkaz</div>
      <div class="flow-desc">Priorytety sektorów, lista pytań z checkboxami i wydruk Karty Poszukiwań (.html).</div>
    </div>
  </div>
  <div class="grid-hero" style="grid-template-columns: 450px 1fr;">
    <div class="col">
      <div class="tile accent-blue" style="flex:1">
        <h3>Warstwa 1: Naprawiony Bielik-4.5B GGUF</h3>
        <ul>
          <li>Korekta rang BPE w pliku GGUF eliminuje błędną tokenizację polskich końcówek.</li>
          <li>Schemat JSON ustawia <code>pytania_do_swiadkow</code> przed listą sektorów przy limicie 680 tokenów — brak uciętych pytań.</li>
          <li>Przełącznik w UI pozwala porównać Bielik-4.5B z Gemma-4-E4B-it.</li>
        </ul>
      </div>
      <div class="tile accent-red" style="flex:1">
        <h3>Warstwa 2: Deterministyczny Audytor (<code>sar/rules.py</code>)</h3>
        <ul>
          <li><b>Ryzyko medyczne:</b> cukrzyca, brak insuliny, Alzheimer, dziecko, mróz i woda zawsze wymuszają właściwy alarm (45m / 90m).</li>
          <li><b>Chronologia i ID:</b> filtruje halucynowane ID i dogenerowuje pytania weryfikacyjne przy &lt;2 pytaniach z SLM.</li>
        </ul>
      </div>
    </div>
    <div class="screen-frame" style="background:#fff">
      <div class="screen-cap"><span>Wyjście do patroli · Karta Poszukiwań i Rozkaz (.html)</span><span class="tag-blue">Gotowe do druku / PDF</span></div>
      <img src="{s_rozkaz}" alt="Eksport Rozkazu Poszukiwawczego">
    </div>
  </div>
  <div class="foot"><span>Kod: sar/slm_extract.py + sar/rules.py + sar/pipeline.py</span><span>Slajd 4 / 7</span></div>
</section>

<!-- SLAJD 5: BENCHMARK 16 SCENARIUSZY (WYKRESY + TABELA) -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge amber">Uczciwy Benchmark · 16 Scenariuszy</span><h2>Regex vs Bielik-4.5B (BPE Fix) vs Gemma-4-E4B-it na Modal T4</h2></div>
    <span class="subline">16 realistycznych spraw (lasy, góry, woda, dzieci, seniorzy) · dane z bench/eval_report.json</span>
  </div>
  <div class="grid-hero" style="grid-template-columns: 1.15fr 1fr;">
    <div class="col" style="gap:9px">
      {bench_bars}
    </div>
    <div class="col" style="justify-content:space-between">
      <div class="tile" style="padding:10px 12px">
        <h3>Zestawienie zmierzonych wyników (GPU Tesla T4)</h3>
        <table>
          <thead>
            <tr><th>System</th><th>Coref</th><th>Konflikty</th><th>Top-1</th><th>Ryzyko</th><th>Czas</th></tr>
          </thead>
          <tbody>
            {bench_rows}
          </tbody>
        </table>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">
        <div class="kpi-solid amber" style="background:#9a3412"><span class="lbl">Regex Baseline</span><span class="val">1 ms</span><span class="hint">Szybki, ale Coref 6.2%</span></div>
        <div class="kpi-solid blue"><span class="lbl">Bielik-4.5B BPE</span><span class="val">15.7 s</span><span class="hint">Top-1 75.0% · 3× szybciej</span></div>
        <div class="kpi-solid teal"><span class="lbl">Gemma-4-E4B-it</span><span class="val">46.3 s</span><span class="hint">Coref 93.8% · cięższy</span></div>
      </div>
      <div class="tile accent-blue">
        <h3>Dlaczego Bielik-4.5B to optymalny punkt równowagi</h3>
        <ul>
          <li><b>+68.8 pp koreferencji</b> (75.0% vs 6.2% Regex) i <b>+38.6 pp Conflict F1</b> (75.0% vs 36.4%).</li>
          <li><b>3× szybszy od Gemma-4-E4B:</b> 15.7 s vs 46.3 s na GPU T4 przy wyższej celności sektora Top-1 (<b>75.0% vs 62.5%</b>).</li>
          <li><b>75.0% trafności ryzyka medycznego</b> w twardej bazie porównawczej dzięki warstwie symbolicznej we wszystkich konfiguracjach.</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="foot"><span>Odtworzenie testu: python bench/run_bench.py · pełny raport w bench/eval_report.json</span><span>Slajd 5 / 7</span></div>
</section>

<!-- SLAJD 6: DRUGI SCENARIUSZ TATRY + WORKFLOW DYŻURKI -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge red">Scenariusz Górski · GOPR / TOPR</span><h2>Tatry Zachodnie: Turysta we mgle i automatyczna weryfikacja tropów</h2></div>
    <span class="subline">Koreferencja "żółta wiatrówka / musztardowa kurtka", kolizja 14:40 vs 14:15 oraz pytania dyspozytora</span>
  </div>
  <div class="grid-hero" style="grid-template-columns: 1.55fr 1fr;">
    <div class="screen-frame">
      <div class="screen-cap"><span>Metro UI · Tatry Zachodnie — wszystkie 3 sekcje + pytania kontrolne</span><span class="tag-ok">Pytania zweryfikowane live</span></div>
      <img src="{s_tatry}" alt="Sztab-SAR Tatry Zachodnie">
    </div>
    <div class="col" style="justify-content:space-between">
      <div class="tile accent-red">
        <h3>Co dzieje się na tym ekranie</h3>
        <ul>
          <li><b>Kolizja M2 ↔ M3:</b> Turyści mijali poszkodowanego pod Rakoniem o 14:40, a telefon anonimowy twierdzi, że zszedł już na Polanę Chochołowską o 14:15.</li>
          <li><b>Sektor A2 (Grzbiet Grzesia) #1:</b> Ślady ześlizgnięcia w śniegu i urwany pasek od ciemnego plecaka spięte z opisem w M2 i M4.</li>
          <li><b>Checklista dyspozytora:</b> Od razu gotowe pytania do turystów z Warszawy i obsługi schroniska.</li>
        </ul>
      </div>
      <div class="tile accent-teal">
        <h3>Praca w wozie sztabowym krok po kroku</h3>
        <ul>
          <li><b>1.</b> Wgraj plik <code>.txt/.log</code> lub wybierz meldunki z radia.</li>
          <li><b>2.</b> Kliknij <b>Analizuj sytuację</b> (działa 100% lokalnie).</li>
          <li><b>3.</b> Dopisz odpowiedź świadka w <b>Nowy meldunek</b> — sektory przeliczą się natychmiast.</li>
          <li><b>4.</b> Pobierz <b>Rozkaz (.html)</b> do wydruku dla patroli.</li>
        </ul>
      </div>
      <div class="tile">
        <h3>Instalator Desktopowy (<code>install.bat</code>)</h3>
        <p>Jedno uruchomienie pobiera <code>llama.cpp</code> (Vulkan GPU / CPU), weryfikuje SHA-256 wag Bielik-4.5B i zapisuje config w <code>%LOCALAPPDATA%\\SztabSAR</code>.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Nowy interfejs Metro UI eliminuje zbędne zaokrąglenia i grupuje kluczowe decyzje w 3 czytelnych kolumnach</span><span>Slajd 6 / 7</span></div>
</section>

<!-- SLAJD 7: LINKI LIVE + ARCHIWUM PROJEKTU + PODSUMOWANIE -->
<section class="slide">
  <div class="hdr">
    <div class="hdr-left"><span class="badge blue">Weryfikacja &amp; Kod Źródłowy</span><h2>Sprawdź działające demo na żywo, kod i powtarzalne testy</h2></div>
    <span class="subline">Licencja MIT · Brak telemetrii · Gotowe do pracy na Windows / Linux / Modal</span>
  </div>
  <div class="grid-3" style="margin-bottom:14px">
    <div class="tile accent-teal">
      <h3>1. Publiczne Demo Live (Modal T4)</h3>
      <p>Pełny interfejs Metro UI dostępny od razu w przeglądarce bez logowania. Wbudowany przełącznik <b>Bielik-4.5B / Gemma-4-E4B / Bez SLM (Regex)</b> oraz eksport Rozkazu.</p>
      <p style="word-break:break-all;margin-top:6px"><a href="{DEMO_URL}">{DEMO_URL}</a></p>
      <p style="margin-top:4px;font-size:12px">Prezentacja PDF online: <code>/prezentacja.pdf</code></p>
    </div>
    <div class="tile accent-blue">
      <h3>2. Repozytorium GitHub</h3>
      <p>Kompletny kod serwera lokalnego (<code>app.py</code>), silnika SLM/reguł (<code>sar/</code>), 16 scenariuszy benchmarku (<code>bench/run_bench.py</code>), testów jednostkowych (<code>tests/</code>) i <code>install.bat</code>.</p>
      <p style="word-break:break-all;margin-top:6px"><a href="{GITHUB_URL}">{GITHUB_URL}</a></p>
    </div>
    <div class="tile accent-red">
      <h3>3. Zgodność z Bielik Awards 2026</h3>
      <ul>
        <li><b>Model bazowy:</b> Bielik-4.5B-v3.0-Instruct Q8_0 (naprawione rangi BPE), poniżej limitu &lt;10B.</li>
        <li><b>Uzasadnienie SLM:</b> udowodniona przepaść +68.8 pp koreferencji względem regex.</li>
        <li><b>Bezpieczeństwo:</b> twardy audytor chronologii i ryzyka medycznego.</li>
      </ul>
    </div>
  </div>
  <div class="grid-2" style="flex:1">
    <div class="screen-frame">
      <div class="screen-cap"><span>Metro UI · Gotowy panel koordynatora akcji</span><span class="tag-ok">Zweryfikowane live</span></div>
      <img src="{s_bory}" alt="Podgląd UI">
    </div>
    <div class="screen-frame" style="background:#fff">
      <div class="screen-cap"><span>Wydruk dla patroli · Rozkaz_Poszukiwawczy_Sztab_SAR.html</span><span class="tag-blue">Eksport 1 kliknięciem</span></div>
      <img src="{s_rozkaz}" alt="Podgląd Rozkazu">
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
