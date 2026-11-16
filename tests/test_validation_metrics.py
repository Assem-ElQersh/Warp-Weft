import unittest

from src.fabric_analysis.validation_metrics import axis_metrics, evaluate_prediction_records


class TestValidationMetrics(unittest.TestCase):
    def test_rejected_predictions_remain_in_coverage_denominator(self):
        result = axis_metrics([31, 32, 30], [31.5, None, 27.0], [10, 11, 12])
        self.assertEqual(result["n_total"], 3)
        self.assertEqual(result["n_predicted"], 2)
        self.assertEqual(result["n_rejected"], 1)
        self.assertAlmostEqual(result["coverage_pct"], 66.67, places=2)
        self.assertAlmostEqual(result["rejection_rate_pct"], 33.33, places=2)
        self.assertAlmostEqual(result["mae"], 1.75)
        self.assertAlmostEqual(result["mean_signed_bias"], -1.25)
        self.assertEqual(result["within_2_pct"], 50.0)

    def test_tolerance_is_inclusive_and_bootstrap_is_reproducible(self):
        first = axis_metrics([31, 31, 31], [29, 30, 33], bootstrap_samples=200, seed=7)
        second = axis_metrics([31, 31, 31], [29, 30, 33], bootstrap_samples=200, seed=7)
        self.assertEqual(first["within_2_pct"], 100.0)
        stricter = axis_metrics([31, 31], [29, 30], tolerance=1.0, bootstrap_samples=0)
        self.assertEqual(stricter["within_2_pct"], 100.0)
        self.assertEqual(stricter["within_tolerance_pct"], 50.0)
        self.assertEqual(first["mae_bootstrap_95_ci"], second["mae_bootstrap_95_ci"])

    def test_zero_accepted_predictions_is_reported_without_fake_zero_error(self):
        result = axis_metrics([31, 27], [None, None])
        self.assertIsNone(result["mae"])
        self.assertEqual(result["coverage_pct"], 0.0)
        self.assertEqual(result["rejection_rate_pct"], 100.0)

    def test_per_weave_and_per_specimen_breakdowns(self):
        records = [
            {"fabric_id":"A","weave_type":"plain","warp_manual_density":31,"weft_manual_density":27,"warp_predicted_density":31,"weft_predicted_density":27,"runtime_ms":10},
            {"fabric_id":"A","weave_type":"plain","warp_manual_density":30,"weft_manual_density":28,"warp_predicted_density":None,"weft_predicted_density":29,"runtime_ms":12},
            {"fabric_id":"B","weave_type":"twill","warp_manual_density":32,"weft_manual_density":27,"warp_predicted_density":30,"weft_predicted_density":None,"runtime_ms":14},
        ]
        result = evaluate_prediction_records(records, bootstrap_samples=50)
        self.assertIn("plain", result["per_weave"])
        self.assertIn("A", result["per_specimen"])
        self.assertEqual(result["per_specimen"]["A"]["warp"]["n_total"], 2)
        self.assertEqual(result["warp"]["n_rejected"], 1)


if __name__ == "__main__":
    unittest.main()
