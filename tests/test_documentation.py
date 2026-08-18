import json
import re
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DocumentationIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dictionary = pd.read_csv(PROJECT_ROOT / "data/metadata/data_dictionary.csv")
        cls.manifest = pd.read_csv(PROJECT_ROOT / "data/metadata/integrity_manifest.csv")

    def test_all_deposited_variables_have_documentation(self):
        self.assertEqual(len(self.dictionary), 218)
        self.assertFalse(self.dictionary["semantic_description"].isna().any())
        self.assertFalse(self.dictionary["semantic_status"].isna().any())
        self.assertEqual(set(self.dictionary.dataset_id), {"D1", "D2", "D3", "D4", "D5"})

    def test_sensitive_contents_are_suppressed(self):
        protected = self.dictionary[
            self.dictionary.privacy_role.str.contains("free_text|structural_identifier", regex=True)
        ]
        self.assertTrue(protected.observed_values_summary.str.contains("contents suppressed").all())

    def test_manifest_covers_raw_files_and_hashes(self):
        raw_files = [path for path in (PROJECT_ROOT / "data/raw").rglob("*") if path.is_file()]
        self.assertEqual(len(self.manifest), len(raw_files))
        self.assertTrue(self.manifest.sha256.map(lambda value: bool(re.fullmatch(r"[0-9a-f]{64}", value))).all())

    def test_configured_columns_are_documented(self):
        configs = json.loads((PROJECT_ROOT / "configs/datasets.json").read_text(encoding="utf-8"))
        documented = {
            dataset_id: set(group.variable_name)
            for dataset_id, group in self.dictionary.groupby("dataset_id")
        }
        for dataset_id, cfg in configs.items():
            configured = set(cfg["structural_identifiers"] + cfg["free_text"] + cfg["sensitive"] + cfg["extended_qids"])
            self.assertTrue(configured.issubset(documented[dataset_id]))

    def test_verified_derived_fields_match_source_rows(self):
        d1 = pd.read_excel(PROJECT_ROOT / "data/raw/D1_BMI_Depression/Data.xlsx")
        q_columns = [column for column in d1 if str(column).strip().startswith("Q ")]
        self.assertTrue((d1[q_columns].sum(axis=1) == d1["Depression score"]).all())

        d3 = pd.read_excel(PROJECT_ROOT / "data/raw/D3_Health_Message/Dataset.xlsx")
        formulas = {
            "Gain_LS": ["P4LS_GD", "P4LS_GUD"],
            "Loss_LS": ["P4LS_LD", "P4LS_LUD"],
            "Gain_MS": ["P4MS_GD", "P4MS_GUD"],
            "Loss_MS": ["P4MS_LD", "P4MS_LUD"],
            "Gain_D": ["P4LS_GD", "P4MS_GD"],
            "Gain_UD": ["P4LS_GUD", "P4MS_GUD"],
            "Loss_D": ["P4LS_LD", "P4MS_LD"],
            "Loss_UD": ["P4LS_LUD", "P4MS_LUD"],
        }
        for output, inputs in formulas.items():
            self.assertTrue((d3[output] - d3[inputs].mean(axis=1)).abs().lt(1e-10).all())


if __name__ == "__main__":
    unittest.main()
