"""AgentProof dashboard — renders the 4-screen demo UI (design_handoff_agentproof_demo).

Injects REAL pipeline data (output.json scores, sandbox ids, agent_final.md, live
Oxylabs salary) into demo.html. With no run artifacts, demo.html stands alone with
the design's scripted data — this script then just opens it as-is.
"""
import json, pathlib, re, webbrowser


def load_real():
    """Build the window.AP_REAL payload from run artifacts. None -> scripted mode."""
    p = pathlib.Path("output.json")
    if not p.exists():
        return None
    out = json.load(open(p))
    spec_p = pathlib.Path("agent_final.md")
    spec = spec_p.read_text() if spec_p.exists() else ""

    first, last = out["rounds"][0]["results"], out["rounds"][-1]["results"]
    skills = []
    for b, f in zip(first, last):   # executed track: real scores, sandbox ids, timings
        skills.append({
            "id": re.sub(r"[^A-Za-z0-9]+", "-", b.get("code") or b["skill"]).lower(),
            "nm": b["skill"], "off": b["required_level"], "exec": 1,
            "base": round(b["score"] * 100), "ref": round(f["score"] * 100),
            "req": b["required_level"], "gapBase": b["gap"], "gapRef": f["gap"],
            "sid": f.get("sandbox_id") or "", "secs": f.get("seconds"),
            "ka": f"graded in Daytona sandbox {str(f.get('sandbox_id') or '?')[:8]}… · "
                  f"{f.get('seconds', '?')}s · score from real execution",
        })
    rub = out.get("rubric")
    if rub:
        for i, s in enumerate(rub["skills"]):   # rubric track: judged once on final spec
            skills.append({
                "id": f"rub{i}", "nm": s["skill"], "off": s["level"], "exec": 0,
                "base": round(s["pct"]), "ref": round(s["pct"]),
                "covered": s["covered"], "total": s["total"],
                "ka": f"{s['covered']}/{s['total']} K&A items · LLM judge · "
                      f"NOT execution-verified",
            })

    salary = None
    try:                       # §10 forced-visible: live salary band if Oxylabs answers
        import oxylabs_fetch
        band = oxylabs_fetch.fetch_salary_band(out["role"])
        if band:
            salary = {"low": band["low"], "high": band["high"], "live": True}
            print(f"Oxylabs: live salary band S${band['low']}–{band['high']}")
    except Exception:
        pass

    return {"role": out["role"], "sector": out["sector"], "track": out.get("track", ""),
            "rounds": len(out["rounds"]),
            "totalSkills": len(first) + (len(rub["skills"]) if rub else 0),
            "batteryCount": len(first),
            "skills": skills, "spec": spec, "salary": salary}


def main():
    tpl_p = pathlib.Path("demo.html")
    if not tpl_p.exists():
        raise SystemExit("demo.html missing — the UI template must sit next to dashboard.py")
    page = tpl_p.read_text()
    real = load_real()
    if real:
        payload = json.dumps(real).replace("</", "<\\/")   # keep </script> in spec text inert
        page = page.replace("<!--AP_REAL-->",
                            f"<script>window.AP_REAL = {payload};</script>")
        print(f"dashboard: REAL mode — {real['batteryCount']} executed skills, "
              f"{len(real['skills']) - real['batteryCount']} rubric skills, "
              f"{real['rounds']} round(s)")
    else:
        print("dashboard: no output.json — scripted demo mode")
    out_p = pathlib.Path("dashboard.html")
    out_p.write_text(page)
    webbrowser.open("file://" + str(out_p.resolve()))
    print("dashboard.html opened")


if __name__ == "__main__":
    main()
