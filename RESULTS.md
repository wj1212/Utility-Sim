# Results as of 26 October 2026

Every number here comes from `python analyze_runs.py`. Nothing is quoted from memory.
If a figure in the slides cannot be found in that output, it should not be in the slides.

```bash
python analyze_runs.py
```

---

## The question

How much do **response curves** and **action inertia** each contribute to behavioural
stability in a utility-driven NPC agent?

---

## What was run

| | |
|---|---|
| Agents in the scene | 2 at a time: one threshold agent, one utility agent |
| Conditions | 2x2 inside the utility agent: curve on/off by inertia on/off |
| Scenarios | normal, and one with the fridge removed from 100s to 160s |
| Seeds | 8 per condition, fixing the starting need values, shared by both agents |
| Sweep | commitment bonus at 0, 0.1, 0.2, 0.3, 0.5 under outage |
| Total | 104 recorded runs, each with its own config manifest |

"Curve off" does not mean the threshold agent. It means the utility agent falls back to
a linear need-to-desire mapping, so the two mechanisms are the only things switched.
The threshold agent runs alongside in every condition as an external reference.

---

## Headline

> The two mechanisms look close to irrelevant when conditions are easy, and decisive
> when the system is put under stress. Action inertia has an optimum: too little and the
> agent thrashes, too much and it neglects whatever it is not currently doing.

---

## 1. Under easy conditions the average shows nothing, and the tail shows everything

| condition | median interrupt rate | interrupts/min |
|---|---|---|
| linear, no inertia | 25.5% | 2.4 |
| linear, inertia | 33.4% | 3.1 |
| curve, no inertia | 23.6% | 2.2 |
| curve, inertia | 24.4% | 2.3 |

Main effects: inertia **+4.3 pp**, curve **-5.4 pp**.

The measured noise floor is 4.9 pp (section 4). Inertia's effect sits inside it. The
curve's is 5.4, which is marginally larger, so "both are inside the noise" (as an earlier
draft of this section said) is arithmetically wrong.

**The defensible statement is that neither effect can be resolved at this sample size.**
The curve's effect runs in the same direction in both scenarios, -5.4 pp calm and -3.6 pp
under outage, so it may well be real and small; with 8 seeds and 4.9 pp of agent
interference it cannot be separated from noise. More seeds, or one agent per run, would
settle it.

That was where this section stopped until the runs were plotted one seed at a time
rather than summarised. The medians hold up, and they hide the result:

| calm scenario | median | worst run | collapses |
|---|---|---|---|
| without inertia | 24.4% | **99%** | **5 / 16** |
| with inertia | 28.0% | 41% | **0 / 16** |

The typical run is the same either way, and inertia makes the median slightly *worse*.
But without it, roughly one calm run in three ends in total thrashing, and with it, none
do. The worst case falls from 99% to 41%.

**So inertia is a reliability mechanism, not a performance mechanism.** That is why the
median never moves and the collapse count always does, here and under stress. An
evaluation that reports only means or medians would conclude these mechanisms are not
worth implementing, and would be wrong for the reason that matters in a shipped game:
the failure is rare, not small.

---

## 2. Under stress, inertia is decisive

Fridge removed from 100s to 160s.

| condition | median interrupt rate | interrupts/min | collapses |
|---|---|---|---|
| linear, no inertia | 81.2% | 14.2 | 5 / 8 |
| linear, inertia | 31.8% | 2.7 | 0 / 8 |
| curve, no inertia | 79.7% | 14.1 | 2 / 8 |
| curve, inertia | 26.2% | 2.3 | 0 / 8 |

Main effects: inertia **-51.4 pp**, curve **-3.6 pp**.

**Collapses: 7 of 16 without inertia, 0 of 16 with.**

A collapse is an interrupt rate at or above 80 percent: the agent abandons nearly
everything it starts and both needs fall to zero together. It is a different kind of
failure from a worse average, which is why it is counted separately.

The curve's effect stays near the noise floor in both scenarios. **This study does not
show a measurable contribution from the response curve.**

---

## 3. Inertia has an optimum, and both predicted failure modes are real

| bonus | median rate | interrupts/min | completion at abandon | collapses |
|---|---|---|---|---|
| 0.00 | 82.3% | 14.5 | 0.41 | 5 / 8 |
| 0.10 | 51.0% | 5.4 | 0.56 | 0 / 8 |
| 0.20 | 27.2% | 2.4 | 0.71 | 0 / 8 |
| **0.30** | **23.5%** | **2.0** | 0.74 | 0 / 8 |
| 0.50 | 37.8% | 3.1 | 0.86 | 0 / 8 |

**Lowest interruption frequency at 0.30, rising again by 0.50.**

The rise is not a ratio artefact: decisions per minute are flat from 0.2 onward
(8.9, 8.7, 8.5), and interrupts per minute rise 2.0 to 3.1. Paired by seed, 0.50 is
worse than 0.30 in **7 of 8 seeds**, mean difference **+12.5 pp**, well clear of the
noise floor.

The two ends fail differently:

- **Too little (0.00):** indecision. Completion at abandon is 0.41, so actions are
  dropped early, and conflicts run at 60 per run because both needs crash together.
- **Too much (0.50):** neglect. Completion is 0.86, so the agent leaves late, and time
  spent below 0.15 after the resource returns is **15x** that at 0.30 (1.5% vs 0.1%).
  It commits so hard that the other need is driven into crisis, and then the crisis is
  what forces the switch.

Both of these were written down as risks in the March deck, before any of this data
existed: *too strong and the agent sleeps through survival emergencies, too weak and it
jitters between actions every cycle.*

---

## 4. Noise floor: 4.9 pp

The threshold agent is configured identically in all four ablation conditions and starts
from the same seeded values, so any variation in its numbers is the other agent
physically deflecting it.

Median within-seed spread across the four conditions: **4.9 percentage points**.

Everything smaller than that is not reported as an effect. This is why section 1 says
"not measurable" rather than quoting +4.3 and -5.4 as findings.

**Known fix, not yet applied:** run one agent at a time. Seeded starting values already
guarantee the pairing, so separate runs lose nothing and remove the interference.

---

## 5. Arbitration finally happens

Decisions taken while both needs were critical:

| scenario | runs with any conflict |
|---|---|
| normal | 7 / 32 |
| outage | 32 / 32 |

The 7 in the normal scenario are almost entirely inside collapsed runs, where both needs
hit zero because the agent was thrashing. That is a failure, not arbitration.

Under outage every run produces genuine conflicts, which means the part of the utility
agent that ranks competing options is finally being exercised. This was listed as an
open limitation in the March deck.

---

## What changed since March

**The 24% figure reported in March does not survive proper randomisation.**

Those eight repeats all started from identical values, so the spread between them was
frame-timing jitter rather than a sample. With eight genuinely different starting states
the difference in the normal scenario disappears.

That is not a loss. The replacement claim is stronger and holds across starting
conditions: inertia prevents collapse, and there is an optimal amount of it.

**The metric contamination flagged in March turned out to be confined to the old
configuration.** When actions fully restored a need, the agent would correctly leave a
finished action and the counter logged it as an interruption: in one run 9 of 9
interruptions were of that kind. After partial restoration was introduced, 0 of 178
interruptions were, so the reported numbers are not affected by it.

---

## Limits

| | |
|---|---|
| One scenario | A single perturbation type, one room, two needs, two objects |
| Curve result is null | No measurable contribution, which may be the scenario's fault rather than the curve's |
| 8 seeds | Enough to see a pattern, not enough for a statistical test |
| Agent interference | 4.9 pp of noise that a one-agent-per-run design would remove |
| One inertia value per scenario | The sweep only ran under outage |

---

## Reproducing any figure

```bash
python analyze_runs.py
```

Sections map to this document: NOISE FLOOR to section 4, ABLATION 2x2 to sections 1 and
2, INERTIA SWEEP to section 3, and the conflicts column throughout to section 5.

Each run also writes `config_<label>_<runid>.csv` next to its data, listing every
parameter in force, so any single run can be traced back to the configuration that
produced it.


---

## 6. The headline that matters to a practitioner

The threshold agent ran alongside the utility agent in all 104 runs, which makes it
possible to answer the question a developer would actually ask: is utility scoring worth
the extra complexity over simple threshold rules?

"Tuned utility agent" here means the full configuration, curve on and inertia on, which
is 8 runs per scenario. The threshold agent ran in all four ablation cells, so it has 32.

| scenario | threshold agent | tuned utility agent |
|---|---|---|
| normal | 2.1 interrupts/min, 4 of 32 collapsed | 2.3 interrupts/min, 0 of 8 collapsed |
| outage | 13.2 interrupts/min, 13 of 32 collapsed | 2.3 interrupts/min, 0 of 8 collapsed |

(An earlier draft of this table quoted the 2.3 from this cell but a collapse count from
both inertia cells pooled. Pooling both gives 2.7 and 2.5 interrupts/min and 0 of 16
collapsed in each scenario, which is the stronger statement but a different denominator.
One definition per row.)

> In calm conditions the two are indistinguishable. Once the environment changes, the
> threshold agent collapses in roughly 40 percent of runs and the tuned utility agent
> never does.

This reframes the contribution. The study is not only "how much does each mechanism add"
but "when does utility AI earn its complexity", and the answer has a condition attached:
it depends on whether the environment is going to change.

## 7. The damage is in the recovery, not the shortage

Interruptions by phase of the outage runs, utility agent, pooled across 8 runs each:

| condition | before (0-100s) | during (100-160s) | after (160s+) |
|---|---|---|---|
| linear, no inertia | 59% | **0%** | 93% |
| curve, no inertia | 58% | **0%** | 92% |
| linear, inertia | 30% | **0%** | 38% |
| curve, inertia | 20% | **0%** | 34% |

Nothing happens while the fridge is gone, in any condition. With one resource removed
there is only one option left, so there is nothing to switch between.

Everything happens when it comes back. Hunger is at zero, energy is wherever it happens
to be, and for the first time both needs demand attention at once. Without inertia the
agent oscillates between them and never recovers. With inertia it commits to one, fixes
it, then handles the other.

> Taking the resource away is not what breaks the agent. Giving it back is.

## 8. Unresolved: why the curve shows nothing

Working hypothesis, not tested. With only two needs there is rarely a subtle ranking to
make: whichever need is lower is the more urgent one, and a straight line orders two
values the same way a curve does. The curve's shape should only matter when several
options are close together, which needs more than two needs to arise.

A third need would be the direct test, and it would serve the half of the title that
currently has no result.
