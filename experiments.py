import random
import statistics
from itertools import accumulate
from unittest import expectedFailure

from fourfifty.events import Label, Event
from fourfifty.simulator import simulate, SimConfig, zipf_weights
import sys

from collections import Counter
# event = Event(timestamp=20.20, client_ip='203.0.113.7', mail_from='alice@example.com', rcpt_to='emily@example.com',
#               message_id=1, label=Label.NORMAL)
# dict_event = {
#     'timestamp': 20.20,
#     'client_ip': '203.0.113.7',
#     'mail_from': 'alice@example.com',
#     'rcpt_to': 'emily@example.com',
#     'message_id': 1,
#     'label': Label.NORMAL}
# print(event)
# print(sys.getsizeof(event))
# print(sys.getsizeof(dict_event))
# # print(vars(event))
# ###################################
# cnt = 0
# for simulation in simulate(SimConfig()):
#     cnt += 1
# print(cnt)
config = SimConfig(duration=600.0)
# counts = Counter(event.mail_from for event in simulate(config))
# print (len(counts))
# total = sum(counts.values())
# print(total)
# top_100 = counts.most_common(100)
# top_share =  sum(count for _, count in top_100) / total
#
# weights = zipf_weights(config.n_senders, config.zipf_s)
# expected_share = sum(weights[:100]) / sum(weights)
#
# print(top_share, expected_share)
# cap = 0.85 * config.n_mailboxes
# rng = random.Random(config.seed)
# # sizes = [min(rng.paretovariate(1)*3, cap) for _ in range (10_000)]
# # print(sum(1 for s in sizes if s == cap))
# # print(min(sizes), statistics.median(sizes), max(sizes))
#
# pool = range(config.n_mailboxes)
# cum = list(accumulate(zipf_weights(config.n_mailboxes, config.zipf_s)))
#
# for size in [3, 10, 100, 1_000, 17_000]:
#     picked = rng.choices(pool, cum_weights=cum, k=size)
#     print(size, len(set(picked)))
labels = Counter(event.label for event in simulate(config))

print(sum(labels.values()))
print(labels[Label.RETRY])