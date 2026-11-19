# The mechanistic justification for this step is: implement rigorous metrology calibration mathematics to convert pixel spatial periods to physical thread densities (D = S / Delta) and propagate optical calibration uncertainties via partial derivative error propagation.

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass
class DensityMeasurement:
    density: float  # threads/cm
    uncertainty: float  # threads/cm (1-sigma)
    relative_uncertainty_pct: float
    pitch_px: float
    scale_px_per_cm: float


def calculate_density_with_uncertainty(
    pitch_px: float,
    scale_px_per_cm: float,
    pitch_std_px: float = 0.5,
    scale_uncertainty_pct: float = 2.0,
) -> DensityMeasurement:
    if pitch_px <= 0 or scale_px_per_cm <= 0:
        return DensityMeasurement(0.0, 0.0, 0.0, pitch_px, scale_px_per_cm)

    density = float(scale_px_per_cm / pitch_px)
    sigma_s = scale_px_per_cm * (scale_uncertainty_pct / 100.0)
    sigma_delta = pitch_std_px

    # Error propagation: (sigma_D / D)^2 = (sigma_S / S)^2 + (sigma_delta / delta)^2
    rel_s = sigma_s / scale_px_per_cm
    rel_delta = sigma_delta / pitch_px
    rel_total = math.sqrt(rel_s**2 + rel_delta**2)
    uncertainty = density * rel_total

    return DensityMeasurement(
        density=density,
        uncertainty=uncertainty,
        relative_uncertainty_pct=rel_total * 100.0,
        pitch_px=pitch_px,
        scale_px_per_cm=scale_px_per_cm,
    )


def two_point_ruler_to_scale(
    pt1: Tuple[float, float], pt2: Tuple[float, float], physical_distance_cm: float = 1.0
) -> float:
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    pixel_dist = math.sqrt(dx * dx + dy * dy)
    assert physical_distance_cm > 0, "Physical distance must be positive"
    return float(pixel_dist / physical_distance_cm)


def compute_planar_homography(
    src_points: np.ndarray,
    target_width_cm: float,
    target_height_cm: float,
    scale_px_per_cm: float = 300.0,
) -> Tuple[np.ndarray, Tuple[int, int]]:
    # src_points: 4x2 array of corner coordinates (top-left, top-right, bottom-right, bottom-left)
    w_px = int(round(target_width_cm * scale_px_per_cm))
    h_px = int(round(target_height_cm * scale_px_per_cm))

    dst_points = np.array(
        [[0, 0], [w_px - 1, 0], [w_px - 1, h_px - 1], [0, h_px - 1]], dtype=np.float32
    )

    h_matrix, _ = cv2.findHomography(src_points.astype(np.float32), dst_points)
    return h_matrix, (w_px, h_px)


def rectify_perspective(
    image: np.ndarray, homography_matrix: np.ndarray, output_shape: Tuple[int, int]
) -> np.ndarray:
    w_px, h_px = output_shape
    return cv2.warpPerspective(image, homography_matrix, (w_px, h_px), flags=cv2.INTER_LINEAR)
