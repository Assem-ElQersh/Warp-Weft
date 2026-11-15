# ==============================================================================
# Unit Regression Test: Multi-Estimator Evidence Fusion & Density Semantics
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
            weave_hint="plain"
        )
        self.assertEqual(res["decision_status"], "VALIDATED")
        self.assertEqual(res["warp_density_ends_per_cm"], 36)
        self.assertEqual(res["weft_density_picks_per_cm"], 30)
        self.assertEqual(res["linear_density_sum_per_cm"], 66.0)
        self.assertEqual(res["areal_intersection_density_per_cm2"], 1080.0)
        self.assertGreater(res["signal_quality_index"], 60.0)

    def test_divergent_estimators_yield_needs_review_status(self):
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
            weave_hint="plain"
        )
        # Must NOT be VALIDATED when estimators contradict!
        self.assertEqual(res["decision_status"], "NEEDS_REVIEW")
        self.assertIn("diverged significantly", res["decision_rationale"])

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
            weave_hint="plain"
        )
        # Linear sum is 38 + 33 = 71 threads/cm
        self.assertEqual(res["linear_density_sum_per_cm"], 71.0)
        # Areal crossing density is 38 * 33 = 1254 crossings/cm²
        self.assertEqual(res["areal_intersection_density_per_cm2"], 1254.0)


if __name__ == "__main__":
    unittest.main()
