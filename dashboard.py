import json, html, pathlib, webbrowser

def bar(pct, color):
    return ('<span style="display:inline-block;background:#1d2735;border-radius:4px;'
            'width:260px;height:14px;vertical-align:middle">'
            f'<span style="display:block;width:{max(2, pct):.0f}%;height:14px;'
            f'border-radius:4px;background:{color}"></span></span>')

def main():
    out = json.load(open("output.json"))
    spec = pathlib.Path("agent_final.md").read_text()
    first, last = out["rounds"][0], out["rounds"][-1]
    rows = ""
    for b, f in zip(first["results"], last["results"]):
        rows += (f"<tr><td style='padding:6px 14px'>{html.escape(b['skill'])} "
                 f"(L{b['required_level']})</td>"
                 f"<td>{bar(b['score']*100, '#ef5350')} {b['score']*100:.0f}%</td>"
                 f"<td>{bar(f['score']*100, '#28c76f')} {f['score']*100:.0f}%</td></tr>")
    rub = out.get("rubric")
    rub_html = ""
    if rub:
        rub_html = (f"<p style='color:#f5a623'>&#9675; Rubric-assessed: "
                    f"<b>{rub['covered']}/{rub['total']}</b> K&amp;A items ({rub['pct']}%) "
                    f"&mdash; <em>NOT execution-verified · never blended</em></p>")
    page = f"""<!doctype html><meta charset="utf-8"><title>AgentProof</title>
<body style="font-family:-apple-system,sans-serif;background:#0a0e13;color:#e8eef5;padding:32px">
<h1 style="margin:0">{html.escape(out['role'])}</h1>
<p style="color:#8b98a7">{html.escape(out['sector'])} · {html.escape(out['track'])} ·
source: SkillsFuture Skills Framework</p>
<h2 style="color:#28c76f">&#10004; Executed: {first['coverage_pct']}% &rarr;
{last['coverage_pct']}% role-readiness</h2>
{rub_html}
<table style="border-collapse:collapse"><tr style="color:#8b98a7;text-align:left">
<th style="padding:6px 14px">skill</th><th>baseline</th><th>refined</th></tr>{rows}</table>
<p style="color:#8b98a7;margin-top:18px">Every green bar = code THIS agent wrote that ran
in a Daytona sandbox.</p>
<h2>Delivered agent spec (agent_final.md)</h2>
<pre style="background:#111823;border:1px solid #1d2735;border-radius:10px;padding:18px;
white-space:pre-wrap;font-size:12.5px">{html.escape(spec)}</pre></body>"""
    pathlib.Path("dashboard.html").write_text(page)
    webbrowser.open("file://" + str(pathlib.Path("dashboard.html").resolve()))
    print("dashboard.html opened")

if __name__ == "__main__":
    main()
