=== Nazwa projektu * ===
Sztab-SAR - Taktyczny Koordynator Poszukiwań Offline (SLM <10B)

=== Skrócony opis projektu * ===
Sztab-SAR to w pełni lokalny (offline / air-gapped) system wsparcia sztabu akcji poszukiwawczo-ratowniczych (OSP, GOPR, Policja) oparty na małym modelu językowym Bielik-4.5B-v3.0-Instruct oraz deterministycznym weryfikatorze taktycznym. Polskie służby dysponują już systemami do dysponowania (SWD PSP), śledzenia tyralier GPS (SIRON), analizy zdjęć z dronów (SARUAV) i lokalizacji SOS (RATUNEK), ale pomiędzy nimi nadal istnieje luka: podczas pierwszych 30 minut akcji potok chaotycznych meldunków radiowych, SMS-ów i zeznań świadków trzeba ręcznie porządkować na papierze. Proste wyrażenia regularne nie łączą synonimicznych opisów (np. "bordowy anorak" i "czerwona kurtka pikowana") ani nie wychwytują logicznych kolizji w relacjach świadków, a w lasach i górach brakuje zasięgu LTE na usługi chmurowe i obowiązuje ochrona danych zaginionego. Sztab-SAR automatycznie scala rysopis, wykrywa sprzeczności czasowo-przestrzenne, generuje pytania weryfikacyjne dla dyspozytora i ustawia priorytetową siatkę sektorów A1-C2. W benchmarku na 16 polskich scenariuszach Bielik-4.5B (z naprawionym tokenizerem BPE w GGUF) podniósł wykrywanie koreferencji z 6.2% (Regex) do 75.0%, wykrywanie konfliktów F1 z 36.4% do 75.0% i działał niemal 3x szybciej niż Gemma-4-E4B (15.7 s vs 46.3 s). Projekt posiada automatyczny instalator lokalny i działające publiczne demo na GPU.

=== Szczegółowy opis projektu wraz z efektami wdrożenia * ===
Kontekst i luka w istniejącym ekosystemie służb
Podczas poszukiwań osób zaginionych w Polsce (lasy, góry, obszary wodne) służby korzystają z wyspecjalizowanych narzędzi: SWD PSP i MAPA ST3 do zarządzania siłami, aplikacji SIRON do koordynacji przeszukanych sektorów GPS, systemu SARUAV do detekcji sylwetek na zdjęciach z dronów oraz aplikacji RATUNEK. Żadne z tych narzędzi nie analizuje jednak w trybie offline strumienia nieustrukturyzowanych meldunków tekstowych i głosowych napływających w pierwszej godzinie akcji z numeru 112, od rodziny, przypadkowych świadków i patroli terenowych. Przesyłanie surowych relacji do chmury jest niemożliwe w strefach bez zasięgu (Bieszczady, Bory Tucholskie) oraz niedopuszczalne ze względu na tajemnicę operacyjną i wrażliwe dane medyczne (choroby przewlekłe, leki, nieletni).

Dlaczego niezbędny jest SLM (<10B) i dlaczego nie wystarcza regex
Zadanie Sztab-SAR wymaga rozumienia potocznej polszczyzny, przestrzeni i logiki zdarzeń:
1. Koreferencja synonimów między meldunkami: świadek na szlaku zgłasza "mężczyznę w musztardowej kurtce przeciwdeszczowej", a rodzina podaje "żółtą wiatrówkę" (albo "liliową podomkę" vs "fioletowy szlafrok", "ciemną kangurkę" vs "czarną bluzę"). Wyrażenia regularne tego nie połączą.
2. Sprzeczności narracyjne i czasowe: system wykazuje, że zgłoszenie z przystanku o 13:10 wyprzedza deklarowane wyjście z domu o 13:30 albo że pies tropiący podjął trop w stronę kanału mimo zeznań ze stacji paliw.
3. Generowanie pytań dla dyspozytora: na podstawie luk w meldunkach model wskazuje konkretne pytania, które pozwalają szybko odsiać fałszywy trop przed zapadnięciem zmroku.

Architektura hybrydowa: Bielik-4.5B (BPE Fix) + deterministyczny audytor
Projekt celowo nie oddaje decyzji o życiu i zdrowiu samej sieci neuronowej. System dzieli odpowiedzialność na dwie warstwy:
- Warstwa SLM (<10B): lokalny Bielik-4.5B-v3.0-Instruct (Q8_0 GGUF przez llama.cpp z naszą naprawą rang BPE w metadanych GGUF dla zachowania poprawnej tokenizacji języka polskiego) oraz opcjonalnie Gemma-4-E4B-it. Model zwraca zwarty JSON ze skorelowanymi tropami, konfliktami, priorytetami sektorów i pytaniami weryfikacyjnymi.
- Warstwa deterministyczna (Python): niezależny kalkulator ryzyka wylicza Poziom Alarmu (KRYTYCZNY, WYSOKI, PODWYŻSZONY) i Złote Okno (45/90/180 min) na podstawie twardych sygnałów (wiek dziecka, cukrzyca, brak insuliny, Alzheimer, krwotok, woda, mróz). Drugi moduł matematycznie weryfikuje kolejność godzin, filtruje wszelkie nieistniejące ID meldunków (M1..Mn) i buduje taktyczną siatkę 6 sektorów A1-C2 z gotowym Rozkazem Poszukiwawczym do wydruku w HTML.

Dojrzałość wdrożenia i funkcje
Aplikacja desktopowa i publiczne demo webowe (Modal T4 GPU) oferują w 100% polski interfejs trzykolumnowy: dziennik meldunków z możliwością dodawania nowych doniesień "na żywo" oraz wgrywania plików .txt/.log, sekcję zespolonego rysopisu i czerwonych konfliktów, a także taktyczną siatkę sektorów z osią czasu. Jednym przełącznikiem można przełączać aktywny model (Bielik-4.5B lub Gemma-4-E4B) albo włączyć tryb porównania z samym parserem Regex. Użytkownik ma do dyspozycji automatyczny instalator Windows (install.bat) i Linux/macOS (install.sh), który sam pobiera llama.cpp i wagi GGUF z weryfikacją SHA-256 oraz zapisuje ustawienia (model, GPU/CPU, wątki) w lokalnym pliku config.json.

Zmierzone efekty i benchmark (16 scenariuszy terenowych, Tesla T4)
W celu uczciwej oceny przetestowaliśmy 16 autorskich scenariuszy polskich akcji ratowniczych (lasy, góry, jeziora, zaginięcia dzieci i seniorów) na trzech konfiguracjach:
- Regex Baseline (bez SLM): koreferencja synonimów 6.2%, wykrywanie konfliktów F1 36.4%, priorytet sektora Top-1 81.2%, ryzyko krytyczne 75.0%, czas 1 ms.
- Bielik-4.5B-v3.0-Instruct (BPE Fix, domyślny): koreferencja 75.0% (12x lepiej niż Regex), wykrywanie konfliktów F1 75.0% (ponad 2x lepiej), priorytet sektora Top-1 75.0%, ryzyko krytyczne 75.0%, średni czas odpowiedzi 15.7 s.
- Gemma-4-E4B-it (tryb opcjonalny): koreferencja 93.8%, konflikty F1 90.0%, priorytet sektora Top-1 62.5%, ryzyko krytyczne 75.0%, średni czas odpowiedzi 46.3 s.

Pomiar wykazał konkretną przewagę wdrożeniową Bielika-4.5B: w zadaniu taktycznym dla polskich służb jest niemal trzykrotnie szybszy od Gemma-4-E4B (15.7 s vs 46.3 s), uzyskał wyższą trafność wskazania pierwszego sektora (75.0% vs 62.5%) przy ogromnym zysku koreferencji względem samych reguł oraz pełnej prywatności 100% offline. Testy jednostkowe całego potoku przechodzą (5 passed w pytest), a kod, instalator i raport ewaluacji są w całości publicznie dostępne na GitHub oraz w działającym demo online.

=== Prezentacja (opcjonalnie) ===
https://ninjagovlad--sztab-sar-demo-sztabservice-web.us-east.modal.run/prezentacja.pdf
