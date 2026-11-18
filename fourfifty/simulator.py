from dataclasses import dataclass
import random
import ipaddress
from ipaddress import IPv4Network

from fourfifty.events import Event, Label

BENCHMARK_NETWORK = IPv4Network('198.18.0.0/15')
@dataclass(frozen=True)
class SimConfig:
    seed: int = 42
    duration: float = 3600.0
    rate: float = 50.0
    n_senders: int = 10_000
    zipf_s: float = 1.0
    n_mailboxes: int = 20_000

def simulate(config):
    rng = random.Random(config.seed)
    clock = 0.0
    message_id = 0

    while True:
        clock += rng.expovariate(config.rate)
        if clock > config.duration:
            return
        message_id += 1
        yield Event(
            timestamp=clock,
            client_ip='203.0.113.7',
            mail_from='alice@example.com',
            rcpt_to='emily@example.com',
            message_id=message_id,
            label=Label.NORMAL
        )

def sender_ip(k):
    if k >= BENCHMARK_NETWORK.num_addresses or k < 0:
        raise ValueError(f"Sender index -{k}- doesn't fit in {BENCHMARK_NETWORK}")
    return str(BENCHMARK_NETWORK[k])

