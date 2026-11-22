import dataclasses
from dataclasses import dataclass
import random
import ipaddress
from ipaddress import IPv4Network
from itertools import accumulate
import heapq
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
    #retries
    retry_chance: float = 0.03
    retry_delay: float = 300.0
    #newsletters
    subscriber_count_big: int = 8_000
    campaign_start: int = 180
    campaign_rate: float = 50.0



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
    promo_picked = rng.sample(range(config.n_mailboxes), k=config.subscriber_count_big)
    subscriber_circle = tuple(sender_address(m) for m in promo_picked)
    harvester = Sender(
            ip=sender_ip(config.n_mailboxes),
            address='bot@harvest.example',
            circle=()
        )
    promo = Sender(
        ip=sender_ip(config.n_mailboxes+1),
        address='news@letter.example',
        circle = subscriber_circle
    )
    scheduled = []
    for i, subscriber in enumerate(subscriber_circle):
        message_id += 1
        promo_event = Event(
            timestamp=config.campaign_start + i / config.campaign_rate,
            client_ip=promo.ip,
            mail_from=promo.address,
            rcpt_to=subscriber,
            label=Label.PROMO,
            message_id=message_id
        )

        heapq.heappush(scheduled, (promo_event.timestamp, promo_event))
    while True:
        clock += rng.expovariate(config.rate+config.harv_speed)
        if clock > config.duration:
            return
        while scheduled and scheduled[0][0] <= clock:
            due_time, event = heapq.heappop(scheduled)
            yield event
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
        current_event =  Event(
            timestamp=clock,
            client_ip= sender.ip,
            mail_from= sender.address,
            rcpt_to=receiver,
            message_id=message_id,
            label=label
        )
        yield current_event
        if current_event.label == Label.NORMAL and rng.random() < config.retry_chance:
            retry_event = dataclasses.replace(current_event, timestamp=clock+config.retry_delay, label=Label.RETRY)
            heapq.heappush(scheduled, (retry_event.timestamp, retry_event))

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