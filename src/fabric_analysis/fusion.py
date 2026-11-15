# ==============================================================================
# Warp & Weft AI — Multi-Estimator Evidence Fusion & Uncertainty Module
# ==============================================================================
# The mechanistic justification for this step is: cross-evaluate spatial projection
# and frequency-domain spectral evidence against physical weave topology constraints,
# reject false certainty when estimators diverge, and separate linear thread count sum
# (threads/cm) from true areal yarn intersection density (crossings/cm²).

from typing import Tuple, Dict, Any, Optional
import numpy as np


def evaluate_evidence_fusion(
    warp_fft: float,
    weft_fft: float,
    warp_proj: float,
    weft_proj: float,
    spnr_x: float,
    spnr_y: float,
    rect_variance: float,
    warp_dispersion: float,
    weft_dispersion: float,
    weave_hint: str = "auto",
    max_agreement_delta: float = 2.5
) -> Dict[str, Any]:
    """
    The mechanistic justification for this step is: validate concordance between
    Fourier harmonic peaks and spatial projection intervals without automatically
    defaulting to FFT on disagreement, producing explicit validation states.
    """
    delta_w = abs(warp_fft - warp_proj)
    delta_wf = abs(weft_fft - weft_proj)

    # 1. Evaluate Axis-Specific Agreement
    warp_agrees = (delta_w <= max_agreement_delta) or (delta_w / max(warp_fft, 1.0) <= 0.06)
    weft_agrees = (delta_wf <= max_agreement_delta) or (delta_wf / max(weft_fft, 1.0) <= 0.06)

    # 2. Decision Logic Branching
    if warp_agrees and weft_agrees:
        # High concordance: consensus average of both independent estimators
        final_warp = round(0.5 * (warp_fft + warp_proj), 1)
        final_weft = round(0.5 * (weft_fft + weft_proj), 1)
        decision_status = "VALIDATED"
        engine_mode = "Dual-Engine Consensus (Verified)"
        rationale = f"Both engines concordant (Δ_warp={delta_w:.1f}, Δ_weft={delta_wf:.1f} ends/cm)."

    elif weave_hint in ("twill", "satin"):
        # Weave float structure known: examine if projection overcounts due to float subpeaks
        # or if FFT resolves fundamental spacing
        if warp_dispersion > 0.25 and spnr_x >= 4.0:
            final_warp = round(warp_fft, 1)
            warp_src = "2D FFT (Float Subpeak Rejection)"
        else:
            final_warp = round(warp_proj, 1) if warp_agrees else round(warp_fft, 1)
            warp_src = "Hybrid Arbiter"

        if weft_dispersion > 0.25 and spnr_y >= 4.0:
            final_weft = round(weft_fft, 1)
            weft_src = "2D FFT (Float Subpeak Rejection)"
        else:
            final_weft = round(weft_proj, 1) if weft_agrees else round(weft_fft, 1)
            weft_src = "Hybrid Arbiter"

        decision_status = "CONSISTENT_WITH_WARNING"
        engine_mode = f"Weave-Aware Fusion ({warp_src} / {weft_src})"
        rationale = (f"Weave architecture ({weave_hint}) introduces float structures. "
                     f"Selected frequency harmonics based on SPNR and interval dispersion.")

    elif warp_agrees or weft_agrees:
        # Partial agreement: one axis is verified, the other exhibits discrepancy
        final_warp = round(0.5 * (warp_fft + warp_proj), 1) if warp_agrees else round(warp_fft, 1)
        final_weft = round(0.5 * (weft_fft + weft_proj), 1) if weft_agrees else round(weft_fft, 1)
        decision_status = "CONSISTENT_WITH_WARNING"
        engine_mode = "Partial Axis Consensus"
        discrepant_axis = "Weft" if warp_agrees else "Warp"
        rationale = f"{discrepant_axis} axis diverged (Δ={max(delta_w, delta_wf):.1f}). Result requires visual audit."

    else:
        # Complete divergence: flag as unvalidated rather than presenting false certainty
        final_warp = round(warp_fft, 1)
        final_weft = round(weft_fft, 1)
        decision_status = "NEEDS_REVIEW"
        engine_mode = "Discrepancy Flagged (Unvalidated)"
        rationale = (f"Estimators diverged significantly (Δ_warp={delta_w:.1f}, Δ_weft={delta_wf:.1f}). "
                     f"Both FFT and Projection candidates retained for manual verification.")

    # 3. Honest Signal Quality Index (SQI)
    mean_spnr = 0.5 * (spnr_x + spnr_y)
    spnr_factor = min(1.0, mean_spnr / 10.0)
    contrast_factor = min(1.0, rect_variance / 0.15)
    discrepancy_factor = max(0.0, 1.0 - (delta_w + delta_wf) / 8.0)
    regularity_factor = max(0.0, 1.0 - 0.5 * (warp_dispersion + weft_dispersion))

    sqi = (0.30 * spnr_factor +
           0.25 * contrast_factor +
           0.30 * discrepancy_factor +
           0.15 * regularity_factor) * 100.0
    sqi = float(np.clip(sqi, 5.0, 99.5))

    # 4. Strict Density Semantics
    final_warp_int = int(round(final_warp))
    final_weft_int = int(round(final_weft))
    # Linear sum: threads per centimeter along both directions (threads/cm)
    linear_density_sum = round(final_warp + final_weft, 1)
    # Areal intersection density: physical yarn crossings per square centimeter (crossings/cm²)
    areal_density = round(float(final_warp_int * final_weft_int), 1)

    # 5. Physical Yarn Pitches
    pitch_warp_um = round((10000.0 / final_warp), 2) if final_warp > 0 else 0.0
    pitch_weft_um = round((10000.0 / final_weft), 2) if final_weft > 0 else 0.0

    return {
        "warp_density_ends_per_cm": int(round(final_warp)),
        "weft_density_picks_per_cm": int(round(final_weft)),
        "warp_density_continuous": float(final_warp),
        "weft_density_continuous": float(final_weft),
        "linear_density_sum_per_cm": float(linear_density_sum),
        "areal_intersection_density_per_cm2": float(areal_density),
        "pitch_warp_um": float(pitch_warp_um),
        "pitch_weft_um": float(pitch_weft_um),
        "decision_status": decision_status,
        "engine_mode": engine_mode,
        "signal_quality_index": round(float(sqi), 1),
        "confidence_score": round(float(sqi), 1),  # Backward compatibility alias
        "delta_warp": round(float(delta_w), 2),
        "delta_weft": round(float(delta_wf), 2),
        "decision_rationale": rationale
    }
