from ipaddress import IPv4Address
from itertools import islice
from collections import Counter

import pytest

from fourfifty.simulator import SimConfig, simulate, sender_ip, sender_address, zipf_weights
from fourfifty.events import Label
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
    expected = (config.rate + config.harv_speed) * config.duration + config.retry_chance * config.rate * (config.duration - config.retry_delay)
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

def test_email_address_generation():
    assert sender_address(0) == 'user0@sender0.example'
    assert sender_address(9_999) == 'user9999@sender9999.example'

def test_zipf_weights():
    assert zipf_weights(3, 1.0) == pytest.approx([1.0, 0.5, 1/3])

def test_simulator_share():
    config = SimConfig(seed=3, duration=600.0)
    counts = Counter(event.mail_from for event in simulate(config) if event.label == Label.NORMAL)
    total = sum(counts.values())
    top_100 = counts.most_common(100)
    top_share = sum(count for _, count in top_100) / total
    weights = zipf_weights(config.n_senders, config.zipf_s)
    expected_share = sum(weights[:100]) / sum(weights)
    assert top_share == pytest.approx(expected_share, abs=0.02)

def test_how_many_over_10k_k():
    config = SimConfig(seed=3, duration=600.0)
    counts = Counter(event.mail_from for event in simulate(config))
    addresses = set()
    for k in range (10_000, config.n_mailboxes):
        addresses.add(sender_address(k))
    overlap = 0
    for mail in counts:
        if mail in addresses:
            overlap += 1
    assert overlap > 0

def test_if_receiver_is_random():
    config = SimConfig(seed=3, duration=600.0)
    counts = Counter(event.rcpt_to for event in simulate(config))
    assert len(counts) > 1_000

def test_harvester_share():
    config = SimConfig(seed=3, duration=600.0)
    counts_harv = Counter(event.mail_from for event in simulate(config) if event.label == Label.HARVEST)
    expected = config.harv_speed * config.duration
    tolerance = math.sqrt(expected) * 3
    assert sum(counts_harv.values()) == pytest.approx(expected, abs=tolerance)

def test_harvester_success_rate():
    config = SimConfig(seed=3, duration=600.0)
    counts = [event.rcpt_to for event in simulate(config) if event.label == Label.HARVEST]
    addresses = set()
    for k in range(config.n_mailboxes):
        addresses.add(sender_address(k))
    overlap = 0
    for mail in counts:
        if mail in addresses:
            overlap += 1
    expected = (config.n_mailboxes/config.harv_cap)
    assert overlap / len(counts) == pytest.approx(expected, abs=0.02)