from fourfifty.bloom import BloomFilter
from fourfifty.simulator import sender_address

def test_no_false_negatives():
    bloom = BloomFilter(m=10_000, k=7)

    for k in range(1000):
        bloom.add(sender_address(k))
    for k in range(1000):
        assert sender_address(k) in bloom

def test_false_positives():
    bloom = BloomFilter(m=10_000, k=7)

    for k in range(1000):
        bloom.add(sender_address(k))

    false_positives = 0
    for k in range(10_000, 20_000):
        if sender_address(k) in bloom:
            false_positives += 1
    share = false_positives / 10_000
    print(share)
    assert share < 0.02
