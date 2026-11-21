from dataclasses import dataclass
import random
import ipaddress
from ipaddress import IPv4Network
from itertools import accumulate

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
    #alpha
    circle_a: float = 1.0
    #multiplier
    circle_m: float = 3.0
    circle_cap: float = 0.85
    dunbars_n: int = 150
    #harvesters
    harv_speed: float = 25.0
    harv_cap: int = 100_000



@dataclass(frozen=True, slots=True)
class Sender:
    ip: str
    address: str
    circle: tuple


def simulate(config):
    rng = random.Random(config.seed)
    clock = 0.0
    message_id = 0
    senders = list()
    mbox_cum_weights = list(accumulate(zipf_weights(config.n_mailboxes, config.zipf_s)))
    for k in rng.sample(range(config.n_mailboxes), config.n_senders):
        circle_size = int(min(rng.paretovariate(config.circle_a) * config.circle_m, config.circle_cap * config.n_mailboxes))
        if circle_size <= config.dunbars_n:
            picked = set(rng.choices(range(config.n_mailboxes), cum_weights=mbox_cum_weights, k=circle_size))
        else:
            picked = rng.sample(range(config.n_mailboxes), k=circle_size)
        sender_circle = tuple(sender_address(m) for m in picked)
        senders.append(Sender(ip=sender_ip(k), address=sender_address(k), circle=sender_circle))
    cum_weights = list(accumulate(zipf_weights(config.n_senders, config.zipf_s)))
    harvester = Sender(
            ip=sender_ip(config.n_mailboxes),
            address=f'bot@harvest.example',
            circle=()
        )
    while True:
        clock += rng.expovariate(config.rate+config.harv_speed)
        if clock > config.duration:
            return
        if rng.random() < config.harv_speed / (config.rate + config.harv_speed):
            sender = harvester
            rec_n = rng.randrange(0, config.harv_cap)
            receiver = sender_address(rec_n)
            label = Label.HARVEST
        else:
            sender = rng.choices(senders, cum_weights=cum_weights)[0]
            receiver = rng.choice(sender.circle)
            label = Label.NORMAL
        message_id += 1
        yield Event(
            timestamp=clock,
            client_ip= sender.ip,
            mail_from= sender.address,
            rcpt_to=receiver,
            message_id=message_id,
            label=label
        )

def sender_ip(k):
    if k >= BENCHMARK_NETWORK.num_addresses or k < 0:
        raise ValueError(f"Sender index -{k}- doesn't fit in {BENCHMARK_NETWORK}")
    return str(BENCHMARK_NETWORK[k])

def sender_address(k):
    return f"user{k}@sender{k}.example"

def zipf_weights(n, s):
    weights = list()
    for k in range(n):
        weights.append(1 / (k + 1) ** s)
    return weights