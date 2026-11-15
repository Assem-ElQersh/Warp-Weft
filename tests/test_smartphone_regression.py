# ==============================================================================
# Unit Regression Test: Smartphone Photography Failure Mode Fixture
# ==============================================================================
# The mechanistic justification for this step is: verify that the production engine
# running on an uncalibrated or noisy smartphone image (1200 x 1600) with heavy
# non-uniform illumination and yarn fuzz does not output a false VALIDATED status.
# It must flag the measurement as CONSISTENT_WITH_WARNING or NEEDS_REVIEW, avoiding
# false certainty.

import unittest
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.pipeline import analyze_fabric


class TestSmartphoneRegression(unittest.TestCase):
    def setUp(self):
        # Construct synthetic smartphone image (1200 x 1600) with heavy non-uniform
        # illumination gradient and random yarn fuzz / noise
        h, w = 1200, 1600
        y, x = np.mgrid[0:h, 0:w]

        # Weak underlying fabric pattern (e.g., ~35 x 30 threads/cm at 400 px/cm)
        warp_freq = 2 * np.pi * (35.0 / 400.0)
        weft_freq = 2 * np.pi * (30.0 / 400.0)
        fabric = 0.2 * np.sin(warp_freq * x) + 0.2 * np.sin(weft_freq * y)

        # Strong illumination gradient (vignetting + diagonal flare typical of phone lens)
        vignette = 0.5 * (1.0 - ((x - w / 2) ** 2 + (y - h / 2) ** 2) / (w ** 2 + h ** 2))
        flare = 0.3 * (x / float(w) + y / float(h))
        illumination = vignette + flare

        # High-frequency surface fuzz / noise
        np.random.seed(42)
        fuzz = np.random.normal(0.0, 0.25, size=(h, w))

        composite = np.clip(fabric + illumination + fuzz, 0.0, 1.0)
        composite_u8 = (composite * 255.0).astype(np.uint8)
        self.smartphone_img = Image.fromarray(composite_u8)

    def test_noisy_smartphone_yields_warning_or_review_status(self):
        res = analyze_fabric(
            img_pil=self.smartphone_img,
            pixels_per_cm=400.0,
            pixels_per_cm_y=400.0,
            auto_skew=True,
            weave_hint="plain",
            prominence=0.08
        )
        self.assertEqual(res["status"], "success")
        results = res["results"]
        # Must NOT be blind VALIDATED consensus
        self.assertIn(results["decision_status"], ["CONSISTENT_WITH_WARNING", "NEEDS_REVIEW"])
        self.assertFalse(np.isnan(results["warp_ends_per_cm"]))
        self.assertFalse(np.isnan(results["weft_picks_per_cm"]))
        # Quality index should reflect the heavy noise / gradient
        self.assertLess(results["signal_quality_index"], 85.0)


if __name__ == "__main__":
    unittest.main()
