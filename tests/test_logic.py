import unittest

from src.pufguard.run_logic import build_decision_rows, parse_shown_atoms


class LogicSerializationTests(unittest.TestCase):
    def test_parse_and_sort_atoms(self):
        atoms = [
            "flag(d2,free_text_present)",
            "action(d2,remove_structural_identifiers)",
            "decision(d2,restricted_review)",
            "flag(d2,structural_identifier_present)",
        ]
        decisions, actions, flags = parse_shown_atoms(atoms)
        self.assertEqual(decisions["D2"], "restricted_review")
        self.assertEqual(actions["D2"], ["remove_structural_identifiers"])
        self.assertCountEqual(flags["D2"], ["free_text_present", "structural_identifier_present"])

        rows = build_decision_rows(atoms)
        self.assertEqual(rows[0]["dataset_id"], "D2")
        self.assertEqual(rows[0]["flags"], "free_text_present; structural_identifier_present")

    def test_missing_decision_is_explicit(self):
        rows = build_decision_rows(["flag(d9,medium_linkability)"])
        self.assertEqual(rows[0]["decision"], "unresolved")


if __name__ == "__main__":
    unittest.main()
