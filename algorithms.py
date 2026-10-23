"""Algoritma inti: Merge Sort, penghitungan Counter, dan Priority Queue (heap)."""
import heapq
from collections import Counter
from itertools import count


def merge_sort(items, key=lambda x: x):
    """Merge Sort stabil. Waktu O(n log n), memori tambahan O(n)."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    return _merge(merge_sort(items[:mid], key), merge_sort(items[mid:], key), key)


def _merge(left, right, key):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):  # <= menjaga kestabilan
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


def count_by(items, field):
    """Rekap jumlah per nilai field (Counter, rata-rata O(1) per update)."""
    return Counter(item[field] for item in items)


class PriorityQueue:
    """Min-heap; angka prioritas kecil keluar lebih dulu, seri -> urutan masuk."""

    def __init__(self):
        self._heap, self._seq = [], count()

    def push(self, item, priority):
        heapq.heappush(self._heap, (priority, next(self._seq), item))  # O(log n)

    def pop(self):
        if not self._heap:
            raise IndexError("antrean kosong")
        return heapq.heappop(self._heap)[2]  # O(log n)

    def peek(self):
        if not self._heap:
            raise IndexError("antrean kosong")
        return self._heap[0][2]

    def __len__(self):
        return len(self._heap)

    def to_list(self):
        """Isi antrean berurutan tanpa mengubah antrean asli."""
        return [e[2] for e in sorted(self._heap)]
