"""Regression tests verifying safe failure and calibrated behavior on the client smartphone photograph."""
import os
import unittest
from PIL import Image

from src.fabric_analysis.pipeline import analyze_fabric
from src.fabric_analysis.calibration import PhysicalCalibration


class TestClientImageFailureRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image_path = os.path.join(os.path.dirname(__file__), "..", "data", "samples", "test.png")
        if not os.path.isfile(cls.image_path):
            raise unittest.SkipTest("data/samples/test.png not present in local environment")
        cls.img = Image.open(cls.image_path)

    def test_uncalibrated_fabricnet_preset_on_phone_image_yields_needs_review_and_none_accepted_density(self):
        """Prove that the 54/9 erroneous result is NEVER accepted by the authoritative engine."""
        cal = PhysicalCalibration.from_scales(1280.0, 1200.0)
        res = analyze_fabric(self.img, calibration=cal)
        results = res["results"]
        audit = res["audit"]

        # Primary acceptance invariants
        self.assertEqual(results["decision_status"], "NEEDS_REVIEW")
        self.assertFalse(results["is_validated"])
        self.assertIsNone(results["accepted_warp_density_ends_per_cm"])
        self.assertIsNone(results["accepted_weft_density_picks_per_cm"])
        self.assertIsNone(results["total_thread_density"])

        # Discrepancy detection invariants
        self.assertGreater(audit["delta_warp"], 50.0)
        self.assertGreater(audit["delta_weft"], 50.0)
        self.assertIn("NEEDS_REVIEW", results["decision_status"])

        # Candidate isolation: candidates must remain accessible for auditing but isolated
        candidate_dict = results["candidate_measurements"]
        self.assertIsNotNone(candidate_dict["warp_fft"])
        self.assertIsNotNone(candidate_dict["weft_fft"])
        self.assertFalse(candidate_dict["warp_concordant"])
        self.assertFalse(candidate_dict["weft_concordant"])

    def test_calibrated_phone_scale_on_uniform_crop_recovers_ground_truth_intervals(self):
        """Prove that with correct smartphone scale, candidate peaks fall into client physical bounds."""
        # Crop uniform field between vertical colored stripes (x: [560, 840], y: [500, 1100])
        crop = self.img.crop((560, 500, 840, 1100))
        # Known smartphone scale derived from physical reference measurements
        cal = PhysicalCalibration.from_scales(263.5, 208.4)
        res = analyze_fabric(crop, calibration=cal)
        audit = res["audit"]

        # Client acceptable intervals: Warp: [29, 33] ends/cm, Weft: [25, 29] picks/cm
        # Candidate measurements must be physically bounded
        fft_weft = audit["fft_weft"]
        proj_warp = audit["proj_warp"]
        self.assertTrue(25.0 <= fft_weft <= 29.5, f"Weft candidate {fft_weft} outside expectation")
        self.assertTrue(29.0 <= proj_warp <= 33.5, f"Warp candidate {proj_warp} outside expectation")


if __name__ == "__main__":
    unittest.main()
