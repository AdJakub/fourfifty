import hashlib

class BloomFilter:
    def __init__(self, m, k):
        self.m = m
        self.k = k
        self.bits = bytearray((m + 7) // 8)

    def _positions(self, item):
        digest = hashlib.sha256(item.encode()).digest()
        h1 = int.from_bytes(digest[:16], "big")
        h2 = int.from_bytes(digest[16:], "big")
        for i in range(self.k):
            yield (h1+ i * h2) % self.m

    def add(self, item):
        for pos in self._positions(item):
            byte = pos // 8
            bit = pos % 8
            self.bits[byte] = self.bits[byte] | (1 << bit)

    def __contains__(self, item):
        for pos in self._positions(item):
            byte = pos // 8
            bit = pos % 8
            if (self.bits[byte] & (1 << bit)) == 0:
                return False
        return True