from fourfifty.simulator import SimConfig, simulate
from fourfifty.events import Label
from collections import Counter
from matplotlib import pyplot as plt
import os, sys
for p in os.environ.get("PYTHONPATH", "").split(";"):
    if p and p not in sys.path:
        sys.path.append(p)
config = SimConfig(duration=600.0)
events = list(simulate(config))
counts = Counter((event.label, int(event.timestamp / 10)) for event in events)
windows = range(int(config.duration/10))
all_ys = []

COLORS = {
    Label.NORMAL:   "#2a78d6", #BLUE,
    Label.RETRY:    "#eda100", #YELLOW,
    Label.PROMO:    "#1baf7a", #AQUA
    Label.COMPROMISED:  "#e34948", # RED
    Label.HARVEST:  "#eb6834", # ORANGE
    Label.BOT:  "#6250d6", #VIOLET
}

minutes = [w * 10 / 60 for w in windows]
shown = [label for label in Label if any(counts[(label, w)] for w in windows)]
all_ys = [[counts[(label, w)] for w in windows] for label in shown]

fig, ax = plt.subplots(figsize=(8, 4), dpi=200)
ax.stackplot(
    minutes, *all_ys,
    labels=[label.value for label in shown],
    colors=[COLORS[label] for label in shown],
    edgecolor="white", linewidth=0.8,
)

ax.set_title("Total mail traffic by type", loc="left", fontsize=12)
ax.set_xlabel("time (minutes)")
ax.set_ylabel("events per 10 s")
ax.set_xlim(0, config.duration / 60)
ax.set_ylim(bottom=0)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#e5e5e5", linewidth=0.6)
ax.set_axisbelow(True)

ax.legend(frameon=False, ncol=len(shown), loc="upper left", bbox_to_anchor=(0, -0.15))

fig.tight_layout()
fig.savefig("total.png", bbox_inches="tight")
plt.show