# Project Refresh — Read This When You're Lost

> Companion to `ProjectPivot.md`.
> **`ProjectPivot.md`** = the strategy (what we're doing and why).
> **This file** = the *conceptual understanding* (what the pieces mean and how they fit).
>
> When you come back after a week away and forget what this project actually *is*, read this first.

---

## The 30-second version

You are building two NPCs who share a body but differ in brain.
- One uses **rigid threshold rules** (baseline).
- The other uses **utility math** — nonlinear **response curves** + **action inertia** (utility agent).

You measure how much more **stable** and **adaptable** the utility agent is.
Eventually (Fall 2026+), you isolate *which of the two mechanisms* deserves the credit.

That's the whole project. Everything else is plumbing.

---

## The three layers (in case the 30-second version feels fuzzy)

### Layer 1 — The BIG question
> *Can lightweight utility AI — just curves and inertia, no LLMs — produce NPCs that feel like they have personalities and behave stably over time?*

This is what Dr. Amini's recommendation letter tells outside readers. Positioning: **lightweight alternative to Generative Agents (Park et al. 2023).**

### Layer 2 — The EXPERIMENT
Two agents in the same room, same body, same needs (hunger, energy), same world. **Different brains.**

| Agent | Brain | Curves? | Inertia? |
|---|---|---|---|
| **Baseline** | *"If hunger < 0.3, go eat."* Hardcoded if-then. | ❌ | ❌ |
| **Utility** | Score every option, pick the best. | ✅ | ✅ |

Run them. Record what happens. Compare.

**The sentence Dr. Amini literally told you to put on Slide 2:**
> *"We compare a baseline threshold agent (rigid) against a utility-scored agent (fluid) across stability and adaptability metrics."*

### Layer 3 — The MECHANISMS (what makes this a thesis, not homework)
Utility has two moving parts doing different jobs:

- **Response curves** → control **personality**. Different curve shape = different character.
- **Action inertia** → controls **stability**. Prevents abandoning a task mid-way.

Your thesis claim: *both mechanisms matter, and we can measure how much each one contributes.*

**What Dr. Amini told you to *say out loud* during the meeting (not required on any slide):**
> *"My contribution is not replicating these existing systems, but experimentally isolating utility-based scanning and inertia mechanisms to quantify their impact on behavioral stability."*

---

## FAQ — the questions you've already asked yourself

### Q1. "We only have hunger and energy. Can we actually build 'personality' with just two needs?"

**Yes.** Personality doesn't come from how many needs you have. It comes from **how the agent weighs them** via curves.

With 2 needs + 3 curve presets (already built in `ResponseCurveWizard`), you get:

| Hunger curve | Energy curve | Personality |
|---|---|---|
| Late-Panic | Human-Like | *Workaholic* — skips meals, naps on time |
| Human-Like | Late-Panic | *Gourmet insomniac* — eats well, stays up too late |
| Human-Like | Human-Like | *Balanced person* |
| Late-Panic | Late-Panic | *Crisis junkie* — always in emergency mode |
| Linear | Linear | *Reactive robot* — no character |

**Five distinct agents from the same C# code, just swapping curve assets.**

That's what Dr. Amini's rec letter means by *"simulating personality traits."*

---

### Q2. "Is believability only about not jittering?"

**No.** Jittering is ONE failure mode. Believability breaks in at least four ways:

| Failure | What it looks like | Which agent shows it |
|---|---|---|
| **Jitter** | Flips action every 2 seconds | Utility without inertia |
| **Rigidity** | Acts identically every run, no character | Baseline |
| **Bad prioritization** | 10% energy + 30% hunger → eats first (wrong call) | Baseline |
| **No anticipation** | Waits until desperate before acting | Both (more fixable in utility) |

- **Stability (no-jitter)** is the one we *measure numerically* because it's easy to count.
- Other failures show up in **qualitative demos / comparison videos**.

So: stability = quantitative claim. Believability = qualitative claim. Both matter.

---

### Q3. "Baseline doesn't jitter in my demo. So where's the problem?"

Baseline looks fine *because your current world is easy.* Decay rates are offset, so hunger and energy never disagree.

**But baseline breaks the moment the world gets harder.** Four scenarios to build later:

#### Scenario A — Contention (two needs low at the same time)
If hunger and energy both cross threshold simultaneously, baseline either picks the first rule always (rigid) or flip-flops every frame. Utility scores both and picks the higher-desire one.

#### Scenario B — Anticipation (a need at 31%, draining fast)
Baseline ignores it until 30%, then panic-responds. Utility sees desire rising continuously and can move proactively.

#### Scenario C — Perturbation (resource removed / blocked)
Baseline rule says "if hungry, go to fridge." Fridge removed? **Baseline stuck.**
Utility scans all affordances, picks next-best option.

#### Scenario D — No personality
Run baseline 10 times. Exact same behavior every time. That's a thermostat, not a character.

**Why this matters:** Your test scenarios aren't built yet. For **Spring 2026** you just need to show *capability* (visible A/B difference). For **Fall 2026** you build:
- Contention scenarios (two needs drop together)
- Perturbation scenarios (block fridge mid-run)
- Long-duration runs (24 sim-hours) to catch habit differences

This is what "adaptability metrics" in Dr. Amini's email refers to.

---

### Q4. "Utility switches mid-sleep — is that the unbelievable thing?"

**Yes.** Humans sleep through minor hunger. Your utility agent doesn't — yet. Possible causes, in order of likelihood:

1. **Inertia bonus too small.** Current `CommitmentBonus = 0.15`. Try 0.25 or 0.30. If 0.30 fixes it → finding: realistic inertia must offset ~1 level of need urgency.
2. **Hunger curve too steep early.** If curve gives desire=0.5 when hunger=0.6 (still pretty full), it's too eager. Late-Panic curve gives ~0.05 at hunger=0.6 → stays asleep.
3. **Re-evaluation interval too short.** `DecisionInterval = 0.5s` = asking "should I still sleep?" every half-second. Try 1.0–2.0s for bigger commits.
4. **Min-action-duration too short.** `MinActionDuration = 1.5s` prevents first-1.5s interruptions. Long tasks (sleep) may need 5–10s.

**The conceptual point:** this is a *finding*, not a bug. You just discovered utility *without the right tuning* is NOT automatically believable. Finding the right tunings IS part of the thesis. When someone asks "why is this research?" one answer is: *because tuning these knobs is a non-obvious engineering problem that deserves systematic study.*

---

## Key tunings to remember (cheatsheet)

Current values in `AgentCore.cs` / `UtilityAgent.cs`:

| Parameter | Current | What it does | Try if behavior is wrong |
|---|---|---|---|
| `CommitmentBonus` | 0.15 | Inertia — extra score for current action | ↑ if agent flips too much; ↓ if agent never switches |
| `ActivationThreshold` | 0.3 | Min score to act (otherwise idle) | ↑ for more idle time; ↓ for more activity |
| `DecisionInterval` | 0.5s | How often brain re-evaluates | ↑ for more committed behavior |
| `MinActionDuration` | 1.5s | Minimum commit before interrupt allowed | ↑ (5–10s) for long tasks like sleep |
| `StopDistance` | 0.5 | How close before "arrived" at target | Tune with SideOffset for collider issues |
| `SideOffset` | ±1.0 | Perpendicular stand distance from object | Baseline and Utility on opposite sides |

---

## What Dr. Amini sees (so you stay aligned)

From his **recommendation letter**, outside readers are told:
- You are doing *"simulating personality traits in NPCs using utility-based AI"*
- Mechanisms: *"nonlinear response curves and action inertia"*
- Goal: *"believable and autonomous agent behaviors in life-simulation environments"*
- Positioning: *"avoiding the heavy computational cost of large generative models"*
- Evidence: *"behavioral stability testing through systematic data logging and analysis"*

From his **email** — two distinct asks:
1. **On Slide 2 (literal, word-for-word):** *"We compare a baseline threshold agent (rigid) against a utility-scored agent (fluid) across stability and adaptability metrics."*
2. **Verbally in the meeting (not required on slide):** *"My contribution is not replicating these existing systems, but experimentally isolating utility-based scanning and inertia mechanisms to quantify their impact on behavioral stability."*

**Before finalizing any slide, ask:** *"If Dr. Amini were handing this slide to a committee member, would it match what his rec letter already told them?"*

---

## If you're ever fully lost — read in this order

1. This file (conceptual refresh)
2. `ProjectPivot.md` (strategy + scope guardrails)
3. Open Unity, run the scene, watch the two agents for 2 minutes
4. Come back and re-read layer 2 of this doc

That's usually enough to reorient in under 10 minutes.

---

*Last updated: 2026-04-19. Update this doc when your understanding of the project changes — not when trivia changes.*
