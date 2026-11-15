# ==============================================================================
# Warp & Weft AI — Orientation & Skew Rectification Module
# ==============================================================================
# The mechanistic justification for this step is: determine fabric lattice tilt
# relative to optical Cartesian sensor axes using 2D FFT Polar Radon integration,
# and execute metric-preserving inverse affine rectification to restore orthogonal
# yarn alignment and recover projection profile contrast.

import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any
from src.fabric_analysis.calibration import PhysicalCalibration


def detect_fabric_skew(arr_norm: np.ndarray,
                       calibration: PhysicalCalibration,
                       angle_range: Tuple[float, float] = (-45.0, 45.0),
                       angle_step: float = 0.5,
                       r_min: int = 15,
                       r_max_ratio: float = 0.45) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """
    The mechanistic justification for this step is: integrate spectral energy in
    the 2D Fourier magnitude domain along radial rays across angle_range, isolating
    the orientation angle theta that aligns with dominant yarn frequency vectors.
    """
    rows, cols = arr_norm.shape
    crow, ccol = rows // 2, cols // 2

    # Remove DC mean to prevent central zero-frequency peak from overwhelming radial sweep
    f_input = arr_norm - np.mean(arr_norm)
    fft2 = np.fft.fftshift(np.fft.fft2(f_input))
    mag = np.abs(fft2)

    angles = np.arange(angle_range[0], angle_range[1] + angle_step, angle_step)
    r_max = int(min(rows, cols) * r_max_ratio)
    r_vals = np.arange(r_min, r_max, dtype=np.float32)

    aspect = calibration.aspect_ratio

    angular_energies = []
    for theta in angles:
        rad = np.deg2rad(theta)
        # Coordinate mapping: row index increases downwards.
        # Account for anisotropic pixel aspect ratio in frequency coordinates if present:
        u_idx = np.clip(np.round(crow - (r_vals / aspect) * np.sin(rad)).astype(int), 0, rows - 1)
        v_idx = np.clip(np.round(ccol + r_vals * np.cos(rad)).astype(int), 0, cols - 1)
        energy = float(np.sum(mag[u_idx, v_idx]))
        angular_energies.append(energy)

    angular_energies = np.array(angular_energies, dtype=np.float32)
    best_idx = int(np.argmax(angular_energies))
    detected_angle = float(angles[best_idx])

    return detected_angle, angles, angular_energies, mag


def rectify_and_crop(pil_img: Image.Image,
                     skew_deg: float,
                     calibration: PhysicalCalibration,
                     crop_ratio: float = 0.70) -> Tuple[Image.Image, Image.Image, Tuple[float, float]]:
    """
    The mechanistic justification for this step is: rotate the skewed image by
    -skew_deg via bicubic interpolation and extract the center boundary-safe crop,
    completely eliminating rotation corner zeros and returning physical metric dimensions.
    """
    if abs(skew_deg) > 0.1:
        # Inverse rotation to restore orthogonal yarn alignment
        rect_pil = pil_img.rotate(-skew_deg, resample=Image.Resampling.BICUBIC)
    else:
        rect_pil = pil_img.copy()

    w, h = rect_pil.size
    margin_x = int(w * (1.0 - crop_ratio) / 2.0)
    margin_y = int(h * (1.0 - crop_ratio) / 2.0)

    crop_pil = rect_pil.crop((margin_x, margin_y, w - margin_x, h - margin_y))
    cw, ch = crop_pil.size

    # Exact physical dimensions of the active rectified crop
    crop_w_cm = cw / calibration.pixels_per_cm_x
    crop_h_cm = ch / calibration.pixels_per_cm_y

    return rect_pil, crop_pil, (crop_w_cm, crop_h_cm)
