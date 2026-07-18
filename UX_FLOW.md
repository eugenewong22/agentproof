# AgentProof — UX & User Flow

Companion to `BUILD_GUIDE.md`. This maps the product experience: how a user requests an
agent, sets skill targets (RPG-style), watches it get proven, and takes away the result.

---

## 1. The core decision: max out, or RPG point-buy?

**Question:** when a user requests an agent for a role, does every skill max out, or do they
distribute a fixed pool of points like character creation?

**Answer: neither. Default every skill to its official required level; charge "points" only for
pushing a skill *above* that baseline.**

### Why not zero-sum point-buy
Classic RPG point-buy models **zero-sum capacity** — a character can't be strong at everything
because stat points are finite. That constraint is real for humans and **false for AI agents.**
Teaching the agent SQL doesn't cost it statistics; guidance for one skill doesn't subtract from
another. A forced point pool would impose scarcity that doesn't exist and would make the delivered
agent *worse than it could freely be*. Never gate the agent's capability behind points.

### Why not max-everything
Maxing is uninformative — every agent becomes identical, the target profile carries no signal, and
the scorecard is uniform. You can't see at a glance that "this associate is a SQL specialist."

### What the user actually wants: intent, not budget
The real need is **prioritization** — "strong on data transformation and SQL, don't care about
visualization." That's target-setting. So:

- **Baseline is free.** Every skill pre-set to its official SkillsFuture required level. The default
  is itself the smart answer: *meet the national standard for this role.*
- **Sliders** let the user raise (specialize), lower, or zero-out (deselect) any skill. This is the
  RPG *feel* — visible levels, a loadout screen — without false scarcity.
- **Optional "proof budget" (stretch):** if you want a genuine game mechanic, charge points **only for
  over-investment above baseline**, framed as *proof/refine effort*, not agent capacity. Staying at
  baseline everywhere costs nothing; pushing a skill to L5 spends budget, so specializing one skill
  means accepting baseline on the rest. Honest ("you get what you invest") and it forces the fun
  tradeoff exactly where the tradeoff is real.

> **One-liner:** points model scarcity; an agent's skills aren't scarce — so don't charge for
> capability, only for how far above the official bar you want to *prove* it.

### The target level does triple duty (mechanics the UX rides on)

| The user sets a skill's target to… | Effect on the system |
|---|---|
| **Below** the agent's real ability | Trivial pass (score ~1.0, gap 0) — easy green, inflates coverage |
| **At / above** the official level | A real gap the refine loop must close — this is where "lift" comes from |
| **0 (deselect)** | Removed from the battery *and* from the generated spec — the agent isn't built or tested for it |
| **Max** | Lower baseline coverage but a bigger, more impressive baseline→final lift (**demo-drama lever**) |

---

## 2. Design principles

1. **Recommend real roles, never invent them.** A user can arrive with a role *or* a task. In task
   mode the system *classifies* the task into actual SkillsFuture roles and recommends them — it never
   fabricates a role or a skill. The proof only means something because it's graded against an
   official bar; inventing the team walks the made-up-skills problem right back in the front door.
2. **Grounded defaults over blank slates.** Never show an empty form. The role's official skills and
   levels are already there; the user *edits*, not authors.
3. **One decision per screen.** Request → (confirm team) → Loadout → Watch → Deliver. Everything after
   "Generate" is automated.
4. **Honesty is visible, not buried.** Execution-verified skills are badged; targeted-but-not-verified
   skills are shown as such. The scorecard never over-claims.
5. **The deliverable and the proof are one object.** What you download is the exact spec that scored.

---

## 3. The user flow (two ways in, one path out)

```
 ┌──────────────┐   A: "I know the role"    ┌──────────────┐   ┌───────────┐   ┌───────────┐
 │  1 REQUEST   │──────────────────────────▶│ 2 SKILL      │──▶│ 3 BUILD & │──▶│ 4 DELIVER │
 │  choose a    │                           │   LOADOUT    │   │   PROVE   │   │ spec +    │
 │  way in ─────┤   B: "Describe the task"  │ (RPG sliders)│   │  (auto)   │   │ scorecard │
 │              │─▶┌──────────────────┐────▶│              │   │           │   │ ⟳ re-spec │
 └──────────────┘  │ 1b CONFIRM TEAM  │     └──────────────┘   └───────────┘   └───────────┘
                   │ recommended REAL │            ▲
                   │ role(s) —approve │            │
                   └──────────────────┘   task pre-weights the sliders
```

Both entry modes converge on the same **Loadout → Prove → Deliver** spine. Mode B adds one screen
(confirm the recommended team) before the loadout.

### Screen 1 — Request (two ways in)
```
┌─ REQUEST AN AGENT ───────────────────────────────────────────────┐
│   ( • I know the role )         ( ○ Describe the task )           │
│                                                                   │
│  ── Mode A: I know the role ──────────────────────────────────    │
│  Role   [ data analyst▏                                    ]  🔍  │
│         ┌───────────────────────────────────────────────────┐    │
│         │ Data Analyst / Associate Data Engineer            │    │
│         │   Infocomm Technology · Data & AI · SSOC 25xxx    │    │
│         │ Data Analyst — Financial Services                 │    │
│         └───────────────────────────────────────────────────┘    │
│                                                                   │
│  ── Mode B: Describe the task ────────────────────────────────    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ I need to review a stack of vendor NDAs and pull the       │  │
│  │ payment terms into a comparison table for Friday.          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Custom instructions (either mode)                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Focus on messy inputs; flag anything ambiguous.           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│   Mode A → [ Next: skill loadout → ]    Mode B → [ Recommend a team → ] │
└───────────────────────────────────────────────────────────────────┘
```
- **Mode A (I know the role):** search-as-you-type over the SkillsFuture roles, grouped by sector,
  SSOC code shown. Goes straight to the loadout.
- **Mode B (describe the task):** free text. The system extracts the task's duties and matches them
  against the ~1,977 *real* SkillsFuture roles — their descriptions and key tasks live in the dataset,
  so this is **retrieval, not invention** → it proposes a team of actual roles on Screen 1b.
- **The task never invents skills; it only *selects real roles*.** Your grounded pipeline then runs
  unchanged. The task also **pre-weights the loadout sliders** — "review NDAs / payment terms" arrives
  with the relevant skills already pushed up, so the free-text does double duty (role selection *and* a
  first-draft profile).
- Custom instructions apply in both modes and are carried verbatim into the generated spec.

### Screen 1b — Confirm recommended team  (Mode B only)
```
┌─ RECOMMENDED TEAM ───────── from your task ──────────────────────┐
│  "Review vendor NDAs and pull payment terms into a comparison"   │
│                                                                   │
│  Matched to these real roles (SkillsFuture):        confidence    │
│  ☑ Legal Reviewer / Paralegal            Legal svcs   ████░  82%  │
│      matched on: contract review, obligation extraction           │
│  ☑ Data Analyst / Assoc. Data Engineer   ICT          ███░░  61%  │
│      matched on: build comparison table, structure data           │
│  ☐ Compliance Specialist                 Legal svcs   ██░░░  38%  │
│                                                                   │
│  You're hiring 2 roles. Deselect any, or add one.                 │
│                                        [ Set loadouts → ]         │
└───────────────────────────────────────────────────────────────────┘
```
- Every recommendation is an **actual** SkillsFuture role with a match confidence and the duties it
  matched on — transparent, editable, human-in-the-loop. The user confirms who gets hired.
- Approving carries each role into its own loadout (Screen 2), sliders pre-weighted from the task.
- **Demo discipline:** cap the recommendation at one role (two at most). Every extra role multiplies
  batteries, sandboxes, and refine loops — see §5.

### Screen 2 — Skill Loadout (the RPG screen — the heart of it)
```
┌─ SKILL LOADOUT ─────────────── Data Analyst / Assoc. Data Engineer ──┐
│  Presets: [ Baseline ]  [ Specialize ]  [ Max ]     Proof budget     │
│           (= official levels, free)                 ▓▓▓▓▓▓░░  6 / 8   │
│                                                                      │
│  skill                        L0 ─────── target ─────── L6   note    │
│  ✔ Data Engineering           ────◆●──────────────      L2   official│
│  ✔ Database Administration    ────◆●──────────────      L2   official│
│  ✔ Data Analytics             ────◆────●──────────      L4   ▲ +2    │
│  ✔ Data Visualisation         ──────◆●────────────      L3   official│
│    Stakeholder Management     ────◆●──────────────      L2   ○ rubric│
│    Data Ethics                ●◆──────────────────      0    off      │
│                                                                      │
│  ◆ = official required level   ● = your target                       │
│  ✔ = execution-verified        ○ = rubric only (not run in sandbox)  │
│                                                                      │
│  ▲ +2 above baseline spends 2 proof-budget points.                   │
│                                        [ Generate agent → ]          │
└──────────────────────────────────────────────────────────────────────┘
```
- Sliders open **pre-set to the official level** (`◆`). Dragging `●` right = specialize (spends budget),
  left = de-emphasise, to 0 = deselect (drops the skill entirely).
- **Arriving from Mode B (task):** the sliders open pre-weighted from the task, not just at baseline —
  the skills the task matched on are already nudged up. The user still confirms or overrides.
- **Presets** are one-tap: *Baseline* (all official), *Specialize* (a starter profile the user tweaks),
  *Max* (all ceiling — warns that baseline coverage will be low and compute higher).
- **Proof budget** (optional/stretch) counts only over-baseline points; it's the honest RPG tradeoff.
  Ship the MVP with the meter hidden and budget effectively unlimited if you're tight on time.
- Non-executable skills stay visible and settable (they shape the spec) but are marked `○ rubric` and
  never claim a sandbox-verified bar.

### Screen 3 — Build & Prove (watch only; fully automated)
```
┌─ BUILDING & PROVING ─────────────────────────────────────────────┐
│  ① Generating agent spec from role + your loadout…      ✓         │
│  ② Baseline — running each skill in a Daytona sandbox (parallel): │
│                                                                   │
│     Data Engineering        ██████████████░░░░░░   71%            │
│     Database Administration ████████░░░░░░░░░░░░   40%  ⚠ gap     │
│     Data Analytics (L4)     ██████░░░░░░░░░░░░░░   32%  ⚠ gap     │
│     Data Visualisation      ████████████░░░░░░░░   58%  ⚠ gap     │
│                             ────────────────────                  │
│              Role-readiness: 58%   (baseline)                     │
│                                                                   │
│  ③ Refining — rewriting the agent's guidance, re-running…  ✓      │
└───────────────────────────────────────────────────────────────────┘
```
- Bars fill live as sandboxes report — this is the "watch Daytona work" moment.
- Refine is a single visible pass; the bars animate upward on re-run.

### Screen 4 — Deliver
```
┌─ DELIVERED ─────────── Data Analyst / Assoc. Data Engineer ───────┐
│                                                                   │
│  Role-readiness:   58%  ────▶  91%                                │
│                                                                   │
│  skill                       baseline        refined              │
│  Data Engineering            ▓▓▓▓▓▓░ 71%      ▓▓▓▓▓▓▓▓▓ 96%       │
│  Database Administration     ▓▓▓░░░░ 40%      ▓▓▓▓▓▓▓▓░ 88%       │
│  Data Analytics (L4)         ▓▓▓░░░░ 32%      ▓▓▓▓▓▓▓▓░ 85%       │
│  Data Visualisation          ▓▓▓▓▓░░ 58%      ▓▓▓▓▓▓▓▓▓ 94%       │
│                                                                   │
│  Every green bar = code THIS agent wrote that ran in a sandbox.   │
│                                                                   │
│  [ ⬇ Download agent spec ]  [ ⧉ Copy ]  [ ⟳ Adjust loadout ]      │
└───────────────────────────────────────────────────────────────────┘
```
- Two artifacts side by side: the **agent/team markdown** (download/copy) and the **scorecard**.
- **Market context strip (Oxylabs):** under the headline, show the role's **salary band** and a compact
  **career map** (prev ← this role → next / lateral). It frames the proof in real-world terms —
  *"here's your associate, here's what this role earns, here's where it grows."* Both are scraped, both
  fallback-silently if unavailable (no empty box).
- **⟳ Adjust loadout** returns to Screen 2 with the same role — the re-spec loop. Cheap iteration.

---

## 4. States & edge cases

| State | Behaviour |
|---|---|
| Role ambiguous / not found (Mode A) | Screen 1 shows ranked suggestions; picking one resolves sector + SSOC |
| Task too vague to classify (Mode B) | Ask **one** clarifying question rather than guessing a role |
| Task matches no role well (Mode B) | Show the top-3 low-confidence matches; let the user pick or switch to Mode A |
| Task matches many roles (Mode B) | Rank by confidence, pre-select the top 1–2, let the user add/remove on Screen 1b |
| Every skill set to 0 | "Generate" disabled — an agent needs at least one skill |
| Only rubric (non-exec) skills selected | Warn: "no skills can be execution-verified — the scorecard will be rubric-only" |
| Kimi battery-gen / agent-gen fails | Silent fallback to seed battery / `agent_seed.md`; user sees a normal run |
| Oxylabs unavailable | No banner needed; tasks generate without market seasoning |
| Refine can't reach the target | Screen 4 shows the honest final (e.g. 78%) and flags which skills still gap — do **not** fake 90% |
| User maxed everything | Proceed, but note longer build + lower baseline (this is fine — bigger lift) |

---

## 5. MVP vs stretch (hackathon scope)

**MVP for the demo (what you actually show on the day):**
- Entry is **Mode A only**, with the role **hardwired** to Data Analyst / Associate Data Engineer
  (no live search, no task classifier).
- Loadout = the executable subset with sliders **defaulted to official levels**; proof budget hidden.
- Screens 3 + 4 realised as the **terminal run + `dashboard.html`** — no need for a clickable web app.
- Single agent (not a team).

**Stretch, in priority order:**
1. Live role search (Screen 1, Mode A) over the full SkillsFuture set.
2. **Task-first entry (Mode B + Screen 1b)** — classify a free-text task into *real* roles and
   recommend a team. For the demo, resolve to **one** role (two at most); open-ended multi-role swarms
   are spoken product vision, not day-of code. Steer the demo task toward an executable role so the
   proof bars stay honest.
3. The proof-budget meter (Screen 2) with over-baseline scoring.
4. Team loadout — a lead + per-skill-cluster specialists (the *lawyer* customer story).
5. In-browser re-spec loop (Screen 4 → 2) instead of re-running from the CLI.

> Per `BUILD_GUIDE.md` §9: a tight, honest loop beats a broad broken one on *Completeness*. The UI is
> the first thing to cut; the loadout defaults + terminal + dashboard already tell the whole story.

---

## 6. How the screens map to the build

| Screen | Modules |
|---|---|
| 1 Request — Mode A | `framework.resolve_role()`, `framework.get_sector()`, `framework.ssoc_code()`; instructions → `agent.generate_agent()` |
| 1 Request — Mode B + 1b | **new `classify.py`** → `recommend_roles(task)`: embeds the task, matches it against `framework` role descriptions + key tasks, returns ranked *real* roles + per-skill weight hints. Optional `framework.ssic_hint(company_type)` re-ranks toward a sector; `oxylabs_fetch.fetch_career_map()` `lateral`/`next` roles suggest teammates. User approves → each role enters its own loadout |
| 2 Loadout | `framework.get_skills()` supplies default levels (via `normalize_level()`); `framework.select_executable()` sets the ✔ badges; each slider overrides that skill's `required_level` (in Mode B, initialised from the classifier's weight hints) |
| 3 Build & Prove | `framework.get_ka()` grounds `battery.generate_skill()`; `agent.generate_agent()` (spec v0) → `run.py` fan-out (`assess.py` per skill in Daytona, `rubric_score()` for `○` skills) → `refine.patch_agent()` → re-run |
| 4 Deliver | `agent_final.md` (download) + `output.json` → `dashboard.py`; market strip from `oxylabs_fetch.fetch_salary_band()` + `fetch_career_map()` |

The slider values are just the per-skill `required_level` the rest of the pipeline already consumes —
so the RPG loadout is a thin UI layer over the mechanics in the build guide, not new machinery.
