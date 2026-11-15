# ==============================================================================
# Unit Regression Test: Synthetic Smartphone Failure Mode Fixture
# ==============================================================================
# The mechanistic justification for this step is: verify that the production engine
# running on an engineered synthetic failure-mode fixture (modeling common smartphone
# optical degradations: out-of-focus blur, oblique illumination vignetting, lens flare,
# and high-frequency surface yarn fuzz) avoids false certainty. It must NOT yield
# a blind VALIDATED consensus; when spatial projection and spectral analysis diverge
# due to optical degradation, the decision status must be NEEDS_REVIEW, accepted
# measurements must be None, and unvalidated candidate values must be isolated.
# NOTE: This evaluates synthetic failure-mode bounds; it does NOT claim that the original
# uncalibrated smartphone photograph is empirically verified.

import unittest
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.pipeline import analyze_fabric


class TestSyntheticSmartphoneFailureModeFixture(unittest.TestCase):
    def setUp(self):
        # Construct synthetic failure-mode fixture (1200 x 1600) with heavy non-uniform
        # illumination gradient, surface fuzz, and optical out-of-focus blur
        h, w = 1200, 1600
        y, x = np.mgrid[0:h, 0:w]

        # Underlying fabric pattern (~35 x 30 threads/cm at 400 px/cm)
        warp_freq = 2 * np.pi * (35.0 / 400.0)
        weft_freq = 2 * np.pi * (30.0 / 400.0)
        fabric = 0.15 * np.sin(warp_freq * x) + 0.15 * np.sin(weft_freq * y)

        # Non-uniform lens vignetting + flare gradient
        vignette = 0.5 * (1.0 - ((x - w / 2) ** 2 + (y - h / 2) ** 2) / (w ** 2 + h ** 2))
        flare = 0.3 * (x / float(w) + y / float(h))
        illumination = vignette + flare

        # High-frequency surface fuzz / noise
        np.random.seed(42)
        fuzz = np.random.normal(0.0, 0.30, size=(h, w))

        composite = np.clip(fabric + illumination + fuzz, 0.0, 1.0)
        composite_u8 = (composite * 255.0).astype(np.uint8)
        raw_pil = Image.fromarray(composite_u8)

        # Smartphone lens out-of-focus blur that attenuates spatial crown sharpness
        self.degraded_smartphone_img = raw_pil.filter(ImageFilter.GaussianBlur(radius=8))

    def test_degraded_synthetic_fixture_yields_needs_review_and_isolates_candidates(self):
        res = analyze_fabric(
            img_pil=self.degraded_smartphone_img,
            pixels_per_cm=400.0,
            pixels_per_cm_y=400.0,
            auto_skew=True,
            weave_hint="plain",
            prominence=0.08
        )
        self.assertEqual(res["status"], "success")
        results = res["results"]

        # Must flag divergence rather than asserting false certainty
        self.assertEqual(results["decision_status"], "NEEDS_REVIEW")
        self.assertFalse(results["is_validated"])

        # Primary accepted measurements must be None
        self.assertIsNone(results["warp_ends_per_cm"])
        self.assertIsNone(results["weft_picks_per_cm"])
        self.assertIsNone(results["linear_density_sum_per_cm"])

        # Candidate measurements must be preserved explicitly
        self.assertIn("candidate_measurements", results)
        candidates = results["candidate_measurements"]
        self.assertGreater(candidates["warp_fft"], 0.0)
        self.assertEqual(candidates["warp_proj"], 0.0)


if __name__ == "__main__":
    unittest.main()
