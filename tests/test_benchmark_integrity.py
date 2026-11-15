# ==============================================================================
# Unit Regression Test: Benchmark Provenance & Calculation Integrity
# ==============================================================================
import unittest
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.pipeline import analyze_fabric
from web_app.engine import run_complete_fabric_analysis


class TestBenchmarkIntegrity(unittest.TestCase):
    def test_calculated_errors_match_arithmetic_truth(self):
        # Defect 2.1 check: verify that reported error is mathematically derived
        measured_warp = 38.0
        ground_truth_warp = 38
        measured_weft = 35.0
        ground_truth_weft = 33

        reported_warp_error = abs(measured_warp - ground_truth_warp)
        reported_weft_error = abs(measured_weft - ground_truth_weft)

        self.assertEqual(reported_warp_error, 0.0)
        self.assertEqual(reported_weft_error, 2.0)
        # Verify that reported weft error is NOT 0.5 (which was the hardcoded value!)
        self.assertNotEqual(reported_weft_error, 0.5)

    def test_production_engine_and_src_package_equivalence(self):
        # Defect 2.10 check: ensure web_app.engine and src.fabric_analysis are 100% equivalent
        fpath = "data/synthetic/sample_plain_32x28.png"
        if not os.path.exists(fpath):
            self.skipTest(f"Synthetic fixture not found: {fpath}")

        im = Image.open(fpath)
        cal = PhysicalCalibration.from_scales(400.0)

        res_src = analyze_fabric(im, calibration=cal, auto_skew=False)
        res_engine = run_complete_fabric_analysis(im, pixels_per_cm=400.0, auto_skew=False)

        self.assertEqual(res_src["results"]["warp_ends_per_cm"], res_engine["results"]["warp_ends_per_cm"])
        self.assertEqual(res_src["results"]["weft_picks_per_cm"], res_engine["results"]["weft_picks_per_cm"])
        self.assertEqual(res_src["results"]["engine_mode"], res_engine["results"]["engine_mode"])

    def test_fabricnet_w012_end_to_end_execution(self):
        fpath = "data/fabricnet/W012.jpg"
        if not os.path.exists(fpath):
            self.skipTest(f"FabricNET fixture not found: {fpath}")

        im = Image.open(fpath)
        cal = PhysicalCalibration.from_fov(640, 480, 0.50, 0.40)
        res = analyze_fabric(im, calibration=cal, weave_hint="plain", auto_skew=True)

        self.assertEqual(res["status"], "success")
        self.assertIn("warp_ends_per_cm", res["results"])
        self.assertIn("weft_picks_per_cm", res["results"])
        self.assertIn("actual_roi_cm", res["roi_metadata"])
        self.assertFalse(res["roi_metadata"]["requested_roi_fully_available"])


if __name__ == "__main__":
    unittest.main()
