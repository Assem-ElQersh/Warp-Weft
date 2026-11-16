import json
import os
import unittest


class TestPublishedFabricNetBenchmarkArtifact(unittest.TestCase):
    def test_artifact_is_strict_json_with_130_rows_and_reconciled_statuses(self):
        path = os.path.join(os.path.dirname(__file__), "..", "results", "fabricnet_benchmark.json")
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        self.assertEqual(payload["schema_version"], "2.1.0")
        self.assertEqual(payload["total_samples"], 130)
        self.assertFalse(payload["calibration"]["is_verified"])
        self.assertEqual(payload["calibration"]["uncertainty_pct"], 5)
        self.assertEqual(len(payload["samples"]), 130)
        self.assertEqual(payload["aggregate_metrics"]["decision_status_breakdown"], {
            "NEEDS_REVIEW": 88,
            "CONSISTENT_WITH_WARNING": 27,
            "VALIDATED": 15,
        })

    def test_accepted_coverage_is_not_confused_with_candidate_estimate_coverage(self):
        path = os.path.join(os.path.dirname(__file__), "..", "results", "fabricnet_benchmark.json")
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        accepted = payload["aggregate_metrics"]["accepted_measurements"]
        self.assertEqual(accepted["warp"]["n_accepted"], 25)
        self.assertEqual(accepted["weft"]["n_accepted"], 32)
        self.assertEqual(accepted["warp"]["n_rejected"], 105)
        self.assertEqual(accepted["weft"]["n_rejected"], 98)
        self.assertEqual(accepted["warp"]["coverage_pct"], 19.23)
        self.assertEqual(accepted["weft"]["coverage_pct"], 24.62)



if __name__ == "__main__":
    unittest.main()
