import hashlib
import math

class HyperLogLog:
    def __init__(self, m):
        self.m = m
        self.buckets = [0] * m
        if self.m == 16:
            self.alpha = 0.673
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.m)

    def add(self, item):
        digest = hashlib.sha256(item.encode()).digest()
        hashed = int.from_bytes(digest, "big")
        bucket_n = hashed % self.m
        rest = hashed // self.m
        zeroes = 0
        while rest % 2 == 0 and rest > 0:
            zeroes += 1
            rest = rest // 2
        self.buckets[bucket_n] = max(self.buckets[bucket_n], zeroes + 1)

    def estimate(self):
        total = sum(2 ** -v for v in self.buckets)
        empty = self.buckets.count(0)
        raw = self.alpha * self.m**2 / total
        if raw <= 2.5 * self.m and empty > 0:
            return self.m * math.log(self.m/empty)
        else:
           return raw
