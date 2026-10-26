# Meeting Script — Friday Aug 7, 11:00 AM

**Read this off the second monitor. No camera on this machine, so he can't see you reading.**

**Tone:** warm, polite, calm. Short sentences. Small pauses. Don't perform.

**I / our rule:**
- **"I"** = something you personally did → *I recorded ten runs, I calibrated it*
- **"our"** = the project and its parts → *our simulation, our agents, our metric, our plan*

---

## Words you'll say a lot

| Word | Say it like |
|---|---|
| inertia | in-**UR**-sha |
| ablation | uh-**BLAY**-shun |
| arbitration | ar-bi-**TRAY**-shun |
| calibrate | **CAL**-i-brate |
| threshold | **THRESH**-hold |

---

# ① OPENING

**[smile — he can't see you, but it comes through in your voice]**

> Good morning, Professor Amini! Thanks for meeting with me today

**[small pause]**

> I'm on my desktop today, and it doesn't have a camera — so it'll just be audio on my end.
> But this is the machine our simulation runs on, so I can run the demo for you later if you'd like.

**[pause]**

> So, if that's okay — I'll go through the slides quickly first, just to remind us where things are.
> And then I'll talk about the update.

**[move on — no need to wait]**

---

# ② QUICK PASS — slides 2 to 7  (about 2 minutes, keep it light)

### Slide 2

> So this is the overall picture.

> Our project is a small 2D simulation in Unity — one room, two agents.

> The two agents are identical. Same body, same needs, same speed, same room.
> The only thing that's different is how they decide what to do next.

> One of them uses simple rules. If hunger drops below a certain number, go and eat.

> The other one gives every option a score, and picks whichever scores highest.

> And we're measuring two things.
> Stability — meaning the agent doesn't keep changing its mind.
> And adaptability — meaning it can adjust when we take something away.

### Slide 3

> On the technical side, there are a few pieces.

> The brain is a swappable component, so I can plug either one into the same body.
> That's what makes the comparison fair.

> Needs, curves, objects — those are all data files, so I can change them without touching any code.

> The agents also look around the room themselves whenever they decide,
> instead of the objects telling them what's there.

> And this last line is the new part. I added a logging layer
> so every decision the agents make now goes into a file, along with all the settings for that run.

### Slide 4

> These were the two things I was worried about early on.

> One was tuning the inertia — too strong and the agent ignores an emergency,
> too weak and it just keeps flip-flopping.

> The other was whether our metrics actually measure what we want them to.

**[slower — plant this]**

> Both of these showed up in the data. I'll come back to them in a few minutes.

### Slide 5

**[respectful — you're describing other people's work]**

> For existing work in emergent NPC decision making — from what I've looked at so far,
> there seem to be two directions.

> The first is classical utility AI. That's where both of our ideas come from.

> The main reference book has a full chapter on response curves,
> and a section on what it calls decision momentum — that's the same idea as our action inertia.

> But it presents them as design tools. There's no comparison that measures what each one adds.
> That's the gap we're trying to work in.

**[pause]**

> The other direction is LLM-based agents, and that work looks genuinely impressive.

> It's a different kind of approach  — the behaviour comes out of the model as a whole,
> so there aren't separate pieces to turn on and off.

> And our whole question is about turning pieces on and off. So we stay on the classical side.

### Slide 6

**[use planning language — none of this is done yet]**

> And this is the approach we'd like to take.

> On the left are the two mechanisms as the book describes them.
> And on the right is what we'd compare to try to separate them —
> each one on its own, and then both together.

> That should let us see which one is doing the work.

### Slide 7

> And these are the improvements we're hoping for.

**[pause]**

> Maybe we can find out how much each mechanism contributes to stability and adaptability.

> Maybe we can see what happens when they're used together.

> And maybe it gives designers something useful for tuning.

**[pause — changing gears]**

---

# ③ THE UPDATE — Slide 8  ⭐ main part, about 3 minutes

> So this is our update.

**[pause — let him look]**

> I got the logging working, and I've now recorded ten runs —
> eight of them repeats of the same setup.

---

### Part 1 — two problems in our setup

> And the first thing those runs showed me was two problems with my own setup.

**[calm]**

> The first one — our two agents weren't starting from the same point.

> The baseline agent waited until a need got quite low before it acted.
> The utility agent was setting off much earlier, while its needs were still high.

**[slow down]**

> So I wasn't really comparing the decision logic.
> I was comparing which agent like got hungry first.

**[pause]**

> I went back and used the response curve to work out where the utility agent should start,
> and now both of them act at the same level.

**[pause]**

> The second one was a hard lock in the shared body — neither agent could interrupt
> an action for the first one and a half seconds.

**[slow down]**

> That was doing part of the inertia's job — keeping the agent on task — so I took it out.

---

### Part 2 — the result

> After fixing those two, I think the comparison is much cleaner.

**[point at the table]**

> Both agents made about the same number of decisions, so the workload is the same.

**[pause]**

> The difference is in interruptions.
> On average the baseline interrupted itself about twelve and a half times. The utility agent, about nine and a half.

**[slow — key number]**

> So roughly twenty-four percent fewer.

> And across all eight runs, the direction never reversed.

**[pause]**

> That's what action inertia is supposed to do, so I found that encouraging.

---

### Part 3 — what it doesn't show  ⚠️ slow down here

**[softer]**

> But I'd like to be careful about what this doesn't show.

> First — in this comparison, the curve and the inertia were both turned on together.
> So I can't tell how much of the twenty-four percent comes from which one.

**[pause]**

> Second — this one I didn't expect.
> In all ten runs, the two needs were never critical at the same time.

> So the agent never had to choose between two urgent things,
> and that's the main job of the response curve.

**[pause]**

> Third, our metric isn't clean yet — this is the one I flagged earlier.
> Some of what I counted as an interruption was the agent leaving an action that had already done its job —
> its energy was full again.

> That's correct behaviour, but the counter treats it the same as changing its mind too often.

**[pause]**

> And the variation between runs comes from small timing differences, not from proper randomization.
> So I'd say the direction looks solid. I wouldn't say it's statistically significant.

**[pause — this line links to the next slide]**

> And those limits are basically what the Fall plan is about.

---

# ④ THE PLAN — Slide 9  (about 2 minutes)

> On the timeline — in Spring I built the simulation and the two agents.
> Over the summer I added the logging, and ran the first set of tests.

**[pause]**

> For Fall I have four things I want to do, and each one has to come before the next.

**[one at a time]**

> First, I want to fix the metric.
> Right now I count every time an agent switches away from an action,
> but some of those switches are actually correct. I need a way to count only the bad ones.

> Second, I want to take a resource away partway through a run.
> At the moment the agents never have two urgent needs at once,
> so the curve never has to rank anything. Removing the fridge is what would create that.

> Third, I want to start each run from a different random state, with a recorded seed.
> Right now every run starts the same way, so my eight repeats aren't really independent samples.

> And fourth, I want to run the two versions I haven't run yet —
> the curve without the inertia, and the inertia without the curve.
> That's what would let me say how much each one contributes.


---

# ⑤ IF HE ASKS "DO YOU HAVE ANY QUESTIONS?"

**Have one ready so you're not blank. Just one. Then stop.**

> Just one — for a thesis at this level, would the four conditions be enough,
> or would you expect more than one scenario?

**[listen, thank him, move to the closing]**

---

# ⑥ CLOSING

> That's everything from my side.

**[if he hasn't seen the demo yet — offer it here]**

> Would you like to see it running before we finish? It only takes a minute.

**[after the demo, or if he says no]**

> I'll send you this version of the slides after we finish.

> Thanks again — this was really helpful.

---
---

# 🎬 DEMO

## ⚠️ SET UP BEFORE THE MEETING

1. Open Unity, load the scene, **don't press Play yet**
2. Select **DecisionLogger** → **Time Scale = 1**
3. **Condition Label = `demo`**
4. **Run Duration = 0** (so it won't stop on its own)
5. **Make the Console visible** — Window → General → Console, docked so you can see it
   next to the Game view. The interrupt lines print there live.
6. Leave Unity open behind PowerPoint on the **main** monitor

## Offering it

> Would you like to see it running? It only takes a minute.

**[share screen → Unity → Play]**

### ⭐ Say this first — it tells him what to look for

> Everything on that results slide came out of watching this.
> Let me show you what it's actually counting.

### As it starts

> The red circle is the baseline agent, and the yellow one is the utility agent.
> The green box is the fridge, and the blue one is the bed.

### Point at the panels

> Each panel is one agent. These bars are hunger and energy, and they drop over time.

> And for the utility agent, this lower part shows the score for each action.
> That's the number it compares when it decides.

### ⭐ THE KEY MOMENT — when they both set off

**This is the one thing worth waiting for. It's visual proof of the fix from slide 8.**

> And here — watch when they leave.

**[pause and let him see it]**

> They start moving at about the same time now. That's the calibration I mentioned earlier.
> Before I fixed it, the yellow one would set off noticeably earlier.

### ⭐ If one walks away mid-action — then point at the Console

> There — it started sleeping, and then hunger got urgent enough to pull it away.

**[point at the Console line that just appeared]**

> And you can see it logged right there. That's one interruption.

> That's exactly what the number on the results slide is counting.

### Before you stop

> Every one of those lines goes into a CSV file, along with all the settings for the run.
> So the results I showed you are just counted from this.

**[stop Play → back to PowerPoint]**

---

## If nothing interesting happens in that minute

> Sometimes a minute goes by without much happening, which is part of the point.
> One run doesn't tell you much either way — that's why I count across eight.

## ⚠️ If the demo contradicts the story
*(e.g. the utility agent interrupts and the baseline doesn't)*

> That's exactly why I count over eight runs instead of watching one.
> A single minute can go either way.

**Say it calmly and move on. It actually strengthens the point about repeats.**

## If something breaks

> Let me stop it there — I'll show you the recorded data instead.

**[back to slide 8, keep going. Do not debug live.]**

---
---

# 🛡️ IF HE ASKS

### "You said both of those early risks showed up — where?"
> The metric one is on this slide — some interruptions turned out to be correct behaviour.
> The inertia one showed up before I fixed the setup.
> Back then the utility agent was interrupted every single time it went to sleep —
> nine times out of nine. The bonus just wasn't strong enough to hold it.

### "How do you know the logging is correct?"
> The log reads the same variable the panel displays.
> So what you see on screen during the demo is exactly what goes into the file.

### "Why does the baseline agent not have inertia?"
> Inertia is a bonus added to a score, and the baseline agent doesn't score anything —
> it just checks thresholds. So there's nowhere to add it.
> The baseline is meant to be the version with neither mechanism.

### "How different were the two starting points?"
> On a scale where one is full and zero is empty, the baseline acted at about zero point two nine.
> The utility agent was acting at around zero point four six.
> After calibrating, they're both at about zero point two nine.

### "How many runs?"
> Ten. Two of them show the before and after of the calibration,
> and the other eight are repeats of the corrected setup.

### "Is twenty-four percent significant?"
> I wouldn't call it significant. The ranges overlap —
> the baseline was between eleven and fifteen, and the utility agent between eight and eleven.
> What I can say is the direction held in all eight.

### "Why isn't that proper randomization?"
> Because every run starts from the same state.
> What varies is just small timing differences between runs.
> To make them real samples I'd need to randomize the starting conditions with a seed.

### "What did you do in June and July?"
> Honestly, the first part of the summer was slow.
> The logging and this data set came together more recently.

### "What's a response curve?"
> It maps a need level to a desire score.
> So instead of a yes-or-no threshold, the agent gets a continuous number it can compare.

### "What's action inertia?"
> It's a bonus added to whatever the agent is already doing,
> so it's a little reluctant to switch. In our setup the bonus is zero point two.

### "How does the agent know what's in the room?"
> It looks around itself each time it decides, and scores whatever it finds.

### "Tell me about the Park paper."
> I have the general picture — twenty-five agents in a sandbox,
> with a memory and planning architecture.
> I'm still working through the details, so I'd rather not overstate what I know.

### "Why is your metric not clean?"
> In one run the utility agent left the bed when its energy was already full.
> That's the right thing to do, but my counter recorded it the same way
> as an agent changing its mind too often.

### "What do you mean, no arbitration?"
> The two needs were never both critical at the same moment,
> so there was always only one obvious thing to do.

### "Have you run the four conditions?"
> Not yet. So far it's baseline against the full utility agent.
> The two middle conditions — curves only, and inertia only — are still to do.

### "Are you sure the book doesn't measure this?"
**You now actually know this — I checked the PDF.**
> Chapter twelve is response curves, and chapter fifteen has a section on decision momentum.
> Both are presented as design tools, with worked examples.
> The one section called "testing the algorithm" just checks that the scores come out sensible —
> it isn't a comparison between versions. And there's no evaluation chapter in the book.

### ⭐ "How is this different from what Dave Mark's book already says?"
**This is the question that tests whether you understand your own contribution.**
> The book defines both mechanisms and explains how to use them.
> What it doesn't do is measure how much each one contributes on its own.
> So our contribution isn't the idea — it's the measurement.
> We're trying to turn a design recommendation into a number.

### ⭐ "What about behaviour trees?"
> Behaviour trees are probably the most common approach in industry,
> but they work differently — a person writes out each branch by hand.
> Our slide scopes this to agents that decide without a scripted response for every situation,
> so trees sit outside that. It's a scoping choice, not a claim that they're worse.

### ⭐ "What about GOAP?"
**This one is more likely than behaviour trees, because GOAP does fit our definition.**
> GOAP is really answering a different question. It plans a sequence of actions
> to reach a goal that's already been chosen.
> Our question is the step before that — which need should the agent serve right now.
> Even in a GOAP system, that goal selection usually still comes down to some kind of score.
> So they sit at different levels rather than competing.

### "How will you measure adaptability?"
> That one is still open, honestly. Right now it's described in words but not as a number.
> I'm thinking about something like how long the agent keeps going to a resource
> that isn't there any more. But I'd like to work it out properly before I commit.

### "Why these two mechanisms and not others?"
> They're the two the book puts at the centre of utility-based decisions,
> and they seem to appear in every implementation.
> So if I can only measure a couple of things properly, those felt like the right ones.

### "Is one room enough?"
> For measuring these two mechanisms, I think so.
> The room is deliberately simple so the only thing changing is the decision logic.
> Adding rooms would bring in pathfinding, which would be another variable.

### "Why zero point two for the bonus?"
> It was a starting value, honestly. I haven't swept that range yet.
> Trying several values is something I should do as part of the ablation.

### "What if the results show no difference?"
> Then that's a result as well. It would mean these mechanisms matter less
> than the design literature suggests, at least in this kind of setup.
> The measurement method would still stand, and that's the part I'd want to be reusable.

### "Can someone else reproduce this?"
> Yes — each run writes its own settings file alongside the data,
> so any result can be traced back to the exact configuration that produced it.

### "When will it be finished?"
> The plan is experiments and data in Fall, and writing in Spring.
> But I'd like to confirm those milestones with you.

### If you don't know
> I'm not sure yet — let me look into it and get back to you.

**That's a perfectly good answer. Please don't guess.**

---

# ⚠️ DON'T SAY

- ❌ "Utility AI is more stable" → ✅ "the direction was consistent"
- ❌ "The inertia caused the twenty-four percent" → ✅ "the curves and inertia changed together"
- ❌ "significant" → ✅ "the direction looks solid"
- ❌ Anything suggesting you've read Park et al. closely
- ❌ Anything that sounds like criticism of other people's work
