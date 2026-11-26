import pytest

from fourfifty.hyperloglog import HyperLogLog
from fourfifty.simulator import sender_address

def test_empty_is_zero():
    h = HyperLogLog(16)
    assert h.estimate() == 0

def test_small_count_is_close():
    h = HyperLogLog(64)
    for k in range(5):
        h.add(sender_address(k))
    assert h.estimate() == pytest.approx(5, abs=1)

def test_large_count_within_expected_error():
    h = HyperLogLog(1024)
    for k in range(10_000):
        h.add(sender_address(k))
    assert h.estimate() == pytest.approx(10_000, rel=0.0975)

def test_duplicates_dont_count():
    h = HyperLogLog(64)
    for _ in range(10_000):
        h.add(sender_address(420))
    h2 = HyperLogLog(64)
    h2.add(sender_address(420))
    assert h.buckets == h2.buckets
