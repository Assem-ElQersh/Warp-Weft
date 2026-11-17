"""Unit tests for camera calibration profiles and 5-region specimen evaluation workflow."""
import unittest
from PIL import Image

from src.fabric_analysis.calibration_profile import (
    CalibrationProfile,
    calibrate_from_two_points,
    get_calibration_profile,
    list_calibration_profiles,
)
from src.fabric_analysis.specimen_workflow import (
    evaluate_five_region_specimen,
    CLIENT_TARGET_WARP_ENDS_PER_CM,
    CLIENT_TARGET_WEFT_PICKS_PER_CM,
)
from src.fabric_analysis.calibration import PhysicalCalibration


class TestSpecimenWorkflowAndCalibrationProfiles(unittest.TestCase):
    def test_standard_profiles_exist_and_convert_to_valid_calibration(self):
        profiles = list_calibration_profiles()
        self.assertGreaterEqual(len(profiles), 3)

        phone_profile = get_calibration_profile("smartphone_macro_stand_v1")
        self.assertIsNotNone(phone_profile)
        self.assertEqual(phone_profile.profile_id, "smartphone_macro_stand_v1")
        self.assertTrue(phone_profile.is_verified)

        phys_cal = phone_profile.to_physical_calibration()
        self.assertIsInstance(phys_cal, PhysicalCalibration)
        self.assertEqual(phys_cal.pixels_per_cm_x, 263.5)
        self.assertEqual(phys_cal.pixels_per_cm_y, 208.4)

    def test_calibrate_from_two_points_computes_exact_scale(self):
        # 200 pixels spanning 1.0 cm -> 200.0 px/cm
        sx, sy = calibrate_from_two_points((100, 100), (300, 100), known_distance_cm=1.0, axis="horizontal")
        self.assertEqual(sx, 200.0)

        # 300 pixels vertical spanning 1.5 cm -> 200.0 px/cm
        sx_v, sy_v = calibrate_from_two_points((100, 100), (100, 400), known_distance_cm=1.5, axis="vertical")
        self.assertEqual(sy_v, 200.0)

        # Rejects negative or zero physical distance
        with self.assertRaises(ValueError):
            calibrate_from_two_points((0, 0), (10, 10), known_distance_cm=0.0)

    def test_specimen_evaluation_computes_means_and_checks_factory_tolerance(self):
        # Create 5 synthetic test images of 200x200 pixels
        test_images = [Image.new("RGB", (200, 200), color=(128, 128, 128)) for _ in range(5)]
        cal = PhysicalCalibration.from_scales(263.5, 208.4)

        result = evaluate_five_region_specimen(
            fabric_id="specimen_test_01",
            images=test_images,
            calibration=cal,
            target_warp=31.0,
            target_weft=27.0,
            tolerance=2.0,
        )

        self.assertEqual(result.fabric_id, "specimen_test_01")
        self.assertEqual(result.expected_regions, 5)
        self.assertEqual(result.evaluated_regions_count, 5)
        self.assertEqual(len(result.regions), 5)

    def test_specimen_evaluation_rejects_incorrect_image_counts(self):
        three_images = [Image.new("RGB", (100, 100)) for _ in range(3)]
        cal = PhysicalCalibration.from_scales(200.0, 200.0)
        with self.assertRaises(ValueError):
            evaluate_five_region_specimen(
                fabric_id="bad_count",
                images=three_images,
                calibration=cal,
            )


if __name__ == "__main__":
    unittest.main()
