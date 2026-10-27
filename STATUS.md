# Where this project stands, 26 October 2026 (late evening)

Read this first when picking the work back up. Findings are in `RESULTS.md`, the
reasoning behind them in `DevLog_2026_10_26.md`, and every figure re-derives from
`python analyze_runs.py`.

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
| Adaptability scenario | scenario built and run; an adaptability **metric** was never formally defined |
| Seeded randomization | done, 8 seeds, reproducible |
| Four-condition ablation | done in both scenarios, plus a strength sweep that was not promised |

Beyond the plan: the noise floor was measured, the inertia strength was swept, and the
threshold agent was finally used as a comparison rather than just a control.

104 runs recorded, each with a config manifest. All committed and pushed to `develop`.

---

## The story, shortest version

1. In calm conditions none of this is measurable. Effects sit below the 4.9 pp noise
   floor, so a benchmark run in a benign scenario would say these mechanisms are not
   worth implementing.
2. Remove a resource for a minute and the picture inverts. Without inertia the agent
   collapses in roughly half the runs. With it, never.
3. The damage is in the recovery, not the shortage. Nothing happens while the fridge is
   gone, because there is only one option. It breaks when both needs become urgent at
   once.
4. Inertia has an optimum near 0.2 to 0.3. Too little is indecision, too much is
   neglect, and both failure modes were written down as risks back in March.
5. Against a plain threshold agent: indistinguishable when calm, and the threshold agent
   collapses in about 40 percent of runs once the environment changes.

The response curve shows no measurable effect in any scenario tested. Hypothesis, not
tested: two needs is too few for ranking to matter.

---

## What is not done

| | |
|---|---|
| Both decks | not started |
| Charts | none exist yet; the U-shaped sweep curve is the one the talk needs |
| Literature | still two sources; a thesis needs far more |
| Written chapters | none |
| Adaptability metric | only an implicit proxy (time below 0.15 after recovery) |
| Agent interference | known 4.9 pp noise; fixed by running one agent per run, not yet done |

---

## Format the 5-minute deck has to follow

Taken from two of Amini's own students' recordings in the Dropbox sample folder:

- Cal State LA template, same one already in use
- 10 to 16 slides for 5 minutes, roughly 20 to 30 seconds each
- **Almost no bullet points.** One of the two decks had none at all
- Nearly every slide is an image, diagram or chart
- Short noun-phrase titles: "Significance", "Data", "Summary"
- Source citations bottom right, same style already in use
- Ends with References, then "Thank you" over a campus photo

This is a different genre from the current deck, which is tables and label-colon-text.
The 5-minute deck should be rebuilt, not trimmed down.

---

## Open questions for Wednesday

- **The title.** "Response Curves and Action Inertia" promises two results and only one
  arrived. Ask whether to narrow it or report the null. Do not change it unilaterally.
- **Adaptability.** The scenario exists but the metric was never defined. Ask what he
  expects it to measure.
- **Scope.** Is one perturbation type and two needs enough, or should a third need be
  added so the curve has something to rank?

---

## Decisions already made, do not relitigate

- The 2x2 lives inside the utility agent. Curve off means a linear mapping, not the
  threshold agent. The threshold agent is an external reference.
- Harmful switching is measured by how far through the action the agent got, not by a
  threshold on the restored need.
- Effects below 4.9 pp are not reported as findings.
- The August 24% figure is superseded and should be presented as a correction.
