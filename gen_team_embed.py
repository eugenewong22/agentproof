"""Regenerate demo.html's TEAM_EMBED from data/demo_team.json (+ xlsx skill trees).

Run after any change to data/demo_team.json:  python3 gen_team_embed.py
Keeps demo.html's scripted standalone mode in lockstep with the manifest that
dashboard.py injects in real mode (both use dashboard.build_team())."""
import json, pathlib, re

import dashboard

team = dashboard.build_team()
if team is None:
    raise SystemExit("data/demo_team.json missing — nothing to embed")

js = json.dumps(team, separators=(",", ":")).replace("</", "<\\/")
p = pathlib.Path("demo.html")
src = p.read_text()
new, n = re.subn(r"const TEAM_EMBED=.*?;//GEN",
                 lambda m: f"const TEAM_EMBED={js};//GEN",   # lambda: no template escapes
                 src, count=1, flags=re.S)
if n != 1:
    raise SystemExit("TEAM_EMBED marker not found in demo.html")
p.write_text(new)
print(f"embedded {len(js):,} bytes · {len(team['agents'])} agents · "
      f"{sum(len(a['sk']) for a in team['agents'])} skills across trees")
