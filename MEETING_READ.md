# READ THIS — Friday 11:00 AM

*Read straight down. Bold = pause or slow down. Nothing to look up.*

---

**[smile — it comes through in your voice]**

Good morning, Professor Amini! Thanks so much for making time this morning.

**— pause —**

I'm on my desktop today, and it doesn't have a camera, so it'll just be audio on my end.
But this is the machine our simulation runs on, so I can run the demo for you later if you'd like.

**— pause —**

So, if that's okay — I'll go through the slides quickly first, just to remind us where things are.
And then I'll talk about the update.

---

## SLIDE 2

So this is the overall picture.

Our project is a small 2D simulation in Unity — one room, two agents.

The two agents are identical. Same body, same needs, same speed, same room.
The only thing that's different is how they decide what to do next.

One of them uses simple rules. If hunger drops below a certain number, go and eat.

The other one gives every option a score, and picks whichever scores highest.

And we're measuring two things.
Stability — meaning the agent doesn't keep changing its mind.
And adaptability — meaning it can adjust when we take something away.

---

## SLIDE 3

On the technical side, there are a few pieces.

The brain is a swappable component, so I can plug either one into the same body.
That's what makes the comparison fair.

Needs, curves, objects — those are all data files, so I can change them without touching any code.

The agents also look around the room themselves whenever they decide,
instead of the objects telling them what's there.

And this last line is the new part. I added a logging layer this summer.
Every decision the agents make now goes into a file, along with all the settings for that run.

---

## SLIDE 4

These were the two things I was worried about early on.

One was tuning the inertia — too strong and the agent ignores an emergency,
too weak and it just keeps flip-flopping.

The other was whether our metrics actually measure what we want them to.

**— slow down —**

Both of these came up in the data. I'll come back to them in a few minutes.

---

## SLIDE 5

For existing work in emergent NPC decision making — from what I've looked at so far,
there seem to be two directions.

The first is classical utility AI. That's where both of our ideas come from.

The main reference book has a full chapter on response curves,
and a section on what it calls decision momentum — that's the same idea as our action inertia.

But it presents them as design tools. There's no comparison that measures what each one adds.
That's the gap we're trying to work in.

**— pause —**

The other direction is LLM-based agents, and that work looks genuinely impressive.

It's a different kind of approach though — the behaviour comes out of the model as a whole,
so there aren't separate pieces to turn on and off.

And our whole question is about turning pieces on and off. So we stay on the classical side.

---

## SLIDE 6

And this is the approach we'd like to take.

On the left are the two mechanisms as the book describes them.
And on the right is what we'd compare to try to separate them —
each one on its own, and then both together.

That should let us see which one is doing the work.

---

## SLIDE 7

And these are the improvements we're hoping for.

**— pause —**

Maybe we can find out how much each mechanism contributes to stability and adaptability.

Maybe we can see what happens when they're used together.

And maybe it gives designers something useful for tuning.

---
---

## SLIDE 8 — the main part

So that's the plan. And this is the update.

**— pause, let him look —**

I got the logging working, and I've now recorded ten runs —
eight of them repeats of the same setup.

### The two problems

And the first thing those runs showed me was two problems with my own setup.

**— calm —**

The first one — our two agents weren't starting from the same point.

The baseline agent waited until a need got quite low before it acted.
The utility agent was setting off much earlier, while its needs were still fairly high.

**— slow down —**

So I wasn't really comparing the decision logic.
I was comparing which agent got hungry first.

**— pause —**

I went back and used the response curve to work out where the utility agent should start,
and now both of them act at the same level.

**— pause —**

The second one was a hard lock I'd added earlier — for the first second and a half of an action,
neither agent could interrupt itself.

**— slow down —**

I put it in to stop them twitching in the demo.
But it was doing part of the inertia's job — keeping the agent on task —
and the baseline was getting that for free, even though it has no inertia.

So I took it out of both.

### The result

After fixing those two, I think the comparison is much cleaner.

**— point at the table —**

Both agents made about the same number of decisions, so the workload is the same.

**— pause —**

The difference is in interruptions.
On average the baseline interrupted itself about twelve and a half times. The utility agent, about nine and a half.

**— slow, this is the key number —**

So roughly twenty-four percent fewer.

And across all eight runs, the direction never reversed.

**— pause —**

That's what action inertia is supposed to do, so I found that encouraging.

### What it doesn't show

**— softer, take your time —**

But I'd like to be careful about what this doesn't show.

First — in this comparison, the curve and the inertia were both turned on together.
So I can't tell how much of the twenty-four percent comes from which one.

**— pause —**

Second — this one I didn't expect.
In all ten runs, the two needs were never critical at the same time.

So the agent never had to choose between two urgent things,
and that's the main job of the response curve.

**— pause —**

Third, our metric isn't clean yet — this is the one I flagged earlier.
Some of what I counted as an interruption was the agent leaving an action that had already done its job —
its energy was full again.

That's correct behaviour, but the counter treats it the same as changing its mind too often.

**— pause —**

And the variation between runs comes from small timing differences, not from proper randomization.
So I'd say the direction looks solid. I wouldn't say it's statistically significant.

**— pause —**

And those limits are basically what the Fall plan is about.

---
---

## SLIDE 9

On the timeline — in Spring I built the simulation and the two agents.
Over the summer I added the logging, and ran the first set of tests.

**— pause —**

For Fall I have four things I want to do, and each one has to come before the next.

**— one at a time —**

First, I want to fix the metric.
Right now I count every time an agent switches away from an action,
but some of those switches are actually correct. I need a way to count only the bad ones.

Second, I want to take a resource away partway through a run.
At the moment the agents never have two urgent needs at once,
so the curve never has to rank anything. Removing the fridge is what would create that.

Third, I want to start each run from a different random state, with a recorded seed.
Right now every run starts the same way, so my eight repeats aren't really independent samples.

And fourth, I want to run the two versions I haven't run yet —
the curve without the inertia, and the inertia without the curve.
That's what would let me say how much each one contributes.

---
---

## CLOSING

That's everything from my side.

**— offer the demo here if he hasn't asked —**

Would you like to see it running before we finish? It only takes a minute.

**— after the demo, or if he says no —**

I'll send you this version of the slides after we finish.

Thanks again — this was really helpful.

---
---

# 🎬 DEMO — only if he says yes

Everything on that results slide came out of watching this.
Let me show you what it's actually counting.

**[press Play]**

The red circle is the baseline agent, and the yellow one is the utility agent.
The green box is the fridge, and the blue one is the bed.

Each panel is one agent. These bars are hunger and energy, and they drop over time.

And for the utility agent, this lower part shows the score for each action.
That's the number it compares when it decides.

**— wait for them to set off —**

And here — watch when they leave.

**— pause and let him see it —**

They start moving at about the same time now. That's the calibration I mentioned earlier.
Before I fixed it, the yellow one would set off noticeably earlier.

**— wait for an interruption —**

There — it started sleeping, and then hunger got urgent enough to pull it away.

**[point at the Console line]**

And you can see it logged right there. That's one interruption.
That's exactly what the number on the results slide is counting.

**— before you stop —**

Every one of those lines goes into a CSV file, along with all the settings for the run.
So the results I showed you are just counted from this.

**[stop Play → back to PowerPoint]**

---

## If nothing much happens

Sometimes a minute goes by without much happening, which is part of the point.
One run doesn't tell you much either way — that's why I count across eight.

## If it contradicts the story

That's exactly why I count over eight runs instead of watching one.
A single minute can go either way.

## If it breaks

Let me stop it there — I'll show you the recorded data instead.

**[back to slide 8. Do not debug live.]**

---
---

# ⚠️ NEVER SAY

- ❌ "Utility AI is more stable" → ✅ "the direction was consistent"
- ❌ "The inertia caused the twenty-four percent" → ✅ "the curve and the inertia were both turned on together"
- ❌ "significant" → ✅ "the direction looks solid"
- ❌ Anything suggesting you've read the LLM paper closely
- ❌ Anything that sounds like criticism of other people's work

**If you don't know:** *"I'm not sure yet — let me look into it and get back to you."*

---

**Answers to likely questions are in MEETING_SCRIPT.md — keep it open in another tab.**
