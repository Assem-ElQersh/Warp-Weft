# ==============================================================================
# Unit Regression Test: Physical Calibration
# ==============================================================================
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.calibration import PhysicalCalibration


class TestPhysicalCalibration(unittest.TestCase):
    def test_isotropic_calibration(self):
        cal = PhysicalCalibration.from_scales(400.0)
        self.assertEqual(cal.pixels_per_cm_x, 400.0)
        self.assertEqual(cal.pixels_per_cm_y, 400.0)
        self.assertEqual(cal.pixel_pitch_um_x, 25.0)
        self.assertEqual(cal.pixel_pitch_um_y, 25.0)
        self.assertTrue(cal.is_isotropic)
        self.assertAlmostEqual(cal.aspect_ratio, 1.0, places=4)

    def test_anisotropic_fabricnet_calibration(self):
        # 640x480 px covering 5.0x4.0 mm (0.5x0.4 cm)
        cal = PhysicalCalibration.from_fov(
            image_width_px=640,
            image_height_px=480,
            fov_width_cm=0.50,
            fov_height_cm=0.40,
            source="fabricnet_microscope_spec"
        )
        self.assertEqual(cal.pixels_per_cm_x, 1280.0)
        self.assertEqual(cal.pixels_per_cm_y, 1200.0)
        self.assertAlmostEqual(cal.pixel_pitch_um_x, 7.8125, places=4)
        self.assertAlmostEqual(cal.pixel_pitch_um_y, 8.3333, places=4)
        self.assertFalse(cal.is_isotropic)
        self.assertAlmostEqual(cal.aspect_ratio, 1280.0 / 1200.0, places=4)

    def test_dpi_calibration(self):
        cal = PhysicalCalibration.from_dpi(300.0)
        # 300 / 2.54 = 118.1102 px/cm
        self.assertAlmostEqual(cal.pixels_per_cm_x, 118.1102, places=3)
        self.assertAlmostEqual(cal.pixels_per_cm_y, 118.1102, places=3)

    def test_invalid_scales_raise_value_error(self):
        with self.assertRaises(ValueError):
            PhysicalCalibration.from_scales(-100.0)
        with self.assertRaises(ValueError):
            PhysicalCalibration.from_scales(0.0)


if __name__ == "__main__":
    unittest.main()
