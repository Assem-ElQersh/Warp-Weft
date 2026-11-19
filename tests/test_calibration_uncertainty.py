# The mechanistic justification for this step is: verify physical scale conversion (D = S / Delta), partial derivative uncertainty propagation, ruler pixel distance conversion, and homography rectification.

import math
import unittest
import numpy as np

from experiments.learned_models.calibration import (
    calculate_density_with_uncertainty,
    compute_planar_homography,
    rectify_perspective,
    two_point_ruler_to_scale,
)


class TestCalibrationUncertainty(unittest.TestCase):
    def test_density_and_uncertainty_propagation(self):
        scale = 400.0  # px/cm
        pitch = 10.0  # px/thread
        # Analytical density = 40.0 threads/cm
        # Uncertainty: scale_pct = 2.0%, pitch_std = 0.5 px (5.0%)
        # rel_total = sqrt(0.02^2 + 0.05^2) = sqrt(0.0029) ~ 0.05385
        # uncertainty = 40.0 * 0.05385 ~ 2.154 threads/cm
        meas = calculate_density_with_uncertainty(
            pitch_px=pitch,
            scale_px_per_cm=scale,
            pitch_std_px=0.5,
            scale_uncertainty_pct=2.0,
        )

        self.assertAlmostEqual(meas.density, 40.0, places=4)
        expected_rel = math.sqrt(0.02**2 + 0.05**2)
        expected_unc = 40.0 * expected_rel
        self.assertAlmostEqual(meas.uncertainty, expected_unc, places=3)
        self.assertAlmostEqual(meas.relative_uncertainty_pct, expected_rel * 100.0, places=2)

    def test_two_point_ruler_to_scale(self):
        pt1 = (100.0, 100.0)
        pt2 = (400.0, 500.0)
        # dx = 300, dy = 400 -> dist = 500 px
        # physical length = 2.0 cm -> scale = 250 px/cm
        scale = two_point_ruler_to_scale(pt1, pt2, physical_distance_cm=2.0)
        self.assertAlmostEqual(scale, 250.0, places=4)

    def test_homography_and_rectification(self):
        # 100x100 square with affine tilt
        src = np.array([[10, 10], [90, 15], [85, 95], [15, 90]], dtype=np.float32)
        h_mat, out_dim = compute_planar_homography(
            src_points=src, target_width_cm=1.0, target_height_cm=1.0, scale_px_per_cm=100.0
        )
        self.assertEqual(out_dim, (100, 100))
        self.assertEqual(h_mat.shape, (3, 3))

        img = np.ones((120, 120), dtype=np.uint8) * 128
        rect = rectify_perspective(img, h_mat, out_dim)
        self.assertEqual(rect.shape, (100, 100))


if __name__ == "__main__":
    unittest.main()
