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


    def test_cluster_bootstrap_resamples_specimens_not_individual_regions(self):
        targets = [10, 10, 10, 20, 20, 20]
        predictions = [9, 9, 9, 22, 22, 22]
        groups = ["A", "A", "A", "B", "B", "B"]
        result = axis_metrics(targets, predictions, groups=groups, bootstrap_samples=100, seed=11)
        self.assertEqual(result["mae_bootstrap_95_ci"]["unit"], "group")
        self.assertEqual(result["mae_bootstrap_95_ci"]["group_count"], 2)
        self.assertEqual(result["mae_bootstrap_95_ci"], axis_metrics(
            targets, predictions, groups=groups, bootstrap_samples=100, seed=11
        )["mae_bootstrap_95_ci"])

    def test_specimen_aggregate_uses_five_region_means_and_rejects_partial_predictions(self):
        records = []
        for region in range(5):
            records.append({
                "fabric_id": "A", "weave_type": "plain",
                "warp_manual_density": 30 + region,
                "weft_manual_density": 26 + region,
                "warp_predicted_density": 31 + region,
                "weft_predicted_density": 27 + region,
                "runtime_ms": 10,
            })
            records.append({
                "fabric_id": "B", "weave_type": "twill",
                "warp_manual_density": 32,
                "weft_manual_density": 28,
                "warp_predicted_density": None if region == 4 else 32,
                "weft_predicted_density": 28,
                "runtime_ms": 12,
            })
        result = evaluate_prediction_records(records, bootstrap_samples=100)
        aggregate = result["specimen_aggregate"]
        self.assertEqual(aggregate["protocol_regions_per_specimen"], 5)
        self.assertEqual(aggregate["warp"]["n_total"], 2)
        self.assertEqual(aggregate["warp"]["n_predicted"], 1)
        self.assertEqual(aggregate["warp"]["n_rejected"], 1)
        self.assertEqual(aggregate["specimens"][0]["fabric_id"], "A")
        self.assertEqual(aggregate["specimens"][0]["warp_manual_density"], 32.0)
        self.assertEqual(aggregate["specimens"][0]["warp_predicted_density"], 33.0)
        self.assertIsNone(aggregate["specimens"][1]["warp_predicted_density"])
        self.assertEqual(aggregate["weft"]["n_predicted"], 2)

    def test_specimen_aggregate_rejects_incomplete_five_region_groups(self):
        records = [{
            "fabric_id": "A", "weave_type": "plain",
            "warp_manual_density": 31, "weft_manual_density": 27,
            "warp_predicted_density": 31, "weft_predicted_density": 27,
        }]
        with self.assertRaisesRegex(ValueError, "exactly 5 region records"):
            evaluate_prediction_records(records)

    def test_per_weave_and_per_specimen_breakdowns(self):
        records = []
        for region in range(5):
            records.append({
                "fabric_id": "A", "weave_type": "plain",
                "warp_manual_density": 31 if region < 3 else 30,
                "weft_manual_density": 27,
                "warp_predicted_density": None if region == 1 else 31,
                "weft_predicted_density": 27,
                "runtime_ms": 10,
            })
            records.append({
                "fabric_id": "B", "weave_type": "twill",
                "warp_manual_density": 32,
                "weft_manual_density": 27,
                "warp_predicted_density": 30,
                "weft_predicted_density": 27,
                "runtime_ms": 14,
            })
        result = evaluate_prediction_records(records, bootstrap_samples=50)
        self.assertIn("plain", result["per_weave"])
        self.assertIn("A", result["per_specimen"])
        self.assertEqual(result["per_specimen"]["A"]["warp"]["n_total"], 5)
        self.assertEqual(result["warp"]["n_rejected"], 1)


if __name__ == "__main__":
    unittest.main()
