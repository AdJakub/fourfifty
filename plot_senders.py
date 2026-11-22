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
counts = Counter(event.mail_from for event in events)
ranked = counts.most_common()
for i, (sender, count) in enumerate(ranked):
    if sender == "bot@harvest.example":
        harv_rank, harv_count = i+1, count
    elif sender == "news@letter.example":
        news_rank, news_count = i+1, count
    else:
        continue
xs = list(range(1, len(ranked) + 1))
ys = [n for sender, n in ranked]

fig, ax = plt.subplots(figsize=(8, 4), dpi=200)
ax.scatter(xs, ys, s=4)
ax.scatter([harv_rank], [harv_count], s=40, color="#eb6834", zorder=3)
ax.scatter([news_rank], [news_count], s=40, color="#1baf7a", zorder=3)

ax.set_yscale("log")
ax.set_xscale("log")
ax.set_title("Emails per sender", loc="left", fontsize=12)
ax.set_xlabel("sender rank")
ax.set_ylabel("emails sent")

ax.spines[["top", "right"]].set_visible(False)
ax.grid(color="#e5e5e5", linewidth=0.6)
ax.set_axisbelow(True)

fig.tight_layout()

ax.annotate("harvester", xy=(harv_rank, harv_count), xytext=(harv_rank * 1.5, harv_count))
ax.annotate("promo", xy=(news_rank, news_count), xytext=(news_rank * 1.5, news_count))
fig.savefig("sender.png", bbox_inches="tight")
plt.show()