# ==============================================================================
# Unit Regression Test: Orientation & Skew Rectification
# ==============================================================================
import unittest
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.orientation import detect_fabric_skew, rectify_and_crop


class TestOrientationRectification(unittest.TestCase):
    def test_skew_detection_synthetic_12deg(self):
        fpath = "data/synthetic/macro_swatch_skewed_12deg.png"
        if not os.path.exists(fpath):
            self.skipTest(f"Synthetic fixture not found: {fpath}")

        img = Image.open(fpath).convert("L")
        arr = np.array(img, dtype=np.float32) / 255.0
        cal = PhysicalCalibration.from_scales(400.0)

        angle, angles, energies, _ = detect_fabric_skew(arr, cal)

        # Ground truth is +12.0 deg; detected angle must be within +-0.5 deg
        self.assertAlmostEqual(angle, 11.5, delta=0.5)

    def test_rectification_improves_contrast_variance(self):
        fpath = "data/synthetic/macro_swatch_skewed_12deg.png"
        if not os.path.exists(fpath):
            self.skipTest(f"Synthetic fixture not found: {fpath}")

        img = Image.open(fpath)
        cal = PhysicalCalibration.from_scales(400.0)
        arr_skewed = np.array(img.convert("L"), dtype=np.float32) / 255.0

        angle, _, _, _ = detect_fabric_skew(arr_skewed, cal)
        rect_pil, crop_pil, _ = rectify_and_crop(img, angle, cal, crop_ratio=0.70)

        arr_rect = np.array(crop_pil.convert("L"), dtype=np.float32) / 255.0

        # Marginal projection variance
        var_skewed = float(np.var(np.mean(arr_skewed, axis=0)))
        var_rect = float(np.var(np.mean(arr_rect, axis=0)))

        # Variance after rectification must be strictly higher (contrast recovery)
        self.assertGreater(var_rect, var_skewed)
        self.assertGreater(var_rect / max(var_skewed, 1e-6), 2.0)


if __name__ == "__main__":
    unittest.main()
