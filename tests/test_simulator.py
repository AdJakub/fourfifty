from ipaddress import IPv4Address
from itertools import islice

import pytest

from fourfifty.simulator import SimConfig, simulate, sender_ip

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

def test_ip():
    assert sender_ip(0) ==  '198.18.0.0'
    assert sender_ip(256) == '198.18.1.0'
    assert sender_ip(255) == '198.18.0.255'
    assert sender_ip(65_536) == '198.19.0.0'


def test_ip_rejection_1():
    with pytest.raises(ValueError):
        sender_ip(131_072)

def test_ip_rejection_2():
    with pytest.raises(ValueError):
        sender_ip(-1)