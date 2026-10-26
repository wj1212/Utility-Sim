"""
Summarise every logged run in UnityProject/RunData.

Usage:
    python analyze_runs.py

Reads each decisions_*.csv, computes the stability and calibration metrics used in
the study, prints a comparison table, and writes RunData/summary.csv.
"""

import csv
import os
import sys
from collections import defaultdict

RUN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UnityProject", "RunData")

# A need at or below this value is treated as critical for the conflict count.
CRITICAL = 0.32


def load_runs(run_dir):
    """Group decision rows by (condition, run_id, agent)."""
    runs = defaultdict(list)
    for name in sorted(os.listdir(run_dir)):
        if not name.startswith("decisions_") or not name.endswith(".csv"):
            continue
        with open(os.path.join(run_dir, name), newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                runs[(row["condition"], row["run_id"], row["agent"])].append(row)
    return runs


def summarise(rows):
    """Compute one agent's metrics for one run."""
    duration = max(float(r["time_s"]) for r in rows)
    decisions = len(rows)
    interrupts = sum(1 for r in rows if r["is_interrupt"] == "1")

    # Need level at which the agent chose to act, per action type.
    eat_at = [float(r["hunger"]) for r in rows if r["to_action"] == "Eat"]
    sleep_at = [float(r["energy"]) for r in rows if r["to_action"] == "Sleep"]
    triggers = eat_at + sleep_at

    # Decisions taken while both needs were simultaneously critical. Arbitration
    # between competing needs only happens here, so a zero means the two decision
    # architectures were never actually asked to choose.
    conflicts = sum(
        1 for r in rows
        if float(r["hunger"]) <= CRITICAL and float(r["energy"]) <= CRITICAL
    )

    return {
        "brain": rows[0]["brain"],
        "duration_s": round(duration, 1),
        "decisions": decisions,
        "decisions_per_min": round(decisions / (duration / 60.0), 2) if duration else 0.0,
        "interrupts": interrupts,
        "interrupt_rate": round(interrupts / decisions, 3) if decisions else 0.0,
        "mean_trigger_need": round(sum(triggers) / len(triggers), 3) if triggers else None,
        "conflict_decisions": conflicts,
    }


def config_signature(run_dir, condition, run_id):
    """The parameters that define a condition, ignoring per-run bookkeeping."""
    path = os.path.join(run_dir, f"config_{condition}_{run_id}.csv")
    if not os.path.isfile(path):
        return None
    # Dropped because they vary per repeat rather than defining the condition.
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


def report_repeats(records):
    """Group runs that share a configuration and report mean and range per brain."""
    groups = defaultdict(list)
    for r in records:
        if r["signature"] is not None:
            groups[r["signature"]].append(r)

    repeated = {k: v for k, v in groups.items() if len({r["condition"] for r in v}) > 1}
    if not repeated:
        return

    for sig, rows in repeated.items():
        labels = sorted({r["condition"] for r in rows})
        print()
        print(f"REPEATED MEASURES  ({', '.join(labels)}, identical configuration, n={len(labels)})")
        print(f"{'brain':<10}{'decisions':>22}{'interrupts':>22}{'interrupt_rate':>22}")
        print("-" * 76)
        for brain in sorted({r["brain"] for r in rows}):
            sub = [r for r in rows if r["brain"] == brain]
            cells = []
            for field in ("decisions", "interrupts", "interrupt_rate"):
                vals = [r[field] for r in sub]
                mean = sum(vals) / len(vals)
                cells.append(f"{mean:.2f} ({min(vals):g}-{max(vals):g})")
            print(f"{brain:<10}" + "".join(f"{c:>22}" for c in cells))

        brains = sorted({r["brain"] for r in rows})
        if len(brains) == 2:
            a, b = brains
            print()
            print(f"{'run':<10}{a:>12}{b:>12}   direction")
            for label in labels:
                va = next(r["interrupts"] for r in rows if r["condition"] == label and r["brain"] == a)
                vb = next(r["interrupts"] for r in rows if r["condition"] == label and r["brain"] == b)
                direction = f"{b} lower" if vb < va else (f"{a} lower" if va < vb else "tied")
                print(f"{label:<10}{va:>12}{vb:>12}   {direction}")


def main():
    if not os.path.isdir(RUN_DIR):
        sys.exit(f"No run directory at {RUN_DIR}. Play the scene with DecisionLogger attached first.")

    runs = load_runs(RUN_DIR)
    if not runs:
        sys.exit(f"No decisions_*.csv found in {RUN_DIR}.")

    records = []
    for (condition, run_id, agent), rows in sorted(runs.items()):
        rec = {"condition": condition, "run_id": run_id, "agent": agent}
        rec.update(summarise(rows))
        rec["signature"] = config_signature(RUN_DIR, condition, run_id)
        records.append(rec)

    header = (
        f"{'condition':<14}{'agent':<10}{'brain':<10}"
        f"{'dur':>6}{'dec':>6}{'/min':>7}{'intr':>6}{'intr%':>7}"
        f"{'trigger':>9}{'conflicts':>11}"
    )
    print()
    print(header)
    print("-" * len(header))

    last_condition = None
    for r in records:
        if last_condition is not None and r["condition"] != last_condition:
            print()
        last_condition = r["condition"]
        trigger = f"{r['mean_trigger_need']:.3f}" if r["mean_trigger_need"] is not None else "-"
        print(
            f"{r['condition']:<14}{r['agent']:<10}{r['brain']:<10}"
            f"{r['duration_s']:>6.0f}{r['decisions']:>6}{r['decisions_per_min']:>7.2f}"
            f"{r['interrupts']:>6}{r['interrupt_rate']:>7.2f}"
            f"{trigger:>9}{r['conflict_decisions']:>11}"
        )

    print()
    print("dur      simulated seconds recorded")
    print("dec      decisions taken; /min is the stability proxy (lower = more stable)")
    print("intr     decisions that interrupted an action already in progress")
    print("trigger  mean need level at which the agent chose to act")
    print(f"conflicts decisions taken while BOTH needs were at or below {CRITICAL}")

    report_repeats(records)

    out_path = os.path.join(RUN_DIR, "summary.csv")
    fields = [
        "condition", "run_id", "agent", "brain", "duration_s", "decisions",
        "decisions_per_min", "interrupts", "interrupt_rate", "mean_trigger_need",
        "conflict_decisions",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
