"""Reguly deterministyczne i weryfikator taktyczny dla Sztab-SAR.

Oddziela semantyke SLM od twardej logiki bezpieczenstwa:
- deterministyczny kalkulator ryzyka medycznego i pogodowego (wiek, choroby, woda, noc/mroz),
- matematyczny audyt osi czasu i kolizji godzin,
- walidacja ugruntowania (grounding) ID meldunkow,
- budowa 6-sektorowej siatki taktycznej SVG/UI.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

# Czynniki ryzyka medycznego / zycia i zdrowia (deterministyczne, bez halucynacji)
MEDICAL_PATTERNS: list[tuple[str, str, int]] = [
    (r"\b(cukrzyc\w*|insulin\w*|hipoglikem\w*)\b", "Cukrzyca / brak insuliny", 4),
    (r"\b(alzheimer\w*|demencj\w*|otępien\w*|zdezorientowan\w*)\b", "Demencja / dezorientacja", 4),
    (r"\b(zawał\w*|rozrusznik\w*|kardiomiopat\w*|leki nasercow\w*|przeciwzakrzepow\w*|krwotok\w*|padaczk\w*|epilepsj\w*|astm\w*|inhalator\w*)\b", "Stan nagly / leki krytyczne", 4),
    (r"\b(samobój\w*|pożegnaln\w*|samookaleczeni\w*)\b", "Ryzyko autoagresji", 5),
    (r"\b(uraz\w*|rozbit\w*|krew\b|krwaw\w*|ślady krwi|złaman\w*|utyka\w*|ześlizgnięci\w*)\b", "Uraz fizyczny / krwawienie", 3),
    (r"\b([1-9]|1[0-2])[- ]?letn\w*\b|\b[1-9]\s+lat\b|\bdzieck\w*\b", "Dziecko (<= 12 lat)", 4),
]

HAZARD_PATTERNS: list[tuple[str, str, int]] = [
    (r"\b(rzek\w*|rozlewisk\w*|bagn\w*|jezior\w*|staw\w*|kanał\w*|strumie\w*|potok\w*|szuwar\w*|studni\w*|zalew\w*|torfowisk\w*|woda|do wody)\b", "Bliskosc wody / bagien / studni", 3),
    (r"\b(mgła|zawieja|śnieg\w*|mróz|noc\b|zmierzch|zmrok|deszcz\w*|[0-5]\s*°C|-\d+\s*°C)\b", "Hipotermia / trudna pogoda / noc", 2),
    (r"\b(bez telefonu|brak telefonu|zostawił telefon|nie ma telefonu|brak kurtki|w samej bluzie|w podomce|boso|kapciach)\b", "Brak lączności lub odpowiedniego ubioru", 2),
]

SECTOR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


@dataclass
class TacticalAssessment:
    alarm_level: str          # KRYTYCZNY | WYSOKI | PODWYZSZONY
    risk_score: int
    golden_window_min: int
    risk_factors: list[str]
    timeline_anomalies: list[dict]
    sectors: list[dict]


def _extract_times_hhmm(text: str) -> list[int]:
    out = []
    for m in re.finditer(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text):
        out.append(int(m.group(1)) * 60 + int(m.group(2)))
    return out


def _fmt_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def compute_deterministic_risk(messages: list[dict], meta: dict) -> tuple[str, int, int, list[str]]:
    """Wylicza Poziom Alarmu i Zlote Okno na podstawie potwierdzonych faktow ze zrodel."""
    blob = " ".join(m.get("text", "") for m in messages)
    pogoda = (meta or {}).get("pogoda", "")
    full = f"{blob} {pogoda}".lower()

    score = 0
    factors: list[str] = []
    seen = set()

    for pat, label, pts in MEDICAL_PATTERNS + HAZARD_PATTERNS:
        if re.search(pat, full, re.IGNORECASE) and label not in seen:
            seen.add(label)
            factors.append(label)
            score += pts

    if score >= 6 or any("autoagresji" in f or "Dziecko" in f or "Cukrzyca" in f for f in factors):
        level = "KRYTYCZNY"
        window = 45
    elif score >= 3:
        level = "WYSOKI"
        window = 90
    else:
        level = "PODWYŻSZONY"
        window = 180

    return level, score, window, factors


def detect_timeline_anomalies(messages: list[dict]) -> list[dict]:
    """Deterministyczna kontrola chronologii: czy obserwacja nie wyprzedza czasu wyjscia zaginionego."""
    departure_min: int | None = None
    departure_msg: dict | None = None
    observations: list[tuple[int, dict, str]] = []

    dep_re = re.compile(r"(wyszedł|wyszła|wypłynął|rozdzielili się|zaginął|zginęła|nie wrócił|zboczył)", re.I)
    obs_re = re.compile(r"(widział\w*|stał\w*|mijał\w*|szedł|szła|biegł\w*|kupował\w*|rozmawiał\w*|pokazuje)", re.I)

    for m in messages:
        txt = m.get("text", "")
        times = _extract_times_hhmm(txt)
        if not times:
            continue
        if dep_re.search(txt):
            # Pierwszy czas w meldunku wyjscia przyjmujemy jako godzine startu incydentu
            if departure_min is None:
                departure_min = times[0]
                departure_msg = m
        elif obs_re.search(txt):
            for t in times:
                observations.append((t, m, txt))

    anomalies: list[dict] = []
    if departure_min is not None and departure_msg is not None:
        for t, msg, txt in observations:
            if t < departure_min - 5:
                anomalies.append({
                    "ids": [departure_msg["id"], msg["id"]],
                    "type": "KONFLIKT CZASU",
                    "description": (
                        f"Meldunek {msg['id']} podaje obserwację o {_fmt_hhmm(t)}, czyli przed zadeklarowanym "
                        f"wyjściem/zaginięciem o {_fmt_hhmm(departure_min)} ({departure_msg['id']}). "
                        "Możliwy błąd zegara świadka albo inna osoba o podobnym ubiorze."
                    ),
                    "severity": "wysoka",
                })
    return anomalies


def build_sector_grid(
    messages: list[dict],
    meta: dict,
    slm_sectors: list[dict] | None = None,
    conflicts: list[dict] | None = None,
) -> list[dict]:
    """Buduje 6-sektorowa siatke taktyczna (A1..C2) laczac wskazania SLM i twarde dowody terenowe."""
    teren = dict((meta or {}).get("teren") or {})
    slm_by_code = {str(s.get("code", "")).upper(): s for s in (slm_sectors or []) if s.get("code")}
    conflict_ids = {cid for c in (conflicts or []) for cid in c.get("ids", [])}

    sectors: list[dict] = []
    for code in SECTOR_ORDER:
        label = teren.get(code, "")
        if not label and code in slm_by_code:
            label = slm_by_code[code].get("name", f"Sektor {code}")
        if not label:
            label = f"Sektor {code}"

        mentions: list[str] = []
        has_physical = False
        has_conflict = False
        has_hazard = False

        code_re = re.compile(rf"\b{re.escape(code)}\b")
        label_words = [w.lower() for w in re.findall(r"[a-ząćęłńóśźż]{4,}", label, re.I)]

        for m in messages:
            txt = m.get("text", "")
            matched = bool(code_re.search(txt)) or any(w in txt.lower() for w in label_words)
            if matched:
                mentions.append(m["id"])
                if re.search(r"ślad\w*|koszyk|krew|pasek|sandał\w*|piła|kajak|katana|telefon|kamera|pies", txt, re.I):
                    has_physical = True
                if re.search(r"rzek\w*|rozlewisk\w*|bagn\w*|studni\w*|żleb\w*|skarpy|szuwar\w*|kanał\w*|torfowisk\w*|zalew\w*|potok\w*|staw", txt, re.I):
                    has_hazard = True
                if m["id"] in conflict_ids:
                    has_conflict = True

        slm_info = slm_by_code.get(code, {})
        slm_prio = int(slm_info.get("priority", 0)) if str(slm_info.get("priority", "")).isdigit() else 0

        score = 0
        if has_physical:
            score += 4
        if has_hazard:
            score += 3
        score += len(mentions) * 2
        if slm_prio == 1:
            score += 5
        elif slm_prio == 2:
            score += 2
        if has_conflict and not has_physical:
            score -= 1

        reason = slm_info.get("reason", "")
        if not reason:
            parts = []
            if has_physical:
                parts.append("ślad fizyczny")
            if has_hazard:
                parts.append("zagrożenie terenowe/woda")
            if has_conflict:
                parts.append("wymaga weryfikacji konfliktu")
            reason = ", ".join(parts) if parts else "brak bezpośrednich śladów"

        sectors.append({
            "code": code,
            "name": label,
            "raw_score": score,
            "mentions": mentions,
            "has_physical": has_physical,
            "has_conflict": has_conflict,
            "reason": reason,
        })

    # Przypisz rangi PRIORYTET 1 / PRIORYTET 2 / NISKI deterministycznie po raw_score
    ranked = sorted(sectors, key=lambda s: s["raw_score"], reverse=True)
    for idx, s in enumerate(ranked):
        if idx == 0 and s["raw_score"] > 0:
            s["priority"] = 1
            s["badge"] = "PRIORYTET 1"
        elif idx <= 2 and s["raw_score"] > 0:
            s["priority"] = 2
            s["badge"] = "PRIORYTET 2"
        else:
            s["priority"] = 3
            s["badge"] = "NISKI / REZERWA"

    return sectors


def ground_and_verify(
    slm_data: dict,
    messages: list[dict],
    meta: dict,
) -> tuple[dict, TacticalAssessment]:
    """Waliduje wynik SLM wobec zrodel i laczy z deterministycznymi regulami."""
    valid_ids = {m["id"] for m in messages}

    level, r_score, window, factors = compute_deterministic_risk(messages, meta)
    det_anomalies = detect_timeline_anomalies(messages)

    # Odfiltruj halucynowane ID meldunkow w klastrach i konfliktach
    clusters = []
    for cl in slm_data.get("klastry_sladow", []) or []:
        if not isinstance(cl, dict):
            continue
        ids = [i for i in (cl.get("ids") or []) if i in valid_ids]
        phrases = [str(p) for p in (cl.get("frazy") or []) if p]
        if phrases:
            clusters.append({
                "tytul": str(cl.get("tytul", "Powiązany ślad")),
                "frazy": phrases,
                "ids": ids,
                "uzasadnienie": str(cl.get("uzasadnienie", "")),
            })

    conflicts: list[dict] = []
    seen_pairs: set[tuple[str, ...]] = set()
    for c in slm_data.get("sprzecznosci", []) or []:
        if not isinstance(c, dict):
            continue
        ids = [i for i in (c.get("ids") or []) if i in valid_ids]
        key = tuple(sorted(ids)) if ids else (str(c.get("opis", ""))[:40],)
        if c.get("opis"):
            conflicts.append({
                "ids": ids,
                "type": str(c.get("typ", "KONFLIKT")),
                "description": str(c.get("opis")),
                "severity": str(c.get("waga", "wysoka")),
            })
            seen_pairs.add(key)

    for det in det_anomalies:
        key = tuple(sorted(det["ids"]))
        if key not in seen_pairs:
            conflicts.insert(0, det)

    sectors = build_sector_grid(messages, meta, slm_data.get("sektory"), conflicts)

    # Zweryfikowana os czasu
    timeline = []
    for ev in slm_data.get("os_czasu", []) or []:
        if not isinstance(ev, dict):
            continue
        mid = ev.get("id", "")
        if mid and mid not in valid_ids:
            continue
        timeline.append({
            "time": str(ev.get("czas", "")),
            "id": str(mid),
            "event": str(ev.get("zdarzenie", "")),
            "confidence": str(ev.get("pewnosc", "średnia")),
        })
    if not timeline:
        for m in messages:
            times = _extract_times_hhmm(m.get("text", ""))
            t_str = _fmt_hhmm(times[0]) if times else m.get("time", "")
            timeline.append({"time": t_str, "id": m["id"], "event": m["text"][:140], "confidence": "źródło"})
    timeline.sort(key=lambda ev: ev.get("time") or "99:99")

    questions = [str(q).strip() for q in (slm_data.get("pytania_do_swiadkow") or []) if str(q).strip()]
    # Jesli SLM zwrocil za malo pytan (lub uciete przy limicie tokenow), dopelnij deterministycznie z faktow
    if len(questions) < 2:
        for c in conflicts[:2]:
            c_ids = ", ".join(c.get("ids") or []) or "źródła"
            q = f"Zweryfikuj konflikt [{c_ids}]: ustal dokładną godzinę na zegarku świadka i czy opis ubioru dotyczy tej samej osoby."
            if q not in questions:
                questions.append(q)
        top_sec = next((s for s in sectors if s.get("priority") == 1), None)
        if top_sec and len(questions) < 3:
            questions.append(f"Skieruj pierwszą grupę / drona do sektora {top_sec['code']} ({top_sec['name']}) i potwierdź fizyczne ślady.")
        if factors and len(questions) < 4:
            questions.append(f"Potwierdź z rodziną stan zdrowia i leki: {factors[0]}.")
    questions = questions[:5]
    profil = slm_data.get("profil_zaginionego") or {}

    cleaned = {
        "profil_zaginionego": {
            "osoba": str(profil.get("osoba", "Brak pełnych danych")),
            "ubior": str(profil.get("ubior", "")),
            "zdrowie": str(profil.get("zdrowie", "")),
            "kierunek": str(profil.get("kierunek", "")),
        },
        "klastry_sladow": clusters,
        "sprzecznosci": conflicts,
        "os_czasu": timeline,
        "pytania_do_swiadkow": questions,
    }
    assessment = TacticalAssessment(
        alarm_level=level,
        risk_score=r_score,
        golden_window_min=window,
        risk_factors=factors,
        timeline_anomalies=det_anomalies,
        sectors=sectors,
    )
    return cleaned, assessment


def run_regex_baseline(messages: list[dict], meta: dict) -> tuple[dict, TacticalAssessment]:
    """Celowo naiwny baseline bez SLM: wylacznie regexy i slowa kluczowe (do porownania w demo i benchmarku)."""
    blob = " ".join(m.get("text", "") for m in messages)
    level, r_score, window, factors = compute_deterministic_risk(messages, meta)
    det_anomalies = detect_timeline_anomalies(messages)

    # Regex potrafi znalezc tylko doslowne slowa ubran, nie skleja synonimow (np. anorak <-> kurtka)
    clothes = re.findall(r"\b(kurtk\w*|bluz\w*|anorak\w*|beret\w*|czapk\w*|kalosz\w*|plecak\w*|kask\w*)\b", blob, re.I)
    clusters = []
    if clothes:
        clusters.append({
            "tytul": "Dosłowne słowa (brak koreferencji)",
            "frazy": list(dict.fromkeys(clothes))[:6],
            "ids": [m["id"] for m in messages[:2]],
            "uzasadnienie": "Dopasowanie wyłącznie leksykalne — regex nie łączy synonimów (np. bordowy anorak ↔ czerwona kurtka).",
        })

    sectors = build_sector_grid(messages, meta, slm_sectors=None, conflicts=det_anomalies)
    timeline = [
        {
            "time": _fmt_hhmm(_extract_times_hhmm(m["text"])[0]) if _extract_times_hhmm(m["text"]) else m.get("time", ""),
            "id": m["id"],
            "event": m["text"][:130],
            "confidence": "regex",
        }
        for m in messages
    ]

    return {
        "profil_zaginionego": {
            "osoba": "Tryb Regex — brak syntezy opisu osoby",
            "ubior": ", ".join(dict.fromkeys(clothes)) or "nie wyodrębniono",
            "zdrowie": ", ".join(factors) or "brak dopasowań słownikowych",
            "kierunek": "wymaga analizy SLM",
        },
        "klastry_sladow": clusters,
        "sprzecznosci": det_anomalies,
        "os_czasu": timeline,
        "pytania_do_swiadkow": ["Tryb Regex nie generuje pytań weryfikacyjnych — włącz analizę SLM."],
    }, TacticalAssessment(
        alarm_level=level,
        risk_score=r_score,
        golden_window_min=window,
        risk_factors=factors,
        timeline_anomalies=det_anomalies,
        sectors=sectors,
    )
