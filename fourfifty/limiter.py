from collections import Counter, defaultdict
from enum import Enum
from dataclasses import dataclass

from fourfifty.countmin import CountMinSketch
from fourfifty.hyperloglog import HyperLogLog
class Decision(Enum):
    ACCEPT = "250 OK"
    TEMPFAIL = "450 TRY AGAIN LATER"

@dataclass(frozen=True)
class LimiterConfig:
    window_len: float = 60.0
    sender_buckets: int = 64
    #COUNT_MIN
    count_min_w: int = 1_000
    count_min_d: int = 4
    # RULE 1
    share_thresh: float = 0.10
    min_emails_for_share: int = 30
    # RULE 2
    max_emails_per_window: int = 5_000
    # RULE 3
    max_recipients_per_window: int = 3_500

class RateLimiter:
    def __init__(self, config, bloom):
        self.config = config
        self.bloom = bloom
        self.window = -1
        self._new_window()

    def _new_window(self):
        self.counts = CountMinSketch(w=self.config.count_min_w, d=self.config.count_min_d)
        self.misses = Counter()
        self.hlls = defaultdict(lambda: HyperLogLog(self.config.sender_buckets))
        self.penalty_box = set()

    def check(self, event):
        email_window = int(event.timestamp // self.config.window_len)
        if email_window != self.window:
            self._new_window()
            self.window = email_window
        for key in event.mail_from, event.client_ip:
            self.counts.add(key)
            if event.rcpt_to not in self.bloom:
                self.misses[key] +=1
            self.hlls[key].add(event.rcpt_to)
            emails_sent = self.counts.estimate(key)
            key_misses = self.misses[key]
            unique_recipients = self.hlls[key].estimate()
            if emails_sent >= self.config.min_emails_for_share and key_misses / emails_sent > self.config.share_thresh:
                self.penalty_box.add(key)
            if emails_sent > self.config.max_emails_per_window:
                self.penalty_box.add(key)
            if unique_recipients > self.config.max_recipients_per_window:
                self.penalty_box.add(key)
        if event.mail_from in self.penalty_box or event.client_ip in self.penalty_box:
            return Decision.TEMPFAIL
        else:
            return Decision.ACCEPT



