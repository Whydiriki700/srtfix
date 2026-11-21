import sys, unittest
sys.path.insert(0, ".")
from srtfix.core import format_ms, parse_srt, render_srt, repair, to_ms

SAMPLE = """1
00:00:01,000 --> 00:00:03,500
Halo dunia.

2
00:00:03,000 --> 00:00:05,000
Cue ini tumpang tindih.

3
00:00:06,000 --> 00:00:07,000

4
00:00:08,000 --> 00:00:09,000
Terakhir.
"""

class TimeTests(unittest.TestCase):
    def test_roundtrip(self):
        self.assertEqual(to_ms(1, 2, 3, 400), 3723400)
        self.assertEqual(format_ms(3723400), "01:02:03,400")
    def test_negative_clamped(self):
        self.assertEqual(format_ms(-5), "00:00:00,000")

class ParseTests(unittest.TestCase):
    def test_parse(self):
        cues, skipped = parse_srt(SAMPLE)
        self.assertEqual(len(cues), 4)
        self.assertEqual(skipped, 0)
        self.assertEqual(cues[0]["start"], 1000)

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.cues, _ = parse_srt(SAMPLE)
    def test_overlap_and_empty(self):
        fixed, report = repair(self.cues)
        self.assertEqual(len(fixed), 3)
        self.assertEqual(report["overlaps_fixed"], 1)
        self.assertEqual(report["dropped_empty"], 1)
        self.assertEqual(fixed[0]["end"], fixed[1]["start"])
    def test_shift(self):
        fixed, _ = repair(self.cues, shift_ms=500)
        self.assertEqual(fixed[0]["start"], 1500)
    def test_negative_shift_clamps(self):
        fixed, report = repair(self.cues, shift_ms=-2000)
        self.assertEqual(fixed[0]["start"], 0)
        self.assertEqual(report["clamped_negative"], 1)
    def test_scale(self):
        fixed, _ = repair(self.cues, scale=2.0)
        self.assertEqual(fixed[0]["start"], 2000)
    def test_render_renumbers(self):
        fixed, _ = repair(self.cues)
        out = render_srt(fixed)
        self.assertTrue(out.startswith("1\n00:00:01,000 --> 00:00:03,000"))
        self.assertIn("\n3\n00:00:08,000", out)

if __name__ == "__main__":
    unittest.main()
