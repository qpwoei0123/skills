import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from score import main


class ScoreTest(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(list(args))
        return status, stdout.getvalue(), stderr.getvalue()

    def test_valid_completeness_scores_are_summed(self):
        status, stdout, stderr = self.run_main("completeness", "16", "14", "24", "8", "15")

        self.assertEqual(status, 0)
        self.assertIn("77%", stdout)
        self.assertEqual(stderr, "")

    def test_score_count_must_match_mode(self):
        status, _, stderr = self.run_main("match", "20", "20", "20", "20", "10")

        self.assertEqual(status, 2)
        self.assertIn("6개", stderr)

    def test_each_score_must_stay_within_its_cap(self):
        cases = [
            (("completeness", "21", "20", "30", "15", "15"), "샘플 양"),
            (("match", "20", "20", "20", "20", "10", "-1"), "자연스러움"),
        ]
        for args, item_name in cases:
            with self.subTest(args=args):
                status, _, stderr = self.run_main(*args)
                self.assertEqual(status, 2)
                self.assertIn(item_name, stderr)


if __name__ == "__main__":
    unittest.main()
