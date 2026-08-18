import unittest

import pandas as pd

from src.pufguard.build_report import format_report


class ReportFormattingTests(unittest.TestCase):
    def test_report_contains_result_and_interpretation_limits(self):
        profiles = pd.DataFrame(
            [
                {
                    "dataset_id": "DX",
                    "short_name": "Fixture",
                    "rows": 10,
                    "columns": 3,
                    "singleton_rate_core": 0.1,
                    "singleton_rate_extended": 0.2,
                    "records_below_k5_rate_extended": 0.3,
                }
            ]
        )
        decisions = pd.DataFrame([{"dataset_id": "DX", "decision": "remediate_before_release"}])
        report = format_report(profiles, decisions)
        self.assertIn("DX: Fixture", report)
        self.assertIn("20.0%", report)
        self.assertIn("does not prove disclosure", report)


if __name__ == "__main__":
    unittest.main()
