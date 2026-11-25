import hashlib


class CountMinSketch:
    def __init__(self, w, d):
        self.w = w
        self.d = d
        self.table = [[0] * w for _ in range (d)]

    def _positions(self, item):
        digest = hashlib.sha256(item.encode()).digest()
        h1 = int.from_bytes(digest[:16], "big")
        h2 = int.from_bytes(digest[16:], "big")
        for i in range(self.d):
            yield (h1 + i * h2) % self.w

    def add(self, item):
        for row, pos in enumerate(self._positions(item)):
            self.table[row][pos] += 1

    def estimate(self, item):
        counters = list()
        for row, pos in enumerate(self._positions(item)):
            counters.append(self.table[row][pos])
        return min(counters)
