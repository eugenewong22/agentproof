# AgentProof — Implementation Plan (Daytona HackSprint)

> **Product in one line:** A lawyer (or any manager) requests an associate for a role and
> gives custom instructions. AgentProof pulls that role's **official** skills from the
> SkillsFuture Skills Framework, **generates the agent/team as a markdown spec**, then
> **proves it** by having *that generated agent* attempt a graded task for each skill inside
> isolated **Daytona** sandboxes — refining the spec until it's role-ready.
>
> **Deliverable = two artifacts stapled together:** (1) the agent/team markdown the user
> takes away, and (2) a role-readiness scorecard proving, by execution, that the exact spec
> being handed over covers X% of the role's required skills.
>
> **Demo money-shot:** per-skill bars going red → green with one headline number
> (e.g. **58% → 91% role-readiness**), where every green bar is code the *generated agent*
> wrote that provably ran in a Daytona sandbox.

---

## 0. What changed since v1 (two locked decisions)

| Decision | v1 (old guide) | v2 (this plan) | Consequence |
|---|---|---|---|
| **Test target** | The raw Kimi model (a hidden base prompt + injected tips) | **The generated agent** — the markdown spec is used *as the candidate's system prompt* | The thing tested IS the thing delivered. Kills the "the markdown was never the tested object" critique. |
| **Skill source** | Hardcoded 3-skill seed + Kimi inventing tasks from a bare skill name | **SkillsFuture Skills Framework** = authoritative role → skills → required levels; SSOC anchors the role | "Point it at a real role" is real, not a prop. Strongest card for *Innovation* + *Real-life problem*. |
| **Oxylabs role** | Scrape SSG skill definitions (redundant once we have the xlsx) | **Fetch live job postings / task material** for the role, feeding the task generator | Non-redundant, keeps all 4 sponsors load-bearing. |
| **Demo role** | "Data Analyst" (invented skills) | **"Data Analyst / Associate Data Engineer"** (real SFw role, executable skills) | Sandbox-execution grading is honest for this role. |

The seed battery and the offline fallbacks from v1 **stay** — they are the safety net (see §9).

**Entry now has two modes** (see UX_FLOW.md and §3 `classify.py`): the user picks a role, *or*
describes a task and the system recommends **real** SkillsFuture roles. Task mode never invents
roles or skills — it retrieves from the dataset — so the proof stays graded against an official bar.

---

## 0.5 — v3 (2026-07-15): the plan, VALIDATED — lessons from the production build

Between Jul 13–15 this exact design was built to production as **MakeMyTeam**
(`/Volumes/ExternalOne/MakeMyTeam` — a separate repo on NON-hackathon infra: Docker sandboxes,
Postgres, DashScope-served Kimi, React SPA). **Every pivot decision in §0 survived contact with
reality.** What follows is the knowledge you carry into Saturday: what's de-risked, the real bugs
you will otherwise lose an hour to, and production-verified constants. **The day-of code is still
built fresh, per this guide, on the hackathon stack** (Daytona SDK + `platform.moonshot.ai` Kimi +
Oxylabs) — check the event's rules on pre-existing code before reusing any verbatim source; the
plan and the lessons are yours either way.

### Validated — build these with confidence, they all work
- **Spec-as-system-prompt** (`candidate.py` identity swap): the graded object IS the deliverable. Works.
- **K&A grounding** (`get_ka`): the single highest-leverage add, exactly as §3 claims. Battery items
  that exercise the official K&A items grade honestly; without it Kimi invents the bar.
- **Refine loop**: markdown patching alone produces real, visible lift in ONE round.
- **The demo role** ("Data Analyst / Associate Data Engineer") resolves cleanly; its executable
  subset behaves as planned; level normalization has no surprises.
- **Mode B via TF-IDF/keyword + Kimi-as-ranker** is the RIGHT day-of choice — production needed a
  local embeddings server for the fancy version; do not attempt embeddings on the day.

### PROMOTED from stretch to core: the two-track honest scorecard (~1 extra hour, the differentiator)
Production's single biggest lesson. A lone "coverage %" over executable skills **silently fabricates
100%** for any role with few executable skills (live-caught: a Contract Specialist scored a fake
100% on 3 unrelated seed skills). Fix = two tracks, NEVER blended, both on the dashboard:
- **✔ Execution-verified** — sandbox-run bars (Daytona), only for genuinely code-gradable skills.
- **○ Rubric-assessed** — LLM-as-judge over the skill's own K&A checklist, badged
  **"NOT execution-verified"**, for everything else.
Headline reads: *"Executed: X/Y level-points (Z%) · Rubric: A/B K&A items (C%)"* — two numbers,
never one blend. This is one judge prompt + one aggregation, and no other team will have it. It
converts the plan's honesty footnote (§5) into the product's visible spine.

### Real bugs production hit — 30 seconds each to avoid on the day
1. **Filter the seed battery to the role's own skill codes** (`seed ∩ role's codes`) — unfiltered,
   every role "passes" the 3 seed skills → fabricated 100%.
2. **Judge truncation:** any text cap you put on what an LLM-judge reads must be ≥ the generator's
   max output. (Production: judge saw 4k chars of an 18k artifact → scored 0/7; full window → 4/7.
   Richer output must never score worse.)
3. **Rubric criteria must be ATOMIC** (one requirement per item) **and artifact-assessable** (about
   what the deliverable contains — never ops/process like uptime, sign-off, audit trails). Compound
   or ops criteria grade 0 unfairly and make honest work look broken.
4. **If refine appends guidance under a "## Learned" anchor, insert any other spec section BEFORE
   that anchor** — otherwise the next refine pass silently destroys it.
5. **Strict JSON:** `response_format json_object` + client-side validate-and-retry; validate each
   generated battery item statically AND by running its own reference solution against its grader in
   the sandbox — an item its own reference can't solve is a bad item, drop it.
6. **Grader convention:** last stdout line `GRADE:{"score": <0..1>}`; parse bottom-up, clamp,
   missing/garbled → 0 + error note. Score→held-level bands: ≥0.7 full level · ≥0.4 level−1 ·
   else level−2 (floored at 0).
7. **Demo-ops:** after rebuilding/restarting the backend, restart/reload whatever fronts it (a stale
   proxy 502s); and verify the SERVED artifact, never trust an exit code alone.

### Production-verified constants (start here, don't rediscover)
Battery gen temp **0.2** · judge temp **0.0** · `MAX_PARALLEL` **4** · sandbox timeout **20s** ·
refine **1 round** suffices for visible lift · seed battery = **3 items** (Data Engineering /
Database Administration / Data Analytics shaped) is enough for the baseline demo.

### The vision lines are now TRUE (say them with receipts, build none of them)
The production sibling actually built what §9 says to only *speak*: cross-role **teams** (real
career-map lead selection + two-stage sandbox **seam** proofs + human-confirmed end-to-end test) and
a **"describe your day → honest agent map"** intake for non-technical users (guided one-question-at-
a-time interview → per-step agent-fits, provable-vs-assessed badged). One sentence each in the demo:
*"and this same engine already scales to cross-role teams and to mapping a non-technical person's
whole workflow — proven in our production build."* Day-of scope stays §9's: ONE role, single agent.

### Fit check — what does NOT carry over (the infra swap table)
| Production (MakeMyTeam) | Day-of (this guide) |
|---|---|
| Docker `--network none` sandbox (`app/sandbox/runner.py`) | **Daytona SDK** sandbox per skill (same boundary, same timeout discipline) |
| Kimi `kimi-k2.5` via DashScope endpoint | Kimi via **`platform.moonshot.ai`** (verify day-of model id at the workshop) |
| Postgres 16 + pgvector + ETL | **openpyxl reads the xlsx directly** (files already in this folder) |
| Redis + Celery + SSE + React SPA | plain `run.py` + `dashboard.html` |
| bge-m3 embeddings (local Ollama) | TF-IDF/keyword + Kimi ranker |
| — (no Oxylabs anywhere in production) | **Oxylabs postings call, forced-visible** (§10 rule) |
The §3 module names map 1:1 to production modules (`framework/classify/battery/agent/candidate/
assess/gap/refine/run`) — the mental model transfers directly even though the code is rewritten.

---

## 1. Input → output contract

```
IN:  EITHER a role   OR   a free-text task    (+ optional custom instructions)
     │
     ├─ classify.py    (task mode only) match the task → real SkillsFuture role(s); optional SSIC company-type hint  (retrieval, not invention)
     ├─ framework.py   pull the role's official skills + levels + per-level Knowledge&Ability rubric (K&A sheet)
     ├─ oxylabs_fetch  pull live postings + salary band + career map for the role   (sponsor: Oxylabs)
     ├─ battery.py     Kimi → one graded coding assessment per executable skill (sponsor: Kimi)
     ├─ agent.py       Kimi → the agent/team markdown spec (the deliverable)   (sponsor: Kimi)
     ├─ assess.py      run the GENERATED AGENT's work per skill in a sandbox   (sponsor: Daytona)
     ├─ gap.py         aggregate → TWO-TRACK scorecard (executed % · rubric %), ranked gaps
     └─ refine.py      patch the markdown spec to close gaps → re-run
     │
OUT: 1) final agent markdown  (the refined, proven spec)
     2) TWO-TRACK scorecard: ✔ executed X% · ○ rubric C% — NEVER blended (§0.5)  (output.json → dashboard.html)
     3) events.jsonl — the real lifecycle stream (spawn→assign→execute→grade→report→teardown)
        that drives the live demo visual
```

**The one sentence you say over the final screen:** *"You asked for an associate. Here's the
team — and here's proof it covers 91% of what this role officially requires, verified by
running its work in a sandbox, not by a model claiming it can."*

---

## 2. The four sponsors, re-mapped (say each name aloud at the moment it works)

| Sponsor | Its now-real job | Why it's load-bearing |
|---|---|---|
| **SkillsFuture (data)** | Authoritative role → skills → required levels + codes, **plus the per-level Knowledge&Ability rubric** that grounds every graded task | The grounding. "This isn't made up — it's Singapore's national framework, graded against its own rubric." |
| **Oxylabs** | Live postings + **salary band** + **career map** for the role → seasons the tasks *and* adds market context to the deliverable | Tasks + salary/progression reflect what employers hire for *today*, not abstract puzzles. Has offline fallback. |
| **Kimi (Moonshot)** | Generates the graded battery **and** generates + refines the agent spec **and** is the model the generated agent drives | The intelligence layer, used three ways. |
| **Daytona** | Runs the generated agent's untrusted code per skill, in parallel, isolated | You cannot safely run arbitrary generated code at scale without it. The whole proof depends on it. |
| **Nosana** | (Roadmap tier) GPU for a deep fine-tune of a local candidate model to close residual gaps | Spoken roadmap, not day-of code — make the honest call in §10. |

---

## 3. Module plan (file-by-file, with delta tags)

Legend: **NEW** = write from scratch · **CHANGED** = meaningful rework of v1 · **SAME** = reuse v1 verbatim.

### `config.py` — **SAME**
Loads env; builds the Kimi (OpenAI-compatible) client + `kimi_chat()` helper; `make_daytona()`.
Note: SkillsFuture proficiency levels run **1–6** (this role tops out at L4). The coverage math
is scale-agnostic, so no change needed — just don't hardcode a max of 5 anywhere.

### `framework.py` — **NEW** (the data layer)
Reads the SkillsFuture xlsx once and answers "what does this role require?"
- `resolve_role(query) -> (sector, track, role)` — fuzzy match on the `Job Role` column; for the
  demo, hardwire the resolved target below so it's deterministic on stage.
- `get_skills(role) -> list[{skill, type, required_level, code}]` — from sheet `Job Role_TSC_CCS`.
- `get_context(role) -> {description, performance_expectation, critical_work_functions:[{cwf, key_tasks:[…]}]}`
  — from `Job Role_Description` + `Job Role_CWF_KT`. Feeds both agent-gen and battery-gen.
- `select_executable(skills, k=4) -> list` — filter to skills a coding grader can honestly test
  (keyword/allowlist on titles like Data Engineering, Database Administration, Data Analytics,
  Data Visualisation). Non-executable skills stay in the agent spec (grounding) but are labelled
  "not execution-verified" on the scorecard (honesty — see §5).
- `get_ka(code, level) -> list[{item, kind}]` — **NEW, the highest-leverage add.** Reads sheet
  `TSC_CCS_K&A` and returns the official per-level **Knowledge & Ability checklist** for a skill
  (`kind` ∈ {knowledge, ability}) plus its one-line `Proficiency Description`. This is the rubric that
  grounds every graded task (`battery.py`) *and* scores the non-executable skills honestly (§5). Without
  it, Kimi invents what "L2 Data Engineering" means; with it, the bar is the framework's own words.
- `get_sector(role) -> {sector, track}` — the **industry level** (39 sectors). Already in every sheet;
  feeds on-screen context and Mode-B scoping. There is nothing to scrape for this.
- `normalize_level(v) -> int` — collapse the **dual scale** (numeric `1–6` *and* legacy
  `Basic/Intermediate/Advanced`) to a single numeric axis. Coverage math stays scale-agnostic; never
  hardcode a max.
- `retired_codes() -> set` — from `TSC_CCS_Key_Retired`; skip any deprecated TSC so the battery never
  tests a dead skill.
- (Optional) `ssoc_code(role)` — look up the 5-digit SSOC code for on-screen "official" credibility.
  SSOC↔SFw is not a hard join we need; treat SSOC as garnish, SkillsFuture as the workhorse.
- (Optional) `ssic_hint(company_type) -> sector | None` — soft map a **company type / industry**
  ("fintech", "law firm") via SSIC (Singapore Standard Industrial Classification) to a Sector, for the
  Mode-B entry hint. Same garnish rule as SSOC — never a hard join. Consumed by `classify.py`.

### `classify.py` — **NEW** (task-first entry — Mode B)
Turns a free-text task into **real** roles. It *retrieves and ranks*; it never fabricates a role or a
skill — that guardrail is the whole reason the proof means anything.
- `recommend_roles(task, k=3) -> list[{role, sector, confidence, matched_on:[…], skill_weights:{skill: bump}}]`
  — match the task against the role corpus that `framework.py` already exposes (each role's
  `description` + `critical_work_functions`/`key_tasks`). Two viable implementations, cheapest first:
  1. **Keyword / TF-IDF over the role corpus** (no extra deps, deterministic, demo-safe), then
  2. **Kimi as a ranker** given the top-N candidates — "which of these *real* roles fit this task, and
     why?" Kimi only *chooses among* dataset roles; it is never asked to name a role from scratch.
- `skill_weights` are per-skill nudges derived from which duties matched — they **pre-weight the
  loadout sliders** (UX_FLOW Screen 2) so the task shapes the first-draft profile.
- Returns roles ranked by confidence with the duties each matched on (for the "confirm team" screen).
- **Optional SSIC company-type hint.** If the user gives a company type instead of / alongside the task
  ("we're a fintech"), call `framework.ssic_hint()` to bias role matching toward that Sector — it
  *re-ranks* real roles, it never invents one. Purely a nudge; the task text still does the work.
- **Demo cap:** resolve to ONE role (two at most). Extra roles multiply batteries/sandboxes/refine
  loops — see §9. Mode A skips this module entirely.

### `oxylabs_fetch.py` — **CHANGED** (role, not skill source)
- `fetch_task_material(role_title) -> str | None` — Oxylabs Web Scraper API (google_search or a
  jobs board) for current postings for the role. Returns a short digest of real duties/tools, or
  `None` on any failure. Never raises. This digest is passed to `battery.generate_skill(...)` so
  generated tasks echo current market demand. If `None`, battery-gen proceeds without it.
- `fetch_salary_band(role_title) -> {low, median, high, currency, source} | None` — scrape the current
  salary range for the role (MyCareersFuture / a jobs board / SFw sector page). Market context for the
  deliverable, shown on Screen 4. Never raises; `None` → the UI just omits the band.
- `fetch_career_map(role_title) -> {prev:[…], next:[…], lateral:[…]} | None` — scrape the role's
  career pathway (vertical + lateral moves) from the SkillsFuture role page. Two payoffs: (1) shown as
  progression context on the deliverable, and (2) the `lateral`/`next` roles are natural teammates —
  feed them to `classify.py` as candidate team members in Mode B. Never raises.
- **These three are the Oxylabs payload** — postings *season the tasks*, salary + career map *enrich the
  deliverable and inform team composition*. All are fallback-guarded; none can crash the run.
- **Demo visibility (hackathon):** `run.py` calls this **once, up front, unconditionally** and prints
  `Oxylabs: pulled N current postings for <role>` *before* the pipeline — so the judges see Oxylabs
  fire. The fallback still guards the rest of the run; this one call exists purely so the integration
  is visible on stage (see §10). Keep two real result snippets on hand in case you're asked.

### `battery.py` — **CHANGED** (grounded + market-seasoned)
- `generate_skill(role, skill, required_level, context, ka_items, task_material) -> {skill, required_level, task_prompt, grader_code, code}`
  — same STRICT-JSON contract as v1 (a `solve(...)` task + a self-contained grader that prints
  `GRADE:{...}`), but the prompt now includes the SkillsFuture skill title/level, the role's key
  tasks (`context`), **the per-level `ka_items` from `framework.get_ka()`**, and the Oxylabs
  `task_material`. The K&A items are the spec: the generated task must exercise those exact
  abilities, and the grader checks them — so the task is provably on-framework, not model-invented.
  Temperature low (0.2).
- `build_battery(role) -> {role, skills:[…]}` — orchestrates framework → select_executable →
  `get_ka` per skill → per-skill generate. Falls back to `battery_seed.json` if generation yields nothing.
- `rubric_score(skill, level, ka_items, agent_spec) -> {covered, total, pct}` — **NEW.** For
  **non-executable** skills, score the agent spec as an LLM-as-judge checklist over the skill's K&A
  items (each item = one point). Gives the `○ rubric` skills an honest, framework-anchored number
  instead of a hand-waved one — without claiming sandbox execution. Keep it clearly badged separate
  from the `✔` executed bars (§5 honesty rule).
- Keep `battery_seed.json` (v1's 3 hand-written skills) as the offline-safe fallback.

### `agent.py` — **NEW** (generates the deliverable)
- `generate_agent(role, skills, context, custom_instructions) -> str` (markdown). Sections:
  1. **Identity** — role name, SSOC code, source = SkillsFuture SFw.
  2. **Required competencies** — each skill → level → one line of "what good looks like."
  3. **Operating instructions** — the user's custom instructions, verbatim + structured.
  4. **Working method** — distilled from the role's critical work functions / key tasks.
  5. **Learned skill guidance** — *empty placeholder that `refine.py` fills.*
- MVP = **one** agent spec. **Stretch (team):** `generate_team()` emits a lead + per-skill-cluster
  specialists, each a sub-section; the executable test then routes each skill task to the matching
  specialist's sub-section as system prompt. Keep team OFF for the Data Analyst demo (single agent
  is cleaner and matches a single scorecard); it's the story you tell for the *lawyer* customer.

### `candidate.py` — **CHANGED** (the identity swap — the crux)
- `candidate_solve(task_prompt, agent_spec) -> code` — calls Kimi with **`agent_spec` (the generated
  markdown) as the system prompt**, then the skill's `task_prompt` as the user message. Strips
  markdown fences. There is no separate hidden base prompt anymore: *the generated agent is the
  system prompt.* This is what makes the scorecard about the deliverable, not about Kimi in the
  abstract.

### `assess.py` — **CHANGED (minor)**
- `assess_skill(daytona, skill_item, agent_spec) -> result` — identical to v1 except it passes
  `agent_spec` into `candidate_solve`. Still: fresh sandbox → run `candidate_code + grader_code`
  together → parse `GRADE:` → map score to held level vs required → clean up in `finally`.
- **Emits lifecycle events (the "ceremonies").** At the exact points it already does the work, call
  `events.emit(...)`. These are not decoration — each one marks a real state transition:

  | Event | Fires when | Real? |
  |---|---|---|
  | `spawn` | `daytona.create()` returns a sandbox | ✅ |
  | `assign` | the skill's `task_prompt` is bound to this agent's spec | ✅ |
  | `execute` | candidate code starts running in the sandbox | ✅ |
  | `grade` | the grader prints `GRADE:{…}` | ✅ |
  | `report` | the score is mapped to held-vs-required level | ✅ |
  | `teardown` | the `finally` block deletes the sandbox | ✅ |

### `events.py` — **NEW** (tiny; the lifecycle stream that feeds the visual)
- `emit(event, **kw)` — append one JSON line to `events.jsonl` **and** print it, so the terminal and
  the dashboard read the same truth. Shape: `{ts, agent, skill, sandbox_id, event, detail}`,
  `event` ∈ the lifecycle table above.
- Never raises, never blocks the run. If the file can't be written, the pipeline continues and
  `dashboard.py` falls back to replaying `output.json` without the live lane animation.
- This is **logging what already happens** — not new machinery. It's the one cheap thing that turns
  the terminal run into a watchable demo. Keep it under ~15 lines.

> **No `handoff.py` day-of.** Agent→agent seams are already built and human-confirmed in the
> production sibling (`MakeMyTeam/backend/app/pipeline/seam.py`). Per §0.5 you **show them with
> receipts, you don't rebuild them on hackathon eve**. See §7.5 for exactly how to present it —
> including the honesty framing that took production a real bug to learn.

### `gap.py` — **SAME**
`gap_report(results) -> {coverage_pct, gaps(sorted), results}` and `print_report(...)`. Coverage =
`(1 − Σgap / Σrequired) × 100`. Works unchanged on the 1–6 scale.

### `refine.py` — **CHANGED** (patch the deliverable, don't inject a hidden prompt)
- `make_injection(gap_item, task_prompt) -> str` — same coach prompt as v1: one concrete, reusable
  instruction to pass this class of task.
- `patch_agent(agent_spec, gaps, battery) -> new_agent_spec` — appends the learned instructions into
  the **"Learned skill guidance"** section of the markdown and returns the updated spec. The re-run
  uses this patched spec, and **the final patched spec is what gets delivered.** So the lift is a
  real v0→v1 improvement of the artifact the user keeps.

### `run.py` — **CHANGED** (orchestrate + emit both artifacts)
- **Resolve entry:** `--task "…"` → `classify.recommend_roles()` → take the top role (demo cap: one);
  otherwise `--role "…"` / hardwired demo role. Carry `skill_weights` (Mode B) into the loadout.
- Then: `build_battery` → `oxylabs_fetch` (seasoning) → `generate_agent` (spec **v0**).
- **Round 0 (baseline):** assess every executable skill IN PARALLEL (ThreadPoolExecutor, one sandbox
  per skill) using **spec v0** → baseline report.
- **Refine loop** (≤ `MAX_ROUNDS`): `patch_agent` → spec **v1** → re-assess in parallel → new report;
  stop at `TARGET_COVERAGE` (90%).
- **Save:** `output.json` (role + per-round two-track reports for the dashboard), `agent_final.md`
  (the delivered spec), **and `events.jsonl`** (the lifecycle stream). Print all three paths.
- Fan-out knob `MAX_PARALLEL` (default **4**, production-verified §0.5) = the "thousands of
  sandboxes, scaled down" story.
- **Single agent, one role.** No `--team`, no chain day-of (§9). The team/seam story is told with
  production receipts (§7.5), not day-of code.

### `dashboard.py` — **CHANGED (light)**
v1's before/after HTML table (red/green bars + headline %). Add: a link/section rendering
`agent_final.md` so the screen shows *the delivered agent* next to *the proof*. Auto-opens in browser.

### `smoke_test.py` — **SAME**
Run **first**. Proves Kimi responds and Daytona can create a sandbox, run `print(2+2)`, and delete it.
If both lines print, the whole stack works and everything else is logic.

---

## 4. The generated-agent test mechanism (spelled out — this is the whole pivot)

The honesty of the demo rests on one thing: **the object being graded must be the object being
handed over.** Mechanism:

1. `agent.py` produces `agent_spec` (markdown) from the role's official skills + custom instructions.
2. For each skill's `task_prompt`, `candidate.py` runs Kimi **with `agent_spec` as the system
   prompt** → produces a `solve(...)` function.
3. `assess.py` runs that function + the hidden grader in a Daytona sandbox → a real pass rate.
4. `refine.py` edits `agent_spec` (adds tactical guidance) → **`agent_spec` v1**.
5. Round 1 repeats steps 2–3 **with v1**. The bars move because the *spec* got better.
6. `agent_spec` v1 is saved as `agent_final.md` — the delivered artifact.

**Baseline is NOT "raw model."** It's "the first-draft generated agent" (v0 — already role-grounded,
but without tactical skill guidance). Final is "the same agent, gaps closed" (v1). The lift is a
genuine improvement of the deliverable.

> **Demo-drama lever:** if v0 scores too high to show a satisfying gap, make v0's competency lines
> terse (role + skills, minimal tactics) and let `refine` add the specifics (edge cases, output
> format, rounding, tie-breaks). That widens baseline→final honestly without faking anything.

---

## 5. The data layer in detail (grounded in the real dataset)

**Resolved demo role (hardwire this on stage):**
`Sector = Infocomm Technology`, `Track = Data and Artificial Intelligence`,
`Role = "Data Analyst / Associate Data Engineer"`.

**Its 14 official skills (from `Job Role_TSC_CCS`) — executable subset marked ✅:**

| Level | Skill | Code | Live test? |
|---|---|---|---|
| L2 | Data Engineering | ICT-DIT-2005-1.1 | ✅ |
| L2 | Database Administration | ICT-OUS-2006-1.1 | ✅ (SQL-style) |
| L2 | Data Analytics | ICT-BIN-2104-1.1 | ✅ |
| L3 | Data Analytics | ICT-BIN-3104-1.1 | ✅ |
| L3 | Data Visualisation | ICT-DIT-3006-1.1 | ✅ (grade the data prep behind the chart) |
| L2 | Stakeholder Management | ICT-SCM-2004-1.1 | — rubric only |
| L2 | Business Needs Analysis | ICT-PMT-2001-1.1 | — |
| L3 | Business Performance Mgmt | ICT-BIN-3070-1.1 | — |
| L3 | Design Thinking Practice | ICT-ACE-3014-1.2 | — |
| L3 | Budgeting / Networking / Project Mgmt | … | — |
| L3 | Data Ethics | ICT-LGL-3004-1.1 | — |
| L4 | Business Innovation | ICT-SNA-4003-1.1 | — |

**Live battery for the demo = the ✅ subset** (4–5 skills: Data Engineering, Database Administration,
Data Analytics, Data Visualisation). This is deliberately close to your v1 seed (Data Transformation,
SQL, Statistics) — so the safety net and the real battery are structurally the same shape.

**Honesty rule:** the agent spec lists **all 14** required skills (that's the grounding). The scorecard
executes only the ✅ subset and labels the rest "not execution-verified." Say this out loud — it reads
as rigor, not as a gap. (Stretch: add an LLM-as-judge rubric score for one non-code skill to show the
mechanism generalises — but that softens "provably executed," so keep it as a stretch, not the spine.)

**Dataset inventory (6 sheets — the guide now uses every load-bearing one):**

| Sheet | Rows | Used for |
|---|---|---|
| `Job Role_Description` | ~2K | identity, description, performance expectation |
| `Job Role_CWF_KT` | ~40K | working method (critical work functions + key tasks) |
| `Job Role_TSC_CCS` | ~44K | role → skill → required level → code (the spine) |
| `TSC_CCS_Key` | ~12K | skill definitions (richer competency lines) |
| **`TSC_CCS_K&A`** | **~150K** | **per-level Knowledge & Ability rubric** — grounds battery tasks + scores rubric-only skills |
| `TSC_CCS_Key_Retired` | ~271 | deprecated TSC codes to skip (`retired_codes()`) |

**Hierarchy:** `Sector (39)` → `Track (250)` → `Job Role (1,977)` → skills/CWF/KT. **Sector is the
industry level you were thinking of** — it's already in every sheet, so nothing is scraped for it. (SSG
officially lists 38 sectors; the file carries 39.)

**Company-type axis = SSIC (optional garnish).** The Skills Framework has no company-type field. To let a
user enter by company type ("fintech", "law firm"), soft-map it via **SSIC** (Singapore Standard
Industrial Classification — 22 Sections → Sub-class, 5-digit) onto a Sector in `framework.ssic_hint()`.
Treat it like SSOC: on-screen credibility + a Mode-B re-rank nudge, never a hard join.

**Proficiency scale is dual.** Levels appear as numeric `1–6` *and* legacy `Basic/Intermediate/Advanced`.
`framework.normalize_level()` collapses both to numeric — never hardcode a max; coverage math is scale-agnostic.

**The K&A rubric, concretely.** For Data Engineering **L2** the K&A sheet lists checklist items like
*"clean the data, checking for outliers or errors"*, *"merge varying datasets from disparate sources into a
common structure"*, *"utilise DBMS software for simple data processing"*. `battery.generate_skill()` builds
the graded task *from these items* (on-framework, not model-invented), and non-executable skills are scored
as a checklist over their K&A items (`rubric_score`) — honest, not hand-waving.

**Market context (Oxylabs, per §3 `oxylabs_fetch.py`):** salary band + career map are **not** in the xlsx —
they're the scrape payload, enriching the deliverable (Screen 4) and feeding candidate teammates to Mode B.

---

## 6. Run order on the day

```bash
# 1. setup during the Daytona workshop (~10:30)
cd ~/Projects/AgentProof
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # daytona openai python-dotenv requests openpyxl
#   ...paste DAYTONA_API_KEY, MOONSHOT_API_KEY, (OXYLABS_*) into .env...
#   ...drop the SkillsFuture + SSOC xlsx into ./data/...

# 2. SMOKE TEST FIRST — prove both APIs before building anything else
python smoke_test.py

# 3. prove the data layer reads the real role
python -c "from framework import resolve_role,get_skills; r=resolve_role('data analyst'); print(get_skills(r))"

# 4. baseline + refine loop on the SAFE SEED battery (no framework, no Kimi-gen)
python run.py                # falls back to battery_seed.json

# 5. render the demo screen
python dashboard.py

# 6. once green end-to-end, switch on the real grounded battery
python run.py --generate     # framework + Oxylabs + Kimi-generated battery

# 7. (stretch) task-first entry — classify a task into a real role, then run the same loop
python run.py --generate --task "review vendor NDAs and pull payment terms into a comparison"
```

**Build in this order (matches H0–H4):**
1. `config.py` + `smoke_test.py` → both APIs respond.
2. `framework.py` → prints the real Data Analyst skill list (proves the grounding cheaply).
3. `battery_seed.json` + `agent.py` + `candidate.py` + `assess.py` → assess ONE skill, driven by a
   generated spec, end-to-end.
4. `run.py` fan-out over the seed skills → baseline report in terminal.
5. `refine.py` (patch the markdown) → the loop shows lift; save `agent_final.md`.
6. `dashboard.py` → the visual. **Stop here and rehearse.**
7. Stretch, in order: real `battery.py --generate` → `oxylabs_fetch` seasoning → `classify.py`
   task-first entry (one role) → mention Nosana.
8. **Only once 1–6 are green and rehearsed:** `events.py` (~15 lines) → `demo_theatre.html` replays
   `events.jsonl` for the live lane animation. No team, no chain (§9) — the seam story is receipts (§7.5).

---

## 7. The 2-minute demo script (rehearse)

1. **Problem (15s):** "Teams are dropping AI agents into real jobs, but nobody can *prove* an agent
   is competent for a role. Self-reported skills are worthless."
2. **The request (15s):** "A lawyer needs a data analyst and gives instructions." Show the **official
   SkillsFuture skill list** AgentProof pulls for the role ("this isn't invented — it's Singapore's
   national framework"), and point at the **Oxylabs** line as it pulls current postings for the role
   live ("Oxylabs is sourcing what employers ask for *today*").
3. **The generated team (15s):** the `agent_final.md` draft appears. "Here's the agent, built for
   those exact skills plus the instructions."
4. **Proof running (30s):** `python run.py`. "For each skill it runs *this agent's* work — live, in
   parallel, each in its own **Daytona** sandbox. **Kimi** is the intelligence; **Oxylabs** sourced
   the real-world tasks." Red bars = baseline.
5. **The lift (20s):** "It reads its own gaps, rewrites the agent's guidance, and re-runs — every
   attempt in a fresh sandbox."
6. **Money shot (25s):** `python dashboard.py`. "Same agent, now 91%. Every green bar is code this
   agent wrote that provably ran in a Daytona sandbox — and the guidance that got it there is baked
   into the spec you take away."
7. **The honesty close (10s, v3):** "And where a skill *can't* be code-graded, we don't pretend — it's
   scored on the framework's own Knowledge-&-Ability rubric and badged 'not execution-verified'. Two
   numbers, never blended. That honesty is the product — and this same engine already scales to
   cross-role teams and to mapping a non-technical person's whole workflow."

---

## 7.5 The team & seam beat — receipts, not day-of code (20s, after the money shot)

Per §0.5 the cross-role team and the agent→agent **seam** are already built and human-confirmed in
the production sibling. You **show** them; you do not rebuild them Saturday. This beat is 20 seconds
and it is the single strongest "this is real" moment you have — *if* you frame it exactly right.

**What the seam actually is** (`MakeMyTeam/backend/app/pipeline/seam.py`, verified):
1. Agent **A**'s candidate (A's generated spec as system prompt) writes **producer** code that emits
   a validated JSON handoff artifact — inside **its own locked-down container**.
2. Agent **B**'s candidate writes **consumer** code that consumes **that real artifact** and produces
   B's first deliverable — inside **its own separate container**.
3. `two_stage.run_seam_stages` chains them. **The containers never talk to each other** — they are
   chained *only* by the validated artifact. Isolation is inherited unchanged.
4. An **LLM judge** scores the receiving role's K&A-grounded `acceptance_criteria` against what
   actually happened. Failing seams retry (producer *and* consumer regenerated), then **escalate to
   the Lead**.

**The honesty framing — say it exactly this way** (this is the part production needed a real bug to learn):

> "The seam is **exercised** — agent A really ran and produced that artifact, agent B really consumed
> it and produced this deliverable. That chain is the real integration signal. But the **score** is an
> LLM judge over acceptance criteria, so it's **rubric-assessed, not execution-verified** — and we
> never blend it into the executed number."

- Every seam result carries `execution_verified: False` and the `SEAM_NOTE` badge. **No code path
  ever sets it True.** Keep seam scores in their own `level2` section — never merged into Level-1.
- **Do not say** "the agents talk to each other" (they don't — that's the point) or "this ran today"
  (it didn't). Both are avoidable own-goals in front of judges who will ask.

**Receipts to have open in a background tab:** `frontend/src/screens/ProveTeam.tsx` and
`ConfirmTeamGraph.tsx` (the built team screens), `backend/tests/test_seam_sandbox.py` (the seam
proven in a real sandbox), and `seam_architecture.html` (the graphic in this folder).

**The one line that ties it together:** *"Everything you just watched is today's build — one role,
proven live. This same engine already scales to cross-role teams with proven handoffs, and to mapping
a non-technical person's whole workflow. That's our production build, not a promise."*

---

## 8. Risks & fallbacks (never dead in the water)

| If this breaks | Do this |
|---|---|
| Daytona quota / rate limit | Lower `MAX_PARALLEL` to 1–2; sandboxes are cheap but limits exist |
| `daytona` import fails | `pip install daytona-sdk`; change import to `from daytona_sdk import ...` |
| Kimi battery-gen returns bad JSON | `build_battery` falls back to `battery_seed.json` — **PRE-WRITTEN, in this folder** (production-proven: 3 items matching the demo role's real L2 executable codes, `GRADE:` convention, tested in dozens of runs); run `run.py` without `--generate` |
| `agent.py` returns junk | Fall back to `agent_seed.md` — **PRE-WRITTEN, in this folder** (grounded in the role's real 14-skill list; deliberately generic so the baseline stays red and refine shows honest lift; ends with the empty `## Learned skill guidance` anchor refine needs) |
| Oxylabs down / no booth key | `fetch_task_material` returns `None`; battery-gen proceeds without seasoning |
| Task (Mode B) too vague to classify | `classify` returns low-confidence matches; prompt for one clarification or fall back to Mode A / the hardwired role |
| Task matches no dataset role well | Show top-3 low-confidence roles; never invent one — let the user pick or switch to Mode A |
| Role not found in xlsx | `resolve_role` returns the hardwired demo target; log a warning, don't crash |
| Level scale surprises (1–6, or Basic/Intermediate/Advanced legacy labels) | Normalise to numeric in `framework.py`; coverage math is scale-agnostic |
| Grader crashes on candidate code | Graders wrap every call in try/except, default score 0 |
| `events.jsonl` not written | `events.emit` never raises; `dashboard.py` falls back to `output.json` without the live lane animation |
| A judge asks "is the seam live?" | Answer straight: *"the day-of build is the single-agent proof; the cross-role seam is from our production build — exercised in real sandboxes, rubric-scored, and badged as such."* Never imply it ran today |
| A role scores suspiciously high (e.g. 100%) on the seed battery | You forgot the `seed ∩ role's-own-codes` filter (§0.5 bug 1) — a fabricated score is worse than a low one |
| Judge marks obviously-met criteria as unmet | Check the text cap handed to the judge covers the FULL artifact (§0.5 bug 2), and that criteria are atomic (§0.5 bug 3) |
| No internet at all | Only Daytona + Kimi need the network; the xlsx read + fallbacks are all local |

---

## 9. Scope discipline (don't blow the day)

- **ONE role, the executable subset (~4 skills).** Resist expanding until the loop is green.
- **Entry = Mode A (pick the role) for the live build.** Task-first (`classify.py`, Mode B) is a
  stretch and must resolve to ONE role; open-ended multi-role teams are *spoken* product vision.
- **Single agent** for the Data Analyst demo. Team-gen + agent→agent seams are **already proven in
  the production sibling** — so they're now *spoken with receipts* (§7.5), which is strictly stronger
  than a rushed live rebuild. **Do not build `handoff.py` on the day** (§0.5: "say them with
  receipts, build none of them").
- **The two-track scorecard IS core, not stretch** (§0.5). A single blended number silently
  fabricates 100%. Two numbers, never one.
- **Fast-refine only** = patch the markdown. Fine-tuning on **Nosana** = spoken roadmap tier.
- Non-executable skills = listed in the spec, labelled "not execution-verified" on the scorecard.
  **v3: the LLM-as-judge rubric track is PROMOTED to core** (see §0.5) — budget ~1 hour AFTER the
  executed loop is green; it's one judge prompt + one aggregation and it is the differentiator.
- **Dashboard working by ~3:30**; spend the last hour rehearsing, not adding features.
- A tight, working, *honest* loop beats a broad broken one on the **Completeness** criterion.

---

## 10. Sponsor coverage checklist (demo-day — do not skip)

"Sponsored Product Usage" is a scored criterion and the brief **requires** integrating the sponsored
products. Before you present, confirm each sponsor isn't just in the code but **visibly firing on
stage** — and say its name at the moment it does its job.

| Sponsor | Must be visible on stage as… | Pre-demo check | If it won't fire live |
|---|---|---|---|
| **Daytona** (title) | Sandboxes spin up per skill; every bar = code that ran in one | smoke_test passes; `MAX_PARALLEL` ≥ 2 so parallelism shows | Must work. If quota dies, drop to 1 sandbox but keep it real — never fake a bar |
| **Kimi** | Generates the battery + the agent spec + drives the candidate | model id verified in the workshop; a real generation prints on screen | Fall back to seed battery / `agent_seed.md`, but say Kimi generated them in a prior run |
| **Oxylabs** | ONE live call pulling current postings for the role, named aloud | run the forced probe (below) once, for real, right before you present | Do **not** let the fallback swallow it silently — see the rule below |
| **Nosana** | Honest call — pick ONE option below, decide *before* the day | — | see Options A / B below |

**The Oxylabs "make it visible" rule.** In the live demo, call Oxylabs **once, unconditionally, up
front** — not buried in the fallback-guarded battery path where it may silently return `None` and
leave your Oxylabs integration at zero on stage. Print `Oxylabs: pulled N current postings for <role>`
so the judges *see* it integrate. The fallback still protects the rest of the run; this one call is
purely for visibility.

**Nosana — decide before the day (do not wing it):**
- **Option A (pragmatic, recommended).** Accept Nosana as a *spoken roadmap* ("deep-refine via a
  fine-tune on Nosana GPU to close residual gaps"). You take a partial on this one sub-point;
  Daytona being load-bearing carries most of the sponsor score, and the other three are real.
- **Option B (all four live).** Serve the **candidate model as GPU inference on Nosana** for at least
  one skill's attempt, and show that bar came from a Nosana-hosted model. Take this **only** if the
  Nosana template + credits make it near-trivial at the booth — it's real work on top of the core
  loop, and the core loop wins first.

> **Rule of thumb:** do not sacrifice a working Daytona + Kimi loop to chase Nosana. A tight demo where
> three sponsors are load-bearing and one is honest roadmap beats a broken demo that touched all four.

**60-second pre-demo pass (run in order):**
1. `smoke_test.py` green (Daytona + Kimi both respond). ☐
2. Oxylabs forced probe printed a real "pulled N postings" line. ☐  *(if red: Oxylabs down → still fine, but drop the "live" claim and show the saved snippets instead)*
3. `run.py` produced a baseline **and** a lifted final, and `agent_final.md` exists. ☐
4. `dashboard.py` opens with red→green bars + headline number. ☐
5. Nosana line decided (A or B) and rehearsed. ☐

---

### Sources (verify model ids / SDK at the event)
- Daytona docs: https://www.daytona.io/docs/en/ (getting-started, python-sdk, file-system-operations, process-code-execution)
- Kimi API: https://platform.moonshot.ai/ · coding-tuned model id e.g. `kimi-k2.7-code` (verify)
- Oxylabs Web Scraper API: https://oxylabs.io/
- Data: SkillsFuture Skills Framework dataset (roles/skills/levels) · SSOC 2024 (occupation taxonomy)
