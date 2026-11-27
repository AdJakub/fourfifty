from collections import Counter

from fourfifty.baseline import valid_mboxes
from fourfifty.bloom import BloomFilter
from fourfifty.events import Label
from fourfifty.limiter import Decision, LimiterConfig, RateLimiter
from fourfifty.simulator import SimConfig, simulate

def score_seed(seed):
    sim_config = SimConfig(seed=seed)
    events = simulate(sim_config)
    bloom = BloomFilter(m=sim_config.n_mailboxes * 10, k=7)

    for address in valid_mboxes(sim_config):
        bloom.add(address)

    limiter = RateLimiter(LimiterConfig(),bloom)

    count = Counter()
    for event in events:
        check = limiter.check(event)
        count[(event.label, check)] += 1

    return count

for seed in (42, 7, 1234):
    count = score_seed(seed)
    print(f"\nSeed {seed}")
    for (label, decision), total in count.most_common():
        print(label.value, decision.value, total)