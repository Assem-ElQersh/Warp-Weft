# The mechanistic justification for this step is: implement unified evaluation metrics covering both computer vision criteria (Precision, Recall, F1/Dice, mIoU, Pixel Accuracy) and physical textile metrology standards (MAE, RMSE, Mean Bias Error, Maximum Error, Percentage within +/- 1.0 and +/- 2.0 threads/cm, and Bland-Altman agreement statistics).

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


def compute_iou(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int = 3) -> Dict[str, float]:
    ious = []
    class_ious = {}
    for c in range(num_classes):
        true_c = y_true == c
        pred_c = y_pred == c
        intersection = np.logical_and(true_c, pred_c).sum()
        union = np.logical_or(true_c, pred_c).sum()
        if union == 0:
            iou = 1.0
        else:
            iou = float(intersection / union)
        ious.append(iou)
        class_ious[f"class_{c}_iou"] = iou
    class_ious["miou"] = float(np.mean(ious))
    return class_ious


def compute_dice(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int = 3) -> Dict[str, float]:
    dices = []
    class_dices = {}
    for c in range(num_classes):
        true_c = y_true == c
        pred_c = y_pred == c
        intersection = np.logical_and(true_c, pred_c).sum()
        total = true_c.sum() + pred_c.sum()
        if total == 0:
            dice = 1.0
        else:
            dice = float((2.0 * intersection) / total)
        dices.append(dice)
        class_dices[f"class_{c}_dice"] = dice
    class_dices["mean_dice"] = float(np.mean(dices))
    return class_dices


def compute_pixel_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    total_pixels = y_true.size
    if total_pixels == 0:
        return 1.0
    correct = (y_true == y_pred).sum()
    return float(correct / total_pixels)


def compute_metrology_metrics(
    y_true: Union[List[float], np.ndarray], y_pred: Union[List[float], np.ndarray]
) -> Dict[str, float]:
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)

    assert len(yt) == len(yp), "Ground truth and prediction arrays must have equal length"
    n = len(yt)
    if n == 0:
        return {
            "n_samples": 0,
            "mae": 0.0,
            "rmse": 0.0,
            "mbe": 0.0,
            "max_error": 0.0,
            "pct_within_1": 0.0,
            "pct_within_2": 0.0,
        }

    diffs = yp - yt
    abs_diffs = np.abs(diffs)

    mae = float(np.mean(abs_diffs))
    rmse = float(np.sqrt(np.mean(diffs**2)))
    mbe = float(np.mean(diffs))
    max_error = float(np.max(abs_diffs))

    within_1 = float((abs_diffs <= 1.0).sum() / n * 100.0)
    within_2 = float((abs_diffs <= 2.0).sum() / n * 100.0)

    # Bland-Altman statistics
    mean_diff = float(np.mean(diffs))
    std_diff = float(np.std(diffs, ddof=1)) if n > 1 else 0.0
    loa_lower = mean_diff - 1.96 * std_diff
    loa_upper = mean_diff + 1.96 * std_diff

    return {
        "n_samples": n,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mbe": round(mbe, 4),
        "max_error": round(max_error, 4),
        "pct_within_1": round(within_1, 2),
        "pct_within_2": round(within_2, 2),
        "bland_altman_mean_diff": round(mean_diff, 4),
        "bland_altman_std_diff": round(std_diff, 4),
        "bland_altman_loa_lower": round(loa_lower, 4),
        "bland_altman_loa_upper": round(loa_upper, 4),
    }


def evaluate_dual_axis_predictions(
    y_true_warp: List[float],
    y_pred_warp: List[float],
    y_true_weft: List[float],
    y_pred_weft: List[float],
) -> Dict[str, Any]:
    warp_metrics = compute_metrology_metrics(y_true_warp, y_pred_warp)
    weft_metrics = compute_metrology_metrics(y_true_weft, y_pred_weft)

    both_within_2 = [
        abs(pw - tw) <= 2.0 and abs(pf - tf) <= 2.0
        for tw, pw, tf, pf in zip(y_true_warp, y_pred_warp, y_true_weft, y_pred_weft)
    ]
    pct_both_within_2 = (
        round(float(sum(both_within_2) / len(both_within_2) * 100.0), 2)
        if both_within_2
        else 0.0
    )

    return {
        "warp": warp_metrics,
        "weft": weft_metrics,
        "composite": {
            "mean_mae": round((warp_metrics["mae"] + weft_metrics["mae"]) / 2.0, 4),
            "pct_both_within_2": pct_both_within_2,
        },
    }
