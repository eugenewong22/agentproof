# Handoff: AgentProof Hackathon Demo UI

## Overview
AgentProof is a verifiable proving ground for role-specialized AI agents (Daytona HackSprint, NUS Singapore). The UI is a 4-screen stage-demo flow: **Request → Skill Loadout → Build & Prove → Deliver**. A user picks a real SkillsFuture role, tunes an RPG-style skill loadout, then watches a scripted run: the agent's code is "executed" in parallel Daytona sandboxes, gaps are found, the agent is refined, and the lift is shown (baseline % → refined %). Repo context: https://github.com/eugenewong22/agentproof (see UX_FLOW.md — this UI implements its MVP flow plus the proof-budget stretch goal).

## About the Design Files
The bundled `AgentProof Demo.dc.html` is a **design reference created in HTML** — a prototype showing intended look and behavior, not production code to copy directly. Recreate it in the target codebase's environment (the repo is Python + a static dashboard; a single static HTML/JS page or a small React app both fit). The prototype's simulation timeline should be replaced by real pipeline events (`run.py` fan-out, `assess.py` grades) where available.

## Fidelity
**High-fidelity.** Colors, type, spacing, copy, and animation timings are final. Recreate pixel-perfectly. Designed for stage projection: dark, high contrast, large type, min ~11px mono fine print at 1240px content width.

## Design Tokens
Colors:
- Background `#0A0A0C` · panel `#131316` · inset/terminal panel `#0E0E11`
- Hairline/border `#232328` · row divider `#1A1A1E` · inactive pip border `#2A2A30`
- Ink `#F4F3EE` · muted `#9C9BA0` · dim `#5F5F66`
- **Lime (accent, "executed/verified/primary") `#C8F135`** — dim tints `rgba(200,241,53,.07/.09/.12)`; passed-sandbox border `#4E661F`
- **Amber (baseline / over-baseline / rubric) `#F5B83D`** — partial-sandbox border `#66551F`
- Red (over-budget / "never blend" warning) `#FF6459`
- Bar gradient: `linear-gradient(90deg,#8CC63F,#C8F135)`
- Selection: lime bg, dark text. Links: `#C8F135`, hover `#E2FF7A`.

Typography (Google Fonts):
- **Unbounded** (500/700/900) — brand wordmark, screen titles (30px/700), big numerals (76–112px/900), level labels (19px/700)
- **Space Grotesk** (400–700) — body (17px), headlines (52px/900 on Request), buttons
- **IBM Plex Mono** (400–600) — all labels/eyebrows (10.5–13px, letter-spacing 1–3px, uppercase), terminal lines (13px), stats, notes

Spacing/shape: sharp corners everywhere (0 radius) except pill sponsor chips (999px). Panels: 1px border, 24–34px padding. Content max-width 1240px, 44px side padding. Progress bars 12px tall. Pips 32×23px.

## Screens / Views

### Persistent header (sticky, all screens)
- Left: 38px lime square with black Unbounded "A" + "AGENTPROOF" (Unbounded 15px/700) + tagline "verified by execution, not by claim" (mono 11px, muted)
- Center: step rail — 4 buttons `01 REQUEST / 02 LOADOUT / 03 PROVE / 04 DELIVER` (mono 12px, 1px border). Current = lime text+border; visited = ink; future = dim. Buttons navigate directly (presenter escape hatch).
- Right: 5 sponsor chips (pills, mono 11.5px, 6px dot): SkillsFuture, Oxylabs, Kimi, Daytona, Nosana. Unlit = dim/border `#232328`; **lit = lime border, ink text, lime dot with `0 0 10px rgba(200,241,53,.8)` glow**, .4s transition. Lighting is cumulative: SkillsFuture from start; Kimi at spec-gen; Daytona+Nosana at sandbox fan-out; Oxylabs on Deliver.
- Header wraps (`flex-wrap`) so chips never clip on narrow viewports.

### 01 Request
Two-column grid (1.05fr/.95fr, 64px gap). Left: lime mono eyebrow `01 · REQUEST AN AGENT`; headline "HIRE AN AGENT. WATCH IT PROVE ITSELF." (Unbounded 52px/900, last phrase lime); 20px muted paragraph; mono stat strip ("1,977 official roles · 0 invented skills · 100% of green bars ran as code").
Right panel: two mode tabs (active "● I know the role" lime-bordered; "○ Describe the task" disabled/dim); selected role card (lime-tinted `rgba(200,241,53,.05)`, border `#2E3A16`) — "Data Analyst / Associate Data Engineer", meta: Sector "Infocomm Technology", SSOC `25131`, "14 · 6 in battery"; Custom instructions textarea (default "Focus on messy inputs; flag anything ambiguous." — carried into the generated spec); full-width lime CTA "Next · Skill loadout →" (dark text, 18px/700).

### 02 Skill Loadout
Header: eyebrow + role title; subtext "◆ official required level is free · pushing above it spends proof budget · L0 drops the skill".
Right of header: preset buttons BASELINE / SPECIALIZE / MAX (mono, hover lime) and the **proof-budget meter**: label, 8 blocks (13×20px), text "n / 8 pts". Blocks fill amber per point spent; if spent > 8 blocks turn red and text reads "n / 8 · over — bigger lift, longer build" (over-budget never blocks Generate).
Skill rows (6, in one panel, grid `34px 1fr auto 160px`):
- Toggle square 26px (lime-filled ✓ when on; row at 42% opacity when off)
- Name (17.5px/600) + badge: "✓ execution-verified" (lime on `rgba(200,241,53,.12)`) or "○ rubric only" (gray) + K&A line (mono 12px dim)
- 6 pips L1–L6: filled ≤ target; pips **above official level fill amber** (they cost budget), at/below fill lime; ◆ lime marker under the official pip; clicking pip N sets target N, clicking the active top pip steps down one (reaching 0 = off)
- Right: level "L4"/"OFF" (Unbounded 19px; lime, amber if over official) + note: "official · free" / "▲ +2 · spends 2 pts" (amber) / "▼ −1 below official" / "off · dropped from battery + spec"
Skills (id · official · mode · baseline% · refined%): Data Engineering L2 exec 71→96; Database Administration L2 exec 40→88; Data Analytics L2 exec 32→85; Data Visualisation L3 exec 58→94; Stakeholder Management L2 rubric 55→70; Data Ethics L1 rubric 44→66.
Defaults: eng2 dba2 **ana4 (▲+2)** viz3 stk2 **eth off** → 2/8 spent. Presets — Baseline: all official incl. eth1; Specialize: ana5 viz4, eth off; Max: all L6.
Footer: legend (✓ vs ○, "never blended") + lime "Generate agent →" (pulsing glow `ap-glow` 2.2s; disabled/gray when every skill is off).

### 03 Build & Prove (auto-runs on entry; ↻ replay restarts)
Grid `1fr 340px`:
- **Pipeline panel**: 5 steps, each icon (· idle dim / ▸ running lime / ✓ done) + label + sponsor tag: 1 Pull official skill profile + K&A rubric — SkillsFuture · 2 Generate agent spec v0 — Kimi · 3 Baseline, prove each skill in parallel — Daytona·Nosana · 4 Skills-gap report → rewrite guidance — Kimi · 5 Re-prove — Daytona. Below: live mono stage line in lime with blinking ▌ cursor.
- **Numbers panel**: "✓ EXECUTED" giant % (Unbounded 76px/900; white while running, lime when done) counting with ease-out cubic; below divider "○ RUBRIC-ASSESSED" amber % + "LLM judge · two numbers, never one blend".
- **Sandbox grid** (2 cols, one card per executable selected skill): name + level chip; terminal (mono 13px): `$ python solve.py` then `› booting isolated sandbox…` → `› executing agent code…` → `GRADE: PASS · 96%` (lime, ≥70) or `GRADE: PARTIAL · 40%` (amber). Status: "queued" → pulsing lime dot "running in sandbox" → "✓ sandbox exited 0" / "⚠ gap logged". Running card: lime border + light sweep overlay (`ap-sweep` 1.1s loop). Cards stagger (~170ms apart).
- **Coverage bars**: per selected skill — name, level, ✓ executed/○ rubric badge, `71% → 96%` mono readout ("—" until known); 12px track: amber baseline fill under lime-gradient refined fill, width transition 1.1s cubic-bezier(.4,0,.2,1).
Timeline (at 1×): steps ~1–1.5s each; baseline round → bars+counters fill → stage "baseline — executed 50% · 3 gaps found" → refine → re-prove → final stage "executed 91% · rubric 70% — gaps closed. spec saved → agent_final.md". Then pulsing "View the scorecard →" appears. Aggregates = round(mean) over selected exec / rubric skills (defaults: 50→91 exec, 55→70 rubric).

### 04 Delivered
- **Money shot**: BASELINE 66px dim numeral → lime arrow → "REFINED · EXECUTION-VERIFIED" 112px/900 lime numeral + "+41 pts lift / one refine pass" (mono).
- Side panel: "○ RUBRIC-ASSESSED 55% → 70%" (amber, Unbounded 38px), "K&A checklist · LLM judge / NOT execution-verified", red mono "two numbers · never one blend".
- **Scorecard**: same bar rows, final values, static.
- **Market strip (Oxylabs)**: salary card "S$4.2k – 7.8k" (lime, Unbounded 26px) "per month · SG market, scraped live"; career map — dashed nodes "Data / BI Analyst" → solid lime current node → "Senior Data Analyst" "Data Engineer", LATERAL "BI Developer" "Data Scientist".
- Footer: honesty note + buttons: lime "⬇ Download agent spec" (downloads generated `agent_final.md` — role, SSOC, custom instructions, loadout/proof table); "⧉ Copy spec" (clipboard, flashes "✓ copied" 1.6s); "⟳ Adjust loadout" (back to 02, state preserved — the re-spec loop).

## Interactions & Behavior
- Deselecting a skill (L0) removes it from the loadout math, sandbox grid, bars, aggregates, and the downloaded spec.
- Navigating to 03 always resets and reruns the simulation; a run-id guard cancels stale async timelines on nav/replay.
- Demo controls (tweakable props in the prototype): `simSpeed` (0.5–2.5×, divides all durations), `autoAdvance` (auto-jump to 04 ~2.8s after finish), `showBudget` (hide meter per MVP).
- Keyframes: `ap-pulse` (opacity blink), `ap-sweep` (terminal sweep), `ap-glow` (lime CTA glow).

## State Management
`screen` ('request'|'loadout'|'prove'|'deliver'), `instr` (string), `targets` ({skillId: 0–6}), `lit` (per-sponsor booleans, cumulative), simulation state (`steps[]`, `sbx[]` card states, bar width/pct maps, `execPct`, `rubPct`, `stage`, `runDone`, `copied`). Derived: spent budget, on/exec/rubric skill lists, aggregate means. Real integration: replace the scripted timeline with pipeline events from `run.py`/`assess.py`; scores per skill from `output.json`.

## Assets
None — no images. Fonts via Google Fonts: Unbounded, Space Grotesk, IBM Plex Mono. Glyphs are plain text (✓ ○ ◆ ▲ ▼ → ▸ ▌).

## Files
- `AgentProof Demo.dc.html` — the full prototype (markup, styles inline, simulation logic). Open in a browser to see every screen and the scripted run.
