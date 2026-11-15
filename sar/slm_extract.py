"""Ekstrakcja semantyczna, koreferencja i analiza sprzecznosci przez lokalny SLM (<10B)."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import dataclass

SYSTEM_PROMPT = """Jesteś koordynatorem sztabu poszukiwawczo-ratowniczego (OSP / GOPR / Policja).
Analizujesz surowe meldunki terenowe i zeznania świadków dotyczące osoby zaginionej.
Zwróć WYŁĄCZNIE zwarty JSON (w jednej linii, bez komentarzy i markdown) o strukturze:
{"profil_zaginionego":{"osoba":"imię/wiek/cechy","ubior":"pełny ubiór z meldunków","zdrowie":"choroby, leki, urazy","kierunek":"ostatni pewny kierunek"},"klastry_sladow":[{"tytul":"krótka nazwa tropu","frazy":["dokładny cytat ubioru/cechy z M1","synonim z M2"],"ids":["M1","M2"],"uzasadnienie":"dlaczego to ten sam trop"}],"sprzecznosci":[{"ids":["M1","M3"],"typ":"KONFLIKT CZASU|KONFLIKT KIERUNKU|FAŁSZYWY TROP","opis":"konkretna rozbieżność godzin lub miejsc","waga":"wysoka"}],"sektory":[{"code":"A2","priority":1,"reason":"krótkie uzasadnienie"}],"pytania_do_swiadkow":["max 3 krótkie pytania do dyspozytora"]}
Zasady:
1. W `klastry_sladow` ZAWSZE łącz w pary synonimy z różnych meldunków opisujące tę samą część ubioru, przedmiot lub uraz (np. różnice odcieni kolorów, fasonów kurtek/bluz/butów/plecaków lub objawów typu utykanie ↔ uraz). Podawaj dokładne frazy z tekstu.
2. Wykrywaj sprzeczne godziny, przeciwne kierunki i fałszywe tropy w `sprzecznosci`.
3. Podawaj wyłącznie istniejące ID (M1, M2...). Bądź zwięzły, pisz po polsku."""


@dataclass
class SlmExtractResult:
    data: dict
    raw_text: str
    latency_ms: int
    ok: bool


def format_prompt_payload(messages: list[dict], meta: dict) -> str:
    teren = (meta or {}).get("teren") or {}
    teren_lines = ", ".join(f"{k}: {v}" for k, v in teren.items())
    msg_lines = "\n".join(
        f"[{m['id']} | {m.get('time', '--:--')} | {m.get('source', 'Meldunek')}] {m.get('text', '')}"
        for m in messages
    )
    return (
        f"Lokalizacja: {(meta or {}).get('miejsce', 'nieznana')}\n"
        f"Pogoda/warunki: {(meta or {}).get('pogoda', 'brak danych')}\n"
        f"Sektory mapy: {teren_lines}\n\n"
        f"Meldunki wejściowe:\n{msg_lines}\n\n"
        f"Zwróć wyłącznie JSON:"
    )


def parse_slm_json(raw: str) -> dict:
    """Wyciaga JSON nawet jesli model otoczy go blokiem markdown lub tekstem."""
    txt = (raw or "").strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", txt, re.S)
    if fence:
        txt = fence.group(1)
    else:
        s = txt.find("{")
        e = txt.rfind("}")
        if s != -1 and e > s:
            txt = txt[s : e + 1]
    try:
        parsed = json.loads(txt)
        return parsed if isinstance(parsed, dict) else {}
    except ValueError:
        # Proba lekkiej naprawy urwanych nawiasow
        for suffix in ("}", "]}", '"}', '"]}'):
            try:
                parsed = json.loads(txt + suffix)
                if isinstance(parsed, dict):
                    return parsed
            except ValueError:
                pass
        return {}


def classify_via_llama_http(messages: list[dict], meta: dict, llama_url: str = "http://127.0.0.1:8794/v1/chat/completions") -> SlmExtractResult:
    """Wywoluje lokalny serwer llama.cpp po HTTP (100% offline)."""
    user_payload = format_prompt_payload(messages, meta)
    body = json.dumps({
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_payload},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.0,
        "max_tokens": 520,
    }).encode("utf-8")

    t0 = time.perf_counter()
    req = urllib.request.Request(llama_url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode("utf-8"))
    content = resp["choices"][0]["message"]["content"]
    ms = int((time.perf_counter() - t0) * 1000)
    data = parse_slm_json(content)
    return SlmExtractResult(data=data, raw_text=content, latency_ms=ms, ok=bool(data))
