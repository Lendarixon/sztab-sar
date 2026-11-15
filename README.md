# Sztab-SAR — Taktyczny Koordynator Poszukiwań Offline (SLM <10B)

**Sztab-SAR** to w pełni lokalny (*offline / air-gapped*) asystent sztabu akcji poszukiwawczo-ratowniczych (**OSP, GOPR, WOPR, Policja**), uruchamiany na zwykłym laptopie w wozie sztabowym bez dostępu do internetu.

- **Demo publiczne (Modal T4 GPU):** https://ninjagovlad--sztab-sar-demo-sztabservice-web.us-east.modal.run
- **Prezentacja PDF (bez logowania):** https://ninjagovlad--sztab-sar-demo-sztabservice-web.us-east.modal.run/prezentacja.pdf
- **Repozytorium GitHub:** https://github.com/Lendarixon/sztab-sar

## Brakujące ogniwo między zgłoszeniem a mapą

Polskie służby korzystają z systemów **SWD PSP / MAPA ST3** (dysponowanie), **SIRON** (śledzenie tyralier GPS), **SARUAV** (detekcja sylwetek ze zdjęć dronów) i aplikacji **RATUNEK** (współrzędne SOS). Między tymi narzędziami pozostaje jednak luka na etapie pierwszych 30 minut akcji: potok niespójnych meldunków radiowych, SMS-ów i zeznań świadków trzeba ręcznie przeanalizować na kartce.

**Dlaczego bez SLM (<10B) to nie działa:**
- **Koreferencja synonimów:** zwykłe wyrażenia regularne nie połączą fraz różnych świadków typu *"bordowy anorak"* oraz *"czerwona kurtka pikowana"* albo *"liliowa podomka"* i *"szlafrok fioletowy"*.
- **Sprzeczności czasowo-przestrzenne:** wykrywanie relacji podających obserwację wcześniej niż zadeklarowane wyjście z domu albo sprzeczne kierunki marszu.
- **Zasada offline:** w lasach i górach brakuje stabilnego LTE, a treść meldunków zawiera dane wrażliwe (choroby, leki, lokalizacje świadków i nieletnich).

## Architektura hybrydowa (SLM + audytor deterministyczny)

1. **Warstwa semantyczna (`sar/slm_extract.py`):** lokalny **Bielik-4.5B-v3.0-Instruct** (GGUF z naprawionymi rangami BPE, opcjonalnie **Gemma-4-E4B-it**) przez `llama.cpp` ze ścisłym wyjściem JSON wyodrębnia profil zaginionego, klastry złączonych śladów, sprzeczności i pytania weryfikacyjne dla dyspozytora.
2. **Warstwa deterministyczna (`sar/rules.py`):**
   - sztywny kalkulator Poziomu Alarmu (`KRYTYCZNY` / `WYSOKI` / `PODWYŻSZONY`) i Złotego Okna na podstawie czynników medycznych, wieku dziecka i bliskości wody/mrozu,
   - matematyczny audytor kolizji godzin wyjścia i obserwacji,
   - filtr ugruntowania odrzucający halucynowane identyfikatory meldunków (`M1..Mn`) oraz generator siatki sektorów `A1-C2` i rozkazu HTML.

## Wyniki benchmarku (16 scenariuszy terenowych, Tesla T4)

| System | Koreferencja synonimów | Konflikty (F1) | Priorytet sektora Top-1 | Ryzyko krytyczne | Średni czas |
|---|---:|---:|---:|---:|---:|
| Regex Baseline (bez SLM) | 6.2% | 36.4% | 81.2% | 75.0% | 1 ms |
| **Bielik-4.5B-v3.0-Instruct (BPE Fix)** | **75.0%** | **75.0%** | **75.0%** | 75.0% | **15.7 s** |
| Gemma-4-E4B-it | 93.8% | 90.0% | 62.5% | 75.0% | 46.3 s |

## Szybki start i instalacja offline

### Windows (instalator automatyczny)
Uruchom dwukrotnie `install.bat` — skrypt instaluje zależności Pythona, pobiera `llama-server.exe` (`llama.cpp` Vulkan/CPU) oraz model `Bielik-4.5B-v3.0-Instruct.Q8_0.gguf` z weryfikacją SHA-256 i otwiera panel w przeglądarce (`http://127.0.0.1:8793`).

```bash
# Opcjonalnie z dodatkowym modelem Gemma-4-E4B:
install.bat --with-gemma
```

### Linux / macOS
```bash
./install.sh
```

### Testy i benchmark
```bash
python -m pytest -q
python bench/run_bench.py --modal-url https://ninjagovlad--sztab-sar-demo-sztabservice-web.us-east.modal.run
```

Konfiguracja (aktywny model, GPU/CPU, liczba wątków) zapisuje się w `%LOCALAPPDATA%\SztabSAR\config.json`.
Licencja: MIT.
