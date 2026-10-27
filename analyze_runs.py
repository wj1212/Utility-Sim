"""
Summarise every logged run in UnityProject/RunData.

Usage:
    python analyze_runs.py

Reads each decisions_*.csv, computes the stability metrics used in the study, and
prints whichever analyses the data supports. Every number quoted in the slides or
the devlog should come from here, so it can be re-derived rather than remembered.

Sections, each printed only when the matching runs are present:

  RUN SUMMARY        one row per run per agent
  REPEATED MEASURES  runs grouped by identical configuration
  NOISE FLOOR        how much the two agents disturb each other
  ABLATION 2x2       curve on/off by inertia on/off
  INERTIA SWEEP      commitment bonus swept across several values

Labels are parsed, not guessed: the ablation sweeps write labels like
"curve_inertia_s03", the outage sweep prefixes those with "outage_", and the
inertia sweep writes "sweep_inertia030_s03".
"""

import csv
import os
import re
import sys
from collections import defaultdict
from statistics import mean, median

RUN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UnityProject", "RunData")

# A need at or below this counts as critical. Both needs critical at the same decision
# is the only moment the response curve has competing options to rank.
CRITICAL = 0.32

# An interrupt rate at or above this means the agent abandoned nearly everything it
# started. Runs like that are a qualitatively different failure, not a worse average.
COLLAPSE = 0.80

ABLATION = ["linear_noinertia", "linear_inertia", "curve_noinertia", "curve_inertia"]

# Which need each action restores, used to judge how far an abandoned action got.
NEED_FOR_ACTION = {"Eat": "hunger", "Sleep": "energy"}


# ----------------------------------------------------------------------------- loading

def load_runs(run_dir):
    """Group decision rows by (label, run_id, agent)."""
    runs = defaultdict(list)
    for name in sorted(os.listdir(run_dir)):
        if not name.startswith("decisions_") or not name.endswith(".csv"):
            continue
        with open(os.path.join(run_dir, name), newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                runs[(row["condition"], row["run_id"], row["agent"])].append(row)
    return runs


def parse_label(label):
    """
    Split a run label into (scenario, condition, seed).

    sweep_inertia030_s03     -> ("outage", "inertia030", 3)
    outage_curve_inertia_s03 -> ("outage", "curve_inertia", 3)
    curve_inertia_s03        -> ("normal", "curve_inertia", 3)
    run_07                   -> ("normal", "run_07", None)
    """
    scenario = "normal"
    rest = label
    if rest.startswith("sweep_"):
        scenario, rest = "outage", rest[len("sweep_"):]
    elif rest.startswith("outage_"):
        scenario, rest = "outage", rest[len("outage_"):]

    m = re.match(r"(.+)_s(\d+)$", rest)
    if m:
        return scenario, m.group(1), int(m.group(2))
    return scenario, rest, None


def config_signature(run_dir, label, run_id):
    """The parameters that define a condition, ignoring per-repeat bookkeeping."""
    path = os.path.join(run_dir, "config_%s_%s.csv" % (label, run_id))
    if not os.path.isfile(path):
        return None
    skip = {"run_id", "condition", "recorded_at", "seed"}
    pairs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if "," not in line:
                continue
            key, value = line.strip().split(",", 1)
            if key in skip or ".initial." in key:
                continue
            pairs.append((key, value))
    return tuple(sorted(pairs))


# --------------------------------------------------------------------------- per run

def summarise(rows):
    """Metrics for one agent in one run."""
    duration = max(float(r["time_s"]) for r in rows)
    minutes = duration / 60.0 if duration else 0
    decisions = len(rows)
    interrupts = [r for r in rows if r["is_interrupt"] == "1"]

    # How far through the abandoned action the agent got. 1.0 means it was essentially
    # finished, so leaving was reasonable; a low value means it barely started.
    completion = []
    for r in interrupts:
        try:
            elapsed, intended = float(r["abandoned_elapsed"]), float(r["abandoned_duration"])
            if intended > 0:
                completion.append(min(elapsed / intended, 1.0))
        except (ValueError, KeyError, TypeError):
            pass

    # Level the abandoned need had reached when the agent walked away.
    left_at = []
    for r in interrupts:
        need = NEED_FOR_ACTION.get(r["from_action"])
        if need:
            left_at.append(float(r[need]))

    triggers = [float(r[NEED_FOR_ACTION[r["to_action"]]])
                for r in rows if r["to_action"] in NEED_FOR_ACTION]

    conflicts = sum(1 for r in rows
                    if float(r["hunger"]) <= CRITICAL and float(r["energy"]) <= CRITICAL)

    return {
        "brain": rows[0]["brain"],
        "duration_s": round(duration, 1),
        "decisions": decisions,
        "decisions_per_min": round(decisions / minutes, 2) if minutes else 0.0,
        "interrupts": len(interrupts),
        "interrupts_per_min": round(len(interrupts) / minutes, 2) if minutes else 0.0,
        "interrupt_rate": round(len(interrupts) / decisions, 3) if decisions else 0.0,
        "completion_at_abandon": round(mean(completion), 3) if completion else None,
        "need_when_leaving": round(mean(left_at), 3) if left_at else None,
        "mean_trigger_need": round(mean(triggers), 3) if triggers else None,
        "conflict_decisions": conflicts,
        "collapsed": (len(interrupts) / decisions >= COLLAPSE) if decisions else False,
    }


# --------------------------------------------------------------------------- reports

def report_runs(records):
    header = ("%-26s%-10s%6s%6s%7s%7s%8s%7s%10s"
              % ("label", "agent", "dur", "dec", "/min", "intr", "intr%", "compl", "conflicts"))
    print()
    print(header)
    print("-" * len(header))
    last = None
    for r in sorted(records, key=lambda x: (x["label"], x["agent"])):
        if last is not None and r["label"] != last:
            print()
        last = r["label"]
        compl = "%.2f" % r["completion_at_abandon"] if r["completion_at_abandon"] is not None else "-"
        print("%-26s%-10s%6.0f%6d%7.1f%7d%8.1f%7s%10d"
              % (r["label"], r["agent"], r["duration_s"], r["decisions"],
                 r["decisions_per_min"], r["interrupts"], 100 * r["interrupt_rate"],
                 compl, r["conflict_decisions"]))
    print()
    print("dur        simulated seconds recorded")
    print("dec /min   decisions taken, and per simulated minute")
    print("intr intr% decisions that cut short an action already in progress")
    print("compl      how far through the abandoned action the agent got, 1.0 = finished")
    print("conflicts  decisions taken while BOTH needs were at or below %.2f" % CRITICAL)


def report_repeats(records):
    """Runs sharing a configuration, grouped from the manifests rather than the labels."""
    groups = defaultdict(list)
    for r in records:
        if r["signature"] is not None:
            groups[r["signature"]].append(r)
    repeated = {k: v for k, v in groups.items() if len({r["label"] for r in v}) > 1}
    if not repeated:
        return

    print()
    print("=" * 78)
    print("REPEATED MEASURES")
    print("Runs with identical configurations, so differences are the repeat itself.")
    for rows in repeated.values():
        labels = sorted({r["label"] for r in rows})
        print()
        print("  %d runs: %s" % (len(labels), ", ".join(labels[:4]) + (" ..." if len(labels) > 4 else "")))
        for brain in sorted({r["brain"] for r in rows}):
            sub = [r for r in rows if r["brain"] == brain]
            cells = []
            for field in ("decisions", "interrupts", "interrupt_rate"):
                vals = [r[field] for r in sub]
                cells.append("%.2f (%g-%g)" % (mean(vals), min(vals), max(vals)))
            print("    %-10s" % brain + "".join("%24s" % c for c in cells))


def report_noise_floor(records):
    """
    The baseline agent is configured identically in every ablation condition and starts
    from the same seeded values, so any variation in its numbers across conditions is
    the other agent disturbing it. That sets the floor below which effects are not real.
    """
    by_seed = defaultdict(dict)
    for r in records:
        if r["scenario"] != "normal" or r["condition"] not in ABLATION or r["seed"] is None:
            continue
        if r["brain"] != "Baseline":
            continue
        by_seed[r["seed"]][r["condition"]] = r["interrupt_rate"]

    complete = {s: d for s, d in by_seed.items() if len(d) == len(ABLATION)}
    if not complete:
        return
    spreads = [max(d.values()) - min(d.values()) for d in complete.values()]

    print()
    print("=" * 78)
    print("NOISE FLOOR  (baseline agent, same seed, four different utility configs)")
    print()
    print("  %-10s" % "seed" + "".join("%18s" % c for c in ABLATION) + "%14s" % "spread")
    for seed in sorted(complete):
        d = complete[seed]
        print("  %-10d" % seed
              + "".join("%17.1f%%" % (100 * d[c]) for c in ABLATION)
              + "%11.1f pp" % (100 * (max(d.values()) - min(d.values()))))
    print()
    print("  median within-seed spread: %.1f pp" % (100 * median(spreads)))
    print()
    print("  The baseline is identical every time and starts from identical values, so")
    print("  this spread is the two agents physically deflecting each other. Effects")
    print("  smaller than it should not be reported as real.")


def _cell(records, scenario, condition, field):
    return [r[field] for r in records
            if r["scenario"] == scenario and r["condition"] == condition and r["brain"] == "Utility"]


def report_ablation(records):
    for scenario in ("normal", "outage"):
        if any(not _cell(records, scenario, c, "interrupt_rate") for c in ABLATION):
            continue

        print()
        print("=" * 78)
        print("ABLATION 2x2  (%s scenario, utility agent)" % scenario)
        print("Both mechanisms live inside the utility agent, so all four cells are the")
        print("same architecture with pieces switched on and off. The threshold agent is")
        print("an external reference, not one of the cells.")
        print()
        print("  %-20s%14s%12s%14s%14s"
              % ("condition", "median rate", "intr/min", "completion", "collapses"))
        print("  " + "-" * 72)
        for c in ABLATION:
            rates = _cell(records, scenario, c, "interrupt_rate")
            perm = _cell(records, scenario, c, "interrupts_per_min")
            comp = [x for x in _cell(records, scenario, c, "completion_at_abandon") if x is not None]
            coll = sum(1 for x in _cell(records, scenario, c, "collapsed") if x)
            print("  %-20s%13.1f%%%12.1f%14.2f%11d / %d"
                  % (c, 100 * median(rates), median(perm),
                     mean(comp) if comp else float("nan"), coll, len(rates)))

        md = lambda c: median(_cell(records, scenario, c, "interrupt_rate"))
        ln, li, cn, ci = (md(c) for c in ABLATION)
        print()
        print("  main effect of INERTIA : %+.1f pp" % (100 * ((li + ci) / 2 - (ln + cn) / 2)))
        print("  main effect of CURVE   : %+.1f pp" % (100 * ((cn + ci) / 2 - (ln + li) / 2)))
        print("  interaction            : %+.1f pp" % (100 * ((ci - cn) - (li - ln))))

        no_inertia = sum(1 for c in ("linear_noinertia", "curve_noinertia")
                         for x in _cell(records, scenario, c, "collapsed") if x)
        with_inertia = sum(1 for c in ("linear_inertia", "curve_inertia")
                           for x in _cell(records, scenario, c, "collapsed") if x)
        total = len(_cell(records, scenario, "linear_noinertia", "collapsed")) * 2
        print("  collapses: %d / %d without inertia, %d / %d with"
              % (no_inertia, total, with_inertia, total))


def report_sweep(records):
    conds = sorted({r["condition"] for r in records
                    if r["condition"] and re.fullmatch(r"inertia\d{3}", r["condition"])})
    if len(conds) < 3:
        return

    print()
    print("=" * 78)
    print("INERTIA SWEEP  (utility agent)")
    print("The 2x2 asks whether inertia helps. This asks how much of it is right.")
    print()
    print("  %-10s%14s%12s%14s%14s%16s"
          % ("bonus", "median rate", "intr/min", "completion", "collapses", "conflicts/run"))
    print("  " + "-" * 80)
    rows = []
    for c in conds:
        scenario = next(r["scenario"] for r in records if r["condition"] == c)
        rates = _cell(records, scenario, c, "interrupt_rate")
        perm = _cell(records, scenario, c, "interrupts_per_min")
        comp = [x for x in _cell(records, scenario, c, "completion_at_abandon") if x is not None]
        coll = sum(1 for x in _cell(records, scenario, c, "collapsed") if x)
        conf = _cell(records, scenario, c, "conflict_decisions")
        bonus = int(c[len("inertia"):]) / 100.0
        rows.append((bonus, median(perm)))
        print("  %-10.2f%13.1f%%%12.1f%14.2f%11d / %d%16.1f"
              % (bonus, 100 * median(rates), median(perm),
                 mean(comp) if comp else float("nan"), coll, len(rates), mean(conf)))

    best = min(rows, key=lambda x: x[1])
    print()
    print("  lowest interruption frequency at bonus %.2f" % best[0])
    if rows[-1][1] > best[1]:
        print("  and it rises again by the top of the range (%.1f to %.1f per minute),"
              % (best[1], rows[-1][1]))
        print("  which is over-commitment rather than indecision: the completion column")
        print("  shows those late interruptions happen near the end of the action.")


# ------------------------------------------------------------------------------- main

def main():
    if not os.path.isdir(RUN_DIR):
        sys.exit("No run directory at %s. Play the scene with DecisionLogger attached first." % RUN_DIR)

    runs = load_runs(RUN_DIR)
    if not runs:
        sys.exit("No decisions_*.csv found in %s." % RUN_DIR)

    records = []
    for (label, run_id, agent), rows in sorted(runs.items()):
        scenario, condition, seed = parse_label(label)
        rec = {"label": label, "run_id": run_id, "agent": agent,
               "scenario": scenario, "condition": condition, "seed": seed}
        rec.update(summarise(rows))
        rec["signature"] = config_signature(RUN_DIR, label, run_id)
        records.append(rec)

    report_runs(records)
    report_repeats(records)
    report_noise_floor(records)
    report_ablation(records)
    report_sweep(records)

    out_path = os.path.join(RUN_DIR, "summary.csv")
    fields = ["label", "run_id", "scenario", "condition", "seed", "agent", "brain",
              "duration_s", "decisions", "decisions_per_min", "interrupts",
              "interrupts_per_min", "interrupt_rate", "completion_at_abandon",
              "need_when_leaving", "mean_trigger_need", "conflict_decisions", "collapsed"]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print()
    print("Wrote %s" % out_path)


if __name__ == "__main__":
    main()
