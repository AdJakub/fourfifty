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
config = SimConfig()
counts = Counter(event.mail_from for event in simulate(config))
total = sum(counts.values())
top_100 = counts.most_common(100)
top_share =  sum(count for _, count in top_100) / total

weights = zipf_weights(config.sender_n, config.zipf_s)
expected_share = sum(weights[:100]) / sum(weights)

print(top_share, expected_share)
