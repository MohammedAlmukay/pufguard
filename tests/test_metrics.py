import unittest

import pandas as pd

from src.pufguard.analyze_corpus import (
    available,
    entropy,
    equivalence_metrics,
    normalize_column,
    nonempty_rate,
    normalized_frame,
)


class EquivalenceMetricTests(unittest.TestCase):
    def test_normalization_and_availability(self):
        self.assertEqual(normalize_column("  Age\u00a0 group  "), "Age group")
        self.assertEqual(available(["Age", "Sex"], ["Sex", "Missing", "Age"]), ["Sex", "Age"])
        frame = normalized_frame(pd.DataFrame({" A\u00a0B ": [" Yes ", None]}))
        self.assertEqual(list(frame.columns), ["A B"])
        self.assertEqual(frame.loc[0, "A B"], "Yes")

    def test_singleton_and_below_k(self):
        frame = pd.DataFrame({
            "age": [1, 1, 2, 3, 3, 3],
            "sex": ["f", "f", "m", "f", "f", "f"],
            "sensitive": [0, 1, 1, 0, 0, 0],
        })
        result = equivalence_metrics(frame, ["age", "sex"], "sensitive")
        self.assertEqual(result["singleton_records"], 1)
        self.assertAlmostEqual(result["singleton_rate"], 1 / 6)
        self.assertEqual(result["minimum_k"], 1)
        self.assertEqual(result["homogeneous_sensitive_records_non_singleton"], 3)

    def test_empty_or_missing_qid_set(self):
        result = equivalence_metrics(pd.DataFrame({"x": [1, 2]}), ["absent"], None)
        self.assertEqual(result["qid_count"], 0)
        self.assertEqual(result["singleton_rate"], 0.0)
        self.assertEqual(result["minimum_k"], 0)

    def test_case_and_missing_values_are_grouped_deterministically(self):
        frame = pd.DataFrame(
            {
                "city": ["Riyadh", " riyadh ", None, None],
                "sensitive": ["A", "A", "B", "C"],
            }
        )
        result = equivalence_metrics(frame, ["city"], "sensitive")
        self.assertEqual(result["equivalence_classes"], 2)
        self.assertEqual(result["minimum_k"], 2)
        self.assertEqual(result["singleton_records"], 0)
        self.assertEqual(result["homogeneous_sensitive_records_non_singleton"], 2)

    def test_entropy_and_nonempty_rate(self):
        self.assertAlmostEqual(entropy(pd.Series(["a", "a", "b", "b"])), 1.0)
        self.assertAlmostEqual(nonempty_rate(pd.Series(["x", " ", None, "y"])), 2 / 3)


if __name__ == "__main__":
    unittest.main()
