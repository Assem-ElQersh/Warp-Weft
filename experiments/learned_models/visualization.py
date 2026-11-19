# The mechanistic justification for this step is: generate publication-grade visual metrology artifacts—including Bland-Altman agreement plots with 95% Limits of Agreement, error distribution histograms, and centerline segmentation overlays—providing human-verifiable evidence for physical thread density measurements.

import os
from typing import List, Optional, Tuple, Union

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_bland_altman(
    y_true: Union[List[float], np.ndarray],
    y_pred: Union[List[float], np.ndarray],
    title: str,
    save_path: str,
    unit: str = "threads/cm",
) -> None:
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)

    mean_vals = (yt + yp) / 2.0
    diffs = yp - yt

    mean_diff = float(np.mean(diffs))
    std_diff = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
    loa_upper = mean_diff + 1.96 * std_diff
    loa_lower = mean_diff - 1.96 * std_diff

    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
    ax.scatter(mean_vals, diffs, alpha=0.7, edgecolors="none", color="#1f77b4")
    ax.axhline(mean_diff, color="#d62728", linestyle="--", label=f"Mean Bias ({mean_diff:+.2f})")
    ax.axhline(loa_upper, color="#2ca02c", linestyle=":", label=f"+1.96 SD ({loa_upper:+.2f})")
    ax.axhline(loa_lower, color="#2ca02c", linestyle=":", label=f"-1.96 SD ({loa_lower:+.2f})")

    ax.set_xlabel(f"Mean Measurement ({unit})")
    ax.set_ylabel(f"Difference: Pred - True ({unit})")
    ax.set_title(title)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)


def plot_scatter_agreement(
    y_true: Union[List[float], np.ndarray],
    y_pred: Union[List[float], np.ndarray],
    title: str,
    save_path: str,
    tolerance: float = 2.0,
    unit: str = "threads/cm",
) -> None:
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)

    min_val = min(float(np.min(yt)), float(np.min(yp))) - 2.0
    max_val = max(float(np.max(yt)), float(np.max(yp))) + 2.0

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.scatter(yt, yp, alpha=0.7, color="#1f77b4", label="Specimens")

    # Ideal 1:1 line
    line_x = np.linspace(min_val, max_val, 100)
    ax.plot(line_x, line_x, color="black", linestyle="-", label="Ideal 1:1 Line")
    ax.plot(line_x, line_x + tolerance, color="red", linestyle="--", label=f"+/- {tolerance} {unit}")
    ax.plot(line_x, line_x - tolerance, color="red", linestyle="--")
    ax.fill_between(line_x, line_x - tolerance, line_x + tolerance, color="red", alpha=0.1)

    ax.set_xlabel(f"Ground Truth ({unit})")
    ax.set_ylabel(f"Predicted ({unit})")
    ax.set_title(title)
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.5)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)


def create_segmentation_overlay(
    image: np.ndarray, mask: np.ndarray, alpha: float = 0.4
) -> np.ndarray:
    if image.dtype != np.uint8:
        img_u8 = np.clip(image * 255.0, 0, 255).astype(np.uint8)
    else:
        img_u8 = image.copy()

    if img_u8.ndim == 2:
        base_rgb = cv2.cvtColor(img_u8, cv2.COLOR_GRAY2RGB)
    else:
        base_rgb = img_u8.copy()

    # Color mapping: 0=background, 1=warp (blue/cyan), 2=weft (orange/magenta)
    h, w = mask.shape[:2]
    overlay = np.zeros((h, w, 3), dtype=np.uint8)
    overlay[mask == 1] = [0, 165, 255]  # Warp: Orange
    overlay[mask == 2] = [255, 0, 128]  # Weft: Magenta

    blended = cv2.addWeighted(base_rgb, 1.0 - alpha, overlay, alpha, 0)
    return blended
