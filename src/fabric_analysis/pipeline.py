# ==============================================================================
# Warp & Weft AI — Authoritative Unified Pipeline
# ==============================================================================
# The mechanistic justification for this step is: provide a single, authoritative
# entry point for fabric thread density analysis shared identically by the production
# web server, REST API, benchmarks, notebooks, and automated regression test suite.

import io
import time
import base64
import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, Dict, Any, Optional

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.roi import extract_metric_roi
from src.fabric_analysis.orientation import detect_fabric_skew, rectify_and_crop
from src.fabric_analysis.spectral import compute_spectral_density_multicandidate
from src.fabric_analysis.spatial import compute_spatial_projection_density
from src.fabric_analysis.fusion import evaluate_evidence_fusion


def pil_to_base64_data_url(img_pil: Image.Image, max_size: int = 500) -> str:
    """Helper to convert PIL Image to Base64 PNG data URL."""
    w, h = img_pil.size
    if max(w, h) > max_size:
        scale = max_size / float(max(w, h))
        rendered = img_pil.resize((int(w * scale), int(h * scale)), Image.Resampling.BICUBIC)
    else:
        rendered = img_pil

    buf = io.BytesIO()
    rendered.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def render_waveform_plot_pillow(signal: np.ndarray,
                                peaks: list,
                                title: str,
                                width: int = 550,
                                height: int = 180) -> str:
    """Render a 1D projection waveform with peak crowns to Base64 PNG."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin_l, margin_r, margin_t, margin_b = 50, 20, 30, 30
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    draw.rectangle([margin_l, margin_t, width - margin_r, height - margin_b], outline=(220, 226, 235), width=1)
    for g in range(1, 4):
        gy = margin_t + int(g * plot_h / 4)
        draw.line([(margin_l, gy), (width - margin_r, gy)], fill=(240, 243, 248), width=1)

    s_min, s_max = float(np.min(signal)), float(np.max(signal))
    s_range = max(1e-4, s_max - s_min)
    n_pts = len(signal)

    coords = []
    for i in range(n_pts):
        px = margin_l + int(i * plot_w / max(1, n_pts - 1))
        py = margin_t + plot_h - int(((signal[i] - s_min) / s_range) * plot_h)
        coords.append((px, py))

    draw.line(coords, fill=(26, 86, 160), width=2)
    for p in peaks:
        px = margin_l + int(p * plot_w / max(1, n_pts - 1))
        py = margin_t + plot_h - int(((signal[p] - s_min) / s_range) * plot_h)
        draw.line([(px - 4, py - 4), (px + 4, py + 4)], fill=(220, 38, 38), width=2)
        draw.line([(px - 4, py + 4), (px + 4, py - 4)], fill=(220, 38, 38), width=2)

    draw.text((margin_l, 8), f"{title} (Peaks: {len(peaks)})", fill=(15, 43, 72))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def render_radon_plot_pillow(angles: np.ndarray,
                             energies: np.ndarray,
                             best_angle: float,
                             width: int = 550,
                             height: int = 180) -> str:
    """Render the Polar Radon radial energy sweep curve to Base64 PNG."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin_l, margin_r, margin_t, margin_b = 50, 20, 30, 30
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    draw.rectangle([margin_l, margin_t, width - margin_r, height - margin_b], outline=(220, 226, 235), width=1)

    e_min, e_max = float(np.min(energies)), float(np.max(energies))
    e_range = max(1e-4, e_max - e_min)
    n_pts = len(angles)

    coords = []
    best_px, best_py = margin_l, margin_t
    for i in range(n_pts):
        px = margin_l + int(i * plot_w / max(1, n_pts - 1))
        py = margin_t + plot_h - int(((energies[i] - e_min) / e_range) * plot_h)
        coords.append((px, py))
        if abs(angles[i] - best_angle) < 0.3:
            best_px, best_py = px, py

    draw.line(coords, fill=(16, 42, 114), width=2)
    draw.line([(best_px, margin_t), (best_px, height - margin_b)], fill=(220, 38, 38), width=2)
    draw.ellipse([best_px - 4, best_py - 4, best_px + 4, best_py + 4], fill=(220, 38, 38))
    draw.text((margin_l, 8), f"Polar Radon Energy Sweep (Peak: {best_angle:+.1f} deg)", fill=(15, 43, 72))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def render_fft_spectrum_image_pillow(mag: np.ndarray, width: int = 280, height: int = 280) -> str:
    """Render the 2D FFT magnitude spectrum to Base64 PNG."""
    log_mag = np.log1p(mag)
    l_min, l_max = np.min(log_mag), np.max(log_mag)
    norm = np.clip((log_mag - l_min) / max(1e-4, l_max - l_min), 0.0, 1.0)

    t = np.linspace(0.0, 1.0, 256)
    lut = np.zeros((256, 3), dtype=np.uint8)
    lut[:, 0] = np.clip(255 * (t ** 0.65 * 1.3), 0, 255).astype(np.uint8)
    lut[:, 1] = np.clip(255 * (t ** 1.8 * 1.5 - 0.08 * t), 0, 255).astype(np.uint8)
    lut[:, 2] = np.clip(255 * (np.sin(t * np.pi) * 0.75 + t ** 3.0 * 0.5), 0, 255).astype(np.uint8)

    indices = (norm * 255).astype(np.uint8)
    rgb = lut[indices]

    pil_img = Image.fromarray(rgb).resize((width, height), Image.Resampling.NEAREST)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def analyze_fabric(
    img_pil: Image.Image,
    calibration: Optional[PhysicalCalibration] = None,
    pixels_per_cm: Optional[float] = None,
    pixels_per_cm_y: Optional[float] = None,
    auto_skew: bool = True,
    prominence: float = 0.012,
    weave_hint: str = "auto",
    target_roi_cm: Tuple[float, float] = (1.0, 1.0),
    custom_roi_px: Optional[Tuple[int, int, int, int]] = None
) -> Dict[str, Any]:
    """
    The mechanistic justification for this step is: execute the integrated,
    authoritative pipeline on an arbitrary fabric image, resolving calibration,
    metric ROI, skew rectification, spectral harmonics, spatial projections,
    evidence-based fusion, and visual diagnostics.
    """
    t_start = time.perf_counter()

    # 1. Resolve Calibration
    # The mechanistic justification for this step is: distinguish authenticated physical calibration
    # from uncalibrated raw images, preventing silent assignment of 400 px/cm as valid physical scale.
    is_uncalibrated = False
    if calibration is None:
        if pixels_per_cm is not None:
            sx = float(pixels_per_cm)
            sy = float(pixels_per_cm_y) if pixels_per_cm_y is not None else sx
            calibration = PhysicalCalibration.from_scales(sx=sx, sy=sy, source="api_parameter")
        else:
            is_uncalibrated = True
            calibration = PhysicalCalibration.from_scales(
                sx=400.0,
                sy=400.0,
                source="uncalibrated",
                is_verified=False,
                uncertainty_pct=50.0
            )

    # 2. Metric ROI Localization
    roi_pil, roi_meta = extract_metric_roi(
        img_pil=img_pil,
        calibration=calibration,
        target_roi_cm=target_roi_cm,
        custom_roi_px=custom_roi_px
    )

    roi_gray = roi_pil.convert("L")
    roi_arr = np.array(roi_gray, dtype=np.float32) / 255.0

    # 3. Orientation Detection & Metric Rectification
    if auto_skew and min(roi_arr.shape) >= 64:
        skew_angle, radon_angles, radon_energies, _ = detect_fabric_skew(roi_arr, calibration)
    else:
        skew_angle = 0.0
        radon_angles = np.array([-45, 0, 45], dtype=np.float32)
        radon_energies = np.array([1, 2, 1], dtype=np.float32)

    rect_pil, crop_pil, (crop_w_cm, crop_h_cm) = rectify_and_crop(
        pil_img=roi_pil,
        skew_deg=skew_angle,
        calibration=calibration,
        crop_ratio=0.70
    )

    crop_gray = crop_pil.convert("L")
    crop_arr = np.array(crop_gray, dtype=np.float32) / 255.0

    # 4. Engine 1: Multi-Candidate 2D Fourier Spectral Analysis
    (warp_fft, weft_fft, spnr_x, spnr_y, fft_mag,
     spectral_meta) = compute_spectral_density_multicandidate(
        crop_arr=crop_arr,
        crop_w_cm=crop_w_cm,
        crop_h_cm=crop_h_cm,
        weave_hint=weave_hint
    )

    # 5. Engine 2: Directional Spatial Projection & Pitch Estimation
    (warp_proj, weft_proj, warp_peaks, weft_peaks,
     p_warp, p_weft, pitch_warp_um, pitch_weft_um,
     rect_var, spatial_meta) = compute_spatial_projection_density(
        crop_arr=crop_arr,
        calibration=calibration,
        crop_w_cm=crop_w_cm,
        crop_h_cm=crop_h_cm,
        prominence=prominence
    )

    # 6. Multi-Estimator Evidence Fusion & Uncertainty Evaluation
    fusion_res = evaluate_evidence_fusion(
        warp_fft=warp_fft,
        weft_fft=weft_fft,
        warp_proj=warp_proj,
        weft_proj=weft_proj,
        spnr_x=spnr_x,
        spnr_y=spnr_y,
        rect_variance=rect_var,
        warp_dispersion=spatial_meta["warp_interval_dispersion"],
        weft_dispersion=spatial_meta["weft_interval_dispersion"],
        weave_hint=weave_hint,
        crop_w_cm=crop_w_cm,
        crop_h_cm=crop_h_cm
    )

    # The mechanistic justification for this step is: if the input image is uncalibrated,
    # physical spatial densities (ends/cm, picks/cm) cannot be physically known and must be
    # suppressed to prevent false metrological assertions.
    if is_uncalibrated:
        fusion_res["accepted_warp_density_ends_per_cm"] = None
        fusion_res["accepted_weft_density_picks_per_cm"] = None
        fusion_res["warp_density_ends_per_cm"] = None
        fusion_res["weft_density_picks_per_cm"] = None
        fusion_res["warp_density_continuous"] = None
        fusion_res["weft_density_continuous"] = None
        fusion_res["linear_density_sum_per_cm"] = None
        fusion_res["areal_intersection_density_per_cm2"] = None
        fusion_res["pitch_warp_um"] = None
        fusion_res["pitch_weft_um"] = None
        fusion_res["is_validated"] = False
        fusion_res["decision_status"] = "UNCALIBRATED"
        fusion_res["decision_rationale"] = (
            "Image is uncalibrated; physical density requires known pixel scale (pixels/cm)."
        )
        fusion_res["candidate_measurements"] = {}

    latency_ms = (time.perf_counter() - t_start) * 1000.0

    # 7. Render Visual Diagnostics
    preview_pil = img_pil.convert("RGB")
    draw_prev = ImageDraw.Draw(preview_pil)
    draw_prev.rectangle(roi_meta["roi_box_px"], outline=(234, 88, 12), width=3)

    img_roi_b64 = pil_to_base64_data_url(preview_pil, max_size=600)
    img_rect_b64 = pil_to_base64_data_url(crop_pil, max_size=350)
    plot_radon_b64 = render_radon_plot_pillow(radon_angles, radon_energies, skew_angle)
    plot_warp_b64 = render_waveform_plot_pillow(p_warp, warp_peaks, "Warp Projection Profile (Vertical Threads)")
    plot_weft_b64 = render_waveform_plot_pillow(p_weft, weft_peaks, "Weft Projection Profile (Horizontal Threads)")
    plot_fft_b64 = render_fft_spectrum_image_pillow(fft_mag)

    total_thread_density = (
        int(fusion_res["accepted_warp_density_ends_per_cm"] + fusion_res["accepted_weft_density_picks_per_cm"])
        if (fusion_res["accepted_warp_density_ends_per_cm"] is not None and fusion_res["accepted_weft_density_picks_per_cm"] is not None)
        else None
    )

    return {
        "status": "success",
        "latency_ms": round(float(latency_ms), 2),
        "calibration": calibration.to_dict(),
        "roi_metadata": roi_meta,
        "results": {
            "accepted_warp_density_ends_per_cm": fusion_res["accepted_warp_density_ends_per_cm"],
            "accepted_weft_density_picks_per_cm": fusion_res["accepted_weft_density_picks_per_cm"],
            "is_validated": fusion_res["is_validated"],
            "candidate_measurements": fusion_res["candidate_measurements"],
            "warp_ends_per_cm": fusion_res["warp_density_ends_per_cm"],
            "weft_picks_per_cm": fusion_res["weft_density_picks_per_cm"],
            "warp_density_continuous": fusion_res["warp_density_continuous"],
            "weft_density_continuous": fusion_res["weft_density_continuous"],
            "total_thread_density": total_thread_density,
            "linear_density_sum_per_cm": fusion_res["linear_density_sum_per_cm"],
            "areal_intersection_density_per_cm2": fusion_res["areal_intersection_density_per_cm2"],
            "pitch_warp_um": fusion_res["pitch_warp_um"],
            "pitch_weft_um": fusion_res["pitch_weft_um"],
            "detected_skew_deg": round(float(skew_angle), 2),
            "decision_status": fusion_res["decision_status"],
            "engine_mode": fusion_res["engine_mode"],
            "signal_quality_index": fusion_res["signal_quality_index"],
            "confidence_score": fusion_res["confidence_score"],
            "decision_rationale": fusion_res["decision_rationale"],
            "calibration_uncertainty": {
                "interpretation": "Calibration-only relative scale envelope; not a statistical confidence interval and excludes image, model, sampling, and manual-count uncertainty.",
                "is_verified": calibration.is_verified,
                "relative_uncertainty_pct": calibration.uncertainty_pct,
                "warp_ends_per_cm": calibration.density_interval(fusion_res["accepted_warp_density_ends_per_cm"]),
                "weft_picks_per_cm": calibration.density_interval(fusion_res["accepted_weft_density_picks_per_cm"]),
                "candidate_measurements": {
                    "warp_fft": None if is_uncalibrated else calibration.density_interval(warp_fft),
                    "warp_projection": None if is_uncalibrated else calibration.density_interval(warp_proj),
                    "weft_fft": None if is_uncalibrated else calibration.density_interval(weft_fft),
                    "weft_projection": None if is_uncalibrated else calibration.density_interval(weft_proj),
                },
            }
        },
        "audit": {
            "fft_warp": round(float(warp_fft), 2),
            "fft_weft": round(float(weft_fft), 2),
            "proj_warp": round(float(warp_proj), 2),
            "proj_weft": round(float(weft_proj), 2),
            "delta_warp": fusion_res["delta_warp"],
            "delta_weft": fusion_res["delta_weft"],
            "spnr_warp": round(float(spnr_x), 1),
            "spnr_weft": round(float(spnr_y), 1),
            "rect_variance": round(float(rect_var), 5),
            "warp_peaks_count": spatial_meta["warp_peaks_count"],
            "weft_peaks_count": spatial_meta["weft_peaks_count"],
            "warp_dispersion": spatial_meta["warp_interval_dispersion"],
            "weft_dispersion": spatial_meta["weft_interval_dispersion"],
            "spectral_diagnostics": spectral_meta,
            "spatial_diagnostics": spatial_meta
        },
        "visuals": {
            "roi_preview": img_roi_b64,
            "rectified_crop": img_rect_b64,
            "radon_sweep": plot_radon_b64,
            "warp_profile": plot_warp_b64,
            "weft_profile": plot_weft_b64,
            "fft_spectrum": plot_fft_b64
        }
    }
