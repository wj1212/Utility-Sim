"""The scoring equation as a slide-ready PNG, transparent background."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = r"C:\Users\jiang\OneDrive\Desktop\Utility-Sim\Figures"
plt.rcParams.update({
    "mathtext.fontset": "dejavusans",
    "font.family": ["Segoe UI", "Arial", "DejaVu Sans"],
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.25,
    "savefig.transparent": True,
})

INK = "#0b0b0b"
MUTED = "#6b6a66"
BLUE = "#2a78d6"
ORANGE = "#eb6834"

fig = plt.figure(figsize=(9.0, 3.0))

# the equation itself
fig.text(0.5, 0.70,
         r"$\mathrm{score}(a)\;=\;f(\mathrm{need}_a)\;+\;\beta\cdot\mathbf{1}[\,a"
         r"\ \mathrm{is\ the\ current\ action}\,]$",
         ha="center", va="center", fontsize=27, color=INK)

# what each symbol is
fig.text(0.5, 0.36, r"$f$      the response curve",
         ha="center", va="center", fontsize=17, color=BLUE)
fig.text(0.5, 0.21, r"$\beta$      the commitment bonus",
         ha="center", va="center", fontsize=17, color=ORANGE)
fig.text(0.5, 0.045, "pick the highest score, if it clears the activation threshold",
         ha="center", va="center", fontsize=14, color=MUTED)

os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "fig_14_equation.png")
fig.savefig(p)
print("wrote", p)
