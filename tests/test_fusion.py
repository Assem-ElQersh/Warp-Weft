# ==============================================================================
# Unit Regression Test: Multi-Estimator Evidence Fusion & Uncertainty Policy
# ==============================================================================
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.fusion import evaluate_evidence_fusion


class TestEvidenceFusion(unittest.TestCase):
    def test_concordant_estimators_yield_validated_status(self):
        res = evaluate_evidence_fusion(
            warp_fft=36.0,
            weft_fft=30.0,
            warp_proj=36.2,
            weft_proj=29.8,
            spnr_x=15.0,
            spnr_y=20.0,
            rect_variance=0.10,
            warp_dispersion=0.08,
            weft_dispersion=0.08,
            weave_hint="plain",
            crop_w_cm=0.40,
            crop_h_cm=0.40
        )
        self.assertEqual(res["decision_status"], "VALIDATED")
        self.assertTrue(res["is_validated"])
        self.assertEqual(res["warp_density_ends_per_cm"], 36)
        self.assertEqual(res["weft_density_picks_per_cm"], 30)
        self.assertEqual(res["accepted_warp_density_ends_per_cm"], 36)
        self.assertEqual(res["accepted_weft_density_picks_per_cm"], 30)
        self.assertEqual(res["linear_density_sum_per_cm"], 66.0)
        self.assertEqual(res["areal_intersection_density_per_cm2"], 1080.0)
        self.assertGreater(res["signal_quality_index"], 60.0)

    def test_divergent_estimators_yield_needs_review_and_none_accepted_density(self):
        # 36 vs 50 on warp; 30 vs 45 on weft
        res = evaluate_evidence_fusion(
            warp_fft=36.0,
            weft_fft=30.0,
            warp_proj=50.0,
            weft_proj=45.0,
            spnr_x=4.0,
            spnr_y=4.0,
            rect_variance=0.01,
            warp_dispersion=0.35,
            weft_dispersion=0.35,
            weave_hint="plain",
            crop_w_cm=0.40,
            crop_h_cm=0.40
        )
        # Must NOT be VALIDATED when estimators contradict
        self.assertEqual(res["decision_status"], "NEEDS_REVIEW")
        self.assertFalse(res["is_validated"])
        # Accepted densities must be strictly None to prevent exposing unvalidated guesses
        self.assertIsNone(res["accepted_warp_density_ends_per_cm"])
        self.assertIsNone(res["accepted_weft_density_picks_per_cm"])
        self.assertIsNone(res["warp_density_ends_per_cm"])
        self.assertIsNone(res["weft_picks_per_cm"])
        self.assertIsNone(res["linear_density_sum_per_cm"])
        self.assertIsNone(res["areal_intersection_density_per_cm2"])
        # Candidates must be explicitly preserved
        candidates = res["candidate_measurements"]
        self.assertEqual(candidates["warp_fft"], 36.0)
        self.assertEqual(candidates["warp_proj"], 50.0)
        self.assertEqual(candidates["weft_fft"], 30.0)
        self.assertEqual(candidates["weft_proj"], 45.0)

    def test_partial_concordance_yields_consistent_with_warning(self):
        # Warp agrees (36.0 vs 36.5), weft diverges (30.0 vs 42.0)
        res = evaluate_evidence_fusion(
            warp_fft=36.0,
            weft_fft=30.0,
            warp_proj=36.5,
            weft_proj=42.0,
            spnr_x=12.0,
            spnr_y=5.0,
            rect_variance=0.08,
            warp_dispersion=0.06,
            weft_dispersion=0.25,
            weave_hint="plain",
            crop_w_cm=0.40,
            crop_h_cm=0.40
        )
        self.assertEqual(res["decision_status"], "CONSISTENT_WITH_WARNING")
        self.assertFalse(res["is_validated"])
        self.assertEqual(res["accepted_warp_density_ends_per_cm"], 36)
        self.assertIsNone(res["accepted_weft_density_picks_per_cm"])
        self.assertIsNone(res["linear_density_sum_per_cm"])

    def test_density_semantics_dimensional_correctness(self):
        res = evaluate_evidence_fusion(
            warp_fft=38.0,
            weft_fft=33.0,
            warp_proj=38.0,
            weft_proj=33.0,
            spnr_x=12.0,
            spnr_y=12.0,
            rect_variance=0.08,
            warp_dispersion=0.05,
            weft_dispersion=0.05,
            weave_hint="plain",
            crop_w_cm=0.40,
            crop_h_cm=0.40
        )
        self.assertEqual(res["linear_density_sum_per_cm"], 71.0)
        self.assertEqual(res["areal_intersection_density_per_cm2"], 1254.0)


if __name__ == "__main__":
    unittest.main()
