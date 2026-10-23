import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from algorithms import PriorityQueue, count_by, merge_sort
from classifier import make_result
from config import bin_for_class, bin_priority, BINS, CLASS_TO_BIN
from prepare_dataset import split_dataset


class TestAlgorithms(unittest.TestCase):
    def test_merge_sort_matches_sorted_and_is_stable(self):
        data = [(3, "a"), (1, "b"), (3, "c"), (2, "d"), (1, "e")]
        self.assertEqual(merge_sort(data, key=lambda x: x[0]), sorted(data, key=lambda x: x[0]))

    def test_merge_sort_edge_cases(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([5]), [5])
        orig = [3, 2, 1]
        merge_sort(orig)
        self.assertEqual(orig, [3, 2, 1])  # input tidak berubah

    def test_count_by(self):
        c = count_by([{"k": "a"}, {"k": "b"}, {"k": "a"}], "k")
        self.assertEqual(c["a"], 2); self.assertEqual(c["b"], 1)

    def test_priority_queue_order_and_ties(self):
        pq = PriorityQueue()
        for item, p in [("x", 3), ("y", 1), ("z", 3), ("w", 1)]:
            pq.push(item, p)
        self.assertEqual(pq.to_list(), ["y", "w", "x", "z"])
        self.assertEqual(len(pq), 4)  # to_list tidak mengosongkan
        self.assertEqual([pq.pop() for _ in range(4)], ["y", "w", "x", "z"])
        with self.assertRaises(IndexError):
            pq.pop()


class TestRules(unittest.TestCase):
    def test_mapping(self):
        self.assertEqual(bin_for_class("battery"), "b3")
        self.assertEqual(bin_for_class("Brown_Glass"), "daur_ulang")
        self.assertEqual(bin_for_class("biological"), "organik")
        self.assertEqual(bin_for_class("kelas-asing"), "verifikasi")

    def test_all_mapped_bins_exist(self):
        for b in CLASS_TO_BIN.values():
            self.assertIn(b, BINS)

    def test_priority_b3_before_organik_and_verifikasi_first(self):
        self.assertLess(bin_priority("verifikasi"), bin_priority("b3"))
        self.assertLess(bin_priority("b3"), bin_priority("organik"))


class TestMakeResult(unittest.TestCase):
    def test_confident(self):
        r = make_result([("plastic", 0.2), ("battery", 0.7), ("paper", 0.1)], 0.6)
        self.assertEqual(r["bin_key"], "b3"); self.assertFalse(r["low_confidence"])
        self.assertEqual(r["top3"][0][0], "Baterai")

    def test_low_confidence_goes_to_verification(self):
        r = make_result([("plastic", 0.45), ("paper", 0.3)], 0.6)
        self.assertEqual(r["bin_key"], "verifikasi"); self.assertTrue(r["low_confidence"])

    def test_empty(self):
        self.assertEqual(make_result([])["bin_key"], "verifikasi")


class TestPrepareDataset(unittest.TestCase):
    def test_split_counts_and_no_overlap(self):
        with tempfile.TemporaryDirectory() as t:
            src, dst = Path(t, "src"), Path(t, "dst")
            for cls in ("a", "b"):
                (src / cls).mkdir(parents=True)
                for i in range(20):
                    Image.new("RGB", (8, 8)).save(src / cls / f"{i}.jpg")
            (src / "a" / "catatan.txt").write_text("bukan gambar")
            summary = split_dataset(src, dst)
            self.assertEqual(summary["a"], {"train": 14, "val": 3, "test": 3})
            names = [set(p.name for p in (dst / s / "a").iterdir()) for s in ("train", "val", "test")]
            self.assertEqual(sum(len(n) for n in names), 20)
            self.assertFalse(names[0] & names[1] or names[0] & names[2] or names[1] & names[2])


class TestComponents(unittest.TestCase):
    def setUp(self):
        from classifier import make_result
        self.res = make_result([("plastic", 0.92), ("white-glass", 0.05), ("paper", 0.02)], 0.6)
        self.res.update(file="a<b>.jpg")
        low = make_result([("plastic", 0.4)], 0.6); low.update(file="x.jpg")
        self.rows = [self.res, low]

    def test_no_blank_lines_or_indent(self):
        import components as c
        out = c.result_html(self.res, self.rows, "", 0.6) + c.empty_html()
        self.assertNotIn("\n", out)

    def test_escape_and_bins(self):
        import components as c
        h = c.queue_html(self.rows)
        self.assertIn("a&lt;b&gt;.jpg", h)
        self.assertLess(h.index("Perlu Verifikasi"), h.index("Anorganik Daur Ulang"))
        self.assertEqual(len(c.BIN_ORDER), 4)

    def test_ring_dash(self):
        import components as c
        self.assertIn('stroke-dasharray="462.4 503.7"', c.ring_svg(0.92, "#1FA05A", 0.6))


if __name__ == "__main__":
    unittest.main()
