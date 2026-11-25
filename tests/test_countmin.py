from fourfifty.events import Event
from fourfifty.simulator import simulate, SimConfig
from fourfifty.countmin import CountMinSketch
from fourfifty.baseline import emails_per_sender
def test_never_underestimates():
    config = SimConfig(seed=3, duration=600.0)
    events = list(simulate(config))
    w = 500
    d = 4
    countmin = CountMinSketch(w, d)
    for event in events:
        countmin.add(event.mail_from)
    answer_k = emails_per_sender(events)
    for sender, count in answer_k.items():
        sender_estimate = countmin.estimate(sender)
        assert sender_estimate >= count

def test_overestimates_are_small():
    config = SimConfig(seed=3, duration=600.0)
    events = list(simulate(config))
    w = 500
    d = 4
    countmin = CountMinSketch(w, d)
    for event in events:
        countmin.add(event.mail_from)
    answer_k = emails_per_sender(events)
    overestimates = list()
    for sender, count in answer_k.items():
        count_estimate = countmin.estimate(sender)
        estimate_true_count = count_estimate - count
        overestimates.append(estimate_true_count)
    average_result = sum(overestimates) / len(overestimates)
    assert average_result < 100