# AgentProof — Phased Implementation Plan (one phase = one loop)

> **How to read this file.** Each phase below is a **self-contained loop** — a bounded
> unit of work with a machine-checkable Definition of Done (DoD). You run one phase per
> `/loop` (or per agent session). A phase is "done" when *every* checkbox in its DoD is
> green and committed to git; the loop exits on the DoD, not on a timer. Do **not**
> start Phase N+1 until Phase N's DoD is green — the gates are real, the dependencies
> are real.

> **Corpus used for this plan (verified 2026-07-18, not assumed):**
> `jobsandskills-skillsfuture-skills-framework-dataset.xlsx` (13.0 MB, 6 sheets) +
> `ssoc2024-classification-structure.xlsx` (1,622 rows) +
> `ssoc2024-type-of-change-at-occupational-level.xlsx` (1,012 rows). The demo role **does
> resolve** in the data: `Sector=Infocomm Technology · Track=Data and Artificial
> Intelligence · Role="Data Analyst / Associate Data Engineer"`, with its exact **14
> skills** (verified row-by-row in `Job Role_TSC_CCS`) and the per-level **Knowledge &
> Ability** items present in `TSC_CCS_K&A` (e.g. `ICT-DIT-2005-1.1` → "Clean the data,
> checking for outliers or errors", "Catalogue data according to set guidelines"). Nothing
> in this plan is invented — see the corpus table at the bottom.

---

## 0. Project review (read first — the verdict on what's already here)

**What this project is.** AgentProof / "Daytona": a verifiable proving ground for
role-specialized agents, built for the Daytona HackSprint. A user points it at a role →
it pulls that role's **official** SkillsFuture skills → generates an agent as a markdown
spec → **proves** the spec by running *that spec's* candidate code per skill in isolated
**Daytona** sandboxes → produces a two-track scorecard → **refines** the spec to close
gaps → re-runs and shows the lift (red → green bars). The deliverable is two stapled
artifacts: the `agent_final.md` spec the user takes away, and a role-readiness scorecard
proving by execution that the spec covers X% of the role's required skills.

**State of the repo today.** This folder is **design + data, no implementation code yet.**
What exists is the validated spec and the data corpus, not the running system:
- `BUILD_GUIDE.md` — the complete, v3-validated day-of guide (the spec to build against).
- `agent_seed.md` — pre-written fallback agent spec (grounded in the real 14-skill list).
- `battery_seed.json` — pre-written 3-item fallback battery (Data Engineering / DB Admin /
  Data Analytics shaped), `GRADE:` convention included.
- `dashboard_mockup.html`, `seam_architecture.html`, `receipts.html` — static visuals.
- `UX_FLOW.md`, `scraping-urls.md`, the hackathon minutes — context.
- The three `.xlsx` files — the data corpus (verified below).
- `SESSION_LOG.md` — empty stubs (no sessions logged yet).

**Verdict.** This is the ideal starting position: the architecture is de-risked (it was
built to production as MakeMyTeam per §0.5), the data is real and present, and the
fallbacks are pre-written. What is missing is the **hackathon-stack implementation** —
the actual `.py` modules, `requirements.txt`, `.env`, and a green end-to-end run. The
phases below build exactly that, each one a loop that converges on a green, committed
checkpoint.

**The one rule that shapes every phase (§0.5, the differentiator).** The scorecard has
**two tracks, never blended**: ✔ Execution-verified (sandbox-run, for code-gradable
skills) and ○ Rubric-assessed (LLM-as-judge over the skill's K&A checklist, badged "NOT
execution-verified", for everything else). A single blended number silently fabricates
100%. Every phase that touches scoring must keep these two tracks separate.

**Loop discipline (applies to every phase).**
- Each phase has a **DoD** with machine-checkable bullets. The loop runs until all are
  green, then stops. A loop that cannot reach green in its budget must *stop and report*,
  not silently lower the bar.
- Each phase **commits to git** when green (conventional commits, one per phase gate).
- Each phase lists its **fallback** (from BUILD_GUIDE §8) so a blocked loop degrades
  gracefully instead of stalling.
- Each phase lists the **§0.5 real bugs** that are relevant to it — 30 seconds to avoid,
  an hour to rediscover.

---

## Corpus table (the data this plan is grounded in)

### SkillsFuture dataset — 6 sheets (verified row counts + headers)

| Sheet | ~Rows | Cols (real headers) | Used for |
|---|---|---|---|
| `Job Role_Description` | 2,031 | Sector, Track, Job Role, Job Role Description, Performance Expectation | role identity, description, performance expectation |
| `Job Role_CWF_KT` | 40,380 | Sector, Track, Job Role, Critical Work Function, Key Tasks | working method (CWF + key tasks) → feeds agent-gen + battery-gen |
| `Job Role_TSC_CCS` | 44,536 | Sector, Track, Job Role, TSC_CCS Title, TSC_CCS Type, Proficiency Level, TSC_CCS Code | role → skill → required level → code (the spine) |
| `TSC_CCS_Key` | 12,008 | TSC Code, Sector, TSC_CCS Category, TSC_CCS Title, TSC_CCS Description, TSC_CCS Type, Latest Update Date | richer competency definitions |
| `TSC_CCS_K&A` | 150,265 | TSC_CCS Type, TSC_CCS Code, Sector, TSC_CCS Category, TSC_CCS Title, TSC_CCS Description, Proficiency Level, Proficiency Description, Knowledge/Ability Items, Knowledge/Ability Classification | **per-level K&A rubric** — grounds battery tasks + scores rubric-only skills |
| `TSC_CCS_Key_Retired` | 271 | TSC Code, Sector, TSC_CCS Category, TSC_CCS Title, TSC_CCS Description, TSC_CCS Type, Retired Date | deprecated codes to skip (`retired_codes()`) |

**Hierarchy:** Sector (39) → Track (~250) → Job Role (1,977) → skills/CWF/KT.
**Proficiency scale is dual:** numeric 1–6 *and* legacy Basic/Intermediate/Advanced →
`normalize_level()` collapses both; coverage math is scale-agnostic (never hardcode a max).

### SSOC 2024 files (garnish — on-screen credibility, never a hard join)

| File | Sheet | ~Rows | Note |
|---|---|---|---|
| `ssoc2024-classification-structure.xlsx` | `SSOC 2024 Structure` | 1,622 | headers at row 5 (rows 1–4 are metadata). Cols: SSOC 2024 code, title, + 2020 mapping |
| `ssoc2024-type-of-change-at-occupational-level.xlsx` | `SSOC2024 Type of Change` | 1,012 | legend at row 5 (Z=No change, C=Code change, T=Title change, …) |

### Demo role (verified present, hardwire on stage)

`Sector=Infocomm Technology · Track=Data and Artificial Intelligence · Role="Data
Analyst / Associate Data Engineer"` → 14 skills in `Job Role_TSC_CCS` (L2→L4).
Executable subset (✅ = code-gradable): Data Engineering L2, Database Administration L2,
Data Analytics L2, Data Analytics L3, Data Visualisation L3. The other 9 are
rubric-assessed only. This is the role every phase below targets until Phase 7 opens
Mode B.

---

## Phase map (8 phases — each is one loop)

| # | Phase (one loop each) | Core artifact at the gate | Sponsors load-bearing |
|---|---|---|---|
| 0 | Scaffold + env + smoke test | `smoke_test.py` prints two OK lines | Daytona + Kimi |
| 1 | Data layer (`framework.py`) | one-liner prints the real 14 skills + K&A | SkillsFuture (data) |
| 2 | Single-skill end-to-end (seed) | ONE skill assessed in a sandbox, prints `GRADE:` | Daytona + Kimi |
| 3 | Fan-out baseline + two-track report | `run.py` → `output.json` baseline, `gap.py` report | Daytona + Kimi |
| 4 | Refine loop + `agent_final.md` | red→green lift on ≥1 skill, spec saved | Kimi |
| 5 | Dashboard (the visual) | `dashboard.py` opens with bars + headline + spec | — (UI) |
| 6 | Real grounded battery + Oxylabs + rubric track | `run.py --generate` two-track scorecard | Kimi + Oxylabs + SkillsFuture |
| 7 | Task-first entry (Mode B) + events stream + Nosana call | `run.py --task "…"` + `events.jsonl` replay | Kimi + Oxylabs + Daytona (+ Nosana roadmap) |

**Dependency graph (strict — a phase's DoD is the next phase's input):**

```
0 ──► 1 ──► 2 ──► 3 ──► 4 ──► 5 ──► 6 ──► 7
                  │           (rehearse gate:    │
                  └─ Phase 3 unblocks            stop & rehearse
                     both 4 and 5                before 6)
```

- Phases 0→5 = the **core demo loop** (BUILD_GUIDE §6 build steps 1–6). Must be green
  and rehearsed before any stretch.
- Phases 6→7 = **stretch → core promotion** (§6 steps 7–8). Phase 6 is the v3-promoted
  two-track differentiator + the real grounded battery; Phase 7 is Mode B + the live
  lifecycle visual + the honest Nosana call.

**Recommended cadence.** Run phases **strictly in order**, one `/loop` per phase. Do not
parallelize — every phase writes files the next phase reads. A phase that hits its budget
without green must **stop, report the blocker, and ask** — never silently lower the DoD
(see Loop discipline above).

---

## Phase 0 — Scaffold, environment, smoke test

**Goal.** Stand up the project skeleton and prove **both** load-bearing APIs respond
before writing any logic. If the two endpoints work, everything else is just code.

**Inputs.** `BUILD_GUIDE.md` §6 (run order), §3 `config.py`/`smoke_test.py`. API keys
(`DAYTONA_API_KEY`, `MOONSHOT_API_KEY`, and `OXYLABS_*` placeholders) supplied by you
into `.env`.

**Files to create.**
- `requirements.txt` — `daytona` (or `daytona-sdk`), `openai`, `python-dotenv`,
  `requests`, `openpyxl`. Pin nothing exotic; standard versions.
- `.env.example` — the keys above, empty values (the real `.env` is gitignored).
- `.gitignore` — `.venv/`, `.env`, `output.json`, `events.jsonl`, `__pycache__/`.
- `config.py` — loads env; builds the Kimi OpenAI-compatible client pointed at
  `https://api.moonshot.ai/v1`; `kimi_chat()` helper; `make_daytona()`.
- `smoke_test.py` — (1) print Kimi's reply to `"ping"`; (2) `make_daytona()` → create a
  sandbox → run `print(2+2)` → assert stdout contains `4` → delete the sandbox. Print
  `KIMI: OK` and `DAYTONA: OK` on success.

**Definition of Done (machine-checkable).**
- [ ] `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` exits 0.
- [ ] `python smoke_test.py` prints a line containing `KIMI: OK` and a line containing `DAYTONA: OK`.
- [ ] `.env` exists and is gitignored; `.env.example` is committed.
- [ ] `git status` is clean after a commit named `phase0: scaffold + smoke test green`.

**Fallback.** `daytona` import fails → `pip install daytona-sdk`, swap the import line
(BUILD_GUIDE §8 row 2). Kimi model id not accepted at `platform.moonshot.ai` → verify
the served id in the workshop and update `config.py` only (§0.5 fit-check table).

**§0.5 watch-items.** None specific to Phase 0; but record the **served Kimi model id**
in `config.py` as a single constant so Phase 2/4 don't rediscover it. Note: the BUILD_GUIDE
says verify day-of model id (e.g. `kimi-k2.7-code`) — confirm against the live endpoint,
don't guess.

**Loop guard.** This phase should converge in one iteration. If the loop fails after
3 attempts to get both OK lines, it must stop and surface the exact failing call (Kimi
HTTP status, or Daytona SDK error) — do not proceed to Phase 1 with a broken stack.

---

## Phase 1 — Data layer (`framework.py`)

**Goal.** Read the SkillsFuture xlsx **once** and answer "what does this role require?"
— pure data, no network beyond the file read. This is the grounding that makes the whole
proof on-framework, not model-invented. BUILD_GUIDE §3 `framework.py` (NEW), §5.

**Inputs.** The 6-sheet SkillsFuture xlsx (corpus table above). The hardwired demo role:
`Infocomm Technology / Data and Artificial Intelligence / "Data Analyst / Associate Data
Engineer"`.

**Functions to implement (per §3).**
- `resolve_role(query) -> (sector, track, role)` — fuzzy match on the `Job Role` column;
  on no match, return the hardwired demo target + log a warning (never crash).
- `get_skills(role) -> list[{skill, type, required_level, code}]` — from
  `Job Role_TSC_CCS` (cols: TSC_CCS Title, TSC_CCS Type, Proficiency Level, TSC_CCS Code).
- `get_context(role) -> {description, performance_expectation, critical_work_functions:[{cwf, key_tasks:[…]}]}`
  — from `Job Role_Description` + `Job Role_CWF_KT`.
- `select_executable(skills, k=4) -> list` — keyword/allowlist on titles: Data
  Engineering, Database Administration, Data Analytics, Data Visualisation. Non-executable
  stay in the spec but are labelled "not execution-verified" (§5 honesty rule).
- `get_ka(code, level) -> list[{item, kind, proficiency_description}]` — from
  `TSC_CCS_K&A` (cols: TSC_CCS Code, Proficiency Level, Proficiency Description,
  Knowledge/Ability Items, Knowledge/Ability Classification). `kind` ∈ {knowledge,
  ability}. **This is the highest-leverage add (§0.5).**
- `normalize_level(v) -> int` — collapse dual scale (numeric 1–6 *and*
  Basic/Intermediate/Advanced) to numeric. Never hardcode a max.
- `retired_codes() -> set` — from `TSC_CCS_Key_Retired`; skip deprecated codes.
- (Optional) `ssoc_code(role)` — look up the 5-digit SSOC code from
  `ssoc2024-classification-structure.xlsx` (headers at row 5). Garnish only.

**Definition of Done (machine-checkable).** This one-liner exits 0 and prints real data:
- [ ] `python -c "from framework import resolve_role,get_skills; r=resolve_role('data analyst'); print(r); print(get_skills(r))"`
      prints the 3-tuple `(Infocomm Technology, Data and Artificial Intelligence, "Data Analyst / Associate Data Engineer")` and **exactly 14** skills.
- [ ] `select_executable(get_skills(r))` returns the 5 skills whose codes start
      `ICT-DIT-2005`, `ICT-OUS-2006`, `ICT-BIN-2104`, `ICT-BIN-3104`, `ICT-DIT-3006`
      (verified in the corpus).
- [ ] `get_ka("ICT-DIT-2005-1.1", 2)` returns a non-empty list including the real items
      *"Clean the data, checking for outliers or errors"* and *"Catalogue data according
      to set guidelines"* (these strings exist in the sheet — assert against them).
- [ ] `retired_codes()` is a set and is non-empty (~271 rows).
- [ ] `normalize_level("Advanced")`, `normalize_level(3)` both return ints with no crash.
- [ ] Commit `phase1: framework data layer — real role resolves`.

**Fallback.** Role not found → return hardwired demo target, log warning (§8). A sheet
fails to load → raise with the sheet name (this phase has no silent fallback — bad data
here poisons everything downstream).

**§0.5 watch-items.**
- **Bug 1 (preview):** the seed battery must later be filtered to the role's *own* skill
  codes (`seed ∩ role's codes`). `framework.py` is where `get_skills` returns those codes
  — make the code list the source of truth so Phase 2/3 can intersect cleanly.
- Don't hardcode a max level of 5 — this role tops out at L4 and the scale runs 1–6.

**Loop guard.** Converges when the one-liner prints 14 real skills + the asserted K&A
strings. If `get_ka` returns the wrong items, the loop must check it is filtering on
**both** `TSC_CCS Code` **and** `Proficiency Level` (the same code has multiple levels).
Stop after 4 iterations if the K&A join won't match — surface the sheet's actual columns.

---

## Phase 2 — Single-skill end-to-end (the crux mechanism, on the seed battery)

**Goal.** Prove the **identity swap** on the thinnest possible slice: ONE skill from
`battery_seed.json`, assessed by a candidate driven by **the generated agent spec as its
system prompt**, running in a **Daytona sandbox**, printing `GRADE:{…}`. BUILD_GUIDE §3
`agent.py`/`candidate.py`/`assess.py`, §4 (the pivot spelled out).

**Why this is a phase.** This is the whole honesty pivot: *the object being graded must
be the object being handed over* (§4). Getting one skill green end-to-end de-risks every
later phase. Do not fan out (Phase 3) until one skill is green.

**Inputs.** `battery_seed.json` (pre-written, 3 items). `agent_seed.md` (pre-written
fallback spec — use as v0 spec if `agent.py` is slow). `framework.py` from Phase 1.

**Files to create.**
- `agent.py` — `generate_agent(role, skills, context, custom_instructions) -> str`
  (markdown). 5 sections per §3: Identity, Required competencies, Operating instructions,
  Working method, **Learned skill guidance** (empty placeholder — §0.5 bug 4: refine
  treats everything after this anchor as its own; do not pre-load it).
- `candidate.py` — `candidate_solve(task_prompt, agent_spec) -> code`. Calls Kimi with
  **`agent_spec` as the system prompt** and `task_prompt` as the user message; strips
  markdown fences. No hidden base prompt (§3 — the generated agent IS the system prompt).
- `assess.py` — `assess_skill(daytona, skill_item, agent_spec) -> result`. Fresh sandbox
  → run `candidate_code + grader_code` together → parse last stdout `GRADE:{...}` → map
  score to held level vs required → `finally` delete sandbox. Emits the lifecycle events
  `spawn/assign/execute/grade/report/teardown` (§3 `events.py` — implement the tiny
  `events.emit` here even though Phase 7 owns the visual; it's ~15 lines and never
  raises).

**Definition of Done (machine-checkable).**
- [ ] `python -c "from agent import generate_agent; import framework as f; r=f.resolve_role('data analyst'); print(generate_agent(r, f.get_skills(r), f.get_context(r), 'none'))"`
      prints a markdown spec that names all 14 skills and ends with the literal anchor `## Learned skill guidance`.
- [ ] A new script `assess_one.py` (or `python -m assess --one`) picks ONE seed skill,
      generates the v0 spec, runs the candidate + grader in a Daytona sandbox, and prints
      `GRADE:{"score": <0..1>}` (parseable). Sandbox is deleted (no orphans).
- [ ] The grader convention holds: last stdout line is `GRADE:{...}`; missing/garbled →
      score 0 + error note (§0.5 bug 6).
- [ ] Commit `phase2: one skill assessed end-to-end, spec-as-system-prompt`.

**Fallback.** `agent.py` returns junk → fall back to `agent_seed.md` as the v0 spec
(BUILD_GUIDE §8). `battery_seed.json` already exists; do not call `battery.py --generate`
in this phase.

**§0.5 watch-items.**
- **Bug 4:** the "Learned skill guidance" anchor must be empty now and stay last; Phase 4
  appends under it and any *other* spec section must be inserted *before* it.
- **Bug 6 (grader convention):** parse `GRADE:` bottom-up, clamp to [0,1], missing/garbled
  → 0 + error note.
- **Bug 5 (preview):** validate each battery item by running its own reference solution
  against its grader — but that's Phase 6's job for generated items; for the seed, just
  confirm the seed grader passes on the seed reference solution once.

**Loop guard.** Converges when `assess_one` prints a parseable `GRADE:` and the sandbox
is gone. If the candidate's code never runs (sandbox import/timeout), the loop lowers to
`MAX_PARALLEL=1` and raises the sandbox timeout to 20s (§0.5 constants) before retrying —
never fakes a bar. Stop after 5 iterations and surface the sandbox stdout/stderr.

---

## Phase 3 — Fan-out baseline + two-track report (`run.py` + `gap.py`)

**Goal.** Run the seed battery over the role's executable skills **in parallel**
(one sandbox per skill) using **spec v0**, and produce the **baseline two-track
scorecard**. BUILD_GUIDE §3 `run.py`/`gap.py`, §5 (honesty rule), §0.5 (two-track
promoted to core).

**Inputs.** Phase 1 `framework.py` (select_executable), Phase 2 `agent.py`/`candidate.py`/
`assess.py`. `battery_seed.json`. Constants from §0.5: `MAX_PARALLEL=4`, sandbox timeout
`20s`.

**Files to create / change.**
- `run.py` — orchestrate: resolve entry (Mode A: `--role` or hardwired demo role) →
  `build_battery` (from seed) → `generate_agent` (spec **v0**) → **Round 0 baseline:**
  assess every executable skill IN PARALLEL (`ThreadPoolExecutor`, `MAX_PARALLEL=4`).
  Save `output.json` (role + per-round reports). Fan-out knob `MAX_PARALLEL`. **Single
  agent, one role** (no `--team`, §9).
- `gap.py` — `gap_report(results) -> {coverage_pct, gaps(sorted), results}` and
  `print_report(...)`. Coverage = `(1 − Σgap / Σrequired) × 100` (scale-agnostic). Emit
  **two tracks** from day one: ✔ executed (the seed subset, filtered to the role's own
  codes — §0.5 bug 1) and ○ rubric (placeholder 0 / "not execution-verified" for the
  other 9 skills; Phase 6 fills the real rubric number). **Two numbers, never blended.**

**Definition of Done (machine-checkable).**
- [ ] `python run.py` (no `--generate`) runs the seed battery, fans out ≥2 sandboxes in
      parallel, and exits 0 with `output.json` written.
- [ ] Terminal `print_report` shows **two separate numbers**: an executed coverage %
      (over the executable subset) and a rubric track (placeholder, badged "NOT
      execution-verified"). No single blended %.
- [ ] The seed battery is filtered to the demo role's own skill codes
      (`seed ∩ role's codes`) — assert no fabricated 100% on unrelated skills
      (§0.5 bug 1).
- [ ] `output.json` keys: `role`, `rounds:[{round, spec_path, executed:{...}, rubric:{...}}]`.
- [ ] Commit `phase3: baseline two-track report, fan-out green`.

**Fallback.** Daytona quota/rate limit → lower `MAX_PARALLEL` to 1–2 (§8). Kimi-gen not
used here (seed only); if a seed grader crashes on candidate code, the grader's
try/except returns score 0 (§8).

**§0.5 watch-items.**
- **Bug 1 (enforce):** `seed ∩ role's-own-codes`. Without it every role "passes" the 3
  seed skills → fabricated 100%. This is the single most important guard in the phase.
- **Bug 6 (score→level bands):** ≥0.7 full level · ≥0.4 level−1 · else level−2 (floored
  at 0). Apply in `gap.py` so the held-level math is honest.
- Two-track discipline: even though the rubric track is a placeholder here, the
  **structure** must be separate so Phase 6 only fills the number, never merges tracks.

**Loop guard.** Converges when `run.py` exits 0, `output.json` is valid JSON with two
tracks, and no sandbox is orphaned. If parallel sandboxes rate-limit, the loop drops to
`MAX_PARALLEL=1` and retries — it does not fake bars. Stop after 4 full-run attempts.

---

## Phase 4 — Refine loop + `agent_final.md` (the lift)

**Goal.** Patch the markdown spec to close gaps → re-run → show **red→green lift** on at
least one skill, and save the patched spec as `agent_final.md` (the delivered artifact).
BUILD_GUIDE §3 `refine.py`, §4 (the demo-drama lever). This is where the money-shot
begins.

**Inputs.** Phase 3 `output.json` baseline (the gaps), `agent.py` (the spec v0),
`battery_seed.json`, `assess.py`. Constants: refine **1 round** suffices for visible
lift (§0.5), `TARGET_COVERAGE=90%`, `MAX_ROUNDS` small (2).

**Files to create / change.**
- `refine.py` — `make_injection(gap_item, task_prompt) -> str` (one concrete, reusable
  coach instruction per gap class). `patch_agent(agent_spec, gaps, battery) ->
  new_agent_spec` — appends learned instructions into the **"Learned skill guidance"**
  section (after the anchor), returns the updated spec.
- `run.py` change — add the **refine loop** (≤ `MAX_ROUNDS`): `patch_agent` → spec v1 →
  re-assess in parallel → new report; stop at `TARGET_COVERAGE` (90%). Save
  `agent_final.md` = the final patched spec. Append round 1 to `output.json`.

**Definition of Done (machine-checkable).**
- [ ] `python run.py` produces **both** a baseline (v0) and a lifted (v1) round in
      `output.json`; `agent_final.md` exists and is the v1 spec.
- [ ] At least one executable skill's score **increased** v0→v1 (honest lift, not a
      fabricated jump). Print `BASELINE: X% → FINAL: Y%` with Y > X.
- [ ] `agent_final.md` ends with the Learned guidance section **populated** (refine
      appended real instructions there), and no spec section was inserted *after* the
      anchor (§0.5 bug 4).
- [ ] Commit `phase4: refine loop shows lift, agent_final.md saved`.

**Fallback.** If refine produces no lift in 1 round, the loop may widen the gap
honestly: make v0's competency lines terse and let refine add specifics (edge cases,
output format, rounding, tie-breaks) — the §4 demo-drama lever. Never fake a bar to
manufacture lift (§8: a fabricated score is worse than a low one).

**§0.5 watch-items.**
- **Bug 4:** if any new spec section is needed, insert it **before** the Learned
  guidance anchor — else the next refine pass silently destroys it.
- **Bug 2 (preview):** any text cap on what a judge reads must be ≥ the generator's max
  output. Not yet a judge here (Phase 6), but keep `agent_final.md` full-length when
  Phase 6's rubric judge reads it.
- Refine = markdown patching only. Fine-tuning on Nosana is **spoken roadmap**
  (Phase 7, §9 scope discipline).

**Loop guard.** Converges when v1 > v0 on ≥1 skill and `agent_final.md` is saved. If
after 2 rounds there is zero lift, the loop must **stop and report** — zero lift means
either the gap report is wrong or the seed battery doesn't exercise a refinable gap; do
not keep looping. (This is the signal to consider the §4 demo-drama lever, not to lower
the DoD.)

---

## Phase 5 — Dashboard (the visual) + the rehearse gate

**Goal.** Render the two-track scorecard as a red→green before/after view with the
headline number, side-by-side with the delivered `agent_final.md`. Then **stop and
rehearse.** BUILD_GUIDE §3 `dashboard.py`, §6 step 6 (Stop here and rehearse), §9.

**Inputs.** Phase 3/4 `output.json` (per-round two-track reports), `agent_final.md`.

**Files to create / change.**
- `dashboard.py` — v1's before/after HTML table (red/green bars + headline %). Add a
  section rendering `agent_final.md` so the screen shows *the delivered agent* next to
  *the proof*. Render **both tracks** (✔ executed bars + ○ rubric bars, never blended).
  Auto-open in browser.
- Optional: lean on `dashboard_mockup.html` as a style reference (already in repo).

**Definition of Done (machine-checkable).**
- [ ] `python dashboard.py` writes `dashboard.html` and opens it; the page shows
      baseline→final bars with the headline `BASELINE X% → FINAL Y%`.
- [ ] Both tracks are visible and labelled: ✔ Execution-verified and ○ Rubric-assessed
      (badged "NOT execution-verified"). No single blended number on screen.
- [ ] The `agent_final.md` spec is rendered in a panel next to the bars.
- [ ] **Rehearse gate:** a dry run of the 2-minute demo script (BUILD_GUIDE §7 steps
      1–6) runs end-to-end (`smoke_test` → `run.py` → `dashboard.py`) without errors.
- [ ] Commit `phase5: dashboard two-track visual + agent panel, rehearse gate green`.

**Fallback.** If `output.json` is malformed, render from the last good round with a
warning banner. Auto-open failing on a headless box → print the file:// URL instead.

**§0.5 watch-items.**
- Two-track honesty on screen: a single blended bar would silently fabricate 100% (§0.5
  — the Contract Specialist fake-100% lesson). The dashboard is where that bug becomes
  visible to judges, so the visual separation matters as much as the data separation.
- §9 scope discipline: dashboard working by ~3:30; spend the last hour rehearsing, not
  adding features. This phase's DoD *includes* the rehearsal.

**Loop guard.** Converges when the dashboard opens with both tracks + the spec panel and
the §7 dry run is clean. **This is a hard stop gate:** do not enter Phase 6 until the
core loop (0→5) is green AND rehearsed. The loop must enforce this — if rehearsal
reveals a flaky step, fix the flake in the phase that owns it before moving on.

---

## Phase 6 — Real grounded battery + Oxylabs seasoning + rubric track (the differentiator)

**Goal.** Replace the seed battery with a **Kimi-generated, K&A-grounded** battery, make
the **Oxylabs** call visibly fire, and fill the **○ rubric track** with a real LLM-as-judge
score over non-executable skills' K&A checklists. This is the v3-promoted two-track
differentiator (§0.5) and where Oxylabs becomes load-bearing. BUILD_GUIDE §3
`battery.py`/`oxylabs_fetch.py`, §2 sponsor map, §10 (Oxylabs visibility rule).

**Inputs.** Phase 1 `framework.get_ka()` (the per-level K&A items), Phase 2–5 pipeline.
Oxylabs credentials (Web Scraper API). Constants: battery-gen temp **0.2**, judge temp
**0.0** (§0.5).

**Files to create / change.**
- `battery.py` — `generate_skill(role, skill, required_level, context, ka_items,
  task_material) -> {skill, required_level, task_prompt, grader_code, code}`. STRICT-JSON
  contract (a `solve(...)` task + self-contained grader printing `GRADE:{...}`); prompt
  includes the skill title/level, the role's key tasks, the **per-level `ka_items`**, and
  the Oxylabs `task_material`. Temp 0.2. `build_battery(role)` orchestrates framework →
  select_executable → get_ka per skill → per-skill generate; falls back to
  `battery_seed.json` if generation yields nothing. `rubric_score(skill, level, ka_items,
  agent_spec) -> {covered, total, pct}` — LLM-as-judge checklist over the skill's K&A
  items (one point each), temp 0.0; badged "NOT execution-verified".
- `oxylabs_fetch.py` — `fetch_task_material(role_title) -> str | None`,
  `fetch_salary_band(role_title) -> {...} | None`, `fetch_career_map(role_title) ->
  {prev, next, lateral} | None`. All never raise; `None` → proceed without seasoning.
- `run.py` change — `--generate` flag runs the real grounded battery; calls Oxylabs
  **once, up front, unconditionally**, prints `Oxylabs: pulled N current postings for
  <role>` (§10 visibility rule). Fills the rubric track for the 9 non-exec skills → real
  two-track headline: *"Executed: X/Y (Z%) · Rubric: A/B (C%)"*.

**Definition of Done (machine-checkable).**
- [ ] `python run.py --generate` produces a Kimi-generated battery grounded in `get_ka`,
      and the run still exits 0 with a two-track `output.json`.
- [ ] Terminal shows the Oxylabs line `Oxylabs: pulled N current postings for Data
      Analyst / Associate Data Engineer` (N≥1 on a live run; if Oxylabs is down, the
      fallback prints `Oxylabs: unavailable, proceeding without seasoning` — never
      silent).
- [ ] The rubric track now shows a **real** number (A/B K&A items, C%) for the
      non-executable skills, badged "NOT execution-verified"; the executed track stays
      separate. Headline reads two numbers, never one blend.
- [ ] Each generated battery item is self-validated: its own reference solution passes
      its own grader in a sandbox (§0.5 bug 5) — bad items are dropped, not shipped.
- [ ] Commit `phase6: grounded battery + Oxylabs live + rubric track`.

**Fallback.** Kimi battery-gen returns bad JSON → `build_battery` falls back to
`battery_seed.json`; run `run.py` (no `--generate`) (§8). Oxylabs down/no key →
`fetch_task_material` returns `None`, battery-gen proceeds unseasoned. Role scores
suspiciously high → check the `seed ∩ role's-own-codes` filter (bug 1).

**§0.5 watch-items (the hard ones live here).**
- **Bug 2 (judge truncation):** any text cap on what the rubric judge reads must be ≥ the
  generator's max output. The rubric judge must see the **full** `agent_final.md` — never
  a 4k truncation of an 18k artifact.
- **Bug 3 (atomic rubric criteria):** each K&A item must be assessed as **one
  requirement, about what the deliverable contains** — never compound, never ops/process
  (uptime, sign-off, audit trails). Compound or ops criteria grade 0 unfairly.
- **Bug 5 (strict JSON):** `response_format json_object` + client-side validate-and-retry;
  validate each item statically AND by running its reference solution against its grader.
- **Bug 6:** grader convention + score→level bands apply to generated graders too.
- Oxylabs visibility (§10): the forced upfront call exists *so judges see it*; the
  fallback guards the rest of the run, not this line.

**Loop guard.** Converges when `--generate` runs green with both tracks populated and the
Oxylabs line printed. If generated items keep failing self-validation, the loop must cap
the retry count, drop the bad items, and `log()` how many were dropped (§0.5 — no silent
caps). If it cannot get ≥1 valid generated item, fall back to the seed battery and
report that honestly.

---

## Phase 7 — Task-first entry (Mode B) + events lifecycle stream + Nosana call

**Goal.** (a) Let a user describe a task → `classify.py` retrieves and ranks **real**
roles (never invents) → runs the same loop on the top role. (b) Wire the `events.jsonl`
lifecycle stream into a live lane animation. (c) Make the honest Nosana call. BUILD_GUIDE
§3 `classify.py`/`events.py`, §6 step 7–8, §7.5, §10 (Nosana Option A/B).

**Inputs.** Phase 1 role corpus (each role's `description` + CWF/key_tasks). Phase 2
`events.emit` (already stubbed). The Nosana decision: **decide A or B before the day**
(§10).

**Files to create / change.**
- `classify.py` — `recommend_roles(task, k=3) -> list[{role, sector, confidence,
  matched_on, skill_weights}]`. Two-tier: (1) keyword/TF-IDF over the role corpus
  (deterministic, demo-safe — **do not attempt embeddings on the day**, §0.5), then
  (2) Kimi-as-ranker over the top-N (Kimi only *chooses among* dataset roles, never names
  one from scratch). Demo cap: resolve to **one** role. Optional `ssic_hint` re-rank.
- `events.py` — formalize `emit(event, **kw)` → append JSON line to `events.jsonl`
  **and** print it. Shape `{ts, agent, skill, sandbox_id, event, detail}`. Never raises.
- `run.py` change — `--task "…"` → `classify.recommend_roles()` → take top role → run
  the loop. Save `events.jsonl`. A `demo_theatre.html` replays `events.jsonl` for the
  live lane animation (spawn→assign→execute→grade→report→teardown).
- Nosana — pick **Option A** (spoken roadmap: "deep-refine via a fine-tune on Nosana GPU
  to close residual gaps") OR **Option B** (serve the candidate model as GPU inference on
  Nosana for ≥1 skill's attempt). Recommended: A, unless the booth makes B trivial.

**Definition of Done (machine-checkable).**
- [ ] `python run.py --generate --task "review vendor NDAs and pull payment terms into a comparison"`
      classifies to a **real** dataset role (e.g. a Legal/Accountancy role), resolves to
      one role, and runs the loop to a two-track `output.json`. No invented role/skill.
- [ ] `events.jsonl` is written with at least one of each lifecycle event
      (spawn/assign/execute/grade/report/teardown) per assessed skill.
- [ ] `demo_theatre.html` replays `events.jsonl` into a visible lane animation (or
      `dashboard.py` falls back cleanly to `output.json` if the events file is absent).
- [ ] Nosana decision (A or B) is recorded in this repo (e.g. a one-line `NOSANA.md`) and
      rehearsed in the §7.5/§10 beat. If B: one skill's bar provably came from a
      Nosana-hosted model.
- [ ] Commit `phase7: task-first entry + events stream + Nosana call decided`.

**Fallback.** Task too vague → `classify` returns low-confidence matches; prompt for one
clarification or fall back to Mode A / hardwired role (§8). Task matches no dataset role
well → show top-3 low-confidence roles; never invent one. `events.jsonl` not writable →
`events.emit` never raises; dashboard falls back to `output.json` (§8).

**§0.5 watch-items.**
- **classify must never fabricate** a role or skill — retrieval + rank only. This
  guardrail is the whole reason the proof means anything (§3, §0.5 Mode B).
- **No `handoff.py` day-of.** Cross-role teams + agent→agent seams are *shown with
  receipts* from the production build (§7.5), not rebuilt. The honesty framing: the seam
  is **exercised** (real artifacts produced/consumed in separate containers) but
  **rubric-assessed, not execution-verified** — never blended into the executed number.
  Never say "the agents talk to each other" or "this ran today."
- §9 scope: open-ended multi-role teams are *spoken* product vision, not day-of code.

**Loop guard.** Converges when `--task` resolves to one real role and runs green with an
events stream. If `classify` cannot retrieve a confident role, the loop must **stop and
ask** for a clarification or fall back to Mode A — never invent a role to keep going.

---

## How to run each phase as a loop

Each phase is one `/loop` invocation. Give the loop the phase's Goal + DoD as its target,
and let it converge on the green checkboxes. Suggested prompts (one per phase):

```
/loop Implement Phase 0 of PHASED_IMPLEMENTATION_PLAN.md. Stop when smoke_test.py
       prints KIMI: OK and DAYTONA: OK and the phase0 commit is made.

/loop Implement Phase 1 ... framework.py prints the real 14 skills + the asserted
       K&A strings; commit phase1.

/loop Implement Phase 2 ... assess_one prints a parseable GRADE: from a sandbox;
       commit phase2.

/loop Implement Phase 3 ... run.py fans out and writes a two-track output.json;
       commit phase3.

/loop Implement Phase 4 ... v1 > v0 on >=1 skill, agent_final.md saved; commit phase4.

/loop Implement Phase 5 ... dashboard opens with both tracks + spec panel and the
       §7 dry run is clean; commit phase5. (Hard stop gate — enforce the rehearsal.)

/loop Implement Phase 6 ... run.py --generate green, Oxylabs line printed, rubric
       track filled; commit phase6.

/loop Implement Phase 7 ... --task resolves to a real role, events.jsonl written,
       Nosana decision recorded; commit phase7.
```

**Between loops:** read the previous phase's diff, confirm the DoD checkboxes are green
in the commit, then start the next. Do not let a later loop edit a prior phase's files to
"make it pass" — fix forward, in the owning phase.

---

## Sponsor coverage at the phase gates (which sponsor goes load-bearing when)

| Sponsor | Becomes load-bearing at | Visible on stage as |
|---|---|---|
| **Daytona** (title) | Phase 0 (smoke), Phase 2 (one sandbox), Phase 3 (fan-out) | sandboxes per skill; every green bar = code that ran in one |
| **Kimi** | Phase 2 (candidate driven by spec), Phase 4 (refine), Phase 6 (battery+spec gen) | generates the battery + the agent + drives the candidate |
| **SkillsFuture** (data) | Phase 1 (the 14 skills + K&A), Phase 6 (rubric track) | "this isn't invented — it's Singapore's national framework" |
| **Oxylabs** | Phase 6 (forced visible call) | `Oxylabs: pulled N current postings for <role>` line |
| **Nosana** | Phase 7 (Option A spoken roadmap, or B live) | the honest roadmap beat (or one Nosana-hosted bar) |

By the end of Phase 6, four sponsors are load-bearing; Phase 7 adds the Nosana honesty
beat. This matches BUILD_GUIDE §10.

---

## Pre-demo 60-second pass (the final gate, after Phase 7)

Run in order (BUILD_GUIDE §10). All must be ☐→☑ before presenting:
1. `smoke_test.py` green (Daytona + Kimi both respond).
2. Oxylabs forced probe printed a real "pulled N postings" line (or, if Oxylabs is down,
   drop the "live" claim and show the saved snippets).
3. `run.py` produced a baseline **and** a lifted final, and `agent_final.md` exists.
4. `dashboard.py` opens with red→green bars + headline number, two tracks visible.
5. Nosana line decided (A or B) and rehearsed.

---

## Scope discipline reminders (do not blow the day — BUILD_GUIDE §9)

- ONE role, the executable subset (~5 skills), until the loop is green. Resist expanding.
- Entry = Mode A (pick the role) for the live build; Mode B (`classify.py`) is Phase 7
  stretch and must resolve to ONE role.
- Single agent for the demo. Team-gen + agent→agent seams are **shown with receipts**
  (§7.5), not rebuilt day-of. **Do not build `handoff.py`.**
- Two-track scorecard is **core, not stretch** (Phase 3 structure, Phase 6 numbers).
- Fast-refine = patch the markdown only. Fine-tuning on Nosana = spoken roadmap.
- A tight, working, *honest* loop beats a broad broken one on the Completeness criterion.

---

## Sources (verify at the event)

- Daytona docs: https://www.daytona.io/docs/en/ (getting-started, python-sdk,
  file-system-operations, process-code-execution)
- Kimi API: https://platform.moonshot.ai/ · coding-tuned model id (verify day-of)
- Oxylabs Web Scraper API: https://oxylabs.io/
- Data: SkillsFuture Skills Framework dataset (the xlsx in this folder) · SSOC 2024
  (the two xlsx in this folder)
- SingStat SSOC direct downloads + SkillsFuture sector URLs: see `scraping-urls.md`
