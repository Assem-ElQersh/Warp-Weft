# ==============================================================================
# Unit Regression Test: Spatial Projection & Pitch Estimation
# ==============================================================================
import unittest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.spatial import (
    compute_spatial_projection_density,
    find_prominent_peaks_adaptive,
    median_filter_1d
)


class TestSpatialProjection(unittest.TestCase):
    def test_high_density_peaks_not_suppressed(self):
        # High density test: 93 picks/cm at 1200 px/cm
        # Pitch = 1200 / 93 = 12.90 pixels.
        # Defect 2.6 showed that old min_dist = 14 suppressed all peaks!
        cal = PhysicalCalibration.from_scales(1280.0, 1200.0)
        n_picks = 93
        span_cm = 0.40  # 4 mm
        h_px = int(span_cm * 1200.0)  # 480 px
        pitch_px = 1200.0 / n_picks  # ~12.9 px

        # Synthesize a 1D waveform with 93 picks/cm
        t = np.arange(h_px)
        sig = 0.5 + 0.4 * np.cos(2 * np.pi * t / pitch_px)

        # Adaptive minimum separation must be <= 5 pixels for 1200 px/cm
        min_dist_y = max(3, int(round(0.40 * 1200.0 / 120.0)))  # 4 pixels
        self.assertLessEqual(min_dist_y, 5)

        peaks = find_prominent_peaks_adaptive(sig, min_dist=min_dist_y, prominence=0.01)

        # In 480 pixels, there should be ~37 peaks (0.40 cm * 93 picks/cm = 37.2)
        expected_peaks = int(round(span_cm * n_picks))
        self.assertAlmostEqual(len(peaks), expected_peaks, delta=2)

    def test_median_filter_removes_single_pixel_spikes(self):
        sig = np.zeros(20, dtype=np.float32)
        sig[5] = 1.0  # isolated single-pixel spike
        filtered = median_filter_1d(sig, kernel_size=3)
        self.assertEqual(filtered[5], 0.0)


if __name__ == "__main__":
    unittest.main()
