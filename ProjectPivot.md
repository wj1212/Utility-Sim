# Project Pivot — Spring 2026

> A north-star document. Read this before making decisions about scope, slides, or code.
> If something we're about to do doesn't map to this page, stop and ask whether we're drifting.

---

## 1. The thesis, in one sentence

> **We compare a baseline threshold agent (rigid) against a utility-scored agent (fluid) across stability and adaptability metrics, experimentally isolating two mechanisms — nonlinear response curves and action inertia — to quantify their individual impact on behavioral stability in NPC simulation.**

If a slide, paragraph, or feature does not support this sentence, it does not belong in the thesis.

---

## 2. The contribution (what makes this research, not engineering)

This project is **not** a lightweight remake of The Sims or RimWorld. Those already exist.

The contribution is the **experimental isolation** of two specific mechanisms within utility-based AI:

1. **Nonlinear response curves** — mapping need level to action desire via non-linear functions (S-curves, exponential, etc.) rather than linear thresholds.
2. **Action inertia** — a mathematical commitment bonus applied to the currently active task, reducing oscillation between candidate actions.

Prior work (RimWorld, Dave Mark's writings, industry talks) demonstrates that utility AI *works*. No prior work cleanly measures **which mechanism produces the stability gains**. That is the gap this thesis fills.

---

## 3. Why this matters (the positioning)

Modern NPC research has two camps:

- **Heavy / Generative** — Stanford's "Generative Agents" (Park et al., 2023). Believable, but expensive, cloud-dependent, non-reproducible.
- **Lightweight / Classical** — utility AI, behavior trees, GOAP. Cheap and local, but under-studied empirically.

This thesis sits firmly in the lightweight camp and asks: *how much of utility AI's behavioral quality comes from each of its mechanisms?* That is a question LLM-based work cannot answer, and that classical-AI practitioners have not rigorously answered either.

---

## 4. What we are NOT doing (scope guardrails)

To resist drift, explicit exclusions:

- ❌ No LLM integration.
- ❌ No social simulation between multiple agents (solo agent only for Spring 2026).
- ❌ No extended needs (Fun, Social, Hygiene) until Core loop is proven.
- ❌ No pathfinding complexity beyond single-room navigation.
- ❌ No art. Greybox only.
- ❌ No "believability" survey this semester (maybe Fall 2026).
- ❌ No feature requests from demos unless they serve the thesis sentence.

---

## 5. Experimental design (the study this project produces)

**Subjects:** Two agent variants in identical environments.

| Variant | Perception | Decision logic | Inertia |
|---|---|---|---|
| **Baseline (Threshold)** | Scanner (shared) | Hard-coded if-then rules on raw need values | None |
| **Utility (Fluid)** | Scanner (shared) | Response curves → utility score → argmax | Commitment bonus on active action |

**Future ablation matrix (Fall 2026 / Spring 2027):** Baseline × Curves-only × Inertia-only × Full-Utility — to attribute gains to specific mechanisms.

**Metrics:**
1. **Stability** — decision changes per simulated minute.
2. **Adaptability** — survival time / completion rate under resource-scarcity perturbations (e.g., Bed removed).
3. **Habits** — time-budget distribution across a 24-hour cycle, verifying curve-bias produces consistent patterns.

**Controls:** Identical environment, identical decay rates, identical perception code, N seeds per condition, confidence intervals reported.

---

## 6. Honest status snapshot (2026-04-18)

**Built:**
- ScriptableObject architecture (`NeedType`, `ResponseCurve`, `SmartObjectData`).
- Metabolism decay loop (`AgentMetabolism`).
- Physics-based movement (`AgentMovement`).
- Tick-based restoration in `AgentController.HandleInteraction()`.
- Greybox room with Fridge + Bed.

**Built but mislabeled:**
- Current `AgentController` is a single hybrid (threshold decision using a curve-evaluated input). Neither a true Baseline nor a true Utility agent.

**Missing:**
- Clean `BaselineAgent` class (pure threshold, no curves).
- Clean `UtilityAgent` class (argmax over candidate actions).
- Action inertia mechanism.
- Live stats UI.
- CSV logging pipeline.
- Ablation test infrastructure.
- Adaptability scenario scripts.

---

## 7. Immediate next steps (this week, in order)

1. **Tonight — Unity split + UI demo.**
   - Extract `BaselineAgent.cs` (pure threshold, no curves).
   - Build `UtilityAgent.cs` (curves + argmax; inertia scaffolded but optional).
   - Add a simple Canvas stats UI showing both agents' needs and current action.
   - Spawn both in the same scene for side-by-side visual comparison.
2. **This week — Commit everything to git** (scripts are not yet committed on this branch).
3. **This week — Revised PPT** using the thesis sentence above, real screenshots, honest status, multi-semester timeline.
4. **This week — Meet with professor.**

---

## 8. Tentative multi-semester timeline

Dates are flexible; deliverables are not.

| Period | Goal | Deliverable |
|---|---|---|
| **Spring 2026 (now → end of May)** | Prototype + capability demo | Split Baseline/Utility agents, visible A/B behavior difference, revised proposal PPT |
| **Summer 2026** | Literature + experimental design | Deep reading, finalize metrics, draft study protocol |
| **Fall 2026** | Data infrastructure + pilot runs | CSV logging pipeline, inertia implementation, first ablation runs |
| **Spring 2027** | Full study + thesis | Multi-seed runs, statistical analysis, write-up, defense |

---

## 9. Minimum reading (before next professor meeting)

1. **Dave Mark** — *"Improving AI Decision Modeling Through Utility Theory"* (GDC 2010 talk, or *Behavioral Mathematics for Game AI* ch. 8–10). → Canonical source for response-curve vocabulary.
2. **Park et al. 2023** — *"Generative Agents: Interactive Simulacra of Human Behavior"* (arXiv:2304.03442). → The "heavy alternative" this thesis deliberately contrasts against.

Third source later if time: Orkin's F.E.A.R. paper (GOAP contrast) OR Millington's *AI for Games* textbook.

---

## 10. Guardrails — things to actively resist

- Scope creep into "making the sim more fun."
- Overclaiming what the code does. If the PPT says "inertia," inertia must exist in the code.
- Premature optimization (CSV pipeline, statistics tooling) before the experimental unit — the two agent variants — cleanly exists.
- Framing the project as a product. Always reframe as an experiment.
- Treating the timeline as a commitment to dates rather than a commitment to milestones.

---

*Last updated: 2026-04-18. Revise this document whenever scope, thesis, or strategy shifts — do not let it go stale.*
