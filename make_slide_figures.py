"""Slide versions of the figures: one point each, everything else greyed.

    python make_slide_figures.py

The figures in make_figures.py carry several things at once, which is right
for a document that gets read and wrong for a slide that gets looked at for
twenty seconds. These are the talk's versions. Same data, one claim each:

    slide_problem        it abandoned most of what it started
    slide_curves         the curve can be straight or bent
    slide_curves_zoom    where decisions happen, the two are the same
    slide_collapse       without inertia it collapses, with it never
    slide_sweep          there is a best value

Output goes to Figures/. The analysis versions are untouched.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.join(ROOT, "UnityProject", "RunData")
OUT = os.path.join(ROOT, "Figures")
MIN_DURATION = 290.0
ABLATION = ["linear_noinertia", "linear_inertia", "curve_noinertia", "curve_inertia"]
PRETTY = {"linear_noinertia": "linear, no inertia", "linear_inertia": "linear, inertia",
          "curve_noinertia": "curve, no inertia", "curve_inertia": "curve, inertia"}

# One accent. Everything else is a shade of grey.
ACCENT = "#2a78d6"
RED = "#d03b3b"
ORANGE = "#eb6834"
INK = "#1a1a1a"
GREY = "#b4b2ad"
PALE = "#dedcd5"
FAINT = "#efeee9"

plt.rcParams.update({
    "font.family": ["Segoe UI", "Arial", "DejaVu Sans"],
    "font.size": 13,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.12,
    "legend.frameon": False,
})


def bare(ax, keep_x=True):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_visible(keep_x)
    ax.spines["bottom"].set_color(PALE)
    ax.tick_params(length=0, colors="#7a7974")


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    fig.savefig(p)
    plt.close(fig)
    print("  ", name)


def load_summary():
    return pd.read_csv(os.path.join(RUN_DIR, "summary.csv"))


def best_file(label):
    best = None
    for p in glob.glob(os.path.join(RUN_DIR, "decisions_%s_*.csv" % label)):
        try:
            end = pd.read_csv(p, usecols=["time_s"]).time_s.max()
        except Exception:
            continue
        if end >= MIN_DURATION and (best is None or end > best[1]):
            best = (p, end)
    return best[0] if best else None


# ------------------------------------------------- the curve, evaluated
KEYS = [(0.00, 1.00, 0.0, 0.0), (0.20, 0.85, -0.9447603, -0.9447603),
        (0.50, 0.35, -1.3378217, -1.3378217), (0.75, 0.10, -1.0587420, -1.0587420),
        (1.00, 0.00, 0.0, 0.0)]


def curve(xs):
    out = []
    for x in xs:
        if x <= 0:
            out.append(1.0); continue
        if x >= 1:
            out.append(0.0); continue
        for (t1, v1, _, m1), (t2, v2, m2, _) in zip(KEYS, KEYS[1:]):
            if t1 <= x <= t2:
                dt = t2 - t1; s = (x - t1) / dt
                out.append((2*s**3 - 3*s**2 + 1) * v1 + (s**3 - 2*s**2 + s) * dt * m1
                           + (-2*s**3 + 3*s**2) * v2 + (s**3 - s**2) * dt * m2)
                break
    return np.array(out)


# =========================================================== 1. the problem
def slide_problem():
    """One claim: it abandoned most of what it started."""
    # the 81% run: outage, linear, no inertia, seed 2
    path = best_file("outage_linear_noinertia_s02")
    d = pd.read_csv(path)
    d = d[d.agent == "Utility"].sort_values("time_s").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9.0, 1.9))
    for i, r in d.iterrows():
        t0 = r.time_s
        t1 = d.time_s.iloc[i + 1] if i + 1 < len(d) else 300.0
        ax.add_patch(Rectangle((t0, 0), max(t1 - t0 - 0.4, 0.3), 1,
                               facecolor=ACCENT if r.to_action == "Eat" else ORANGE,
                               edgecolor="none"))
    ax.set_xlim(0, 300); ax.set_ylim(0, 1); ax.set_yticks([])
    ax.set_xticks(range(0, 301, 60))
    ax.set_xlabel("time  (seconds)", color="#7a7974")
    bare(ax)
    handles = [Rectangle((0, 0), 1, 1, facecolor=ACCENT),
               Rectangle((0, 0), 1, 1, facecolor=ORANGE)]
    ax.legend(handles, ["eating", "sleeping"], loc="upper left",
              bbox_to_anchor=(0, -0.45), ncol=2, fontsize=12)
    save(fig, "slide_problem.png")


# =========================================================== 2. the curve
def slide_curves():
    """One claim: it can be straight, or it can be bent."""
    xs = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(xs, 1 - xs, "-", color=GREY, linewidth=2.2, zorder=2)
    ax.plot(xs, curve(xs), "-", color=ACCENT, linewidth=3.2, zorder=3)
    ax.text(0.79, 1 - 0.79 + 0.06, "straight", color="#8f8d88", fontsize=13)
    ax.text(0.58, curve(np.array([0.58]))[0] - 0.10, "bent", color=ACCENT,
            fontsize=14, fontweight="bold")
    ax.set_xlabel("need      (1 = satisfied,  0 = empty)", color="#7a7974")
    ax.set_ylabel("desire to act", color="#7a7974")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.04)
    ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    bare(ax)
    save(fig, "slide_curves.png")


# =========================================================== 3. the overlap
def slide_curves_zoom():
    """One claim: at the point where decisions happen, the two are the same.

    An earlier version shaded the whole interquartile band, which showed the
    two lines apart at both ends and together only in the middle. That is the
    opposite of the claim. The claim is about one point, so draw one point.
    """
    rows = []
    for lab in ABLATION:
        for s_ in range(1, 9):
            p = best_file("%s_s%02d" % (lab, s_))
            if p:
                d = pd.read_csv(p)
                rows.append(d[d.agent == "Utility"][["hunger", "energy"]])
    vals = np.concatenate([r.values.ravel() for r in rows])
    med = float(np.median(vals))

    xs = np.linspace(0, 1, 400)
    yc, yl = curve(np.array([med]))[0], 1 - med

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(xs, 1 - xs, "-", color=PALE, linewidth=2.4, zorder=2)
    ax.plot(xs, curve(xs), "-", color=PALE, linewidth=2.4, zorder=2)

    ax.plot([med, med], [0, max(yc, yl) + 0.1], "-", color=GREY,
            linewidth=1.4, zorder=3)
    ax.text(med, max(yc, yl) + 0.14, "the typical decision", ha="center",
            color="#7a7974", fontsize=12.5)

    ax.plot([med], [yl], "o", color=ACCENT, markersize=15,
            markeredgecolor="white", markeredgewidth=2.5, zorder=5)
    ax.plot([med], [yc], "o", color=ACCENT, markersize=15,
            markeredgecolor="white", markeredgewidth=2.5, zorder=5)
    ax.annotate("%.2f apart" % abs(yc - yl), xy=(med, (yc + yl) / 2),
                xytext=(med + 0.22, (yc + yl) / 2 + 0.10), color=ACCENT,
                fontsize=15, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=ACCENT, linewidth=1.3))

    ax.set_xlabel("need", color="#7a7974")
    ax.set_ylabel("desire to act", color="#7a7974")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.2)
    ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    bare(ax)
    save(fig, "slide_curves_zoom.png")


# =========================================================== 4. the collapses
def slide_collapse(summary):
    """One claim: without inertia it collapses, with it never."""
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.0), sharey=True,
                             gridspec_kw=dict(wspace=0.42))
    for ax, scen, head in [(axes[0], "normal", "Nothing removed"),
                           (axes[1], "outage", "Resource removed")]:
        for row, cond in enumerate(ABLATION):
            d = summary[(summary.scenario == scen) & (summary.condition == cond) &
                        (summary.agent == "Utility")].sort_values("seed")
            y = len(ABLATION) - 1 - row
            for i, (_, r) in enumerate(d.iterrows()):
                if r.collapsed:
                    ax.plot(i, y, "o", color=RED, markersize=14,
                            markeredgecolor="white", markeredgewidth=2)
                else:
                    ax.plot(i, y, "o", color=FAINT, markersize=14,
                            markeredgecolor="none")
            n = int(d.collapsed.sum())
            ax.text(8.6, y, "%d" % n, va="center", fontsize=15,
                    color=RED if n else "#6f6e6a", fontweight="bold")
        ax.set_xlim(-1.0, 9.6); ax.set_ylim(-0.9, 3.8); ax.axis("off")
        ax.text(3.5, 3.5, head, fontsize=14, color=INK, ha="center")

    for row, cond in enumerate(ABLATION):
        axes[0].text(-1.6, len(ABLATION) - 1 - row, PRETTY[cond], va="center",
                     ha="right", fontsize=12.5, color="#5a5955")
    axes[0].plot(0.0, -0.7, "o", color=RED, markersize=11, markeredgecolor="white",
                 markeredgewidth=1.6)
    axes[0].text(0.5, -0.7, "collapsed", va="center", fontsize=12, color="#7a7974")
    save(fig, "slide_collapse.png")


# =========================================================== 5. the sweep
def slide_sweep(summary):
    """One claim: there is a best value."""
    pairs = [(0.0, "inertia000"), (0.1, "inertia010"), (0.2, "inertia020"),
             (0.3, "inertia030"), (0.5, "inertia050")]
    x = [b for b, _ in pairs]
    y = [summary[(summary.condition == c) & (summary.agent == "Utility")]
         .interrupt_rate.median() * 100 for _, c in pairs]

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(x, y, "-", color=PALE, linewidth=3.5, zorder=2, solid_capstyle="round")
    ax.plot(x, y, "o", color=GREY, markersize=9, markeredgecolor="white",
            markeredgewidth=2.5, zorder=3)
    i = int(np.argmin(y))
    ax.plot([x[i]], [y[i]], "o", color=ACCENT, markersize=20,
            markeredgecolor="white", markeredgewidth=3, zorder=5)
    ax.text(x[i], y[i] - 13, "%.1f" % x[i], ha="center", fontsize=22,
            fontweight="bold", color=ACCENT)

    ax.set_xlabel("commitment bonus", color="#7a7974")
    ax.set_ylabel("interruptions   (%)", color="#7a7974")
    ax.set_xlim(-0.04, 0.56); ax.set_ylim(0, 100)
    ax.set_xticks(x); ax.set_yticks([0, 50, 100])
    bare(ax)
    save(fig, "slide_sweep.png")


def main():
    summary = load_summary()
    print("slide figures:")
    slide_problem()
    slide_curves()
    slide_curves_zoom()
    slide_collapse(summary)
    slide_sweep(summary)


if __name__ == "__main__":
    main()
