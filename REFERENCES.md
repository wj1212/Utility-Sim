# References

Eight sources, which is the right order of magnitude for a five-minute talk. Dikshant's
sample deck lists five, and cites three of them across eight background slides.

The **Checked** column says how far each entry was verified on 26 October 2026.
`search` means the bibliographic details were confirmed against a source online in this
session. `knowledge` means the entry is from standing knowledge and the details should be
confirmed before the written thesis, though the work itself is well known and real.

**Nothing here has been read in full.** For Wednesday that is fine: the list needs to be
correct and each entry needs a one-sentence purpose, which is what is below. Reading
comes before the written chapters, not before a progress meeting.

---

## The list, formatted for the slide

```
Bratman, M. E. (1987). Intention, Plans, and Practical Reason. Harvard University Press.

Colledanchise, M., & Ogren, P. (2018). Behavior Trees in Robotics and AI: An
    Introduction. CRC Press.

Kinny, D., & Georgeff, M. (1991). Commitment and effectiveness of situated agents.
    In Proceedings of the 12th International Joint Conference on Artificial
    Intelligence (IJCAI-91), 82-88.

Maes, P. (1989). How to do the right thing. Connection Science, 1(3), 291-323.

Mark, D. (2009). Behavioral Mathematics for Game AI. Course Technology.

Mark, D., & Dill, K. (2010). Improving AI Decision Modeling Through Utility Theory.
    Game Developers Conference.

Orkin, J. (2006). Three States and a Plan: The AI of F.E.A.R. Game Developers
    Conference.

Tyrrell, T. (1993). Computational Mechanisms for Action Selection. PhD thesis,
    University of Edinburgh.
```

---

## What each one is for

| # | Source | Checked | Why it is cited |
|---|---|---|---|
| 1 | Bratman 1987 | knowledge | The philosophical case that an agent which reconsiders every option at every moment is not behaving rationally. The argument for why action inertia should exist at all. |
| 2 | Colledanchise & Ogren 2018 | knowledge | Behavior trees, the architecture most game and robotics work actually uses. Names the alternative this project is not using. |
| 3 | **Kinny & Georgeff 1991** | **search** | **The closest prior result.** Compared "bold" agents that never reconsider against "cautious" ones that reconsider constantly, varying how fast the environment changes. See the note below. |
| 4 | Maes 1989 | knowledge | Spreading-activation action selection, an early formal treatment of choosing among competing drives. |
| 5 | Mark 2009 | search | Where response curves come from. The direct source for the mechanism in the title. |
| 6 | Mark & Dill 2010 | search | The GDC talk that put utility scoring alongside state machines and planners as a mainstream architecture. |
| 7 | Orkin 2006 | search | GOAP in F.E.A.R.: three states plus an A* planner. The planning alternative to scoring. |
| 8 | Tyrrell 1993 | search | A systematic comparison of action-selection mechanisms in a simulated creature with many competing needs. The methodological ancestor of this setup. |

---

## The one that matters: Kinny & Georgeff 1991

**Verified:** the paper is real, IJCAI-91, pages 82 to 88. Secondary sources describe the
finding as: in more static domains, bold agents that never reconsider their intentions
outperform cautious agents that reconsider before every step, and the reverse holds in
highly dynamic domains.

**Not verified:** the original text, and the exact experimental setup. The description
above is secondhand.

### Why it is worth raising on Wednesday

Our result looks like it points the other way. The outage scenario is the dynamic one,
and there the committed agent wins outright while the constantly-reconsidering one
collapses in nearly half of runs.

A possible reason for the difference, which is a hypothesis and not a finding:

> Their environment changes in a way that **invalidates the goal**, so not reconsidering
> means pursuing something that no longer exists. Our environment changes in a way that
> makes **several valid goals urgent at once**, and switching between them costs travel
> time and lost progress.
>
> Theirs asks whether the goal still holds. Ours asks whether the agent can afford to
> switch between goals that all still hold.

If that distinction survives reading the paper, it is a genuine contribution statement
and it is more interesting than the result on its own.

### How to say it on Wednesday

> "I found a 1991 paper that ran a version of this experiment, and the direction looks
> opposite to ours. I think the difference is in what kind of change the environment
> makes, but I have not read the original yet, so I would rather check before claiming
> it."

**Do not say the result contradicts theirs.** The setups differ and the reading has not
been done. Claiming it and being wrong in front of Kazim would cost more than the point
is worth.

---

## How citations go on the slides

Dikshant's pattern, which is the house style here:

- Background and motivation slides carry a citation, bottom right, small and grey:
  `(Mark, 2009)`
- Slides showing our own data carry nothing
- One source can appear on several consecutive slides. He puts `(Shungu, 2016)` on five.

In the five-minute deck that means citations on slides 3, 4 and 5 only. Everything from
slide 8 on is our own data.
