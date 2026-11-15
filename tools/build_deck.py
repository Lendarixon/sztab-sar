"""Generuje 7-slajdowa prezentacje PDF (16:9) dla Sztab-SAR na podstawie zmierzonych wynikow benchmarku."""
from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "tools" / "_deck.html"
PDF_PATH = ROOT / "Sztab_SAR_Prezentacja.pdf"
BENCH_PATH = ROOT / "bench" / "eval_report.json"
BRAVE = Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe")

GITHUB_URL = "https://github.com/Lendarixon/sztab-sar"
DEMO_URL = "https://ninjagovlad--sztab-sar-demo-sztabservice-web.us-east.modal.run"


def load_bench_rows() -> str:
    if not BENCH_PATH.is_file():
        return "<tr><td colspan='6'>Brak pliku bench/eval_report.json</td></tr>"
    data = json.loads(BENCH_PATH.read_text(encoding="utf-8"))
    rows = []
    for r in data.get("results", []):
        rows.append(
            f"<tr>"
            f"<td><b>{html.escape(r['system'])}</b></td>"
            f"<td>{r['coreference_acc']*100:.1f}%</td>"
            f"<td>{r['conflict_f1']*100:.1f}%</td>"
            f"<td>{r['sector_top1_acc']*100:.1f}%</td>"
            f"<td>{r['medical_risk_acc']*100:.1f}%</td>"
            f"<td>{r['avg_latency_ms']} ms</td>"
            f"</tr>"
        )
    return "\n".join(rows)


def build_html() -> str:
    bench_rows = load_bench_rows()
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
  background: #0a0c11; color: #eceff4;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}}
.slide {{
  width: 1280px; height: 720px; padding: 52px 66px; position: relative;
  overflow: hidden; page-break-after: always; display: flex; flex-direction: column;
  background:
    radial-gradient(780px 440px at 90% -10%, rgba(220,38,38,0.20), transparent 65%),
    radial-gradient(640px 400px at -5% 110%, rgba(47,111,230,0.18), transparent 65%),
    #0a0c11;
}}
.slide:last-child {{ page-break-after: auto; }}
.tag {{
  display: inline-block; font-size: 13px; font-weight: 600; letter-spacing: .08em;
  text-transform: uppercase; color: #fca5a5; background: rgba(220,38,38,.16);
  border: 1px solid rgba(220,38,38,.38); padding: 6px 14px; border-radius: 999px;
  align-self: flex-start; margin-bottom: 18px;
}}
h1 {{ font-size: 54px; font-weight: 300; line-height: 1.1; margin: 0 0 18px; letter-spacing: -0.02em; }}
h1 b {{ font-weight: 700; color: #f87171; }}
h2 {{ font-size: 35px; font-weight: 500; margin: 0 0 22px; }}
p.lead {{ font-size: 21px; color: #b4bac6; line-height: 1.5; max-width: 960px; margin: 0 0 26px; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; flex: 1; }}
.grid3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; flex: 1; }}
.card {{
  background: rgba(20,23,31,0.88); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 14px; padding: 22px 24px; display: flex; flex-direction: column; gap: 10px;
}}
.card.hi {{ border-color: rgba(248,113,113,.5); background: rgba(220,38,38,.09); }}
.card.ok {{ border-color: rgba(47,191,143,.45); background: rgba(47,191,143,.08); }}
.card h3 {{ margin: 0; font-size: 19px; color: #fff; }}
.card p, .card li {{ margin: 0; font-size: 16px; color: #b4bac6; line-height: 1.5; }}
.card ul {{ margin: 6px 0 0 18px; padding: 0; display: flex; flex-direction: column; gap: 7px; }}
.stat {{ font-size: 44px; font-weight: 700; color: #60a5fa; line-height: 1.1; }}
.stat.ok {{ color: #2fbf8f; }}
.stat.red {{ color: #f87171; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 16px; }}
th, td {{ border: 1px solid rgba(255,255,255,0.12); padding: 12px 14px; text-align: left; }}
th {{ background: rgba(255,255,255,0.06); color: #fff; font-weight: 600; }}
.foot {{ position: absolute; bottom: 24px; left: 66px; right: 66px; display: flex; justify-content: space-between; font-size: 13px; color: #717b8f; }}
a {{ color: #60a5fa; text-decoration: none; }}
</style>
</head>
<body>

<section class="slide">
  <span class="tag">Bielik Awards 2026 · Kategoria SLM (&lt;10B)</span>
  <h1><b>Sztab-SAR</b><br>Koordynator Poszukiwań Offline</h1>
  <p class="lead">Pierwszy lokalny system SLM (&lt;10B) łączący chaotyczne meldunki radiowe, zgłoszenia 112 i zeznania świadków podczas akcji poszukiwawczych OSP, GOPR i Policji — bez zasięgu internetu i bez wysyłania danych w chmurę.</p>
  <div class="grid3" style="margin-top:auto">
    <div class="card hi"><div class="stat red">100%</div><h3>Offline w lesie i górach</h3><p>Działa na laptopie w wozie sztabowym bez LTE, zachowując tajemnicę operacyjną i dane medyczne.</p></div>
    <div class="card"><div class="stat">Bielik 4.5B</div><h3>Naprawiony tokenizer GGUF</h3><p>Korekta rang BPE + Gemma-4-E4B jako opcja porównawcza w jednym interfejsie.</p></div>
    <div class="card ok"><div class="stat ok">0 halucynacji</div><h3>Twardy weryfikator Python</h3><p>Deterministyczny scoring ryzyka medycznego, audyt kolizji godzin i weryfikacja ID meldunków.</p></div>
  </div>
  <div class="foot"><span>Sztab-SAR · OSP / GOPR / WOPR / Policja</span><span>Slajd 1 / 7</span></div>
</section>

<section class="slide">
  <span class="tag">Problem w terenie</span>
  <h2>Brakujące ogniwo między meldunkiem a mapą SIRON / SWD</h2>
  <div class="grid2">
    <div class="card">
      <h3>Co służby już mają</h3>
      <ul>
        <li><b>SWD PSP / MAPA ST3</b> — dysponowanie zastępów i siatka mapowa.</li>
        <li><b>SIRON</b> — mobilne śledzenie tyralier i przeszukanych sektorów GPS.</li>
        <li><b>SARUAV</b> — detekcja sylwetek na zdjęciach lotniczych z dronów.</li>
        <li><b>Aplikacja RATUNEK</b> — transmisja współrzędnych SOS dzwoniącego.</li>
      </ul>
    </div>
    <div class="card hi">
      <h3>Gdzie nadal pracuje człowiek z kartką</h3>
      <ul>
        <li>W pierwszych 30 minutach akcji spływa potok sprzecznych relacji przez radio i telefon.</li>
        <li>Świadek A widział <i>"bordowy anorak"</i>, rodzina zgłasza <i>"czerwoną kurtkę pikowaną"</i> — regex nie łączy synonimów.</li>
        <li>Zeznanie o 13:10 wyprzedza godzinę wyjścia 13:30 — trzeba wyłapać fałszywy trop zanim zmrok zabierze szanse.</li>
        <li>W Bieszczadach czy Borach Tucholskich często nie ma zasięgu sieci na chmurowe API.</li>
      </ul>
    </div>
  </div>
  <div class="foot"><span>Dlaczego chmura odpada: brak LTE + RODO i dane zdrowotne zaginionego</span><span>Slajd 2 / 7</span></div>
</section>

<section class="slide">
  <span class="tag">Dlaczego SLM (&lt;10B) jest niezbędny</span>
  <h2>Zadanie niemożliwe dla wyrażeń regularnych i słowników</h2>
  <div class="grid3">
    <div class="card">
      <h3>1. Koreferencja synonimów</h3>
      <p>Model łączy potoczne opisy różnych świadków: <i>"bordowy anorak" ↔ "czerwona kurtka"</i>, <i>"liliowa podomka" ↔ "fioletowy szlafrok"</i>, <i>"kuleje" ↔ "uraz kostki"</i>.</p>
    </div>
    <div class="card">
      <h3>2. Detekcja kolizji czasu i trasy</h3>
      <p>Rozpoznaje sprzeczności narracyjne: np. świadek widział osobę przy stacji paliw o 21:20, ale psy podjęły ślad nad kanałem melioracyjnym.</p>
    </div>
    <div class="card">
      <h3>3. Pytania weryfikacyjne</h3>
      <p>SLM wskazuje dyspozytorowi luki w wywiadzie: o co natychmiast dopytać świadka lub rodzinę, aby rozstrzygnąć konflikt tropów.</p>
    </div>
  </div>
  <div class="foot"><span>Neuro-symboliczny duet: semantyka SLM + deterministyczny audytor</span><span>Slajd 3 / 7</span></div>
</section>

<section class="slide">
  <span class="tag">Architektura bez halucynacji</span>
  <h2>Jak łączymy Bielik-4.5B z deterministycznym silnikiem zasad</h2>
  <div class="grid2">
    <div class="card">
      <h3>Warstwa 1: Lokalny SLM (&lt;10B)</h3>
      <ul>
        <li><b>Bielik-4.5B-v3.0-Instruct (Q8_0 BPE Fix)</b> z naprawionymi rangami BPE w GGUF — natywnie rozumie polską składnię terenową i potoczną.</li>
        <li>Opcjonalnie <b>Gemma-4-E4B-it</b> przełączana jednym kliknięciem.</li>
        <li>Ekstrakcja ustrukturyzowanego JSON: profil zaginionego, klastry śladów, oś czasu, sprzeczności, priorytety sektorów.</li>
      </ul>
    </div>
    <div class="card ok">
      <h3>Warstwa 2: Deterministyczny Audytor Python</h3>
      <ul>
        <li><b>Kalkulator Alarmu i Złotego Okna:</b> wiek dziecka, cukrzyca/insulina, Alzheimer, leki przeciwzakrzepowe, bliskość wody i mróz sztywno wyliczają poziom KRYTYCZNY.</li>
        <li><b>Audytor Chronologii:</b> matematycznie wykrywa obserwacje sprzed deklarowanej godziny wyjścia.</li>
        <li><b>Filtr ID:</b> odrzuca każde nieistniejące ID meldunku (M1..Mn) i buduje siatkę 6 sektorów A1–C2.</li>
      </ul>
    </div>
  </div>
  <div class="foot"><span>Wyjście: taktyczna siatka sektorów + Rozkaz Poszukiwawczy (.html)</span><span>Slajd 4 / 7</span></div>
</section>

<section class="slide">
  <span class="tag">Uczciwy benchmark · 16 scenariuszy terenowych</span>
  <h2>Regex Baseline vs Bielik-4.5B (BPE Fix) vs Gemma-4-E4B</h2>
  <p class="lead" style="margin-bottom:14px">Wszystkie pomiary wykonane na żywo na GPU Tesla T4 (Modal) na 16 polskich scenariuszach poszukiwawczych (las, góry, woda, zaginięcia dzieci i seniorów).</p>
  <div class="card" style="padding:18px 22px">
    <table>
      <thead>
        <tr><th>System</th><th>Koreferencja synonimów</th><th>Konflikty (F1)</th><th>Priorytet sektora Top-1</th><th>Ryzyko medyczne</th><th>Śr. czas</th></tr>
      </thead>
      <tbody>
        {bench_rows}
      </tbody>
    </table>
  </div>
  <div class="foot"><span>Szczegóły każdego scenariusza zapisane w bench/eval_report.json</span><span>Slajd 5 / 7</span></div>
</section>

<section class="slide">
  <span class="tag">Dojrzałość wdrożenia</span>
  <h2>Gotowy instalator desktopowy i publiczne demo live</h2>
  <div class="grid2">
    <div class="card">
      <h3>Lokalny instalator offline (Windows / Linux)</h3>
      <ul>
        <li><code>install.bat</code> automatycznie instaluje zależności, pobiera <b>llama.cpp</b> (Vulkan GPU / CPU) oraz wagi <b>Bielik-4.5B</b> z weryfikacją SHA-256.</li>
        <li>Trwała konfiguracja w <code>%LOCALAPPDATA%\\SztabSAR\\config.json</code> (model, GPU/CPU, wątki).</li>
        <li>Tryb porównania na żywo: jednym przełącznikiem porównujesz SLM z samym trybem Regex oraz dodajesz nowe meldunki w trakcie akcji.</li>
      </ul>
    </div>
    <div class="card hi">
      <h3>Praktyczny workflow w wozie sztabowym</h3>
      <ul>
        <li>Wklejasz lub wgrywasz plik <code>.txt/.log</code> z dyżurki lub wpisujesz kolejne meldunki na żywo z radia.</li>
        <li>W sekundę widzisz złączone rysopisy, czerwone konflikty godzin i priorytetową siatkę A1–C2.</li>
        <li>Jednym kliknięciem pobierasz gotową <b>Kartę Poszukiwań / Rozkaz (.html)</b> do wydruku lub przekazania patrolom.</li>
      </ul>
    </div>
  </div>
  <div class="foot"><span>Kod licencjonowany na MIT · Zero telemetryki i chmury w trybie lokalnym</span><span>Slajd 6 / 7</span></div>
</section>

<section class="slide">
  <span class="tag">Linki do weryfikacji i testów</span>
  <h2>Sprawdź kod, benchmark i działające demo na żywo</h2>
  <div class="grid2">
    <div class="card ok">
      <h3>Publiczne Demo Live (Modal T4 GPU)</h3>
      <p>Działa bezpośrednio w przeglądarce bez logowania (Bielik-4.5B BPE Fix + przełącznik na Gemma-4-E4B + tryb porównania z Regex):</p>
      <p style="font-size:16px;word-break:break-all"><a href="{DEMO_URL}">{DEMO_URL}</a></p>
    </div>
    <div class="card">
      <h3>Repozytorium GitHub + Instalator</h3>
      <p>Pełny kod źródłowy, 16 scenariuszy testowych, skrypty benchmarku oraz automatyczny instalator <code>install.bat</code>:</p>
      <p style="font-size:17px"><a href="{GITHUB_URL}">{GITHUB_URL}</a></p>
    </div>
  </div>
  <div class="foot"><span>Bielik Awards 2026 · Sztab-SAR</span><span>Slajd 7 / 7</span></div>
</section>

</body>
</html>"""


def main():
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
