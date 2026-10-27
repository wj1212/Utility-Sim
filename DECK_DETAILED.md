> **方向已变，内容待重写。**
>
> 新计划：**沿用八月那份 pptx 的十个章节标题**（那是教授给的模板），把
> "Pilot Testing and Findings" 扩成五六页，而不是这份文件里的 33 页自定义结构。
> 依据：Dikshant 的五分钟 deck 不用那套标题，二十分钟那份用的是完整骨架。
>
> 另外这份里写着 adaptability "metric not defined"，**那是错的** —— 二月的定义就是
> 崩溃计数加恢复期时间，一直测着，只是没贴标签。见 `DevLog_2026_10_27.md`。

---

# Detailed deck: content sheet

The second file Amini asked for: "a longer one going over details with results."

**Audience note.** Mirza Kazim Alikhan has not followed this project. Slides 2 to 4
assume nothing. Do not compress them.

**Structure note.** The 20-minute sample deck in the Dropbox folder is 32 slides, and it
gets there by advancing one step per slide rather than by packing slides. Three slides
titled `Evaluation Metrics`, three titled `Results`. Same approach here: **33 slides, one
idea each.** A dense slide is harder to present than two sparse ones.

**Base file.** Build on `Wenjie_Jiang_Progress_Update_August2026.pptx`. Its skeleton was
already approved in August, so keep the layouts and replace the content.

Notation used below is the same as `DECK_5MIN.md`: layout name, figure file, text,
then what to say.

---

# Part A — What this is  (slides 1 to 4)

## 1. Title
**TITLE.** Same as the five-minute deck, with "Progress Update, October 2026" instead of
the date line.

## 2. The Project
**TITLE_AND_BODY** · `The Project`

```
A 2D Unity simulation of a single room.

An agent has two needs that fall over time, hunger and energy,
and two objects that restore them, a fridge and a bed.

Two different decision-making brains are plugged into the same body
and compared on how stable their behaviour is.
```

**Say** "The setup is deliberately small. One room, two needs, two objects. Everything
interesting is in how the agent picks between them."

## 3. The Problem
**TITLE_ONLY** · `The Problem` · figure `fig_13_problem.png`

**Say** "Each stripe is one decision. The second half is the agent changing its mind
constantly, abandoning eighty one percent of what it starts. Nothing is broken. This is
what reasonable rules do on their own."

## 4. The Question
**TITLE_AND_BODY** · `The Question`

Two framings side by side, left and right:

```
From the thesis title          From Professor Amini, August 2026

How much do response curves    How can an agent avoid unnecessary
and action inertia each        switching while still reacting
contribute to behavioural      quickly when something important
stability?                     changes?
```

**Say** "The title asks how much each mechanism contributes. The question Professor
Amini sent in August asks the same thing in domain-general terms, and the second framing
turned out to be the one the data answers most directly."

---

# Part B — The model  (slides 5 to 10)

> Amini noted the August deck had no equations. This part is the answer to that.

## 5. Same Body, Two Brains
**TITLE_AND_BODY** · `Same Body, Two Brains`

```
Both agents share identical movement, metabolism and actions.
The only difference is the component that chooses what to do next.

Baseline    a threshold rule
Utility     a scoring system
```

## 6. The Threshold Agent
**TITLE_AND_BODY** · `The Baseline: Threshold Rules`

```
if hunger < 0.30 → eat
else if energy < 0.30 → sleep
else → idle

A fixed priority order. No scoring, no comparison.
```

**Say** "This is the baseline, and it is what most simple game AI actually does. Needs
are checked in a fixed order against a fixed line. Nothing is weighed against anything
else."

## 7. The Utility Agent
**TITLE_AND_BODY** · `The Utility Agent: Scoring`

```
Every action is scored every decision tick.
The highest score wins, provided it clears an activation threshold.

Scores come from a response curve over the need,
plus a bonus for whatever the agent is already doing.
```

## 8. The Equation
**MAIN_POINT.** Insert > Equation, 32pt centred.

```
score(a) = f(need_a) + β · 1[a = current action]

a* = argmax score(a)     subject to    score(a*) > θ
```

Underneath, 16pt grey:

```
f    response curve, a need-to-desire mapping
β    commitment bonus: action inertia
θ    activation threshold, so doing nothing stays an option
```

**Say** "The whole thesis is in this line. f is one mechanism, beta is the other."

## 9. Response Curves
**TITLE_ONLY** · `Response Curves` · figure `fig_09_curves.png`

**Say** "Three mappings from need to desire. Orange is the threshold agent: a cliff at
zero point three. Green is the utility agent with the curve switched off, a straight
line, and that is the control condition. Blue is the tuned five-point curve. The
important detail is that blue and green cross the activation threshold at the same need
value, so switching the curve off does not change when the agent starts acting. Only how
it ranks options."

**Citation** `(Mark, 2009)`

## 10. Action Inertia
**TITLE_ONLY** · `Action Inertia` · figure `fig_12_mechanism.png`

**Say** "Beta is a flat bonus added to whatever the agent is currently doing. It makes
the current action slightly harder to displace. In the agent-theory literature this is
commitment to an intention, and the argument for why it should exist goes back to
Bratman."

**Citation** `(Bratman, 1987)`

---

# Part C — The experiment  (slides 11 to 14)

## 11. The Design
**TITLE_AND_BODY** · `A 2x2, Inside One Agent`

A 2x2 table:

```
                 inertia off      inertia on
curve off        linear,          linear,
                 no inertia       inertia
curve on         curve,           curve,
                 no inertia       inertia
```

## 12. Why the Baseline Is Not a Cell
**TITLE_AND_BODY** · `A Correction to the August Design`

```
August described the ablation as "baseline vs curves-only"
and "baseline vs inertia-only".

That cannot work. The threshold agent does not score anything,
and inertia is a bonus added to a score, so there is nowhere
to put it.

All four cells live inside the utility agent.
The threshold agent runs alongside as an external reference.
```

**Say** "This is a change from what I presented in August, and it is worth being
explicit about. Turning the curve off means clearing the curve list, which falls back to
a straight line. That needs no new code, only different inspector values."

> Raising this yourself is better than having it found. It also shows the design was
> thought through rather than inherited.

## 13. Method
**TITLE_AND_BODY** · `Method`

```
8 seeds per configuration, fixing the starting need values
The same 8 starting states are seen by every configuration
300 simulated seconds per run, at 10x speed
104 runs recorded in total

Each run writes its own decision log and its own config manifest,
so any single run traces back to the settings that produced it.

Every figure in this deck:    python make_figures.py
Every number in this deck:    python analyze_runs.py
```

**Say** "Both of those commands run from the repository and regenerate everything here.
If a number is in this deck and not in that output, it should not be in this deck."

## 14. The Stress Scenario
**TITLE_AND_BODY** · `The Outage Scenario`

```
The fridge is disabled from second 100 to second 160, then returns.

Permanent removal was tried first and discarded: with one option
gone there is nothing left to arbitrate between.

Removing it temporarily lets hunger fall far below threshold while
it is unavailable, so both needs are urgent when it comes back.
```

---

# Part D — Corrections  (slides 15 to 17)

> Put these before the results, not after. Volunteering them is cheap now and expensive
> later.

## 15. The August Figure Does Not Survive
**TITLE_AND_BODY** · `Correction: the 24% Figure`

```
August reported a 24% reduction in interruptions.

Those eight repeats all started from identical values, so the
spread between them was frame-timing jitter, not a sample.

With eight genuinely different starting states, the difference
in the calm scenario disappears.
```

**Say** "I would rather report this than leave it standing. The replacement claim is
stronger anyway, because it holds across starting conditions."

## 16. The Contamination Was Confined
**TITLE_AND_BODY** · `Correction: the Metric Contamination`

```
March flagged a risk: when an action fully restores a need, the
agent correctly leaves a finished action and the counter logs it
as an interruption.

Checked directly. Under the old full-restoration configuration,
9 of 9 interruptions in one run were of that kind.
After partial restoration was introduced, 0 of 178 were.

The reported numbers are not affected.
```

## 17. The Noise Floor
**TITLE_ONLY** · `How Much of This Is Noise?` · figure `fig_04_ablation_strip.png`

**This is the densest figure in the deck. Walk through it slowly.**

**Say** "Each small dot is one seed. The thick bar is the median. Left panel is calm,
right panel is the outage, and the pink band on the right of each is the collapse
threshold. Now, the noise measurement. The threshold agent is configured identically in
all four conditions and starts from the same seeded values, so any variation in its
numbers is purely the other agent physically bumping into it. That median spread is four
point nine percentage points, drawn to scale at the bottom left. Anything smaller than
that bracket is not an effect."

**Then** "That matters immediately, because in the calm panel every condition sits
within about that much of every other."

---

# Part E — Results  (slides 18 to 27)

## 18. Calm Conditions: the Averages
**TITLE_AND_BODY** · `Calm Conditions: the Averages`

```
condition             median rate    interrupts/min
linear, no inertia       25.5%            2.4
linear, inertia          33.4%            3.1
curve, no inertia        23.6%            2.2
curve, inertia           24.4%            2.3

Main effects:   inertia +4.3 pp     curve -5.4 pp
Noise floor:    4.9 pp
```

**Say** "Both main effects are inside the noise. On this evidence neither mechanism does
anything. This is where the analysis stopped until the runs were plotted one at a time."

## 19. Calm Conditions: the Tail
**TITLE_ONLY** · `Calm Conditions: the Tail` · figure `fig_03_collapse_dots.png`

```
                     median    worst run    collapsed
without inertia       24.4%        99%        5 / 16
with inertia          28.0%        41%        0 / 16
```

**Say** "Same runs, one dot per seed, red if that run collapsed, meaning it abandoned
over eighty percent of everything it started. In the calm scenario, where the averages
said nothing, five of sixteen runs without inertia collapsed and none with it did. The
worst case falls from ninety nine percent to forty one. Inertia does not improve the
typical run. It removes the catastrophic one."

> **The key slide of the deck.** Inertia is a reliability mechanism, not a performance
> mechanism, and that single sentence explains every other result here.

## 20. Under Stress
**TITLE_AND_BODY** · `Under Stress`

```
condition             median rate    interrupts/min    collapsed
linear, no inertia       81.2%           14.2            5 / 8
linear, inertia          31.8%            2.7            0 / 8
curve, no inertia        79.7%           14.1            2 / 8
curve, inertia           26.2%            2.3            0 / 8

Main effects:   inertia -51.4 pp     curve -3.6 pp
```

**Say** "Under the outage the inertia effect is fifty one points, more than ten times the
noise floor. Collapses go from seven of sixteen to zero of sixteen. The curve effect is
still inside the noise."

## 21. Where the Damage Happens
**TITLE_ONLY** · `Where the Damage Happens` · figure `fig_06_phases_all4.png`

**Say** "All four conditions, split by phase. While the fridge is gone, every condition
is at zero. With one option removed there is nothing to switch between. The damage is
entirely in the recovery, when both needs are urgent at once. Taking the resource away
is not what breaks the agent. Giving it back is."

> A detail worth having ready if asked: the first interruption after the outage happens
> at exactly second 160.000, the instant the fridge returns, and it is a switch from
> sleeping to eating.

## 22. The Same Seed, Twice
**TITLE_ONLY** · `The Same Seed, Twice` · figure `fig_10_timeline.png`

**Say** "Identical starting conditions, identical shock. Above without inertia, below
with it. The one above never recovers."

## 23. What the Needs Do
**TITLE_ONLY** · `What the Needs Do` · figure `fig_11_traces.png`

**Say** "The same two runs as needs over time. Hunger hits zero during the outage in
both, which is expected since the fridge is gone. The difference is after. Above, both
needs sit pinned near zero while the agent thrashes between them. Below, the sawtooth
comes straight back."

## 24. How Much Commitment
**TITLE_ONLY** · `How Much Commitment` · figure `fig_01_sweep.png`

```
bonus    median rate    intr/min    completion    collapsed
0.00        82.3%        14.5         0.41         5 / 8
0.10        51.0%         5.4         0.56         0 / 8
0.20        27.2%         2.4         0.71         0 / 8
0.30        23.5%         2.0         0.74         0 / 8
0.50        37.8%         3.1         0.86         0 / 8
```

**Say** "Five values of beta, eight seeds each, under the outage. The best is around zero
point two to zero point three, and it gets worse again by zero point five."

## 25. Is the Rise Real?
**TITLE_ONLY** · `Is the Rise Real?` · figure `fig_02_sweep_two_panel.png`

```
Decisions per minute are flat from 0.2 onward:  8.9, 8.7, 8.5
Paired by seed, 0.50 is worse than 0.30 in 7 of 8 seeds
Mean paired difference: +12.5 pp
```

**Say** "A fair objection is that interrupt rate is a ratio, so the rise could be the
denominator moving. It is not. Decisions per minute are flat, the per-minute count rises
on its own, and paired seed by seed, zero point five is worse in seven of eight."

> Expect this question from Kazim. Having the slide ready is better than answering it
> from memory.

## 26. Two Ways to Fail
**TITLE_ONLY** · `Two Ways to Fail` · figure `fig_07_completion.png`

```
Too little (0.00)   completion at abandon 0.41, leaves early, nothing finishes
                    60 conflicts per run, both needs crash together

Too much (0.50)     completion at abandon 0.86, leaves late
                    time below 0.15 after recovery is 15x that at 0.30
```

**Say** "Both ends fail, differently. At zero the agent leaves too early. At zero point
five it holds on so hard the other need goes into crisis, and the crisis is what forces
the switch. Late crisis-driven switching rather than early indecisive switching. Both of
these were written down as risks in the March deck, before any of this data existed."

## 27. Against Plain Threshold Rules
**TITLE_ONLY** · `Does Utility Scoring Earn Its Complexity?` · figure
`fig_08_threshold_slope.png`

```
scenario    threshold agent                 tuned utility agent
calm        2.1 /min,  4 of 32 collapsed    2.3 /min,  0 of 8 collapsed
outage     13.2 /min, 13 of 32 collapsed    2.3 /min,  0 of 8 collapsed
```

**Say** "The threshold agent ran alongside in all hundred and four runs, which makes this
answerable. In calm conditions the two are indistinguishable. Once the environment
changes, the threshold agent collapses in about forty percent of runs and the tuned
utility agent in none. So utility scoring earns its complexity, with a condition
attached: it depends on whether the environment is going to change."

---

# Part F — Where it stands  (slides 28 to 31)

## 28. Promised and Delivered
**TITLE_AND_BODY** · `The Fall Plan`

```
Promised in August                        Status

Stability metric                          done
Adaptability scenario                     scenario done, metric not defined
Seeded randomization                      done, 8 seeds
Four-condition ablation                   done in both scenarios

Not promised, also done

Noise floor measured                      4.9 pp
Inertia strength sweep                    5 values x 8 seeds
Threshold agent used as a comparison      not just as a control
```

## 29. Limits
**TITLE_AND_BODY** · `Limits`

```
One perturbation type, one room, two needs, two objects
The curve result is null, which may be the scenario's fault
8 seeds: enough to see a pattern, not enough for a significance test
4.9 pp of agent interference a one-agent-per-run design would remove
The sweep only ran under the outage scenario
No written chapters yet
```

**Say** "The one I would fix first is the interference, and it costs nothing. The seeding
already guarantees the pairing, so running one agent per run loses no information."

## 30. Open Questions
**TITLE_AND_BODY** · `Questions for You`

```
1  The title promises two results and one arrived. Narrow the title,
   or report the null and keep it?

2  Adaptability has a scenario but no defined metric. Proposal: time
   spent below 0.15 after the resource returns. Does that measure
   what you meant?

3  Two needs may be too few for curve shape to matter. Is adding a
   third need worth the time, or is the scope already right?

4  Kinny and Georgeff 1991 ran a version of this and the direction
   looks opposite. I have not read the original yet.
```

**Say** "Four things I would rather decide with you than on my own."

> **End the content here.** Wednesday is a working session, not a defence. Handing back
> four specific decisions is a better close than a summary.

## 31. Next
**TITLE_AND_BODY** · `Next`

```
One agent per run, removing the 4.9 pp interference
Read Kinny and Georgeff, and the rest of the reference list
Begin written chapters
Whatever comes out of the four questions above
```

## 32. References
**TITLE_AND_BODY.** The list in `REFERENCES.md`.

## 33. Thank You
**TITLE** or **BLANK**.

---

## Figure usage, at a glance

| Figure | 5-min | Detailed |
|---|---|---|
| `fig_01_sweep` | 14 | 24 |
| `fig_02_sweep_two_panel` | — | 25 |
| `fig_03_collapse_dots` | 11 | 19 |
| `fig_04_ablation_strip` | — | 17 |
| `fig_05_phases` | 13 | — |
| `fig_06_phases_all4` | — | 21 |
| `fig_07_completion` | 15 | 26 |
| `fig_08_threshold_slope` | spare | 27 |
| `fig_09_curves` | 4 | 9 |
| `fig_10_timeline` | 12 | 22 |
| `fig_11_traces` | — | 23 |
| `fig_12_mechanism` | 5 | 10 |
| `fig_13_problem` | 2 | 3 |
| Unity screenshot | 8, 9 | 13, 14 |

The only asset not yet made is the Unity screenshot.
