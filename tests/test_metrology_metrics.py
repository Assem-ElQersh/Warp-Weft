# The mechanistic justification for this step is: verify mathematical correctness of physical metrology metrics (MAE, RMSE, MBE, Bland-Altman LoA) and segmentation vision metrics against analytical numerical fixtures.

import math
import unittest
import numpy as np

from experiments.learned_models.metrics import (
    compute_dice,
    compute_iou,
    compute_metrology_metrics,
    compute_pixel_accuracy,
    evaluate_dual_axis_predictions,
)


class TestMetrologyMetrics(unittest.TestCase):
    def test_metrology_metrics_analytical_fixture(self):
        yt = [30.0, 32.0, 28.0]
        yp = [31.0, 31.0, 30.0]
        # diffs: [+1.0, -1.0, +2.0]
        # abs diffs: [1.0, 1.0, 2.0]
        metrics = compute_metrology_metrics(yt, yp)

        self.assertAlmostEqual(metrics["mae"], 4.0 / 3.0, places=3)
        self.assertAlmostEqual(metrics["rmse"], math.sqrt(6.0 / 3.0), places=3)
        self.assertAlmostEqual(metrics["mbe"], 2.0 / 3.0, places=3)
        self.assertEqual(metrics["max_error"], 2.0)
        self.assertAlmostEqual(metrics["pct_within_1"], 66.67, places=1)
        self.assertEqual(metrics["pct_within_2"], 100.0)

    def test_bland_altman_statistics(self):
        yt = [30.0, 30.0, 30.0, 30.0]
        yp = [31.0, 31.0, 31.0, 31.0]
        # diffs all +1.0
        metrics = compute_metrology_metrics(yt, yp)
        self.assertAlmostEqual(metrics["bland_altman_mean_diff"], 1.0, places=4)
        self.assertAlmostEqual(metrics["bland_altman_std_diff"], 0.0, places=4)
        self.assertAlmostEqual(metrics["bland_altman_loa_lower"], 1.0, places=4)
        self.assertAlmostEqual(metrics["bland_altman_loa_upper"], 1.0, places=4)

    def test_dual_axis_evaluation(self):
        y_tw = [31.0, 32.0]
        y_pw = [31.5, 33.0]
        y_tf = [27.0, 28.0]
        y_pf = [28.0, 27.5]

        res = evaluate_dual_axis_predictions(y_tw, y_pw, y_tf, y_pf)
        self.assertIn("warp", res)
        self.assertIn("weft", res)
        self.assertIn("composite", res)
        self.assertEqual(res["composite"]["pct_both_within_2"], 100.0)

    def test_segmentation_iou_dice(self):
        # 10x10 ground truth mask with 3 classes
        y_true = np.zeros((10, 10), dtype=np.uint8)
        y_true[:5, :] = 1
        y_true[5:, :] = 2

        # Identical prediction
        y_pred = y_true.copy()
        iou = compute_iou(y_true, y_pred, num_classes=3)
        dice = compute_dice(y_true, y_pred, num_classes=3)
        acc = compute_pixel_accuracy(y_true, y_pred)

        self.assertAlmostEqual(iou["miou"], 1.0, places=4)
        self.assertAlmostEqual(dice["mean_dice"], 1.0, places=4)
        self.assertAlmostEqual(acc, 1.0, places=4)


if __name__ == "__main__":
    unittest.main()
