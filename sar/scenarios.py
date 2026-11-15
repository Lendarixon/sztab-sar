"""Scenariusze demonstracyjne i 16-przypadkowy zestaw testowy do benchmarku Sztab-SAR."""
from __future__ import annotations

DEMO_SCENARIOS: list[dict] = [
    {
        "id": "bory_senior",
        "title": "Bory Tucholskie — senior z cukrzycą (sprzeczne czasy)",
        "meta": {
            "miejsce": "Okolice Tucholi / Bory Tucholskie",
            "pogoda": "8°C, lekki deszcz, zmierzch za 50 min",
            "godzina_start": "15:10",
            "teren": {
                "A1": "Las / Ambona nr 4",
                "A2": "Rozlewisko / Rzeka Brda",
                "B1": "Leśniczówka Dębina",
                "B2": "Przystanek PKS i szosa",
                "C1": "Młodnik sosnowy",
                "C2": "Zabudowania wsi i działki",
            },
        },
        "messages": [
            {
                "id": "M1",
                "time": "14:40",
                "source": "Rodzina (Zięć)",
                "text": "Teść Janusz K., 74 lata, wyszedł z domu ok. 13:30 na grzyby. Ma cukrzycę typu 1, nie zabrał insuliny ani telefonu. Ubrany był w czerwoną kurtkę pikowaną, ciemne kalosze i szary beret.",
            },
            {
                "id": "M2",
                "time": "14:52",
                "source": "Świadek (Rowerzysta)",
                "text": "Około 14:15 widziałem starszego pana w bordowym anoraku i czapce przy leśniczówce Dębina (sektor B1). Wyglądał na zdezorientowanego, szedł wolno w stronę rzeki Brdy (sektor A2).",
            },
            {
                "id": "M3",
                "time": "14:58",
                "source": "Świadek (Pasażerka PKS)",
                "text": "Jestem pewna, że pan w czerwonym stroju stał na przystanku PKS (sektor B2) już o 13:10 i pytał o autobus do Chojnic.",
            },
            {
                "id": "M4",
                "time": "15:05",
                "source": "Patrol OSP-2",
                "text": "Przy ambonie nr 4 (sektor A1) w stronę rozlewiska Brdy (A2) znaleźliśmy porzucony pusty koszyk wiklinowy i świeże ślady dużych butów kierujące się w dół skarpy do wody.",
            },
        ],
    },
    {
        "id": "tatry_hipotermia",
        "title": "Tatry Zachodnie — turysta we mgle (ryzyko hipotermii)",
        "meta": {
            "miejsce": "Dolina Chochołowska / Grześ",
            "pogoda": "1°C, gęsta mgła, wiatr 60 km/h",
            "godzina_start": "16:20",
            "teren": {
                "A1": "Polana Chochołowska",
                "A2": "Grzbiet Grzesia",
                "B1": "Żleb pod Rakoń",
                "B2": "Schronisko / Szlak zielony",
                "C1": "Potok i mostek drewniany",
                "C2": "Granica lasu (szlak żółty)",
            },
        },
        "messages": [
            {
                "id": "M1",
                "time": "15:30",
                "source": "Dyspozytor 112",
                "text": "Zgłoszenie od partnerki: Marek W., 39 lat, rozdzielili się we mgle pod Grzesiem ok. 14:00. Ma żółtą wiatrówkę, czarny plecak z napisem Alpine i uraz prawej kostki.",
            },
            {
                "id": "M2",
                "time": "15:55",
                "source": "Turyści (grupa z Warszawy)",
                "text": "O 14:40 mijaliśmy samotnego faceta w musztardowej kurtce przeciwdeszczowej blisko żlebu pod Rakoniem (sektor B1). Mocno utykał na prawą nogę i nie miał kijów.",
            },
            {
                "id": "M3",
                "time": "16:08",
                "source": "Obsługa schroniska",
                "text": "Ktoś dzwonił z bramki alarmowej, że mężczyzna z ciemnym plecakiem zszedł już na Polanę Chochołowską (A1) o 14:15, ale od 14:20 nie logował się do BTS-a przy schronisku (B2).",
            },
            {
                "id": "M4",
                "time": "16:15",
                "source": "GOPR Zespół-1",
                "text": "Na zejściu z Grzesia (A2) w stronę żlebu B1 widać ślady ześlizgnięcia w śniegu oraz urwany pasek od ciemnego plecaka.",
            },
        ],
    },
    {
        "id": "drawsko_dziecko",
        "title": "Jezioro Drawsko — zaginione dziecko na kempingu",
        "meta": {
            "miejsce": "Pole namiotowe Stare Drawsko",
            "pogoda": "17°C, porywisty wiatr od jeziora",
            "godzina_start": "18:45",
            "teren": {
                "A1": "Plaża i pomost główny",
                "A2": "Szuwary i zatoka północna",
                "B1": "Alejka przyczep i sanitariaty",
                "B2": "Sklep i brama wjazdowa",
                "C1": "Las za ogrodzeniem",
                "C2": "Przystań kajakowa",
            },
        },
        "messages": [
            {
                "id": "M1",
                "time": "18:10",
                "source": "Matka",
                "text": "Zaginął 6-letni Antoś! Ostatni raz bawił się przy sanitarjatach (B1) o 17:45. Ma na sobie niebieską bluzę z dinozaurem, krótkie spodenki moro i zielone sandały.",
            },
            {
                "id": "M2",
                "time": "18:22",
                "source": "Wędkarz",
                "text": "Koło 18:00 widziałem małego chłopca w granatowym polarze ze smokiem, jak biegł po pomoście (sektor A1) w stronę szuwarów w zatoce północnej (A2).",
            },
            {
                "id": "M3",
                "time": "18:30",
                "source": "Ochrona kempingu",
                "text": "Kamera przy bramie (B2) nie zarejestrowała wyjścia dziecka poza teren między 17:30 a 18:25. Natomiast przy przystani kajakowej (C2) znaleziono jeden zielony sandałek.",
            },
            {
                "id": "M4",
                "time": "18:38",
                "source": "Wczasowicz z przyczepy 14",
                "text": "Żona mówi, że widziała chłopca w niebieskiej bluzie przy sklepie (B2) o 18:20 razem z panią w białym kapeluszu, ale nie mamy pewności czy miał sandały.",
            },
        ],
    },
    {
        "id": "wypadek_szok",
        "title": "Droga S7 — kierowca oddalił się w szoku po dachowaniu",
        "meta": {
            "miejsce": "Węzeł Ostróda Południe / pas zadrzewień",
            "pogoda": "4°C, noc, mgła przy gruncie",
            "godzina_start": "22:15",
            "teren": {
                "A1": "Miejsce dachowania i rów",
                "A2": "Zagajnik olszynowy za ekranem",
                "B1": "Kanał melioracyjny",
                "B2": "Stacja paliw 800 m na płd.",
                "C1": "Droga techniczna",
                "C2": "Baza drogowa / wiadukt",
            },
        },
        "messages": [
            {
                "id": "M1",
                "time": "21:40",
                "source": "PSP JRG-1",
                "text": "Dachowanie osobówki w rowie (sektor A1). W środku otwarte poduszki, krew na zagłówku kierowcy, dokumenty na nazwisko Tomasz N., 42 l. Brak kierującego w pojeździe.",
            },
            {
                "id": "M2",
                "time": "21:55",
                "source": "Świadek (Kierowca TIR)",
                "text": "Zaraz po zdarzeniu, ok. 21:30, widziałem mężczyznę z rozbitym czołem w jasnej bluzie odblaskowej, który przeskoczył za ekran akustyczny do zagajnika (sektor A2).",
            },
            {
                "id": "M3",
                "time": "22:02",
                "source": "Policja Patrol-3",
                "text": "Kasjer ze stacji paliw (B2) twierdzi, że o 21:20 kupował u niego kawę pan w kamizelce roboczej z bandażem na głowie. Pies tropiący podjął jednak trop z A1 w stronę kanału melioracyjnego (B1).",
            },
            {
                "id": "M4",
                "time": "22:10",
                "source": "Dyspozytor Medyczny",
                "text": "Rodzina potwierdza, że Tomasz przyjmuje leki przeciwzakrzepowe (ryzyko krwotoku po urazie głowy). Zostawił kurtkę zimową w aucie — jest w samej bluzie.",
            },
        ],
    },
]


# 16 scenariuszy ewaluacyjnych do benchmarku: Regex Baseline vs Bielik-4.5B vs Gemma-4-E4B
BENCHMARK_CASES: list[dict] = [
    {
        "id": "eval_01",
        "title": "Grzybiarz z cukrzycą i konfliktem przystanku",
        "meta": DEMO_SCENARIOS[0]["meta"],
        "messages": DEMO_SCENARIOS[0]["messages"],
        "expected": {
            "coref_terms": ["bordowym anoraku", "czerwoną kurtkę"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "A2",
        },
    },
    {
        "id": "eval_02",
        "title": "Turysta w Tatrach z urazem kostki",
        "meta": DEMO_SCENARIOS[1]["meta"],
        "messages": DEMO_SCENARIOS[1]["messages"],
        "expected": {
            "coref_terms": ["musztardowej kurtce", "żółtą wiatrówkę"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "B1",
        },
    },
    {
        "id": "eval_03",
        "title": "Dziecko na kempingu nad jeziorem",
        "meta": DEMO_SCENARIOS[2]["meta"],
        "messages": DEMO_SCENARIOS[2]["messages"],
        "expected": {
            "coref_terms": ["granatowym polarze", "niebieską bluzę"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "A2",
        },
    },
    {
        "id": "eval_04",
        "title": "Kierowca po dachowaniu na lekach przeciwzakrzepowych",
        "meta": DEMO_SCENARIOS[3]["meta"],
        "messages": DEMO_SCENARIOS[3]["messages"],
        "expected": {
            "coref_terms": ["kamizelce roboczej", "jasnej bluzie odblaskowej"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "B1",
        },
    },
    {
        "id": "eval_05",
        "title": "Seniorka z demencją w kapciach przy rzece",
        "meta": {"miejsce": "Włocławek / bulwary", "pogoda": "2°C, noc", "teren": {"A1": "Kładka nad Wisłą", "A2": "Park miejski", "B1": "Osiedle", "B2": "Dworzec"}},
        "messages": [
            {"id": "M1", "time": "20:10", "source": "Córka", "text": "Mama Zofia, 81 lat, ma zaawansowanego Alzheimera, wyszła z mieszkania na osiedlu (B1) o 19:30 w samym szlafroku fioletowym i kapciach."},
            {"id": "M2", "time": "20:25", "source": "Mieszkaniec", "text": "O 19:55 widziałem starszą panią w liliowej podomce boso przy wejściu na kładkę nad Wisłą (A1)."},
            {"id": "M3", "time": "20:32", "source": "Straż Miejska", "text": "Brak śladów na dworcu (B2), kamera z 19:58 pokazuje postać wchodzącą na wał przeciwpowodziowy przy A1."},
        ],
        "expected": {
            "coref_terms": ["liliowej podomce", "szlafroku fioletowym"],
            "has_conflict": False,
            "medical_risk": True,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_06",
        "title": "Rowerzysta górski bez kolizji czasowej — czysty trop",
        "meta": {"miejsce": "Beskid Sądecki", "pogoda": "6°C, zmierzch", "teren": {"A1": "Zjazd do potoku", "A2": "Polana Jaworzyna", "B1": "Parking leśny", "B2": "Szlak niebieski"}},
        "messages": [
            {"id": "M1", "time": "17:00", "source": "Kolega", "text": "Piotr, 31 l., nie wrócił na parking leśny (B1). Jechał na zielonym rowerze gravel w seledynowym kasku."},
            {"id": "M2", "time": "17:20", "source": "Biegacz", "text": "O 16:15 widziałem kolarza w limonkowym kasku skręcającego z polany (A2) w stromy zjazd do potoku (A1)."},
            {"id": "M3", "time": "17:35", "source": "GOPR", "text": "Na zjeździe (A1) świeże ślady hamowania i wyłamana barierka nad skarpą potoku."},
        ],
        "expected": {
            "coref_terms": ["limonkowym kasku", "seledynowym kasku"],
            "has_conflict": False,
            "medical_risk": False,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_07",
        "title": "Zagubiony myśliwy z kardiomiopatią — konflikt kierunku",
        "meta": {"miejsce": "Puszcza Knyszyńska", "pogoda": "-3°C, śnieg", "teren": {"A1": "Karmowisko Północ", "A2": "Torfowisko Południe", "B1": "Droga pożarowa 7", "B2": "Osada leśna"}},
        "messages": [
            {"id": "M1", "time": "19:00", "source": "Koło Łowieckie", "text": "Kolega Ryszard, 66 lat, ma rozrusznik serca. Wyszedł o 15:00 w oliwkowym polarze myśliwskim z psem gończym."},
            {"id": "M2", "time": "19:15", "source": "Leśniczy", "text": "O 17:40 słyszałem ujadanie psa na północ przy karmowisku (A1), tam szedł mężczyzna w zielonkawej bluzie moro."},
            {"id": "M3", "time": "19:22", "source": "OSP", "text": "Świadek z osady (B2) twierdzi jednak, że o 17:45 widział Ryszarda daleko na południe przy torfowisku (A2), co wyklucza obecność w A1 o 17:40."},
        ],
        "expected": {
            "coref_terms": ["zielonkawej bluzie", "oliwkowym polarze"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_08",
        "title": "Nastolatek po kłótni — groźba samookaleczenia",
        "meta": {"miejsce": "Kraków / Zakrzówek", "pogoda": "5°C, noc", "teren": {"A1": "Skałki nad zalewem", "A2": "Las Łęgowy", "B1": "Przystanek tramwajowy", "B2": "Blokowisko"}},
        "messages": [
            {"id": "M1", "time": "23:05", "source": "Matka", "text": "16-letni Kacper wyszedł z domu (B2) o 22:15 po ostrej kłótni, zostawił pożegnalną wiadomość na biurku i nie bierze telefonu. Miał czarną bluzę z kapturem i białe trampki."},
            {"id": "M2", "time": "23:18", "source": "Spacerowicz z psem", "text": "O 22:40 widziałem młodego chłopaka w ciemnej kangurce i jasnych tenisówkach siedzącego na krawędzi skałek nad zalewem (A1)."},
        ],
        "expected": {
            "coref_terms": ["ciemnej kangurce", "czarną bluzę"],
            "has_conflict": False,
            "medical_risk": True,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_09",
        "title": "Kajakarz na rzece Bug — dwa sprzeczne raporty czasowe",
        "meta": {"miejsce": "Dolina Bugu / Drohiczyn", "pogoda": "11°C, wiatr", "teren": {"A1": "Zakręt pod skarpą", "A2": "Wyspa piaszczysta", "B1": "Stanica wodna", "B2": "Most drogowy"}},
        "messages": [
            {"id": "M1", "time": "16:30", "source": "Wypożyczalnia", "text": "Kajakarz w pomarańczowej kamizelce wypłynął ze stanicy (B1) o 14:00, miał oddać sprzęt o 16:00."},
            {"id": "M2", "time": "16:40", "source": "Wędkarz", "text": "Widziałem pusty żółty kajak dryfujący koło wyspy (A2) o 15:20, a w nim jaskrawoczerwoną kapokę."},
            {"id": "M3", "time": "16:48", "source": "Rolnik", "text": "Ja widziałem tego pana całego i zdrowego przy moście (B2) jeszcze o 13:15 zanim w ogóle wziął kajak ze stanicy!"},
        ],
        "expected": {
            "coref_terms": ["jaskrawoczerwoną kapokę", "pomarańczowej kamizelce"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "A2",
        },
    },
    {
        "id": "eval_10",
        "title": "Biegacz w Puszczy Kampinoskiej — skręcenie i brak zasięgu",
        "meta": {"miejsce": "Kampinos / Truskaw", "pogoda": "4°C, deszcz", "teren": {"A1": "Wydma Łużowa", "A2": "Bagna Cichowąż", "B1": "Parking Truskaw", "B2": "Szlak czerwony"}},
        "messages": [
            {"id": "M1", "time": "19:30", "source": "Żona", "text": "Adam, 35 l., ma astmę wysiłkową i zapomniał inhalatora w aucie na parkingu (B1). Biega w neonowej koszulce i ciemnych legginsach."},
            {"id": "M2", "time": "19:45", "source": "Leśniczy", "text": "O 18:10 słyszałem wołanie o pomoc z rejonu bagien Cichowąż (A2) i mignęła mi odblaskowa koszulka biegowa."},
        ],
        "expected": {
            "coref_terms": ["odblaskowa koszulka", "neonowej koszulce"],
            "has_conflict": False,
            "medical_risk": True,
            "priority_sector": "A2",
        },
    },
    {
        "id": "eval_11",
        "title": "Dziecko w centrum handlowym / parku — fałszywy trop ochrony",
        "meta": {"miejsce": "Park Śląski Chorzów", "pogoda": "14°C", "teren": {"A1": "Staw Łabędzi", "A2": "Wesołe Miasteczko", "B1": "Rosarium", "B2": "Kolejka Elka"}},
        "messages": [
            {"id": "M1", "time": "15:10", "source": "Ojciec", "text": "4-letnia Maja zginęła o 14:45 w Rosarium (B1). Ma różową sukienkę w grochy i żółty plecaczek z pszczółką."},
            {"id": "M2", "time": "15:18", "source": "Sprzedawca lodów", "text": "O 14:55 dziewczynka w malinowej sukience z żółtym tornisterkiem biegła prosto na pomost przy Stawie Łabędzim (A1)."},
            {"id": "M3", "time": "15:24", "source": "Ochrona", "text": "Koledzy z bramy twierdzą, że dziecko wyszło o 14:30 kolejką Elką (B2), co nie zgadza się z czasem zniknięcia z Rosarium o 14:45."},
        ],
        "expected": {
            "coref_terms": ["malinowej sukience", "różową sukienkę"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_12",
        "title": "Pracownik leśny w Bieszczadach — drzewo i brak kontaktu",
        "meta": {"miejsce": "Nadleśnictwo Baligród", "pogoda": "0°C, mżawka", "teren": {"A1": "Oddział 44 (zrąb)", "A2": "Potok Jabłonka", "B1": "Składnica drewna", "B2": "Droga leśna"}},
        "messages": [
            {"id": "M1", "time": "16:15", "source": "Brygadzista", "text": "Zaginął pilarz Jan, 52 l., nie wrócił ze zrębu (A1) na zbiórkę o 15:30. Ubrany w pomarańczowe spodnie robocze z szelkami i niebieski kask."},
            {"id": "M2", "time": "16:28", "source": "Kierowca wywózki", "text": "Piła spalinowa stoi włączona bez operatora w oddziale 44 (A1), obok leży błękitny hełm ochronny i ślady krwi na korze."},
        ],
        "expected": {
            "coref_terms": ["błękitny hełm", "niebieski kask"],
            "has_conflict": False,
            "medical_risk": True,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_13",
        "title": "Mężczyzna z epilepsją w sadzie — konflikt lokalizacji",
        "meta": {"miejsce": "Gmina Grójec", "pogoda": "6°C, mgła", "teren": {"A1": "Stary sad i studnia", "A2": "Staw hodowlany", "B1": "Domostwo", "B2": "Droga powiatowa"}},
        "messages": [
            {"id": "M1", "time": "17:45", "source": "Siostra", "text": "Brat Paweł, 28 l., ma ciężką padaczkę i nie wziął leków od rana. Wyszedł z domu (B1) o 16:30 w grafitowej puchówce."},
            {"id": "M2", "time": "18:00", "source": "Sąsiad", "text": "O 17:05 widziałem go w ciemnoszarej kurtce puchowej jak wchodził w stary sad przy nieogrodzonej studni (A1)."},
            {"id": "M3", "time": "18:10", "source": "OSP-1", "text": "Kuzyn zapewnia, że o 17:00 rozmawiał z Pawłem na drodze powiatowej (B2) 3 km dalej — oba zeznania w tym samym czasie są sprzeczne."},
        ],
        "expected": {
            "coref_terms": ["ciemnoszarej kurtce", "grafitowej puchówce"],
            "has_conflict": True,
            "medical_risk": True,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_14",
        "title": "Narciarz biegowy w Górach Izerskich — zasłabnięcie",
        "meta": {"miejsce": "Jakuszyce / Hala Izerska", "pogoda": "-8°C, zawieja", "teren": {"A1": "Chatka Górzystów", "A2": "Torfowiska Izerskie", "B1": "Polana Jakuszycka", "B2": "Granica CZ"}},
        "messages": [
            {"id": "M1", "time": "15:50", "source": "Recepcja", "text": "Turystka 58 l., po zawale rok temu, nie wróciła z pętli na Halę. Ma biało-błękitny kombinezon i czerwone rękawice."},
            {"id": "M2", "time": "16:10", "source": "GOPR", "text": "Świadek mijał kobietę w jasnym stroju z niebieskimi wstawkami i szkarłatnych rękawiczkach na skraju torfowisk (A2), wyglądała na skrajnie wyczerpaną."},
        ],
        "expected": {
            "coref_terms": ["szkarłatnych rękawiczkach", "czerwone rękawice"],
            "has_conflict": False,
            "medical_risk": True,
            "priority_sector": "A2",
        },
    },
    {
        "id": "eval_15",
        "title": "Wędkarz nad Wisłą — porzucony sprzęt i sprzeczna godzina",
        "meta": {"miejsce": "Płock / Kępa Polska", "pogoda": "5°C, noc", "teren": {"A1": "Ostroga nr 3", "A2": "Starorzecze", "B1": "Parking nad wałem", "B2": "Sklep wiejski"}},
        "messages": [
            {"id": "M1", "time": "21:00", "source": "Żona", "text": "Mąż Janek, 60 l., pojechał nad rzekę po pracy o 17:00. Miał zielony sztormiak i latarkę czołówkę."},
            {"id": "M2", "time": "21:15", "source": "Policja", "text": "Na ostrodze nr 3 (A1) stoją wędki, otwarta skrzynka i oliwkowy płaszcz przeciwdeszczowy na kamieniach."},
            {"id": "M3", "time": "21:20", "source": "Świadek spod sklepu", "text": "Widziałem Janka pod sklepem (B2) w tym płaszczu o 16:15, ale wtedy mówił żonie, że jest jeszcze w pracy w mieście!"},
        ],
        "expected": {
            "coref_terms": ["oliwkowy płaszcz", "zielony sztormiak"],
            "has_conflict": True,
            "medical_risk": False,
            "priority_sector": "A1",
        },
    },
    {
        "id": "eval_16",
        "title": "Wędrowiec z psem w Roztoczu — jasna diagnoza, bez konfliktu",
        "meta": {"miejsce": "Roztoczański Park Narodowy", "pogoda": "7°C, zmrok", "teren": {"A1": "Stawy Echo", "A2": "Bukowa Góra", "B1": "Zwierzyniec parking", "B2": "Szlak centralny"}},
        "messages": [
            {"id": "M1", "time": "17:20", "source": "Partnerka", "text": "Michał, 46 l., zboczył ze szlaku po 15:30 szukać uciekłego psa. Ma brązową kurtkę skórzaną i buty trekkingowe."},
            {"id": "M2", "time": "17:35", "source": "Leśniczy", "text": "Pies kręci się sam na grobli przy Stawach Echo (A1), obok leży telefon i beżowo-brązowa skórzana katana na krzaku."},
        ],
        "expected": {
            "coref_terms": ["skórzana katana", "brązową kurtkę skórzaną"],
            "has_conflict": False,
            "medical_risk": False,
            "priority_sector": "A1",
        },
    },
]
