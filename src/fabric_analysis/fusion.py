# ==============================================================================
# Warp & Weft AI — Multi-Estimator Evidence Fusion & Uncertainty Module
# ==============================================================================
# The mechanistic justification for this step is: cross-evaluate spatial projection
# and frequency-domain spectral evidence against physical weave aperture constraints,
# reject false certainty when estimators diverge, strictly separate verified consensus
# measurements from unvalidated candidates, and eliminate ungrounded relative 6% tolerances.

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
    crop_w_cm: float = 0.40,
    crop_h_cm: float = 0.40,
    max_agreement_delta: Optional[float] = None
) -> Dict[str, Any]:
    """
    The mechanistic justification for this step is: validate concordance between
    Fourier harmonic peaks and spatial projection intervals using physical aperture
    quantization limits Delta_quant = max(2.0, 1.0 / L_roi) rather than arbitrary
    percentage tolerances. If an axis fails concordance or exhibits degraded SPNR / high
    spatial dispersion, its accepted measurement is set to None and candidate values
    are retained explicitly under candidate_measurements to prevent false certainty.
    """
    delta_w = abs(warp_fft - warp_proj)
    delta_wf = abs(weft_fft - weft_proj)

    # 1. Physically Grounded Acceptance Policy
    # Physical aperture quantization limit: Delta = 1.0 / L_roi (e.g. 2.5 ends/cm for 0.4 cm)
    tol_warp = max_agreement_delta if max_agreement_delta is not None else max(2.0, 1.0 / max(crop_w_cm, 0.1))
    tol_weft = max_agreement_delta if max_agreement_delta is not None else max(2.0, 1.0 / max(crop_h_cm, 0.1))

    # An axis is concordant if:
    # 1. Spatial and spectral estimates agree within aperture quantization tolerance
    # 2. Both candidates are above physical floor (5.0 ends/cm)
    # 3. Frequency domain peak has adequate SPNR (>= 3.0)
    # 4. Spatial peak intervals are sufficiently regular (dispersion <= 0.30)
    warp_valid = (
        (delta_w <= tol_warp) and
        (warp_fft >= 5.0) and (warp_proj >= 5.0) and
        (spnr_x >= 3.0) and
        (warp_dispersion <= 0.30)
    )

    weft_valid = (
        (delta_wf <= tol_weft) and
        (weft_fft >= 5.0) and (weft_proj >= 5.0) and
        (spnr_y >= 3.0) and
        (weft_dispersion <= 0.30)
    )

    # 2. Decision Logic Branching & Accepted vs Candidate Separation
    accepted_warp: Optional[float] = None
    accepted_weft: Optional[float] = None
    is_validated = False

    if warp_valid and weft_valid:
        accepted_warp = round(0.5 * (warp_fft + warp_proj), 1)
        accepted_weft = round(0.5 * (weft_fft + weft_proj), 1)
        decision_status = "VALIDATED"
        is_validated = True
        engine_mode = "Dual-Engine Consensus (Verified)"
        rationale = (f"Both engines concordant within physical aperture quantization limit "
                     f"(Δ_warp={delta_w:.1f} <= {tol_warp:.1f}, Δ_weft={delta_wf:.1f} <= {tol_weft:.1f} ends/cm).")

    elif warp_valid or weft_valid:
        decision_status = "CONSISTENT_WITH_WARNING"
        is_validated = False
        if warp_valid:
            accepted_warp = round(0.5 * (warp_fft + warp_proj), 1)
            accepted_weft = None
            engine_mode = "Partial Axis Consensus (Warp Verified, Weft Divergent)"
            rationale = (f"Warp axis concordant (Δ={delta_w:.1f} ends/cm). "
                         f"Weft axis diverged (Δ={delta_wf:.1f} > {tol_weft:.1f} picks/cm) and requires review.")
        else:
            accepted_warp = None
            accepted_weft = round(0.5 * (weft_fft + weft_proj), 1)
            engine_mode = "Partial Axis Consensus (Weft Verified, Warp Divergent)"
            rationale = (f"Weft axis concordant (Δ={delta_wf:.1f} picks/cm). "
                         f"Warp axis diverged (Δ={delta_w:.1f} > {tol_warp:.1f} ends/cm) and requires review.")

    else:
        decision_status = "NEEDS_REVIEW"
        is_validated = False
        accepted_warp = None
        accepted_weft = None
        engine_mode = "Discrepancy Flagged (Unvalidated)"
        rationale = (f"Estimators diverged beyond aperture tolerance "
                     f"(Δ_warp={delta_w:.1f} vs {tol_warp:.1f}, Δ_weft={delta_wf:.1f} vs {tol_weft:.1f}). "
                     f"Both FFT and Projection candidates retained for visual inspection.")

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

    # 4. Strict Density Semantics & Derived Metrics
    accepted_warp_int = int(round(accepted_warp)) if accepted_warp is not None else None
    accepted_weft_int = int(round(accepted_weft)) if accepted_weft is not None else None

    if accepted_warp is not None and accepted_weft is not None:
        linear_density_sum: Optional[float] = round(accepted_warp + accepted_weft, 1)
        areal_density: Optional[float] = round(float(accepted_warp_int * accepted_weft_int), 1)
    else:
        linear_density_sum = None
        areal_density = None

    pitch_warp_um = round((10000.0 / accepted_warp), 2) if (accepted_warp is not None and accepted_warp > 0) else None
    pitch_weft_um = round((10000.0 / accepted_weft), 2) if (accepted_weft is not None and accepted_weft > 0) else None

    # Candidate measurements dict (always populated)
    candidate_measurements = {
        "warp_fft": round(float(warp_fft), 2),
        "warp_proj": round(float(warp_proj), 2),
        "weft_fft": round(float(weft_fft), 2),
        "weft_proj": round(float(weft_proj), 2),
        "delta_warp": round(float(delta_w), 2),
        "delta_weft": round(float(delta_wf), 2),
        "warp_concordant": bool(warp_valid),
        "weft_concordant": bool(weft_valid),
        "tolerance_warp": round(float(tol_warp), 2),
        "tolerance_weft": round(float(tol_weft), 2)
    }

    return {
        "accepted_warp_density_ends_per_cm": accepted_warp_int,
        "accepted_weft_density_picks_per_cm": accepted_weft_int,
        "warp_density_ends_per_cm": accepted_warp_int,
        "weft_density_picks_per_cm": accepted_weft_int,
        "warp_ends_per_cm": accepted_warp_int,
        "weft_picks_per_cm": accepted_weft_int,
        "warp_density_continuous": accepted_warp,
        "weft_density_continuous": accepted_weft,
        "is_validated": is_validated,
        "linear_density_sum_per_cm": linear_density_sum,
        "areal_intersection_density_per_cm2": areal_density,
        "pitch_warp_um": pitch_warp_um,
        "pitch_weft_um": pitch_weft_um,
        "decision_status": decision_status,
        "engine_mode": engine_mode,
        "signal_quality_index": round(float(sqi), 1),
        "confidence_score": round(float(sqi), 1),
        "delta_warp": round(float(delta_w), 2),
        "delta_weft": round(float(delta_wf), 2),
        "decision_rationale": rationale,
        "candidate_measurements": candidate_measurements
    }
