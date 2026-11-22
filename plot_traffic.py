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
for label in Label:
    ys = [counts[(label, w)] for w in windows]
    plt.plot(windows, ys, label=label.value)
    plt.legend()
    plt.xlabel("time(10s)")
    plt.ylabel("Mail events")
    plt.savefig("traffic.png")
