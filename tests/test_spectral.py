# ==============================================================================
# Unit Regression Test: Multi-Candidate 2D Spectral Analysis
# ==============================================================================
import unittest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.spectral import compute_spectral_density_multicandidate, parabolic_sub_bin_interpolation


class TestSpectralAnalysis(unittest.TestCase):
    def test_parabolic_sub_bin_interpolation(self):
        # Peak exactly between bin 10 and 11
        slice_1d = np.zeros(20, dtype=np.float32)
        slice_1d[9] = 5.0
        slice_1d[10] = 10.0
        slice_1d[11] = 8.0

        exact_k, peak_mag = parabolic_sub_bin_interpolation(slice_1d, 10)
        # Should interpolate towards 10.5
        self.assertGreater(exact_k, 10.0)
        self.assertLess(exact_k, 10.5)
        self.assertEqual(peak_mag, 10.0)

    def test_synthetic_2d_sinusoid_frequency_recovery(self):
        # 1 cm x 1 cm at 400 px/cm. Sinusoid with 36 cycles (warp) and 30 cycles (weft)
        W, H = 400, 400
        x = np.linspace(0, 1.0, W, endpoint=False)
        y = np.linspace(0, 1.0, H, endpoint=False)
        xx, yy = np.meshgrid(x, y)

        target_warp = 36.0
        target_weft = 30.0
        pattern = 0.5 + 0.25 * np.cos(2 * np.pi * target_warp * xx) + 0.25 * np.cos(2 * np.pi * target_weft * yy)
        pattern = pattern.astype(np.float32)

        warp_d, weft_d, spnr_x, spnr_y, _, meta = compute_spectral_density_multicandidate(
            crop_arr=pattern,
            crop_w_cm=1.0,
            crop_h_cm=1.0,
            weave_hint="plain"
        )

        self.assertAlmostEqual(warp_d, target_warp, delta=0.5)
        self.assertAlmostEqual(weft_d, target_weft, delta=0.5)
        self.assertGreater(spnr_x, 10.0)
        self.assertGreater(spnr_y, 10.0)
        self.assertTrue(len(meta["warp_candidates"]) > 0)


if __name__ == "__main__":
    unittest.main()
