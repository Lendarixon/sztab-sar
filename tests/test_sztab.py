"""Testy jednostkowe Sztab-SAR: weryfikator ryzyka, kolizje czasu, ugruntowanie ID i baseline vs SLM."""
from __future__ import annotations

from sar.pipeline import build_rozkaz_html, run_sar_analysis
from sar.rules import compute_deterministic_risk, detect_timeline_anomalies, ground_and_verify
from sar.scenarios import DEMO_SCENARIOS
from sar.slm_extract import SlmExtractResult, parse_slm_json


def test_deterministic_medical_and_hazard_scoring():
    sc = DEMO_SCENARIOS[0]
    level, score, window, factors = compute_deterministic_risk(sc["messages"], sc["meta"])
    assert level == "KRYTYCZNY"
    assert window <= 45
    assert any("Cukrzyca" in f for f in factors)
    assert any("wody" in f.lower() for f in factors)


def test_timeline_conflict_detected_before_departure():
    msgs = [
        {"id": "M1", "time": "14:40", "source": "Rodzina", "text": "Wyszedł z domu o 13:30 na spacer."},
        {"id": "M2", "time": "14:55", "source": "Świadek", "text": "Widziałem go na przystanku już o 13:10."},
    ]
    anomalies = detect_timeline_anomalies(msgs)
    assert len(anomalies) == 1
    assert anomalies[0]["ids"] == ["M1", "M2"]
    assert anomalies[0]["type"] == "KONFLIKT CZASU"


def test_grounding_filters_hallucinated_ids():
    sc = DEMO_SCENARIOS[0]
    fake_slm = {
        "profil_zaginionego": {"osoba": "Janusz K., 74 l.", "ubior": "czerwona kurtka", "zdrowie": "cukrzyca", "kierunek": "Brda A2"},
        "klastry_sladow": [
            {"tytul": "Kurtka", "frazy": ["czerwona kurtka", "bordowy anorak"], "ids": ["M1", "M2", "M99"], "uzasadnienie": "Synonimy"}
        ],
        "sprzecznosci": [],
        "os_czasu": [{"czas": "14:15", "id": "M2", "zdarzenie": "Leśniczówka", "pewnosc": "wysoka"}, {"czas": "19:00", "id": "M99", "zdarzenie": "Fake", "pewnosc": "niska"}],
        "sektory": [{"code": "A2", "priority": 1, "reason": "Ślady nad Brdą"}],
        "pytania_do_swiadkow": ["Czy miał laskę?"],
    }
    cleaned, assessment = ground_and_verify(fake_slm, sc["messages"], sc["meta"])
    assert "M99" not in cleaned["klastry_sladow"][0]["ids"]
    assert all(ev["id"] != "M99" for ev in cleaned["os_czasu"])
    assert assessment.sectors[0]["code"] in ("A1", "A2", "B1", "B2", "C1", "C2")
    top = [s for s in assessment.sectors if s["priority"] == 1][0]
    assert top["code"] == "A2"


def test_parse_slm_json_handles_fences():
    raw = 'Oto analiza:\n```json\n{"profil_zaginionego": {"osoba": "Test"}, "sektory": [{"code": "A1", "priority": 1}]}\n```'
    parsed = parse_slm_json(raw)
    assert parsed["profil_zaginionego"]["osoba"] == "Test"
    assert parsed["sektory"][0]["code"] == "A1"


def test_regex_vs_slm_and_export_html():
    sc = DEMO_SCENARIOS[1]
    res_rx = run_sar_analysis(sc["messages"], sc["meta"], use_slm=False)
    assert res_rx["mode"] == "regex"
    assert res_rx["assessment"]["alarm_level"] in ("KRYTYCZNY", "WYSOKI")

    mock_slm = lambda ms, mt: SlmExtractResult(
        data={
            "profil_zaginionego": {"osoba": "Marek W., 39 l.", "ubior": "żółta wiatrówka", "zdrowie": "uraz kostki", "kierunek": "żleb B1"},
            "klastry_sladow": [{"tytul": "Kurtka", "frazy": ["żółta wiatrówka", "musztardowa kurtka"], "ids": ["M1", "M2"], "uzasadnienie": "Synonimy koloru"}],
            "sprzecznosci": [{"ids": ["M2", "M3"], "typ": "KONFLIKT KIERUNKU", "opis": "M3 twierdzi że zszedł na polanę, ale M2 i M4 wskazują na żleb B1", "waga": "wysoka"}],
            "os_czasu": [],
            "sektory": [{"code": "B1", "priority": 1, "reason": "Ślady ześlizgnięcia i pasek plecaka"}],
            "pytania_do_swiadkow": ["Czy bramka alarmowa miała zapis wideo?"],
        },
        raw_text="{}",
        latency_ms=420,
        ok=True,
    )
    res_slm = run_sar_analysis(sc["messages"], sc["meta"], use_slm=True, classify_fn=mock_slm)
    assert res_slm["mode"] == "slm"
    assert len(res_slm["analysis"]["klastry_sladow"][0]["frazy"]) == 2
    html_out = build_rozkaz_html(res_slm, sc["meta"], sc["messages"])
    assert "Karta Poszukiwań" in html_out
    assert "B1" in html_out
