# ==============================================================================
# Dual-Engine Computer Vision Mathematical Core for Thread Density Analysis
# ==============================================================================
# The mechanistic justification for this step is: implement an ultra-lightweight,
# deterministic computer vision engine combining 2D Fast Fourier Transform (2D FFT)
# harmonic extraction and 1D Directional Spatial Projection profiling with automated
# Polar Radon skew rectification, executing in < 20 ms on standard CPUs without
# external deep learning weights or heavy cloud dependencies.

import io
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def rgb_to_grayscale(img_pil):
    """
    The mechanistic justification for this step is: convert arbitrary RGB/RGBA
    macro captures into normalized floating-point luminance arrays [0.0, 1.0].
    """
    if img_pil.mode != "L":
        img_gray = img_pil.convert("L")
    else:
        img_gray = img_pil
    return np.array(img_gray, dtype=np.float32) / 255.0


def detect_skew_polar_radon(arr, angle_range=(-45, 45), step=0.5, r_min=15, r_max_ratio=0.45):
    """
    The mechanistic justification for this step is: map the 2D FFT magnitude spectrum
    into polar coordinates and integrate spectral energy along radial rays to isolate
    the dominant non-orthogonal yarn rotation axis.
    """
    rows, cols = arr.shape
    crow, ccol = rows // 2, cols // 2
    f_input = arr - np.mean(arr)
    fft2 = np.fft.fftshift(np.fft.fft2(f_input))
    mag = np.abs(fft2)

    angles = np.arange(angle_range[0], angle_range[1] + step, step)
    r_max = int(min(rows, cols) * r_max_ratio)
    r_vals = np.arange(r_min, r_max, dtype=np.float32)

    angular_energies = []
    for theta in angles:
        rad = np.deg2rad(theta)
        # Coordinate alignment: row index increases downwards; CCW visual rotation shifts row upward (-sin)
        u_idx = np.clip(np.round(crow - r_vals * np.sin(rad)).astype(int), 0, rows - 1)
        v_idx = np.clip(np.round(ccol + r_vals * np.cos(rad)).astype(int), 0, cols - 1)
        energy = float(np.sum(mag[u_idx, v_idx]))
        angular_energies.append(energy)

    angular_energies = np.array(angular_energies, dtype=np.float32)
    best_idx = int(np.argmax(angular_energies))
    detected_angle = float(angles[best_idx])
    
    return detected_angle, angles, angular_energies, mag


def rectify_and_crop(pil_img, skew_deg, crop_ratio=0.70):
    """
    The mechanistic justification for this step is: rotate the skewed image by
    -skew_deg using bicubic interpolation and extract the center boundary-safe
    crop to eliminate zero-padding artifacts.
    """
    if abs(skew_deg) > 0.1:
        rect_pil = pil_img.rotate(-skew_deg, resample=Image.Resampling.BICUBIC)
    else:
        rect_pil = pil_img.copy()

    w, h = rect_pil.size
    margin_x = int(w * (1.0 - crop_ratio) / 2.0)
    margin_y = int(h * (1.0 - crop_ratio) / 2.0)

    crop_pil = rect_pil.crop((margin_x, margin_y, w - margin_x, h - margin_y))
    return rect_pil, crop_pil


def parabolic_sub_bin_interpolation(slice_1d, center_idx, search_offset=5):
    """
    The mechanistic justification for this step is: apply 3-point quadratic parabolic
    sub-bin interpolation on the integer DFT peak neighborhood to eliminate binning
    discretization error caused by spatial sub-window cropping.
    """
    search_region = slice_1d[center_idx + search_offset :]
    if len(search_region) == 0:
        return 0.0, 0.0
    rel_peak = int(np.argmax(search_region))
    peak_idx = rel_peak + center_idx + search_offset

    if 0 < peak_idx < len(slice_1d) - 1:
        alpha = float(slice_1d[peak_idx - 1])
        beta = float(slice_1d[peak_idx])
        gamma = float(slice_1d[peak_idx + 1])
        denom = alpha - 2.0 * beta + gamma
        if abs(denom) > 1e-7:
            delta = 0.5 * (alpha - gamma) / denom
        else:
            delta = 0.0
        exact_k = (peak_idx - center_idx) + delta
        peak_mag = beta
    else:
        exact_k = float(peak_idx - center_idx)
        peak_mag = float(slice_1d[peak_idx])

    # Spectral Peak-to-Noise Ratio (SPNR)
    noise_floor = float(np.median(slice_1d[center_idx + search_offset :])) + 1e-5
    spnr = peak_mag / noise_floor
    return exact_k, spnr


def compute_2d_fft_density(crop_arr, crop_w_cm, crop_h_cm):
    """
    The mechanistic justification for this step is: extract fundamental spatial
    frequencies (u0, v0) along orthogonal frequency axes and scale to metric density.
    """
    cH, cW = crop_arr.shape
    ccrow, cccol = cH // 2, cW // 2

    F_crop = np.fft.fftshift(np.fft.fft2(crop_arr - np.mean(crop_arr)))
    mag_crop = np.abs(F_crop)

    # Horizontal slice -> Warp (columns)
    slice_x = mag_crop[ccrow, :]
    k_x, spnr_x = parabolic_sub_bin_interpolation(slice_x, cccol, search_offset=4)
    warp_fft = k_x / max(crop_w_cm, 1e-5)

    # Vertical slice -> Weft (rows)
    slice_y = mag_crop[:, cccol]
    k_y, spnr_y = parabolic_sub_bin_interpolation(slice_y, ccrow, search_offset=4)
    weft_fft = k_y / max(crop_h_cm, 1e-5)

    return warp_fft, weft_fft, spnr_x, spnr_y, mag_crop


def find_prominent_peaks(sig, min_dist=5, prominence=0.012):
    """
    The mechanistic justification for this step is: identify structural yarn crowns
    in spatial 1D projection waveforms by filtering for local maxima that exceed
    dynamic distance constraints and optical contrast prominence.
    """
    n = len(sig)
    peaks = []
    for i in range(1, n - 1):
        if sig[i] > sig[i - 1] and sig[i] > sig[i + 1]:
            left_w = max(0, i - min_dist)
            right_w = min(n, i + min_dist + 1)
            left_min = np.min(sig[left_w:i])
            right_min = np.min(sig[i + 1 : right_w])
            prom = sig[i] - max(left_min, right_min)
            if prom >= prominence:
                if not peaks or (i - peaks[-1]) >= min_dist:
                    peaks.append(i)
    return peaks


def compute_1d_projection_density(crop_arr, crop_w_cm, crop_h_cm, pixels_per_cm, prominence=0.012):
    """
    The mechanistic justification for this step is: integrate pixel intensities
    along columns and rows to produce directional waveforms, count physical yarn
    crowns, and calculate calibrated center-to-center yarn pitch.
    """
    p_warp = np.mean(crop_arr, axis=0)  # Average down columns -> Warp profile
    p_weft = np.mean(crop_arr, axis=1)  # Average across rows -> Weft profile

    min_dist = max(4, int(pixels_per_cm / 85.0))

    warp_peaks = find_prominent_peaks(p_warp, min_dist=min_dist, prominence=prominence)
    weft_peaks = find_prominent_peaks(p_weft, min_dist=min_dist, prominence=prominence)

    warp_proj = len(warp_peaks) / max(crop_w_cm, 1e-5)
    weft_proj = len(weft_peaks) / max(crop_h_cm, 1e-5)

    # Physical center-to-center pitch (um)
    pitch_warp_um = (10000.0 / warp_proj) if warp_proj > 0 else 0.0
    pitch_weft_um = (10000.0 / weft_proj) if weft_proj > 0 else 0.0

    var_warp = float(np.var(p_warp))
    var_weft = float(np.var(p_weft))
    rect_variance = 0.5 * (var_warp + var_weft)

    return warp_proj, weft_proj, warp_peaks, weft_peaks, p_warp, p_weft, pitch_warp_um, pitch_weft_um, rect_variance


def evaluate_consensus(warp_fft, weft_fft, warp_proj, weft_proj, spnr_x, spnr_y, rect_var, weave_hint="auto"):
    """
    The mechanistic justification for this step is: validate agreement between
    frequency and spatial domains, arbitrate weave architecture boundaries (Plain
    consensus vs. Twill/Satin 2D FFT dominance), and calculate an objective
    multi-attribute quality score Q in [0, 100%].
    """
    delta_w = abs(warp_fft - warp_proj)
    delta_wf = abs(weft_fft - weft_proj)

    # For plain weaves with high agreement (delta <= 2.0), consensus averages both engines
    # For twill/satin with float structures, 2D FFT captures fundamental weave period
    if weave_hint in ("twill", "satin"):
        final_warp = round(warp_fft)
        final_weft = round(weft_fft)
        engine_mode = "2D FFT Dominant (Float Structure)"
    elif delta_w <= 3.0 and delta_wf <= 3.0:
        final_warp = int(round(0.5 * (warp_fft + warp_proj)))
        final_weft = int(round(0.5 * (weft_fft + weft_proj)))
        engine_mode = "Dual-Engine Consensus"
    else:
        # Default to 2D FFT as primary spectral estimator
        final_warp = int(round(warp_fft))
        final_weft = int(round(weft_fft))
        engine_mode = "2D FFT Primary (Discrepancy Arbiter)"

    # Multi-attribute confidence score Q
    mean_spnr = 0.5 * (spnr_x + spnr_y)
    spnr_score = min(1.0, mean_spnr / 10.0)
    var_score = min(1.0, rect_var / 0.15)
    discrepancy_score = max(0.0, 1.0 - (delta_w + delta_wf) / 6.0)

    quality_score = (0.35 * spnr_score + 0.35 * var_score + 0.30 * discrepancy_score) * 100.0
    quality_score = max(10.0, min(99.9, quality_score))

    return final_warp, final_weft, delta_w, delta_wf, quality_score, engine_mode


def render_waveform_plot(signal, peaks, title, x_label="Pixel Coordinate", y_label="Mean Intensity", width=550, height=180):
    """
    The mechanistic justification for this step is: render publication-grade
    1D projection waveforms with identified peak crown markers into a Base64
    PNG string using pure Pillow.
    """
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin_l, margin_r, margin_t, margin_b = 50, 20, 30, 30
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    # Frame & Grid
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

    # Waveform line
    draw.line(coords, fill=(26, 86, 160), width=2)

    # Peak markers
    for p in peaks:
        px = margin_l + int(p * plot_w / max(1, n_pts - 1))
        py = margin_t + plot_h - int(((signal[p] - s_min) / s_range) * plot_h)
        # Red cross marker
        draw.line([(px - 4, py - 4), (px + 4, py + 4)], fill=(220, 38, 38), width=2)
        draw.line([(px - 4, py + 4), (px + 4, py - 4)], fill=(220, 38, 38), width=2)

    # Text headers
    draw.text((margin_l, 8), f"{title} (Peaks: {len(peaks)})", fill=(15, 43, 72))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def render_radon_plot(angles, energies, best_angle, width=550, height=180):
    """
    The mechanistic justification for this step is: render the Polar Radon radial
    energy sweep curve highlighting the global orientation maximum.
    """
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
    best_px, best_py = 0, 0
    for i in range(n_pts):
        px = margin_l + int(i * plot_w / max(1, n_pts - 1))
        py = margin_t + plot_h - int(((energies[i] - e_min) / e_range) * plot_h)
        coords.append((px, py))
        if abs(angles[i] - best_angle) < 0.25:
            best_px, best_py = px, py

    draw.line(coords, fill=(16, 42, 114), width=2)

    # Vertical line at best angle
    draw.line([(best_px, margin_t), (best_px, height - margin_b)], fill=(220, 38, 38), width=2)
    draw.ellipse([best_px - 4, best_py - 4, best_px + 4, best_py + 4], fill=(220, 38, 38))

    draw.text((margin_l, 8), f"Polar Radon Energy Sweep (Peak: {best_angle:+.1f} deg)", fill=(15, 43, 72))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def render_fft_spectrum_image(mag, width=280, height=280):
    """
    The mechanistic justification for this step is: render the 2D FFT magnitude
    spectrum with an inferno colormap into a Base64 PNG data URL.
    """
    log_mag = np.log1p(mag)
    l_min, l_max = np.min(log_mag), np.max(log_mag)
    norm = np.clip((log_mag - l_min) / max(1e-4, l_max - l_min), 0.0, 1.0)

    # Inferno Colormap LUT
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


def pil_to_base64_data_url(img_pil, max_size=500):
    """
    The mechanistic justification for this step is: compress and encode PIL images
    to base64 data URLs for seamless web transmission.
    """
    w, h = img_pil.size
    if max(w, h) > max_size:
        scale = max_size / float(max(w, h))
        target_size = (int(w * scale), int(h * scale))
        rendered = img_pil.resize(target_size, Image.Resampling.BICUBIC)
    else:
        rendered = img_pil

    buf = io.BytesIO()
    rendered.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def run_complete_fabric_analysis(img_pil, pixels_per_cm=400.0, auto_skew=True, prominence=0.012, weave_hint="auto", custom_roi=None):
    """
    The mechanistic justification for this step is: execute the integrated dual-engine
    pipeline end-to-end on an arbitrary uploaded image, returning comprehensive
    metrics, pitch calculations, quality scores, and visual diagnostic plots.
    """
    import time
    t_start = time.perf_counter()

    orig_w, orig_h = img_pil.size
    img_gray = img_pil.convert("L")
    arr_full = np.array(img_gray, dtype=np.float32) / 255.0

    # 1. Region of Interest (ROI) Localization
    roi_side_px = int(pixels_per_cm * 1.0)
    if custom_roi and len(custom_roi) == 4:
        rx, ry, rw, rh = custom_roi
        rx = max(0, min(orig_w - 10, int(rx)))
        ry = max(0, min(orig_h - 10, int(ry)))
        rw = max(10, min(orig_w - rx, int(rw)))
        rh = max(10, min(orig_h - ry, int(rh)))
        roi_box = (rx, ry, rx + rw, ry + rh)
    else:
        # Default to center 1.0 cm x 1.0 cm
        crop_w = min(orig_w, roi_side_px)
        crop_h = min(orig_h, roi_side_px)
        cx, cy = orig_w // 2, orig_h // 2
        roi_box = (cx - crop_w // 2, cy - crop_h // 2, cx + crop_w // 2, cy + crop_h // 2)

    roi_pil = img_pil.crop(roi_box)
    roi_gray = roi_pil.convert("L")
    roi_arr = np.array(roi_gray, dtype=np.float32) / 255.0

    # 2. Skew Detection & Affine Rectification
    if auto_skew and min(roi_arr.shape) >= 64:
        skew_angle, radon_angles, radon_energies, _ = detect_skew_polar_radon(roi_arr)
    else:
        skew_angle = 0.0
        radon_angles = np.array([-45, 0, 45])
        radon_energies = np.array([1, 2, 1])

    rect_pil, crop_pil = rectify_and_crop(roi_pil, skew_angle, crop_ratio=0.70)
    crop_gray = crop_pil.convert("L")
    crop_arr = np.array(crop_gray, dtype=np.float32) / 255.0

    cW_px, cH_px = crop_pil.size
    crop_w_cm = cW_px / pixels_per_cm
    crop_h_cm = cH_px / pixels_per_cm

    # 3. Engine 1: 2D FFT Spectral Harmonics
    warp_fft, weft_fft, spnr_x, spnr_y, fft_mag = compute_2d_fft_density(crop_arr, crop_w_cm, crop_h_cm)

    # 4. Engine 2: 1D Spatial Marginal Projection
    (warp_proj, weft_proj, warp_peaks, weft_peaks,
     p_warp, p_weft, pitch_w, pitch_wf, rect_var) = compute_1d_projection_density(
        crop_arr, crop_w_cm, crop_h_cm, pixels_per_cm, prominence=prominence
    )

    # 5. Consensus & Quality Score
    final_warp, final_weft, delta_w, delta_wf, quality_score, engine_mode = evaluate_consensus(
        warp_fft, weft_fft, warp_proj, weft_proj, spnr_x, spnr_y, rect_var, weave_hint=weave_hint
    )

    t_latency_ms = (time.perf_counter() - t_start) * 1000.0

    # 6. Generate Diagnostic Visualizations
    # Overlay ROI box on preview
    preview_pil = img_pil.convert("RGB")
    draw_prev = ImageDraw.Draw(preview_pil)
    draw_prev.rectangle(roi_box, outline=(234, 88, 12), width=3)

    img_roi_b64 = pil_to_base64_data_url(preview_pil, max_size=600)
    img_rect_b64 = pil_to_base64_data_url(crop_pil, max_size=350)
    plot_radon_b64 = render_radon_plot(radon_angles, radon_energies, skew_angle)
    plot_warp_b64 = render_waveform_plot(p_warp, warp_peaks, "Warp Projection Profile (Vertical Threads)")
    plot_weft_b64 = render_waveform_plot(p_weft, weft_peaks, "Weft Projection Profile (Horizontal Threads)")
    plot_fft_b64 = render_fft_spectrum_image(fft_mag)

    return {
        "status": "success",
        "latency_ms": round(t_latency_ms, 2),
        "calibration": {
            "pixels_per_cm": float(pixels_per_cm),
            "pixel_pitch_um": round(10000.0 / pixels_per_cm, 2),
            "roi_box": list(roi_box),
            "crop_span_cm": round(crop_w_cm, 3)
        },
        "results": {
            "warp_ends_per_cm": int(final_warp),
            "weft_picks_per_cm": int(final_weft),
            "total_thread_density": int(final_warp + final_weft),
            "pitch_warp_um": round((10000.0 / final_warp) if final_warp > 0 else 0.0, 2),
            "pitch_weft_um": round((10000.0 / final_weft) if final_weft > 0 else 0.0, 2),
            "detected_skew_deg": round(skew_angle, 2),
            "confidence_score": round(quality_score, 1),
            "engine_mode": engine_mode
        },
        "audit": {
            "fft_warp": round(float(warp_fft), 2),
            "fft_weft": round(float(weft_fft), 2),
            "proj_warp": round(float(warp_proj), 2),
            "proj_weft": round(float(weft_proj), 2),
            "delta_warp": round(float(delta_w), 2),
            "delta_weft": round(float(delta_wf), 2),
            "spnr_warp": round(float(spnr_x), 1),
            "spnr_weft": round(float(spnr_y), 1),
            "rect_variance": round(float(rect_var), 5),
            "warp_peaks_count": len(warp_peaks),
            "weft_peaks_count": len(weft_peaks)
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
