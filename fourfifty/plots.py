from collections import Counter

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

from fourfifty.events import Label
from fourfifty.baseline import recipients_per_sender

COLORS = {
    Label.NORMAL: "#2a78d6",  # BLUE,
    Label.RETRY: "#eda100",  # YELLOW,
    Label.PROMO: "#1baf7a",  # AQUA
    Label.COMPROMISED: "#e34948",  # RED
    Label.HARVEST: "#eb6834",  # ORANGE
    Label.BOT: "#6250d6",  # VIOLET
}

def plot_total(events, config, path):
    counts = Counter((event.label, int(event.timestamp / 10)) for event in events)
    windows = range(int(config.duration / 10))



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
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

def plot_recipients(events, path):
    counts = recipients_per_sender(events)
    ranked = counts.most_common()
    harv_rank = news_rank = None
    for i, (sender, count) in enumerate(ranked):
        if sender == "bot@harvest.example":
            harv_rank, harv_count = i + 1, count
        elif sender == "news@letter.example":
            news_rank, news_count = i + 1, count
        else:
            continue
    xs = list(range(1, len(ranked) + 1))
    ys = [n for sender, n in ranked]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=200)
    ax.scatter(xs, ys, s=4)
    if harv_rank:
        ax.scatter([harv_rank], [harv_count], s=40, color="#eb6834", zorder=3)
        ax.annotate("harvester", xy=(harv_rank, harv_count), xytext=(harv_rank * 1.5, harv_count))

    if news_rank:
        ax.scatter([news_rank], [news_count], s=40, color="#1baf7a", zorder=3)
        ax.annotate("promo", xy=(news_rank, news_count), xytext=(news_rank * 1.5, news_count))

    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_title("Recipients per sender", loc="left", fontsize=12)
    ax.set_xlabel("sender rank")
    ax.set_ylabel("different recipients")

    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#e5e5e5", linewidth=0.6)
    ax.set_axisbelow(True)

    fig.tight_layout()


    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)