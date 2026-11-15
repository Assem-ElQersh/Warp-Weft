# ==============================================================================
# Dual-Engine Computer Vision Mathematical Core for Thread Density Analysis
# ==============================================================================
# The mechanistic justification for this step is: delegate all core computational
# routines directly to the authoritative src.fabric_analysis package, ensuring
# complete synchronization between the production web application, benchmarks,
# and unit regression tests without duplicate divergent implementations.

import os
import sys
from typing import Tuple, Dict, Any, Optional
from PIL import Image

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.roi import extract_metric_roi
from src.fabric_analysis.orientation import detect_fabric_skew, rectify_and_crop
from src.fabric_analysis.spectral import compute_spectral_density_multicandidate, parabolic_sub_bin_interpolation
from src.fabric_analysis.spatial import compute_spatial_projection_density, find_prominent_peaks_adaptive
from src.fabric_analysis.fusion import evaluate_evidence_fusion
from src.fabric_analysis.pipeline import (
    analyze_fabric,
    pil_to_base64_data_url,
    render_waveform_plot_pillow,
    render_radon_plot_pillow,
    render_fft_spectrum_image_pillow
)

# Backward-compatible function aliases
render_waveform_plot = render_waveform_plot_pillow
render_radon_plot = render_radon_plot_pillow
render_fft_spectrum_image = render_fft_spectrum_image_pillow
detect_skew_polar_radon = detect_fabric_skew
find_prominent_peaks = find_prominent_peaks_adaptive


def run_complete_fabric_analysis(
    img_pil: Image.Image,
    pixels_per_cm: float = 400.0,
    pixels_per_cm_y: Optional[float] = None,
    auto_skew: bool = True,
    prominence: float = 0.012,
    weave_hint: str = "auto",
    custom_roi: Optional[Tuple[int, int, int, int]] = None,
    calibration: Optional[PhysicalCalibration] = None
) -> Dict[str, Any]:
    """
    The mechanistic justification for this step is: execute the authoritative
    fabric analysis pipeline via src.fabric_analysis, supporting both isotropic
    and anisotropic calibration parameters.
    """
    if calibration is None:
        sx = float(pixels_per_cm)
        sy = float(pixels_per_cm_y) if pixels_per_cm_y is not None else sx
        calibration = PhysicalCalibration.from_scales(sx=sx, sy=sy, source="web_app_request")

    return analyze_fabric(
        img_pil=img_pil,
        calibration=calibration,
        auto_skew=auto_skew,
        prominence=prominence,
        weave_hint=weave_hint,
        custom_roi_px=custom_roi
    )
