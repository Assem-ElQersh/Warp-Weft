# ==============================================================================
# Warp & Weft AI — Directional Spatial Projection & Pitch Estimation Module
# ==============================================================================
# The mechanistic justification for this step is: integrate 2D textile pixel
# arrays along orthogonal axes into marginal 1D intensity waveforms, localize
# individual yarn crowns with adaptive prominence thresholding, and calculate
# calibrated center-to-center yarn pitch using robust median interval statistics
# to eliminate boundary quantization and endpoint truncation errors.

import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from src.fabric_analysis.calibration import PhysicalCalibration


def median_filter_1d(signal: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    The mechanistic justification for this step is: apply a 3-tap rank-median
    filter to remove single-pixel fiber hairiness micro-spikes without blurring
    underlying yarn crown summits.
    """
    pad = kernel_size // 2
    padded = np.pad(signal, pad, mode="edge")
    filtered = np.zeros_like(signal)
    for i in range(len(signal)):
        filtered[i] = np.median(padded[i : i + kernel_size])
    return filtered


def find_prominent_peaks_adaptive(signal: np.ndarray,
                                  min_dist: int = 3,
                                  prominence: float = 0.012) -> List[int]:
    """
    The mechanistic justification for this step is: identify structural yarn crowns
    by verifying that candidate local maxima exceed both an adaptive spatial distance
    constraint and optical contrast prominence relative to neighboring troughs.
    """
    n = len(signal)
    peaks = []
    for i in range(1, n - 1):
        if signal[i] > signal[i - 1] and signal[i] >= signal[i + 1]:
            left_w = max(0, i - min_dist)
            right_w = min(n, i + min_dist + 1)
            left_min = np.min(signal[left_w:i]) if i > left_w else signal[i]
            right_min = np.min(signal[i + 1 : right_w]) if right_w > i + 1 else signal[i]
            prom = signal[i] - max(left_min, right_min)
            if prom >= prominence:
                if not peaks or (i - peaks[-1]) >= min_dist:
                    peaks.append(i)
                elif signal[i] > signal[peaks[-1]]:
                    peaks[-1] = i
    return peaks


def compute_spatial_projection_density(
    crop_arr: np.ndarray,
    calibration: PhysicalCalibration,
    crop_w_cm: float,
    crop_h_cm: float,
    prominence: float = 0.012,
    max_density_bound: float = 120.0
) -> Tuple[float, float, List[int], List[int], np.ndarray, np.ndarray, float, float, float, Dict[str, Any]]:
    """
    The mechanistic justification for this step is: extract column and row projections,
    determine peak centers, calculate robust inter-peak interval statistics (median pitch,
    dispersion, active span density), and report physical yarn dimensions in micrometers.
    """
    sx = calibration.pixels_per_cm_x
    sy = calibration.pixels_per_cm_y

    # 1. Marginal Projections
    p_warp_raw = np.mean(crop_arr, axis=0)  # Down columns -> Warp waveform
    p_weft_raw = np.mean(crop_arr, axis=1)  # Across rows -> Weft waveform

    # 2. 1D Median Filtering
    p_warp = median_filter_1d(p_warp_raw, kernel_size=3)
    p_weft = median_filter_1d(p_weft_raw, kernel_size=3)

    # 3. Adaptive Minimum Peak Separation
    min_dist_x = max(3, int(round(0.40 * sx / max_density_bound)))
    min_dist_y = max(3, int(round(0.40 * sy / max_density_bound)))

    # 4. Prominence Peak Detection
    warp_peaks = find_prominent_peaks_adaptive(p_warp, min_dist=min_dist_x, prominence=prominence)
    weft_peaks = find_prominent_peaks_adaptive(p_weft, min_dist=min_dist_y, prominence=prominence)

    def analyze_intervals(peaks, scale_px_cm, crop_span_cm):
        if len(peaks) < 2:
            return 0.0, 0.0, 0.0, 0.0, "insufficient_peaks"

        intervals = np.diff(peaks).astype(np.float32)
        med_pitch_px = float(np.median(intervals))
        q75, q25 = np.percentile(intervals, [75, 25])
        iqr = float(q75 - q25)
        dispersion = float(iqr / max(med_pitch_px, 1e-4))

        # Pitch-based density (ends/cm)
        density_pitch = scale_px_cm / max(med_pitch_px, 1e-4)

        # Active span density (peaks over exact span between first and last detected crown)
        span_px = float(peaks[-1] - peaks[0])
        span_cm = span_px / scale_px_cm
        density_span = (len(peaks) - 1) / max(span_cm, 1e-4)

        # Physical center-to-center pitch in micrometers
        pitch_um = 10000.0 / density_pitch

        return density_pitch, density_span, pitch_um, dispersion, "success"

    (warp_pitch_density, warp_span_density, pitch_warp_um,
     warp_dispersion, status_w) = analyze_intervals(warp_peaks, sx, crop_w_cm)

    (weft_pitch_density, weft_span_density, pitch_weft_um,
     weft_dispersion, status_wf) = analyze_intervals(weft_peaks, sy, crop_h_cm)

    # Traditional raw peak count / crop_span for legacy audit comparison
    raw_warp_count = len(warp_peaks) / max(crop_w_cm, 1e-5)
    raw_weft_count = len(weft_peaks) / max(crop_h_cm, 1e-5)

    # Use pitch-based density as authoritative spatial estimate when dispersion is low (< 0.25)
    final_warp_spatial = warp_pitch_density if warp_dispersion <= 0.25 and warp_pitch_density > 0 else raw_warp_count
    final_weft_spatial = weft_pitch_density if weft_dispersion <= 0.25 and weft_pitch_density > 0 else raw_weft_count

    var_warp = float(np.var(p_warp))
    var_weft = float(np.var(p_weft))
    rect_variance = 0.5 * (var_warp + var_weft)

    spatial_diagnostics = {
        "warp_peaks_count": len(warp_peaks),
        "weft_peaks_count": len(weft_peaks),
        "warp_pitch_density": round(float(warp_pitch_density), 2),
        "weft_pitch_density": round(float(weft_pitch_density), 2),
        "warp_span_density": round(float(warp_span_density), 2),
        "weft_span_density": round(float(weft_span_density), 2),
        "raw_warp_density": round(float(raw_warp_count), 2),
        "raw_weft_density": round(float(raw_weft_count), 2),
        "warp_interval_dispersion": round(float(warp_dispersion), 3),
        "weft_interval_dispersion": round(float(weft_dispersion), 3),
        "warp_profile_variance": round(float(var_warp), 5),
        "weft_profile_variance": round(float(var_weft), 5),
        "adaptive_min_dist_x": int(min_dist_x),
        "adaptive_min_dist_y": int(min_dist_y)
    }

    return (
        final_warp_spatial,
        final_weft_spatial,
        warp_peaks,
        weft_peaks,
        p_warp,
        p_weft,
        pitch_warp_um,
        pitch_weft_um,
        rect_variance,
        spatial_diagnostics
    )
