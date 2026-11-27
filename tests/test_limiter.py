
from fourfifty.events import Event, Label
from fourfifty.bloom import BloomFilter
from fourfifty.limiter import RateLimiter, LimiterConfig, Decision
from fourfifty.simulator import sender_address

def make_event(sender, rcpt, timestamp=0.0, ip="198.18.0.0"):
    return Event(timestamp=timestamp, client_ip=ip, mail_from=sender, rcpt_to=rcpt, message_id=0, label=Label.NORMAL)

def make_bloom():
    bloom = BloomFilter(m=1_000, k=3)
    for address in ["a@x.example", "b@x.example", "c@x.example"]:
        bloom.add(address)
    return bloom

def test_quiet_sender_is_accepted():
    limiter = RateLimiter(LimiterConfig(), make_bloom())
    addresses = ["a@x.example", "b@x.example", "c@x.example"]
    timestamp = 5.0
    for i in range(5):
        timestamp += 10
        event = make_event("quiet@x.example", rcpt=addresses[i%len(addresses)], timestamp=timestamp)
        assert limiter.check(event) == Decision.ACCEPT

def test_volume_limit():
    limiter = RateLimiter(LimiterConfig(max_emails_per_window=3), make_bloom())
    addresses = ["a@x.example", "b@x.example", "c@x.example"]
    timestamp = 5.0
    for i in range(4):
        timestamp += 10
        event = make_event("loud@x.example", rcpt=addresses[i%len(addresses)], timestamp=timestamp)
        if i < 3:
            assert limiter.check(event) == Decision.ACCEPT
        if i == 3:
            assert limiter.check(event) == Decision.TEMPFAIL

def test_window_rollover():
    limiter = RateLimiter(LimiterConfig(max_emails_per_window=1), make_bloom())
    addresses = ["a@x.example", "b@x.example"]
    timestamp = 59.7
    for i in range(2):
        timestamp += 0.2
        event = make_event("window@x.example", rcpt=addresses[i%len(addresses)], timestamp=timestamp)
        assert limiter.check(event) == Decision.ACCEPT

def test_bloom_miss():
    accepted = [0, 1, 2]
    rejected = [3]
    limiter = RateLimiter(LimiterConfig(share_thresh=0.25, min_emails_for_share=4), make_bloom())
    addresses = ["a@x.example", "b@x.example", "admin@x.example", "hr@x.example"]
    for i in range(4):
        event =  make_event("window@x.example", rcpt=addresses[i%len(addresses)])
        check = limiter.check(event)

        if i in accepted:
            assert check == Decision.ACCEPT
        if i in rejected:
            assert check == Decision.TEMPFAIL

def test_min_sample():
    limiter = RateLimiter(LimiterConfig(min_emails_for_share=4), make_bloom())
    addresses = ["admin@x.example", "hr@x.example"]
    for i in range(3):
        event = make_event("window@x.example", rcpt=addresses[i % len(addresses)])
        check = limiter.check(event)
        assert check == Decision.ACCEPT

def test_too_many_uniq_recipients_are_blocked():
    bloom2 = BloomFilter(m=1_000, k=3)
    for n in range(4_000):
        bloom2.add(sender_address(n))
    limiter = RateLimiter(LimiterConfig(max_recipients_per_window=350), bloom2)
    for n in range(4_000):
        event = make_event(sender="hll@x.example", rcpt=sender_address(n))
        check = limiter.check(event)
        if n <= 100:
            assert check == Decision.ACCEPT
    assert check == Decision.TEMPFAIL