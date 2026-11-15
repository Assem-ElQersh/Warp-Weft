# ==============================================================================
# Unit Regression Test: Region of Interest (ROI) Localization
# ==============================================================================
import unittest
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.roi import extract_metric_roi


class TestROILocalization(unittest.TestCase):
    def test_full_roi_available_on_large_image(self):
        # 800x800 image at 400 px/cm (2.0x2.0 cm)
        img = Image.new("L", (800, 800), color=128)
        cal = PhysicalCalibration.from_scales(400.0)

        roi_pil, meta = extract_metric_roi(img, cal, target_roi_cm=(1.0, 1.0))

        self.assertTrue(meta["requested_roi_fully_available"])
        self.assertEqual(meta["actual_roi_cm"], [1.0, 1.0])
        self.assertEqual(roi_pil.size, (400, 400))
        self.assertIsNone(meta["warning"])

    def test_undersized_image_reports_actual_coverage(self):
        # 640x480 image at 1280x1200 px/cm (0.5x0.4 cm)
        img = Image.new("L", (640, 480), color=128)
        cal = PhysicalCalibration.from_scales(1280.0, 1200.0)

        roi_pil, meta = extract_metric_roi(img, cal, target_roi_cm=(1.0, 1.0))

        self.assertFalse(meta["requested_roi_fully_available"])
        self.assertEqual(meta["actual_roi_cm"], [0.5, 0.4])
        self.assertEqual(roi_pil.size, (640, 480))
        self.assertIsNotNone(meta["warning"])
        self.assertIn("exceeds available image resolution", meta["warning"])

    def test_custom_roi_bounds(self):
        img = Image.new("L", (1000, 1000), color=128)
        cal = PhysicalCalibration.from_scales(400.0)

        roi_pil, meta = extract_metric_roi(
            img, cal, target_roi_cm=(1.0, 1.0), custom_roi_px=(100, 150, 400, 400)
        )
        self.assertEqual(roi_pil.size, (400, 400))
        self.assertEqual(meta["roi_box_px"], [100, 150, 500, 550])


if __name__ == "__main__":
    unittest.main()
