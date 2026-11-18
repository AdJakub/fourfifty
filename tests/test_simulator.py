from itertools import islice

from fourfifty.simulator import SimConfig, simulate

import math

def test_same_seed_same_stream():
    config = SimConfig()
    first_run = list(islice(simulate(config), 100))
    second_run = list(islice(simulate(config), 100))
    assert first_run == second_run

def test_time_never_goes_back():
    config = SimConfig()
    events = list(islice(simulate(config), 1000))
    for earlier, later in zip(events, events[1:]):
        assert later.timestamp >= earlier.timestamp


def test_count_is_plausible():
    config = SimConfig(duration=600.0)
    expected = 30_000
    tolerance = math.sqrt(expected) * 3
    count = sum(1 for _ in simulate(config))
    assert abs(count - expected) <= tolerance
