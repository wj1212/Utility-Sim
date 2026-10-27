"""Build every figure used in the slides, from the recorded runs.

    python make_figures.py

Writes PNGs into Figures/. Nothing here is drawn by hand or typed from memory:
each figure reads UnityProject/RunData, the same source analyze_runs.py reads,
so a figure and a reported number cannot drift apart.

Palette and mark rules follow one convention throughout: thin marks, hairline
solid gridlines, one y-axis per panel, a legend whenever two or more series
share a panel, and direct labels only on the points that carry the argument.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.join(ROOT, "UnityProject", "RunData")
OUT_DIR = os.path.join(ROOT, "Figures")

OUTAGE_START, OUTAGE_END = 100.0, 160.0
COLLAPSE = 0.80
ACTIVATION = 0.71          # the utility agent's score threshold
ABLATION = ["linear_noinertia", "linear_inertia", "curve_noinertia", "curve_inertia"]
PRETTY = {
    "linear_noinertia": "linear, no inertia",
    "linear_inertia":   "linear, inertia",
    "curve_noinertia":  "curve, no inertia",
    "curve_inertia":    "curve, inertia",
}

# ------------------------------------------------------------------ palette
BLUE    = "#2a78d6"
ORANGE  = "#eb6834"
AQUA    = "#1baf7a"
YELLOW  = "#eda100"
CRIT    = "#d03b3b"
GOOD    = "#0ca30c"
INK     = "#0b0b0b"
INK2    = "#52514e"
MUTED   = "#898781"
GRID    = "#e1e0d9"
AXIS    = "#c3c2b7"
SURFACE = "#ffffff"
BANDFILL = "#eef4fc"

plt.rcParams.update({
    "font.family": ["Segoe UI", "Arial", "DejaVu Sans"],
    "font.size": 11,
    "text.color": INK,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "axes.linewidth": 0.8,
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 10.5,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "legend.frameon": False,
    "legend.fontsize": 10.5,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
})


def tidy(ax, xgrid=False, ygrid=True):
    """Hairline recessive grid, no top or right spine."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(ygrid, axis="y")
    ax.grid(xgrid, axis="x")
    ax.tick_params(length=0)


def save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, name)
    fig.savefig(p)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


# ------------------------------------------------------------------ loading
def load_summary():
    return pd.read_csv(os.path.join(RUN_DIR, "summary.csv"))


def decision_files():
    """label -> path, for the newest file per label."""
    out = {}
    for p in sorted(glob.glob(os.path.join(RUN_DIR, "decisions_*.csv"))):
        base = os.path.basename(p)[len("decisions_"):-len(".csv")]
        label = base.rsplit("_", 3)[0]
        out[label] = p
    return out


def utility_rows(path):
    d = pd.read_csv(path)
    return d[d.agent == "Utility"].copy()


# ------------------------------------------- 1 & 2: the inertia sweep
def sweep_table(summary):
    rows = []
    for bonus, cond in [(0.0, "inertia000"), (0.1, "inertia010"), (0.2, "inertia020"),
                        (0.3, "inertia030"), (0.5, "inertia050")]:
        d = summary[(summary.condition == cond) & (summary.agent == "Utility")]
        rows.append({
            "bonus": bonus,
            "rate": d.interrupt_rate.median() * 100,
            "per_min": d.interrupts_per_min.median(),
            "completion": d.completion_at_abandon.mean(),
            "collapses": int(d.collapsed.sum()),
            "n": len(d),
        })
    return pd.DataFrame(rows)


def fig_sweep(sw):
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    ax.add_patch(Rectangle((0.19, 0), 0.12, 100, facecolor=BANDFILL,
                           edgecolor="none", zorder=0))
    ax.text(0.25, 92, "usable range", ha="center", va="top",
            color=BLUE, fontsize=10.5)

    ax.plot(sw.bonus, sw.rate, "-", color=BLUE, linewidth=2, zorder=3)
    ax.plot(sw.bonus, sw.rate, "o", color=BLUE, markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)

    best = sw.loc[sw.rate.idxmin()]
    ax.plot([best.bonus], [best.rate], "o", color=BLUE, markersize=13,
            markeredgecolor=SURFACE, markeredgewidth=2.5, zorder=5)
    ax.annotate(f"best: {best.rate:.1f}%  at  {best.bonus:.1f}",
                xy=(best.bonus, best.rate), xytext=(best.bonus + 0.045, best.rate - 13),
                color=BLUE, fontsize=11.5, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=BLUE, linewidth=1))

    ax.annotate("too little commitment\nthe agent cannot settle",
                xy=(0.0, sw.rate.iloc[0]), xytext=(0.012, sw.rate.iloc[0] - 26),
                color=CRIT, fontsize=11, linespacing=1.35,
                arrowprops=dict(arrowstyle="-", color=CRIT, linewidth=1))
    ax.annotate("too much commitment\nthe other need hits crisis",
                xy=(0.5, sw.rate.iloc[-1]), xytext=(0.355, sw.rate.iloc[-1] + 21),
                color=CRIT, fontsize=11, linespacing=1.35, ha="left",
                arrowprops=dict(arrowstyle="-", color=CRIT, linewidth=1))

    ax.set_xlabel("commitment bonus  $\\beta$")
    ax.set_ylabel("interruptions  (% of decisions)")
    ax.set_xlim(-0.03, 0.56)
    ax.set_ylim(0, 100)
    ax.set_xticks(sw.bonus)
    ax.set_yticks(range(0, 101, 20))
    tidy(ax)
    save(fig, "fig_01_sweep.png")


def fig_sweep_two_panel(sw):
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.0), sharex=True,
                             gridspec_kw=dict(hspace=0.22))
    for ax, col, lab, fmt in [
        (axes[0], "rate", "interruptions\n(% of decisions)", "{:.1f}%"),
        (axes[1], "per_min", "interruptions\nper minute", "{:.1f}"),
    ]:
        ax.add_patch(Rectangle((0.19, 0), 0.12, 1e4, facecolor=BANDFILL,
                               edgecolor="none", zorder=0))
        ax.plot(sw.bonus, sw[col], "-", color=BLUE, linewidth=2, zorder=3)
        ax.plot(sw.bonus, sw[col], "o", color=BLUE, markersize=7,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
        lo = sw.loc[sw[col].idxmin()]
        ax.annotate(fmt.format(lo[col]), xy=(lo.bonus, lo[col]),
                    xytext=(lo.bonus, lo[col] + sw[col].max() * 0.13),
                    color=BLUE, fontsize=11, fontweight="bold", ha="center")
        ax.set_ylabel(lab, fontsize=10.5, linespacing=1.3)
        ax.set_ylim(0, sw[col].max() * 1.32)
        tidy(ax)
    axes[1].set_xlabel("commitment bonus  $\\beta$")
    axes[1].set_xticks(sw.bonus)
    axes[0].text(0.0, sw.rate.max() * 1.22,
                 "both measures turn up again at 0.5, so the rise is not an artefact of the ratio",
                 fontsize=10.5, color=INK2)
    save(fig, "fig_02_sweep_two_panel.png")


# ------------------------------------------- 3: collapse as a dot matrix
def fig_collapse_dots(summary):
    """The median hides this; the dots do not. Calm beside outage, deliberately."""
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.1), sharey=True,
                             gridspec_kw=dict(wspace=0.46))
    for ax, scen, head in [(axes[0], "normal", "Calm"),
                           (axes[1], "outage", "Resource removed for 60 s")]:
        for row, cond in enumerate(ABLATION):
            d = summary[(summary.scenario == scen) & (summary.condition == cond) &
                        (summary.agent == "Utility")].sort_values("seed")
            y = len(ABLATION) - 1 - row
            for i, (_, r) in enumerate(d.iterrows()):
                if r.collapsed:
                    ax.plot(i, y, "o", color=CRIT, markersize=13,
                            markeredgecolor=SURFACE, markeredgewidth=2)
                else:
                    ax.plot(i, y, "o", color=SURFACE, markersize=13,
                            markeredgecolor=AXIS, markeredgewidth=1.5)
            n = int(d.collapsed.sum())
            ax.text(8.5, y, f"{n} of 8", va="center", fontsize=11,
                    color=CRIT if n else GOOD, fontweight="bold")
        ax.set_xlim(-0.9, 10.6)
        ax.set_ylim(-1.15, 3.9)
        ax.axis("off")
        ax.text(3.5, 3.62, head, fontsize=12, color=INK, ha="center")

    for row, cond in enumerate(ABLATION):
        axes[0].text(-1.5, len(ABLATION) - 1 - row, PRETTY[cond], va="center",
                     ha="right", fontsize=11, color=INK2)

    ax = axes[0]
    ax.plot(0.0, -0.85, "o", color=CRIT, markersize=10,
            markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.text(0.45, -0.85, "collapsed", va="center", fontsize=10.5, color=INK2)
    ax.plot(3.9, -0.85, "o", color=SURFACE, markersize=10,
            markeredgecolor=AXIS, markeredgewidth=1.5)
    ax.text(4.35, -0.85, "survived", va="center", fontsize=10.5, color=INK2)
    ax.text(7.5, -0.85, "one dot per seed", va="center", fontsize=10.5, color=MUTED)
    save(fig, "fig_03_collapse_dots.png")


# ------------------------------------------- 4: the 2x2 with the noise floor
def fig_ablation_strip(summary, noise_pp):
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5), sharey=True,
                             gridspec_kw=dict(wspace=0.08))
    rng = np.random.default_rng(7)
    for ax, scen, head in [(axes[0], "normal", "Calm"),
                           (axes[1], "outage", "Resource removed for 60 s")]:
        for row, cond in enumerate(ABLATION):
            d = summary[(summary.scenario == scen) & (summary.condition == cond) &
                        (summary.agent == "Utility")]
            y = len(ABLATION) - 1 - row
            vals = d.interrupt_rate.values * 100
            ax.plot(vals, y + rng.uniform(-0.17, 0.17, len(vals)), "o",
                    color=BLUE, markersize=6, alpha=0.40,
                    markeredgecolor="none", zorder=2)
            med = np.median(vals)
            ax.plot([med], [y], "|", color=BLUE, markersize=26,
                    markeredgewidth=3, zorder=4)
            ax.text(med, y + 0.33, f"{med:.0f}%", ha="center", fontsize=10.5,
                    color=BLUE, fontweight="bold")
        ax.axvspan(COLLAPSE * 100, 100, color="#fbeeee", zorder=0)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.95, 3.75)
        ax.set_xticks(range(0, 101, 25))
        ax.set_xlabel("interruptions  (% of decisions)")
        ax.set_title(head, fontsize=12, color=INK, pad=10, loc="left")
        tidy(ax, xgrid=True, ygrid=False)
        ax.set_yticks(range(len(ABLATION)))
        ax.spines["left"].set_visible(False)

    axes[0].set_yticklabels([PRETTY[c] for c in reversed(ABLATION)], fontsize=11)
    axes[0].tick_params(axis="y", labelcolor=INK2)
    axes[1].text(90, -0.78, "collapse", color=CRIT, fontsize=10, ha="center")

    # the noise floor, drawn to scale so "not measurable" is visible, not asserted
    ax = axes[0]
    ax.annotate("", xy=(6, -0.72), xytext=(6 + noise_pp, -0.72),
                arrowprops=dict(arrowstyle="|-|,widthA=0.35,widthB=0.35",
                                color=ORANGE, linewidth=1.4))
    ax.text(6 + noise_pp + 2.5, -0.72, f"noise floor, {noise_pp:.1f} pp",
            va="center", fontsize=10, color=ORANGE)
    save(fig, "fig_04_ablation_strip.png")


# ------------------------------------------- 5 & 6: interruptions by phase
def phase_table(files):
    """Pooled interrupt rate per phase, per ablation condition, under outage."""
    rows = []
    for cond in ABLATION:
        parts = []
        for seed in range(1, 9):
            lab = f"outage_{cond}_s{seed:02d}"
            p = files.get(lab)
            if p:
                parts.append(utility_rows(p))
        if not parts:
            continue
        d = pd.concat(parts, ignore_index=True)
        phase = pd.cut(d.time_s, [-1, OUTAGE_START, OUTAGE_END, 1e9],
                       right=False, labels=["before", "during", "after"])
        g = d.groupby(phase, observed=False).is_interrupt.agg(["mean", "size"])
        rows.append({
            "condition": cond,
            "before": g.loc["before", "mean"] * 100,
            "during": g.loc["during", "mean"] * 100,
            "after":  g.loc["after",  "mean"] * 100,
            "n": int(g["size"].sum()),
        })
    return pd.DataFrame(rows)


def _phase_axes(ax, ph):
    ax.axvspan(0.62, 1.38, color="#f4f3ef", zorder=0)
    ax.text(1.0, 14, "resource gone", ha="center", fontsize=10.5, color=INK2)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["before\n0 to 100 s", "during\n100 to 160 s", "after\n160 s on"],
                       fontsize=10.5, linespacing=1.4)
    ax.set_ylabel("interruptions  (% of decisions)")
    ax.set_ylim(0, 108)
    ax.set_yticks(range(0, 101, 25))
    tidy(ax)


def fig_phases_two(ph):
    """Pooled to the one contrast that matters: inertia on or off."""
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    groups = [("without inertia", ["linear_noinertia", "curve_noinertia"], CRIT),
              ("with inertia",    ["linear_inertia", "curve_inertia"],    BLUE)]
    w = 0.3
    for k, (lab, conds, col) in enumerate(groups):
        sub = ph[ph.condition.isin(conds)]
        vals = [sub[c].mean() for c in ("before", "during", "after")]
        xs = np.array([0, 1, 2]) + (k - 0.5) * (w + 0.025)
        ax.bar(xs, vals, width=w, color=col, label=lab, zorder=3)
        for x, v in zip(xs, vals):
            if v < 1:
                ax.text(x, 3.5, "0%", ha="center", fontsize=12,
                        fontweight="bold", color=col)
            else:
                ax.text(x, v + 3, f"{v:.0f}%", ha="center", fontsize=11.5,
                        fontweight="bold", color=col)
    _phase_axes(ax, ph)
    ax.legend(loc="upper left", bbox_to_anchor=(0.005, 1.0))
    save(fig, "fig_05_phases.png")


def fig_phases_all(ph):
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    cols = {"linear_noinertia": CRIT, "curve_noinertia": ORANGE,
            "linear_inertia": BLUE, "curve_inertia": AQUA}
    order = ["linear_noinertia", "curve_noinertia", "linear_inertia", "curve_inertia"]
    w = 0.19
    for k, cond in enumerate(order):
        r = ph[ph.condition == cond].iloc[0]
        vals = [r.before, r.during, r.after]
        xs = np.array([0, 1, 2]) + (k - 1.5) * (w + 0.015)
        ax.bar(xs, vals, width=w, color=cols[cond], label=PRETTY[cond], zorder=3)
        for x, v in zip(xs, vals):
            if v < 1:
                ax.text(x, 2.5, "0", ha="center", fontsize=10,
                        fontweight="bold", color=cols[cond])
    _phase_axes(ax, ph)
    ax.legend(loc="upper left", ncol=2, bbox_to_anchor=(0.005, 1.0))
    save(fig, "fig_06_phases_all4.png")


# ------------------------------------------- 7: completion at abandonment
def fig_completion(sw):
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.add_patch(Rectangle((0.19, 0), 0.12, 2, facecolor=BANDFILL,
                           edgecolor="none", zorder=0))
    ax.plot(sw.bonus, sw.completion, "-", color=ORANGE, linewidth=2, zorder=3)
    ax.plot(sw.bonus, sw.completion, "o", color=ORANGE, markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
    for _, r in sw.iloc[[0, -1]].iterrows():
        ax.text(r.bonus, r.completion + 0.055, f"{r.completion:.2f}",
                ha="center", fontsize=11.5, fontweight="bold", color=ORANGE)
    ax.text(0.015, 0.30, "leaves early\nnothing gets finished", fontsize=11,
            color=INK2, linespacing=1.35)
    ax.text(0.5, 0.52, "leaves late\nonly a crisis moves it", fontsize=11,
            color=INK2, linespacing=1.35, ha="right")
    ax.set_xlabel("commitment bonus  $\\beta$")
    ax.set_ylabel("how far the abandoned action got")
    ax.set_xlim(-0.03, 0.56)
    ax.set_ylim(0, 1.0)
    ax.set_xticks(sw.bonus)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    tidy(ax)
    save(fig, "fig_07_completion.png")


# ------------------------------------------- 8: threshold rules vs utility
def fig_threshold_slope(summary):
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    series = []

    base = summary[(summary.agent == "Baseline") &
                   (summary.condition.isin(ABLATION))]
    series.append(("threshold rules", ORANGE, [
        (base[base.scenario == "normal"].interrupts_per_min.median(),
         int(base[base.scenario == "normal"].collapsed.sum()),
         len(base[base.scenario == "normal"])),
        (base[base.scenario == "outage"].interrupts_per_min.median(),
         int(base[base.scenario == "outage"].collapsed.sum()),
         len(base[base.scenario == "outage"])),
    ]))

    tuned = summary[(summary.agent == "Utility") &
                    (summary.condition == "curve_inertia")]
    series.append(("utility, tuned inertia", BLUE, [
        (tuned[tuned.scenario == "normal"].interrupts_per_min.median(),
         int(tuned[tuned.scenario == "normal"].collapsed.sum()),
         len(tuned[tuned.scenario == "normal"])),
        (tuned[tuned.scenario == "outage"].interrupts_per_min.median(),
         int(tuned[tuned.scenario == "outage"].collapsed.sum()),
         len(tuned[tuned.scenario == "outage"])),
    ]))

    for lab, col, pts in series:
        ys = [p[0] for p in pts]
        ax.plot([0, 1], ys, "-", color=col, linewidth=2.2, zorder=3)
        ax.plot([0, 1], ys, "o", color=col, markersize=9,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
        ax.text(-0.045, ys[0], f"{ys[0]:.1f}", ha="right", va="center",
                fontsize=12, fontweight="bold", color=col)
        ax.text(1.045, ys[1], f"{ys[1]:.1f}", ha="left", va="center",
                fontsize=12, fontweight="bold", color=col)
        ax.text(1.045, ys[1] - 0.95, f"{pts[1][1]} of {pts[1][2]} runs collapsed",
                ha="left", va="center", fontsize=10.5, color=col)
        ax.text(0.5, (ys[0] + ys[1]) / 2 + (0.75 if col == ORANGE else -1.0),
                lab, ha="center", fontsize=11.5, color=col, fontweight="bold")

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["calm", "resource removed"], fontsize=11.5, color=INK2)
    ax.set_ylabel("interruptions per minute")
    ax.set_xlim(-0.28, 1.42)
    ax.set_ylim(0, 15.5)
    tidy(ax)
    save(fig, "fig_08_threshold_slope.png")


# ------------------------------------------- 9: the three need-to-score mappings
def hermite(keys, xs):
    """Unity AnimationCurve evaluation: cubic Hermite between keyframes."""
    out = []
    for x in xs:
        if x <= keys[0][0]:
            out.append(keys[0][1]); continue
        if x >= keys[-1][0]:
            out.append(keys[-1][1]); continue
        for (t1, v1, _, m1), (t2, v2, m2, _) in zip(keys, keys[1:]):
            if t1 <= x <= t2:
                dt = t2 - t1
                s = (x - t1) / dt
                h00 = 2 * s**3 - 3 * s**2 + 1
                h10 = s**3 - 2 * s**2 + s
                h01 = -2 * s**3 + 3 * s**2
                h11 = s**3 - s**2
                out.append(h00 * v1 + h10 * dt * m1 + h01 * v2 + h11 * dt * m2)
                break
    return np.array(out)


def fig_curves():
    # Curve_Utility.asset, verbatim: (time, value, inSlope, outSlope)
    keys = [(0.00, 1.00,  0.0000000,  0.0000000),
            (0.20, 0.85, -0.9447603, -0.9447603),
            (0.50, 0.35, -1.3378217, -1.3378217),
            (0.75, 0.10, -1.0587420, -1.0587420),
            (1.00, 0.00,  0.0000000,  0.0000000)]
    xs = np.linspace(0, 1, 400)
    curve = hermite(keys, xs)
    linear = 1 - xs

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.axhline(ACTIVATION, color=MUTED, linewidth=1)
    ax.text(0.985, ACTIVATION + 0.025, f"act threshold  $\\theta$ = {ACTIVATION}",
            ha="right", fontsize=10.5, color=MUTED)

    ax.plot(xs, linear, "-", color=AQUA, linewidth=2,
            label="linear  (curve switched off)", zorder=3)
    ax.plot(xs, curve, "-", color=BLUE, linewidth=2.4,
            label="tuned response curve", zorder=4)
    ax.plot([k[0] for k in keys], [k[1] for k in keys], "o", color=BLUE,
            markersize=6.5, markeredgecolor=SURFACE, markeredgewidth=1.8, zorder=5)

    # the threshold agent: a ramp that dies at 0.3, from Curve_Baseline.asset
    ax.plot([0, 0.3, 0.3, 1], [1, 0, 0, 0], "-", color=ORANGE, linewidth=2,
            label="threshold agent", zorder=2)

    crossings = []
    for col, ys in [(BLUE, curve), (AQUA, linear)]:
        i = int(np.argmin(np.abs(ys - ACTIVATION)))
        crossings.append(xs[i])
        ax.plot([xs[i]], [ys[i]], "o", color=col, markersize=10,
                markeredgecolor=SURFACE, markeredgewidth=2.5, zorder=6)
    ax.annotate("both start acting at the same need,\nso the two conditions stay matched",
                xy=(float(np.mean(crossings)), ACTIVATION),
                xytext=(0.40, 0.88), color=INK2, fontsize=10.5, linespacing=1.35,
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))

    ax.set_xlabel("need  (1 = satisfied, 0 = empty)")
    ax.set_ylabel("desire to act on it")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.12)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.02))
    tidy(ax)
    save(fig, "fig_09_curves.png")


# ------------------------------------------- 10: what the agent actually did
ACTION_COL = {"Eat": BLUE, "Sleep": ORANGE, "idle": "#dedcd5"}


def pick_pair(summary, files):
    """A seed that collapsed without inertia and survived with it."""
    for seed in range(1, 9):
        a = summary[(summary.scenario == "outage") & (summary.seed == seed) &
                    (summary.condition == "linear_noinertia") & (summary.agent == "Utility")]
        b = summary[(summary.scenario == "outage") & (summary.seed == seed) &
                    (summary.condition == "linear_inertia") & (summary.agent == "Utility")]
        if len(a) and len(b) and bool(a.collapsed.iloc[0]) and not bool(b.collapsed.iloc[0]):
            la, lb = f"outage_linear_noinertia_s{seed:02d}", f"outage_linear_inertia_s{seed:02d}"
            if la in files and lb in files:
                return seed, files[la], files[lb], a.interrupt_rate.iloc[0], b.interrupt_rate.iloc[0]
    return None


def fig_timeline(pair):
    seed, pa, pb, ra, rb = pair
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 3.5), sharex=True,
                             gridspec_kw=dict(hspace=0.55))
    for ax, path, head, rate, col in [
        (axes[0], pa, "without inertia", ra, CRIT),
        (axes[1], pb, "with inertia",    rb, BLUE),
    ]:
        d = utility_rows(path).sort_values("time_s").reset_index(drop=True)
        end = 300.0
        for i, r in d.iterrows():
            t0 = r.time_s
            t1 = d.time_s.iloc[i + 1] if i + 1 < len(d) else end
            ax.add_patch(Rectangle((t0, 0), max(t1 - t0 - 0.35, 0.25), 1,
                                   facecolor=ACTION_COL.get(r.to_action, MUTED),
                                   edgecolor="none"))
        ax.axvspan(OUTAGE_START, OUTAGE_END, ymin=0, ymax=1,
                   facecolor="none", edgecolor=INK2, linewidth=1.1, zorder=5)
        ax.set_xlim(0, end)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        for s in ("top", "right", "left", "bottom"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
        ax.set_title(f"{head}      {rate*100:.0f}% of decisions were interruptions",
                     fontsize=11.5, color=col, loc="left", pad=6)

    axes[0].text(OUTAGE_START + 30, 1.5, "resource gone", ha="center",
                 fontsize=10.5, color=INK2)
    axes[1].set_xlabel("time  (seconds)")
    axes[1].set_xticks(range(0, 301, 50))
    axes[1].tick_params(axis="x", length=0, labelcolor=MUTED)

    handles = [Rectangle((0, 0), 1, 1, facecolor=ACTION_COL[a]) for a in ("Eat", "Sleep")]
    axes[1].legend(handles, ["eating", "sleeping"],
                   loc="upper left", bbox_to_anchor=(0, -0.52), ncol=2)
    axes[1].text(300, -0.62, f"same starting conditions, seed {seed}",
                 transform=axes[1].get_xaxis_transform(), ha="right",
                 fontsize=10.5, color=MUTED)
    save(fig, "fig_10_timeline.png")


# ------------------------------------------- 11: the two needs over time
def fig_traces(pair):
    seed, pa, pb, ra, rb = pair
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 4.8), sharex=True,
                             gridspec_kw=dict(hspace=0.30))
    for ax, path, head, col in [
        (axes[0], pa, "without inertia", CRIT),
        (axes[1], pb, "with inertia",    BLUE),
    ]:
        d = utility_rows(path).sort_values("time_s")
        ax.axvspan(OUTAGE_START, OUTAGE_END, color="#f4f3ef", zorder=0)
        ax.plot(d.time_s, d.hunger, "-", color=BLUE, linewidth=1.6,
                label="hunger", zorder=3)
        ax.plot(d.time_s, d.energy, "-", color=ORANGE, linewidth=1.6,
                label="energy", zorder=3)
        itr = d[d.is_interrupt == 1]
        ax.plot(itr.time_s, np.full(len(itr), 1.04), "|", color=INK2,
                markersize=7, markeredgewidth=1.1, zorder=4)
        ax.set_ylim(0, 1.12)
        ax.set_xlim(0, 300)
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_ylabel("need")
        ax.set_title(head, fontsize=11.5, color=col, loc="left", pad=6)
        tidy(ax)
    for ax in axes:
        ax.text(OUTAGE_START + 30, 0.93, "resource gone", ha="center",
                fontsize=10, color=INK2)
    axes[1].text(0, -0.40, "each tick along the top of a panel is one interruption",
                 transform=axes[1].get_xaxis_transform(), fontsize=10, color=MUTED)
    axes[0].legend(loc="lower left", ncol=2, bbox_to_anchor=(0.0, 0.02))
    axes[1].set_xlabel("time  (seconds)")
    axes[1].set_xticks(range(0, 301, 50))
    save(fig, "fig_11_traces.png")


# ------------------------------------------- 12: how a decision is made
def fig_mechanism():
    fig, ax = plt.subplots(figsize=(9.0, 3.1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")

    def box(x, y, w, h, text, edge, fill="#ffffff", fs=11, weight="normal"):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.035,rounding_size=0.09",
                                    facecolor=fill, edgecolor=edge, linewidth=1.4))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=INK, linespacing=1.4, fontweight=weight)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                     arrowstyle="-|>", mutation_scale=13,
                                     color=MUTED, linewidth=1.2,
                                     shrinkA=0, shrinkB=0))

    box(0.15, 1.95, 1.65, 0.75, "hunger\n0.28", AXIS, "#f7f7f5")
    box(0.15, 0.55, 1.65, 0.75, "energy\n0.64", AXIS, "#f7f7f5")
    box(2.45, 1.95, 1.9, 0.75, "response\ncurve  $f$", BLUE, BANDFILL)
    box(2.45, 0.55, 1.9, 0.75, "response\ncurve  $f$", BLUE, BANDFILL)
    box(5.0, 1.95, 1.75, 0.75, "eat\n0.78", AXIS)
    box(5.0, 0.55, 1.75, 0.75, "sleep\n0.21", AXIS)
    box(7.35, 1.95, 2.45, 0.75, "+ $\\beta$ if already\ndoing it", ORANGE, "#fdf0e9")
    box(7.35, 0.4, 2.45, 1.05, "pick the highest,\nif it clears $\\theta$", INK, "#f7f7f5",
        fs=11, weight="bold")

    for y in (2.325, 0.925):
        arrow(1.88, y, 2.40, y)
        arrow(4.42, y, 4.95, y)
    arrow(6.82, 2.325, 7.30, 2.325)
    arrow(8.57, 1.90, 8.57, 1.50)
    arrow(6.82, 0.925, 7.30, 0.925)

    ax.text(0.98, 2.95, "need", ha="center", fontsize=10.5, color=MUTED)
    ax.text(8.57, 1.68, "already eating", ha="center", fontsize=9.5, color=ORANGE)
    ax.text(3.40, 2.95, "shape it", ha="center", fontsize=10.5, color=MUTED)
    ax.text(5.88, 2.95, "score", ha="center", fontsize=10.5, color=MUTED)
    ax.text(8.57, 2.95, "commit", ha="center", fontsize=10.5, color=MUTED)
    save(fig, "fig_12_mechanism.png")


# ------------------------------------------------------------------- main
def main():
    summary = load_summary()
    files = decision_files()

    print("figures:")
    sw = sweep_table(summary)
    fig_sweep(sw)
    fig_sweep_two_panel(sw)
    fig_collapse_dots(summary)

    # noise floor: the baseline agent is identical in all four cells, so its
    # within-seed spread across them is interference, not an effect.
    spreads = []
    for scen in ("normal", "outage"):
        b = summary[(summary.agent == "Baseline") & (summary.scenario == scen) &
                    (summary.condition.isin(ABLATION))]
        for seed, g in b.groupby("seed"):
            if len(g) == len(ABLATION):
                spreads.append((g.interrupt_rate.max() - g.interrupt_rate.min()) * 100)
    noise_pp = float(np.median(spreads))
    fig_ablation_strip(summary, noise_pp)

    ph = phase_table(files)
    fig_phases_two(ph)
    fig_phases_all(ph)
    fig_completion(sw)
    fig_threshold_slope(summary)
    fig_curves()
    fig_mechanism()

    pair = pick_pair(summary, files)
    if pair:
        fig_timeline(pair)
        fig_traces(pair)
    else:
        print("  !! no seed collapsed without inertia and survived with it")

    print()
    print("numbers these figures assert, for cross-checking against RESULTS.md")
    print("  noise floor            ", f"{noise_pp:.1f} pp")
    print("  sweep")
    print(sw.to_string(index=False))
    print("  phases (pooled, utility agent)")
    print(ph.to_string(index=False))


if __name__ == "__main__":
    main()
