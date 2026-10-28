# Where this project stands, 27 October 2026 (early hours)

Read this first when picking the work back up.

| | |
|---|---|
| The talk | `演讲稿_中文.md` — what to say, beat by beat |
| The project explained | `项目讲解.md` — the whole thing as a story |
| The numbers | `RESULTS.md`, all reproducible from `python analyze_runs.py` |
| The figures | `Figures/`, all rebuilt by `python make_figures.py` |
| Why things were decided | `DevLog_2026_10_26.md` and `DevLog_2026_10_27.md` |

---

## Next deadline

**Wednesday 28 October, 1:00 PM**, Zoom with Prof. Amini and Mirza Kazim Alikhan.
It is a working session to go over the presentation and the results, not a final talk.

He asked for **two PPTX files**:

1. An **almost final 5-minute presentation**
2. A **longer one going over details with results**

Kazim has not followed the project, so the longer deck should not assume background.

---

## What is done

The whole Fall plan from the August deck, in one day:

| August commitment | state |
|---|---|
| Stability metric | done, plus the old contamination traced and shown to be gone |
| Adaptability scenario | done, and the metric exists after all: February defined adaptability as time without reaching a critical failure state under resource scarcity, which is exactly the collapse count plus time below 0.15 after recovery. It was measured and never labelled. |
| Seeded randomization | done, 8 seeds, reproducible |
| Four-condition ablation | done in both scenarios, plus a strength sweep that was not promised |

Beyond the plan: the noise floor was measured, the inertia strength was swept, and the
threshold agent was finally used as a comparison rather than just a control.

104 runs recorded, each with a config manifest. All committed and pushed to `develop`.

---

## The story, shortest version

1. In calm conditions the averages show nothing. Inertia's main effect is +4.3 pp
   against a 4.9 pp noise floor. But 5 of 16 no-inertia runs collapse there and 0 of 16
   inertia runs do, worst case 99% against 41%. **Inertia is a reliability mechanism,
   not a performance one:** it does not move the median, it removes the tail. An
   evaluation reporting only means would conclude these mechanisms are not worth
   implementing, and would be wrong.
2. Remove a resource for a minute and the effect becomes impossible to miss. Without
   inertia the agent collapses in roughly half the runs. With it, never.
3. The damage is in the recovery, not the shortage. Nothing happens while the fridge is
   gone, because there is only one option. It breaks when both needs become urgent at
   once.
4. Inertia has an optimum near 0.2 to 0.3. Too little is indecision, too much is
   neglect, and both failure modes were written down as risks back in March.
5. Against a plain threshold agent: indistinguishable when calm, and the threshold agent
   collapses in about 40 percent of runs once the environment changes.
6. The response curve's effect cannot be resolved: -5.4 pp calm and -3.6 pp under
   outage, against 4.9 pp of noise. **And the design is part of the reason.** The two
   curve conditions were matched at the activation threshold, and the median decision
   happens at need 0.28, where the two mappings differ by 0.01. They were made nearly
   identical where the agent actually operates, and then compared. See `RESULTS.md`
   section 8.

---

## What is not done

| | |
|---|---|
| The 5-minute talk | **scripts done in both languages.** `演讲稿_中文.md` for meaning, `演讲稿_英文.md` to read aloud, slide by slide with what goes on each one. Estimated 6 minutes 20 seconds; not yet timed aloud. |
| The slides | **being built by Wenjie** from the English script. 17 slides. Build order when short of time: 1, 10, 7, 14, 15, 17 first. |
| The figures | **not yet redrawn.** The existing set is too busy: each chart should make one point, everything else greyed. The four the talk uses are `fig_13_problem`, `fig_09_curves`, `fig_03_collapse_dots`, `fig_01_sweep`. `fig_09` also needs its third line dropped: it draws the threshold agent as a desire curve, but `BaselineAgent.Decide()` never evaluates a curve. |
| The detailed deck | not written. Plan: reuse the ten section headings from the August deck (they are a template the professor supplied) and expand "Pilot Testing and Findings" into five or six slides. |
| Unity screenshot | the one asset only Wenjie can make; a top-down shot showing both agents, the fridge and the bed |
| `DecisionLogger.AutoStart` | still on. It records an unlabelled run on every Play, which is where the partial `demo` records come from. Harmless now that incomplete runs are excluded, but it should be off while AblationRunner drives the logger. |
| Charts | **done.** 13 figures in `Figures/`, rebuilt by `python make_figures.py` |
| Literature | **8 sources listed** in `REFERENCES.md`, none read in full |
| Written chapters | none |
| The August adaptability idea | "how long the agent keeps going to a resource that isn't there any more" cannot be measured as built: `ResourceOutage` calls `SetActive(false)` and `FindObjectsByType` skips inactive objects, so the fridge leaves the agent's perception entirely. Measuring it needs the object to stay visible with a dead affordance instead. |
| Agent interference | known 4.9 pp noise; fixed by running one agent per run, not yet done |

---

## What the sample decks actually show

Both samples in the Dropbox folder are by the same student of Amini's, at two stages.

**The 5-minute one is a proposal.** 18 slides, no results at all, ending on "we plan to
work on designing deep neural network architectures". Eight of its eighteen slides are
background. Its speaker notes are plain spoken English, run-on sentences, one typo, and
one idea per slide at roughly 17 seconds each. It quotes essentially no numbers, because
at that stage there were none.

**The 20-minute one is the final.** 32 slides, same first nine slides reused verbatim,
then evaluation metrics across three slides *before* results, then a dense six-row
results table that he reads out number by number, then Conclusion and Future Work.

**So the format does not forbid numbers; his stage did.** Ours has results, so the right
model is the 20-minute skeleton compressed, not the 5-minute one copied.

Two things worth stealing: **metrics explained before results**, and **one idea per
slide, repeating the title across several slides** rather than packing one.

The ten headings in `Wenjie_Jiang_Progress_Update_August2026.pptx` are a supplied
template for the written progress format, not for the talk. His 5-minute deck does not
use them. Use them for the detailed deck, not the 5-minute one.

---

## Open questions for Wednesday

- **The title.** Both halves have results now, one large and one unresolved with a known
  cause, so the title does not need narrowing. Worth confirming he agrees.
- **How long is the 5-minute talk really?** The content runs about 6 minutes with both
  findings, 5 with only the reliability one. Ask what the slot is for and whether 6 is
  acceptable before butchering it.
- **The curve conditions.** Say that they were matched at the activation point and that
  this is probably why the effect cannot be resolved. Ask whether to separate them where
  decisions happen and rerun.
- **Adaptability.** Measured, but under the name "collapse" rather than "adaptability".
  Confirm the mapping is what he expected, and say that the specific metric floated in
  August needs the outage reimplemented to leave the object visible but broken.
- **Scope.** Is one perturbation type and two needs enough, or should a third need be
  added so the curve has something to rank?

---

## Decisions already made, do not relitigate

- The 2x2 lives inside the utility agent. Curve off means a linear mapping, not the
  threshold agent. The threshold agent is an external reference.
- Harmful switching is measured by how far through the action the agent got, not by a
  threshold on the restored need.
- 4.9 pp is the measurement noise, not a significance test. An effect smaller than it is
  not reportable; an effect slightly larger than it is not thereby established either.
  Say "cannot be resolved at this sample size", never "below the noise floor" for the
  curve, whose 5.4 is larger than 4.9.
- The August 24% figure is superseded and should be presented as a correction.
- No claims about how any commercial game is implemented. Our own architecture is
  scanning-based and that is verifiable in the code; everything else is "what public
  descriptions say".
- No comparative put-downs. Threshold rules answer a different question and answer it
  well; our own data has them at 2.1 interrupts/min against 2.3 in calm conditions.
