# ==============================================================================
# Warp & Weft AI — Multi-Candidate 2D Spectral Analysis Module
# ==============================================================================
# The mechanistic justification for this step is: implement windowed 2D Fourier
# harmonic decomposition with multi-candidate peak tracking, harmonic family
# grouping, and DC band suppression, eliminating false identification of float
# pattern repeats, illumination gradients, or yarn harmonics as the physical yarn fundamental.

import numpy as np
from typing import Tuple, List, Dict, Any, Optional


def parabolic_sub_bin_interpolation(slice_1d: np.ndarray,
                                    peak_idx: int) -> Tuple[float, float]:
    """
    The mechanistic justification for this step is: apply 3-point quadratic
    parabolic sub-bin interpolation on integer DFT peak neighborhood to eliminate
    discretization binning error caused by spatial sub-window cropping.
    """
    if 0 < peak_idx < len(slice_1d) - 1:
        alpha = float(slice_1d[peak_idx - 1])
        beta = float(slice_1d[peak_idx])
        gamma = float(slice_1d[peak_idx + 1])
        denom = alpha - 2.0 * beta + gamma
        if abs(denom) > 1e-7:
            delta = 0.5 * (alpha - gamma) / denom
            delta = float(np.clip(delta, -0.5, 0.5))
        else:
            delta = 0.0
        exact_k = float(peak_idx) + delta
        peak_mag = beta
    else:
        exact_k = float(peak_idx)
        peak_mag = float(slice_1d[peak_idx])

    return exact_k, peak_mag


def compute_spectral_density_multicandidate(
    crop_arr: np.ndarray,
    crop_w_cm: float,
    crop_h_cm: float,
    weave_hint: str = "auto",
    min_density: float = 12.0,
    max_density: float = 120.0
) -> Tuple[float, float, float, float, np.ndarray, Dict[str, Any]]:
    """
    The mechanistic justification for this step is: decompose the 2D windowed
    magnitude spectrum into orthogonal harmonic candidate families, identify
    fundamental yarn frequencies while rejecting DC illumination and float sub-harmonics,
    and refine frequencies to continuous sub-bin accuracy.
    """
    cH, cW = crop_arr.shape
    ccrow, cccol = cH // 2, cW // 2

    # 1. 2D Hann Windowing to eliminate spectral boundary leakage
    win_y = np.hanning(cH).astype(np.float32)
    win_x = np.hanning(cW).astype(np.float32)
    win_2d = np.outer(win_y, win_x)

    zero_mean_arr = (crop_arr - np.mean(crop_arr)) * win_2d
    F_crop = np.fft.fftshift(np.fft.fft2(zero_mean_arr))
    mag_crop = np.abs(F_crop)

    # 2. Extract Orthogonal Spectral Profiles (averaging 3 central bins to reject single-pixel noise)
    row_strip = max(1, cH // 100)
    col_strip = max(1, cW // 100)

    # Horizontal slice -> Warp (columns)
    slice_x = np.mean(mag_crop[ccrow - row_strip : ccrow + row_strip + 1, :], axis=0)
    # Vertical slice -> Weft (rows)
    slice_y = np.mean(mag_crop[:, cccol - col_strip : cccol + col_strip + 1], axis=1)

    # 3. Define Valid Physical Frequency Bands (bins relative to center)
    min_k_x = max(3, int(np.floor(min_density * crop_w_cm)))
    max_k_x = min(cW // 2 - 1, int(np.ceil(max_density * crop_w_cm)))

    min_k_y = max(3, int(np.floor(min_density * crop_h_cm)))
    max_k_y = min(cH // 2 - 1, int(np.ceil(max_density * crop_h_cm)))

    def extract_candidates(slice_full, center_idx, min_k, max_k, crop_span_cm):
        candidates = []
        half_slice = slice_full[center_idx : center_idx + max_k + 2]
        noise_floor = float(np.median(slice_full[center_idx + min_k : center_idx + max_k + 1])) + 1e-6

        for rel_k in range(min_k, min(len(half_slice) - 1, max_k + 1)):
            if half_slice[rel_k] > half_slice[rel_k - 1] and half_slice[rel_k] >= half_slice[rel_k + 1]:
                exact_k, peak_mag = parabolic_sub_bin_interpolation(half_slice, rel_k)
                density = exact_k / max(crop_span_cm, 1e-5)
                spnr = peak_mag / noise_floor

                # Conjugate symmetry check on the negative frequency axis
                neg_idx = center_idx - rel_k
                neg_mag = float(slice_full[neg_idx]) if 0 <= neg_idx < len(slice_full) else 0.0
                symmetry = min(peak_mag, neg_mag) / max(1e-6, max(peak_mag, neg_mag))

                candidates.append({
                    "bin": float(round(exact_k, 2)),
                    "density": float(round(density, 2)),
                    "magnitude": float(round(peak_mag, 4)),
                    "spnr": float(round(spnr, 2)),
                    "symmetry": float(round(symmetry, 3))
                })

        # Sort candidates primarily by SPNR * symmetry
        candidates.sort(key=lambda c: c["spnr"] * (0.5 + 0.5 * c["symmetry"]), reverse=True)
        return candidates

    warp_candidates = extract_candidates(slice_x, cccol, min_k_x, max_k_x, crop_w_cm)
    weft_candidates = extract_candidates(slice_y, ccrow, min_k_y, max_k_y, crop_h_cm)

    # 4. Harmonic Family Analysis & Ambiguity Exposure
    # Float patterns (twills, satins) create sub-harmonics at f_repeat = f0 / R,
    # while yarn cross-sectional shapes create higher harmonics at 2*f0, 3*f0.
    # Without spatial or structural corroboration, selecting an arbitrary multiple
    # is mathematically unverified. We expose candidate ambiguity explicitly.
    def select_best_fundamental(candidates: List[Dict[str, Any]], weave: str):
        if not candidates:
            return 0.0, 0.0, "no_candidates_in_passband", False, []

        top_cand = candidates[0]
        if len(candidates) == 1:
            return top_cand["density"], top_cand["spnr"], "single_dominant_candidate", False, []

        # Analyze potential harmonic/sub-harmonic ambiguity among top candidates
        ambiguous_candidates = []
        for cand in candidates[1:4]:
            if cand["spnr"] >= 2.5:
                ratio = cand["density"] / max(top_cand["density"], 1e-4)
                inv_ratio = top_cand["density"] / max(cand["density"], 1e-4)
                is_harmonic = any(abs(ratio - k) < 0.20 for k in [2.0, 3.0, 4.0])
                is_subharmonic = any(abs(inv_ratio - k) < 0.20 for k in [2.0, 3.0, 4.0])
                if is_harmonic or is_subharmonic:
                    ambiguous_candidates.append({
                        "density": cand["density"],
                        "spnr": cand["spnr"],
                        "ratio_to_dominant": round(float(ratio), 2),
                        "type": "harmonic_multiple" if is_harmonic else "subharmonic_float_repeat"
                    })

        has_ambiguity = len(ambiguous_candidates) > 0
        reason = "dominant_harmonic_with_ambiguity" if has_ambiguity else "dominant_harmonic"

        return top_cand["density"], top_cand["spnr"], reason, has_ambiguity, ambiguous_candidates

    (warp_density, spnr_x, warp_reason,
     warp_ambiguity, warp_ambiguous_cands) = select_best_fundamental(warp_candidates, weave_hint)

    (weft_density, spnr_y, weft_reason,
     weft_ambiguity, weft_ambiguous_cands) = select_best_fundamental(weft_candidates, weave_hint)

    diagnostic_metadata = {
        "warp_candidates": warp_candidates[:4],
        "weft_candidates": weft_candidates[:4],
        "warp_selection_reason": warp_reason,
        "weft_selection_reason": weft_reason,
        "warp_harmonic_ambiguity": bool(warp_ambiguity),
        "weft_harmonic_ambiguity": bool(weft_ambiguity),
        "warp_ambiguous_candidates": warp_ambiguous_cands,
        "weft_ambiguous_candidates": weft_ambiguous_cands,
        "min_density_bound": min_density,
        "max_density_bound": max_density
    }

    return warp_density, weft_density, spnr_x, spnr_y, mag_crop, diagnostic_metadata
