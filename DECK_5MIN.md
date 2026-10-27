> **已被取代，不要照这份做。**
>
> 讲稿看 `演讲稿_中文.md`（2026-10-27 重写，中文，自带上下文）。
>
> 这份留作记录。它有三处已知问题：把阈值规则说成"从来不比较"（是贬低，而且不准确）、
> 结构是按 slide 预算写的不是按内容、以及若干没有数据支撑的说法。

---

# Five-minute deck: content sheet

Everything needed to build the slides. Figures are in `Figures/`. Every number
traces to `python analyze_runs.py`; every figure to `python make_figures.py`.

**Target: 18 slides, 5 minutes, about 17 seconds a slide.** That is the pace in the
two sample decks from Amini's own students, so it is the pace he expects.

---

## Rules this deck follows

Taken from `Thesis Presentation - 5 min.pptx` in the Dropbox sample folder:

| | |
|---|---|
| Almost no bullet points | Dikshant's 18 slides have nearly none |
| One idea per slide | Never two |
| A visual on nearly every slide | He reuses one image across three slides with added marks |
| Short titles | "Significance", "Data", "Proposal" |
| Citation bottom right, small grey | On every background slide, none on his own results |
| Ends References, then Thank you | Over a photo |

**Only the easy-to-read figures are used here.** The dense ones (`fig_02`, `fig_04`,
`fig_06`, `fig_11`) are held back for the detailed deck, where there is time to explain
them.

**Layouts**: names below match the template already in
`Wenjie_Jiang_Progress_Update_August2026.pptx`. In PowerPoint use
Home > New Slide > (layout name).

---

## Slide 1 — Title

**Layout** TITLE

```
Response Curves and Action Inertia
in Utility-Based NPC Agents

Wenjie Jiang
Advisor: Navid Amini, PhD
October 2026
```

**Say** "This project is about how a game character decides what to do next, and
specifically about how to stop it from changing its mind too often."

---

## Slide 2 — The Problem

**Layout** TITLE_ONLY · title: `The Problem`

**Figure** `fig_13_problem.png` — centred, full width inside a 0.5 inch margin, below
the title. It is a wide short image, so it will sit about mid-slide. Leave the space
under it empty.

**Say** "Each stripe is one thing the agent decided to do. In the first half it eats,
then sleeps, then eats, in reasonable blocks. In the second half it is shredded. Eighty
one percent of its decisions threw away something it had already started. Nothing is
broken here. This is what a reasonable set of rules does on its own."

**No citation.** This is our own data.

---

## Slide 3 — Significance

**Layout** TITLE_AND_BODY · title: `Significance`

**Visual** A free illustration, right half of the slide. Search Vecteezy or unDraw for
"robot assistant" or "smart home". Dikshant used a free Vecteezy vector on his
Significance slide, so this matches the house style.

**Text** left half, one short paragraph, not bullets:

```
The same trade-off appears wherever an autonomous system chooses
among competing demands: autonomous vehicles, home appliances,
and assistive healthcare devices. A fall-prevention wearable that
re-evaluates too eagerly becomes an alarm nobody listens to. One
that commits too hard misses the fall.
```

**Say** "This is not only a game problem. Professor Amini put it in one sentence: how
can an agent avoid unnecessary switching while still reacting quickly when something
important changes? A fall-prevention wearable has exactly this problem. Alert too
readily and it gets ignored. Hold too long and it misses the event."

**Citation** bottom right: `Kinny & Georgeff, 1991`

> This slide is where the project stops looking like a game demo. Do not cut it.

---

## Slide 4 — Two Ways to Decide

**Layout** TITLE_ONLY · title: `Two Ways to Decide`

**Figure** `fig_09_curves.png` — centred, full width inside the margin.

**Say** "The orange line is a threshold rule: do nothing until hunger passes a line,
then act. That is the standard approach and it is what the baseline agent uses. The
blue line is utility scoring: every option gets a score every tick, and the highest one
wins. The green line is utility scoring with the curve switched off, which is the
control. Both utility versions start acting at the same point, so the comparison is
fair."

**Citation** bottom right: `Mark, 2009`

---

## Slide 5 — How a Decision Is Made

**Layout** TITLE_ONLY · title: `How a Decision Is Made`

**Figure** `fig_12_mechanism.png` — centred, full width inside the margin.

**Say** "Two needs come in. Each is pushed through a response curve that turns how empty
it is into how much the agent wants to fix it. That gives one score per action. Then the
action the agent is already doing gets a bonus added, and the highest score wins. Those
two pieces, the curve and the bonus, are what this thesis measures."

**Citation** bottom right: `Mark, 2009`

---

## Slide 6 — The Two Mechanisms

**Layout** MAIN_POINT (title only, large centred text)

Type the equation into a text box, 32pt, centred. In PowerPoint use
Insert > Equation so it renders properly:

```
score(a) = f(need_a) + β · 1[a = current action]

choose argmax score(a),  if score(a) > θ
```

Underneath, 16pt grey, two lines:

```
f      the response curve
β      the commitment bonus, the action inertia
```

**Say** "Here it is as one line. f is the response curve. Beta is the commitment bonus,
what this project calls action inertia: a fixed amount added to whatever the agent is
already doing. Theta is the activation threshold, so the agent can also choose to do
nothing. The whole thesis is about what f and beta are each worth."

> Amini noted the August deck had no equations. This slide answers that.

---

## Slide 7 — The Question

**Layout** MAIN_POINT

```
How much does each mechanism
actually contribute?
```

Smaller underneath, 16pt:

```
Four configurations inside the same agent:
curve on or off  ×  inertia on or off
```

**Say** "So the experiment is a two by two. Turn the curve on and off, turn the bonus on
and off, inside the same agent, same body, same starting conditions. The threshold agent
runs alongside the whole time as a reference."

---

## Slide 8 — Method

**Layout** TITLE_ONLY · title: `Method`

**Figure** A Unity screenshot. **This one is on Wenjie.** A top-down shot showing both
agents, the fridge and the bed, with the UI visible. Place it centred, about 60 percent
of the slide width, left side. On the right, four short lines, 16pt:

```
2D Unity simulation, one room
104 recorded runs
8 seeds per configuration
300 simulated seconds each
```

**Say** "Everything runs unattended in Unity. One room, two needs, two objects. Eight
different starting states per configuration, fixed by seed so every configuration sees
the same eight. A hundred and four runs in total, each one writing its own log and its
own record of the settings that produced it."

---

## Slide 9 — The Stress Test

**Layout** TITLE_ONLY · title: `The Stress Test`

**Visual** Simplest version: a Unity screenshot with the fridge missing, beside the
normal one, with a label. Or skip the picture and use one line of large text:

```
The fridge is removed from
second 100 to second 160.
```

**Say** "Calm conditions turned out to be too easy, so the agent gets a shock. The
fridge disappears for sixty seconds and then comes back. While it is gone hunger keeps
falling and there is nothing to do about it."

---

## Slide 10 — The Averages Say Nothing

**Layout** BIG_NUMBER

Big number: `4.3 pp`

Underneath, 16pt:

```
the difference inertia makes to the average run in calm conditions

the measurement noise between two agents sharing a room is 4.9 pp
```

**Say** "First result, and it is a negative one. In calm conditions, switching inertia
on moves the average by four point three percentage points. Two agents sharing a room
bump into each other, and that alone is worth four point nine. The effect is smaller
than the noise. On this evidence the honest conclusion is that inertia does nothing."

> Do not rush this slide. It sets up the next one.

---

## Slide 11 — The Tail Says Everything

**Layout** TITLE_ONLY · title: `The Tail Says Everything`

**Figure** `fig_03_collapse_dots.png` — centred, full width inside the margin.

**Say** "Then the same runs, one dot per seed, red if that run collapsed. Collapsed
means the agent abandoned more than eighty percent of everything it started. Look at the
calm panel on the left, the one where the averages said nothing. Without inertia, five
of sixteen runs collapsed. With it, none. The worst calm run goes from ninety nine
percent down to forty one. Inertia does not make the typical run better. It removes the
catastrophic one."

> **This is the most important slide in the deck.** It is the finding, and it is the
> one that came from drawing the data instead of averaging it.

---

## Slide 12 — What Changes

**Layout** TITLE_ONLY · title: `What Changes`

**Figure** `fig_10_timeline.png` — centred, full width inside the margin.

**Say** "The same seed, the same starting conditions, run twice. Above, no inertia.
Below, inertia switched on. Same shock at the same moment. The one on top never
recovers."

> Cut this slide first if running long. Slide 11 already makes the point.

---

## Slide 13 — Where the Damage Happens

**Layout** TITLE_ONLY · title: `Where the Damage Happens`

**Figure** `fig_05_phases.png` — centred, full width inside the margin.

**Say** "Splitting those runs into before, during and after the outage gave the result I
did not expect. While the fridge is gone, the interruption rate is zero. In every single
condition. With one option removed there is nothing to switch between, so nothing
happens. All of the damage is after it comes back, when both needs are urgent at the
same time. Taking the resource away is not what breaks the agent. Giving it back is."

---

## Slide 14 — How Much Commitment

**Layout** TITLE_ONLY · title: `How Much Commitment`

**Figure** `fig_01_sweep.png` — centred, full width inside the margin.

**Say** "So inertia helps. The next question is how much of it. Sweeping the bonus from
zero to zero point five gives a U. Too little and the agent cannot settle. Too much and
it gets worse again, which is the part I did not expect. The best value is around zero
point two to zero point three."

> **The climax. Give it the most time of any slide, around 30 seconds.**

---

## Slide 15 — Two Ways to Fail

**Layout** TITLE_ONLY · title: `Two Ways to Fail`

**Figure** `fig_07_completion.png` — centred, full width inside the margin.

**Say** "The two ends of that U fail differently. This is how far through an action the
agent got before abandoning it. At zero it is forty one percent, so it leaves early and
finishes nothing. At zero point five it is eighty six percent, so it holds on almost to
the end. It commits so hard that the other need falls into crisis, and the crisis is
what finally forces the switch. Both of these failure modes were written down as risks
in March, before any of this data existed."

---

## Slide 16 — Summary

**Layout** MAIN_POINT, or a dark background slide

Three short lines, 20pt, left aligned, generous spacing:

```
Action inertia is a reliability mechanism, not a performance one.
It does not improve the average run. It removes the catastrophic one.

There is an optimal amount, near 0.2 to 0.3.
Too little and the agent cannot settle. Too much and it neglects.

The response curve shows no measurable effect with two needs.
A third need is the direct test.
```

**Say** "Three things. Inertia is about reliability, not performance: it does not move
the average, it removes the failures. There is an optimal amount and both sides of it
fail, in different ways. And the response curve, the other half of the title, shows
nothing measurable yet. With only two needs there is rarely a close call to rank, so
adding a third need is the test that would settle it."

> Say the null result out loud. Hiding it would be worse, and the honest version has a
> clear next step attached.

---

## Slide 17 — References

**Layout** TITLE_AND_BODY · title: `References`

Use the list in `REFERENCES.md`, 12pt, hanging indent.

---

## Slide 18 — Thank You

**Layout** TITLE or BLANK

```
Thank you
```

Over a Cal State LA campus photo if one is handy. Dikshant ends exactly this way.

---

## If it runs long

Cut in this order: **12**, then **15**, then **9**. Never cut 11, 13 or 14.

## If it runs short

Add `fig_08_threshold_slope.png` as a slide after 15, titled
`Against Plain Threshold Rules`: "in calm conditions the threshold agent and the tuned
utility agent are indistinguishable, two point one against two point three. Once the
environment changes, the threshold agent collapses in thirteen of thirty two runs and
the tuned one in none."
