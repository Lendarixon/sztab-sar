"""Generuje czystą, minimalistyczną prezentację PDF (16:9) dla Sztab-SAR."""
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
        return "<p>Brak danych bench/eval_report.json</p>"
    metrics = [
        ("Koreferencja synonimów", "coreference_acc"),
        ("Detekcja konfliktów (F1)", "conflict_f1"),
        ("Priorytet sektora Top-1", "sector_top1_acc"),
        ("Klasyfikacja ryzyka med.", "medical_risk_acc"),
    ]
    colors = ["#94a3b8", "#0067b8", "#1e293b"]
    blocks = []
    for title, key in metrics:
        rows = []
        for idx, r in enumerate(results):
            val = float(r.get(key, 0.0)) * 100.0
            col = colors[idx % len(colors)]
            short = (
                "Regex (bez SLM)" if "Regex" in r["system"]
                else ("Bielik-4.5B BPE Fix" if "Bielik" in r["system"] else "Gemma-4-E4B-it")
            )
            fw = "700" if "Bielik" in r["system"] else "500"
            rows.append(
                f"<div class='bar-row'>"
                f"<span class='bar-lbl' style='font-weight:{fw}'>{html.escape(short)}</span>"
                f"<div class='bar-track'><div class='bar-fill' style='width:{val:.1f}%;background:{col}'></div></div>"
                f"<span class='bar-val' style='font-weight:{fw}'>{val:.1f}%</span>"
                f"</div>"
            )
        blocks.append(f"<div class='m-block'><div class='m-title'>{title}</div>{''.join(rows)}</div>")
    return "".join(blocks)


def build_bench_rows(results: list[dict]) -> str:
    if not results:
        return ""
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
            f"<td>{html.escape(short)}</td>"
            f"<td>{r['coreference_acc']*100:.1f}%</td>"
            f"<td>{r['conflict_f1']*100:.1f}%</td>"
            f"<td>{r['sector_top1_acc']*100:.1f}%</td>"
            f"<td>{lat}</td>"
            f"</tr>"
        )
    return "\n".join(out)


def build_html() -> str:
    results = load_bench_data()
    bench_bars = build_bench_bars(results)
    bench_rows = build_bench_rows(results)

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
* {{ box-sizing: border-box; }}
body {{
  margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
  background: #f8fafc; color: #0f172a;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}}
.slide {{
  width: 1280px; height: 720px; padding: 48px 64px 54px; position: relative;
  overflow: hidden; page-break-after: always; display: flex; flex-direction: column;
  background: #f8fafc;
}}
.slide:last-child {{ page-break-after: auto; }}

.eyebrow {{
  font-size: 13px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
  color: #0067b8; margin-bottom: 12px;
}}
h1 {{ font-size: 68px; font-weight: 700; line-height: 1.02; margin: 0 0 18px; letter-spacing: -0.03em; color: #0f172a; }}
h2 {{ font-size: 32px; font-weight: 700; line-height: 1.15; margin: 0 0 26px; letter-spacing: -0.02em; color: #0f172a; }}
h3 {{ font-size: 18px; font-weight: 700; margin: 0 0 8px; color: #0f172a; }}
p {{ margin: 0; font-size: 18px; line-height: 1.5; color: #334155; }}
.lead {{ font-size: 23px; line-height: 1.45; color: #334155; max-width: 920px; }}

.cols-2 {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: minmax(0, 1fr); gap: 44px; flex: 1; min-height: 0; }}
.cols-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 28px; border-top: 2px solid #e2e8f0; padding-top: 24px; }}
.stat-num {{ font-size: 36px; font-weight: 700; color: #0f172a; line-height: 1.1; margin-bottom: 6px; }}
.stat-num.accent {{ color: #0067b8; }}
.stat-lbl {{ font-size: 15px; color: #475569; line-height: 1.4; }}

.stack {{ display: flex; flex-direction: column; gap: 22px; min-height: 0; }}
.sep {{ border-top: 1px solid #cbd5e1; padding-top: 18px; }}

.quote-row {{
  border-left: 3px solid #0067b8; padding: 6px 0 6px 16px;
  font-size: 17px; line-height: 1.45; color: #1e293b;
}}
.quote-row.muted {{ border-left-color: #cbd5e1; color: #475569; }}
.num-item {{ display: flex; gap: 16px; align-items: flex-start; }}
.num-tag {{ font-size: 20px; font-weight: 700; color: #0067b8; line-height: 1.2; flex-shrink: 0; width: 30px; }}

.shot-col {{ display: flex; flex-direction: column; gap: 10px; min-height: 0; height: 100%; }}
.shot-cap {{ font-size: 16px; font-weight: 700; color: #0f172a; }}
.shot-cap span {{ font-weight: 500; color: #475569; margin-left: 8px; }}
.shot-wrap {{
  flex: 1; min-height: 0; display: flex; justify-content: flex-start; align-items: flex-start; overflow: hidden;
}}
.shot-wrap img {{ width: auto; max-width: 100%; height: 100%; object-fit: contain; object-position: top left; display: block; border: 1px solid #cbd5e1; }}
.shot-wrap.light img {{ width: 100%; height: auto; max-height: 100%; }}

.m-block {{ padding-bottom: 14px; border-bottom: 1px solid #e2e8f0; }}
.m-block:last-child {{ border-bottom: none; padding-bottom: 0; }}
.m-title {{ font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 8px; }}
.bar-row {{ display: grid; grid-template-columns: 160px 1fr 56px; align-items: center; gap: 12px; margin-bottom: 5px; }}
.bar-lbl {{ font-size: 14px; color: #334155; }}
.bar-track {{ height: 12px; background: #e2e8f0; }}
.bar-fill {{ height: 100%; }}
.bar-val {{ font-size: 14px; color: #0f172a; text-align: right; }}

table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
th, td {{ border-bottom: 1px solid #cbd5e1; padding: 11px 8px; text-align: left; }}
th {{ font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: #475569; border-bottom: 2px solid #0f172a; }}
tr.hi-row td {{ font-weight: 700; color: #0067b8; background: #eff6ff; }}

.foot {{
  position: absolute; bottom: 20px; left: 64px; right: 64px;
  display: flex; justify-content: space-between; font-size: 13px; color: #64748b;
}}
a {{ color: #0067b8; text-decoration: none; font-weight: 600; }}
code {{ background: #e2e8f0; color: #0f172a; padding: 2px 6px; font-size: 14px; }}
</style>
</head>
<body>

<!-- SLAJD 1: CZYSTY TYTUŁ -->
<section class="slide" style="justify-content:space-between">
  <div style="margin-top:36px">
    <div class="eyebrow">Bielik Awards 2026 · Kategoria SLM (&lt;10B)</div>
    <h1>Sztab-SAR</h1>
    <p class="lead">Lokalny koordynator poszukiwań osób zaginionych dla OSP, GOPR i Policji. Scala sprzeczne meldunki radiowe w jeden plan działania — całkowicie offline.</p>
  </div>
  <div class="cols-4">
    <div>
      <div class="stat-num">100% offline</div>
      <div class="stat-lbl">Praca w wozie sztabowym bez LTE i bez wysyłania danych medycznych w chmurę</div>
    </div>
    <div>
      <div class="stat-num accent">Bielik-4.5B</div>
      <div class="stat-lbl">Polski model &lt;10B (Q8_0 BPE Fix) z przełącznikiem porównawczym na Gemma-4</div>
    </div>
    <div>
      <div class="stat-num accent">+68.8 pp</div>
      <div class="stat-lbl">Skok koreferencji synonimów względem klasycznego Regexu (75.0% vs 6.2%)</div>
    </div>
    <div>
      <div class="stat-num">0 halucynacji</div>
      <div class="stat-lbl">Twardy audytor w Pythonie kontrolujący godziny, ryzyko medyczne i ID meldunków</div>
    </div>
  </div>
  <div class="foot"><span>{DEMO_URL}</span><span>1 / 7</span></div>
</section>

<!-- SLAJD 2: PROBLEM -->
<section class="slide">
  <div class="eyebrow">Problem terenowy</div>
  <h2>Dlaczego na początku akcji gubi się właściwy trop?</h2>
  <div class="cols-2">
    <div class="stack" style="justify-content:space-between">
      <div>
        <h3>Luka w obecnych narzędziach</h3>
        <p>Systemy <b>SWD PSP</b>, <b>SIRON</b>, <b>SARUAV</b> i <b>RATUNEK</b> obsługują mapy, GPS tyralier oraz drony — żaden z nich nie analizuje jednak treści sprzecznych zeznań świadków.</p>
      </div>
      <div class="sep">
        <h3>Dlaczego chmura odpada</h3>
        <p>W głębokim lesie i górach często nie ma zasięgu sieci, a meldunki zawierają wrażliwe dane zdrowotne i operacyjne podlegające RODO.</p>
      </div>
    </div>
    <div class="stack" style="justify-content:space-between">
      <div>
        <h3>Przykład: Bory Tucholskie</h3>
        <div class="stack" style="gap:12px;margin-top:12px">
          <div class="quote-row muted"><b>M1 · 13:30 Rodzina:</b> wyszedł z cukrzycą bez insuliny, miał <b>czerwoną kurtkę pikowaną</b>.</div>
          <div class="quote-row muted"><b>M2 · 14:15 Świadek:</b> pan w <b>bordowym anoraku</b> szedł w stronę rzeki Brdy (sektor A2).</div>
          <div class="quote-row muted"><b>M3 · Pasażerka PKS:</b> pan w czerwonym stroju stał na przystanku (B2) już o <b>13:10</b>.</div>
          <div class="quote-row"><b>Decyzja Sztab-SAR:</b> łączy kurtkę z anorakiem (M1↔M2), wykrywa kolizję 13:10 &lt; 13:30 i kieruje patrol #1 nad rzekę (A2).</div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot"><span>Scenariusz operacyjny bory_senior</span><span>2 / 7</span></div>
</section>

<!-- SLAJD 3: POROWNANIE 1:1 -->
<section class="slide">
  <div class="eyebrow">Konieczność użycia SLM (&lt;10B)</div>
  <h2>Zbliżenie 1:1 — Bielik-4.5B vs wyszukiwanie bez SLM (Regex)</h2>
  <div class="cols-2" style="gap:28px">
    <div class="shot-col">
      <div class="shot-cap">Z Bielik-4.5B <span>75.0% koreferencji · 75.0% Conflict F1</span></div>
      <div class="shot-wrap"><img src="{s_bielik}" alt="Synteza Bielik"></div>
    </div>
    <div class="shot-col">
      <div class="shot-cap">Bez SLM (Regex) <span>6.2% koreferencji · brak pytań</span></div>
      <div class="shot-wrap"><img src="{s_regex}" alt="Synteza Regex"></div>
    </div>
  </div>
  <div class="foot"><span>Wycinki panelu syntezy w skali 1:1 bez zmniejszania tekstu</span><span>3 / 7</span></div>
</section>

<!-- SLAJD 4: DZIENNIK MELDUNKOW -->
<section class="slide">
  <div class="eyebrow">Praca dyspozytora</div>
  <h2>Automatyczne podświetlenie tropów i praca na żywo</h2>
  <div class="cols-2" style="grid-template-columns: 440px 1fr;">
    <div class="shot-wrap"><img src="{s_col1}" alt="Kolumna meldunków 1:1"></div>
    <div class="stack" style="justify-content:center;gap:30px">
      <div class="num-item">
        <div class="num-tag">01</div>
        <div>
          <h3>Koreferencja z odmianą wyrazów</h3>
          <p>System sam podświetla powiązane opisy mimo polskiej deklinacji — <i>„czerwoną kurtkę pikowaną”</i> w M1 oraz <i>„bordowym anoraku”</i> w M2.</p>
        </div>
      </div>
      <div class="num-item sep">
        <div class="num-tag">02</div>
        <div>
          <h3>Natychmiastowe oznaczenie konfliktów</h3>
          <p>Sprzeczne meldunki (jak obserwacja o 13:10 przed wyjściem o 13:30) od razu dostają wyraźny znacznik przy źródle.</p>
        </div>
      </div>
      <div class="num-item sep">
        <div class="num-tag">03</div>
        <div>
          <h3>Dopisywanie odpowiedzi z radia</h3>
          <p>Po uzyskaniu odpowiedzi na pytanie weryfikacyjne dyspozytor dopisuje nowy meldunek lub wgrywa plik <code>.txt</code> i przelicza sektory.</p>
        </div>
      </div>
    </div>
  </div>
  <div class="foot"><span>Wycinek 1:1 kolumny wejściowej interfejsu</span><span>4 / 7</span></div>
</section>

<!-- SLAJD 5: ARCHITEKTURA + TATRY -->
<section class="slide">
  <div class="eyebrow">Bezpieczeństwo operacyjne</div>
  <h2>Semantyka SLM + twarde reguły w Pythonie</h2>
  <div class="cols-2" style="grid-template-columns: 1fr 450px;">
    <div class="stack" style="justify-content:center;gap:28px">
      <div>
        <h3>1. Warstwa semantyczna (Bielik-4.5B GGUF)</h3>
        <p>Wersja z naprawionymi rangami BPE rozumie polską mowę potoczną, grupuje synonimy (np. <i>żółta wiatrówka = musztardowa kurtka</i>) oraz wskazuje luki wymagające dopytania świadków.</p>
      </div>
      <div class="sep">
        <h3>2. Audytor deterministyczny (<code>sar/rules.py</code>)</h3>
        <p>Sztywno wylicza złote okno medyczne (45 lub 90 minut przy cukrzycy, urazie lub mrozie), kontroluje kolejność godzin, odrzuca nieistniejące ID i gwarantuje wygenerowanie pytań dla dyspozytora.</p>
      </div>
    </div>
    <div class="shot-col">
      <div class="shot-cap">Tatry Zachodnie <span>Sektory A1–C2 i pytania kontrolne</span></div>
      <div class="shot-wrap"><img src="{s_tatry}" alt="Tatry sektory i pytania 1:1"></div>
    </div>
  </div>
  <div class="foot"><span>Scenariusz górski tatry_hipotermia zweryfikowany na Modal T4</span><span>5 / 7</span></div>
</section>

<!-- SLAJD 6: BENCHMARK -->
<section class="slide">
  <div class="eyebrow">Ewaluacja · 16 scenariuszy terenowych (Tesla T4)</div>
  <h2>Bielik-4.5B: 3× szybszy od Gemmy przy najwyższej celności Top-1</h2>
  <div class="cols-2" style="grid-template-columns: 1.1fr 1fr;">
    <div class="stack" style="justify-content:space-between">
      {bench_bars}
    </div>
    <div class="stack" style="justify-content:center;gap:26px">
      <table>
        <thead><tr><th>System</th><th>Coref</th><th>Konflikty</th><th>Top-1</th><th>Czas</th></tr></thead>
        <tbody>{bench_rows}</tbody>
      </table>
      <p><b>Bielik-4.5B</b> osiąga o <b>+68.8 pp</b> wyższą koreferencję niż Regex, najwyższy wynik priorytetu sektora Top-1 (<b>75.0% vs 62.5%</b> dla Gemmy) i działa <b>3× szybciej</b> (15.7 s vs 46.3 s).</p>
    </div>
  </div>
  <div class="foot"><span>Dane pomiarowe: bench/eval_report.json · python bench/run_bench.py</span><span>6 / 7</span></div>
</section>

<!-- SLAJD 7: ROZKAZ I LINKI -->
<section class="slide">
  <div class="eyebrow">Wdrożenie i testy</div>
  <h2>Rozkaz Poszukiwawczy (.html), instalator offline i demo live</h2>
  <div class="cols-2" style="grid-template-columns: 1.12fr 1fr;">
    <div class="shot-col">
      <div class="shot-cap">Wydruk dla patroli <span>Rozkaz_Poszukiwawczy_Sztab_SAR.html</span></div>
      <div class="shot-wrap light"><img src="{s_rozkaz}" alt="Rozkaz operacyjny"></div>
    </div>
    <div class="stack" style="justify-content:center;gap:26px">
      <div>
        <h3>Demo publiczne (Modal T4 GPU)</h3>
        <p style="font-size:14.5px;white-space:nowrap"><a href="{DEMO_URL}">{DEMO_URL}</a></p>
      </div>
      <div class="sep">
        <h3>Repozytorium i instalator offline</h3>
        <p style="font-size:16px;margin-bottom:6px"><a href="{GITHUB_URL}">{GITHUB_URL}</a></p>
        <p style="font-size:16px">Skrypt <code>install.bat</code> pobiera <code>llama.cpp</code> oraz wagi Bielika z kontrolą SHA-256.</p>
      </div>
      <div class="sep">
        <h3>Zgodność konkursowa</h3>
        <p style="font-size:16px">Model <b>Bielik-4.5B (&lt;10B)</b> · Licencja MIT · 5/5 testów jednostkowych.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Bielik Awards 2026 · Sztab-SAR</span><span>7 / 7</span></div>
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
