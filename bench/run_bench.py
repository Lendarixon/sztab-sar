"""Benchmark Sztab-SAR (16 scenariuszy): Regex Baseline vs Bielik-4.5B vs Gemma-4-E4B."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sar.pipeline import run_sar_analysis  # noqa: E402
from sar.scenarios import BENCHMARK_CASES  # noqa: E402


def _norm(s: str) -> str:
    return (s or "").lower()


def _stem_match(term: str, blob: str) -> bool:
    t = _norm(term)
    b = _norm(blob)
    if t in b:
        return True
    words = [w[: max(4, len(w) - 2)] for w in t.split() if len(w) >= 4]
    return bool(words) and all(w in b for w in words)


def score_case(case: dict, result: dict) -> dict:
    exp = case["expected"]
    analysis = result.get("analysis", {})
    assessment = result.get("assessment", {})

    # 1. Coreference: czy oba synonimiczne okreslenia trafily do JEDNEGO klastra sladow
    coref_hit = False
    t1, t2 = exp["coref_terms"]
    for cl in analysis.get("klastry_sladow", []):
        joined = " ".join([cl.get("tytul", ""), cl.get("uzasadnienie", ""), " ".join(cl.get("frazy", []))])
        if _stem_match(t1, joined) and _stem_match(t2, joined):
            coref_hit = True
            break

    # 2. Wykrycie sprzecznosci (Conflict detection)
    pred_conflict = len(analysis.get("sprzecznosci", [])) > 0
    exp_conflict = bool(exp["has_conflict"])
    conflict_ok = (pred_conflict == exp_conflict)

    # 3. Wykrycie ryzyka zycia / medycznego (KRYTYCZNY)
    pred_med = assessment.get("alarm_level") == "KRYTYCZNY"
    med_ok = (pred_med == bool(exp["medical_risk"]))

    # 4. Sektor priorytet 1
    top_sectors = [s["code"] for s in assessment.get("sectors", []) if s.get("priority") == 1]
    sector_ok = exp["priority_sector"] in top_sectors

    return {
        "id": case["id"],
        "coref": coref_hit,
        "conflict_ok": conflict_ok,
        "pred_conflict": pred_conflict,
        "exp_conflict": exp_conflict,
        "med_ok": med_ok,
        "sector_ok": sector_ok,
        "top_sectors": top_sectors,
        "latency_ms": result.get("latency_ms", 0),
    }


def eval_mode(label: str, use_slm: bool, modal_url: str | None = None, model_key: str | None = None) -> dict:
    rows = []
    if modal_url and use_slm and model_key:
        req = urllib.request.Request(
            f"{modal_url.rstrip('/')}/api/model",
            data=json.dumps({"model": model_key}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            print(f"[{label}] Aktywny model na Modal:", json.loads(r.read().decode("utf-8")).get("model"))

    for case in BENCHMARK_CASES:
        if modal_url:
            req = urllib.request.Request(
                f"{modal_url.rstrip('/')}/api/analyze",
                data=json.dumps({
                    "messages": case["messages"],
                    "meta": case["meta"],
                    "use_slm": use_slm,
                    "model": model_key,
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                res = json.loads(r.read().decode("utf-8"))
        else:
            res = run_sar_analysis(case["messages"], case["meta"], use_slm=use_slm)
        row = score_case(case, res)
        rows.append(row)
        print(f"  {case['id']}: coref={row['coref']} conf={row['conflict_ok']} sec={row['sector_ok']} ({row['latency_ms']}ms)")

    n = len(rows)
    # Conflict F1
    tp = sum(1 for r in rows if r["pred_conflict"] and r["exp_conflict"])
    fp = sum(1 for r in rows if r["pred_conflict"] and not r["exp_conflict"])
    fn = sum(1 for r in rows if not r["pred_conflict"] and r["exp_conflict"])
    f1 = round((2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else 0.0, 3)

    summary = {
        "system": label,
        "n_cases": n,
        "coreference_acc": round(sum(1 for r in rows if r["coref"]) / n, 3),
        "conflict_acc": round(sum(1 for r in rows if r["conflict_ok"]) / n, 3),
        "conflict_f1": f1,
        "medical_risk_acc": round(sum(1 for r in rows if r["med_ok"]) / n, 3),
        "sector_top1_acc": round(sum(1 for r in rows if r["sector_ok"]) / n, 3),
        "avg_latency_ms": int(sum(r["latency_ms"] for r in rows) / n),
        "cases": rows,
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modal-url", default="", help="URL publiczny wdrozenia Modal (np. https://...modal.run)")
    ap.add_argument("--out", default=str(ROOT / "bench" / "eval_report.json"))
    args = ap.parse_args()

    results = []
    print("=== Ewaluacja: Regex Baseline ===")
    results.append(eval_mode("Regex Baseline (bez SLM)", use_slm=False))

    if args.modal_url:
        print("\n=== Ewaluacja: Bielik-4.5B-v3.0 (BPE Fix) ===")
        results.append(eval_mode("Bielik-4.5B-v3.0-Instruct (BPE Fix)", use_slm=True, modal_url=args.modal_url, model_key="bielik"))
        print("\n=== Ewaluacja: Gemma-4-E4B-it ===")
        results.append(eval_mode("Gemma-4-E4B-it", use_slm=True, modal_url=args.modal_url, model_key="gemma"))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nZapisano raport:", out_path)
    for r in results:
        print(
            f"  {r['system']}: Coref={r['coreference_acc']*100:.1f}% | "
            f"ConflictF1={r['conflict_f1']*100:.1f}% | SectorTop1={r['sector_top1_acc']*100:.1f}% | "
            f"Risk={r['medical_risk_acc']*100:.1f}% | AvgLatency={r['avg_latency_ms']}ms"
        )


if __name__ == "__main__":
    main()
