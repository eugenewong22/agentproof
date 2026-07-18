def gap_report(results):
    """coverage = (1 - sum(gap)/sum(required)) * 100 — scale-agnostic (works on 1-6)."""
    total_req = sum(r["required_level"] for r in results) or 1
    total_gap = sum(r["gap"] for r in results)
    coverage = round((1 - total_gap / total_req) * 100, 1)
    gaps = sorted((r for r in results if r["gap"] > 0), key=lambda r: -r["gap"])
    return {"coverage_pct": coverage, "gaps": gaps, "results": results}

def print_report(report, label=""):
    print(f"\n=== {label}  role-readiness (executed): {report['coverage_pct']}% ===")
    for r in report["results"]:
        bar = "#" * int(r["score"] * 20)
        flag = "   <-- gap" if r["gap"] else ""
        note = f"  ({r['error']})" if r.get("error") else ""
        print(f"  {r['skill'][:28]:28} L{r['held_level']}/{r['required_level']}"
              f"  score {r['score']:.2f} |{bar:<20}|{flag}{note}")
