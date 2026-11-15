# ==============================================================================
# Warp & Weft AI — Region of Interest (ROI) Localization Module
# ==============================================================================
# The mechanistic justification for this step is: extract calibrated physical
# inspection windows while explicitly tracking and disclosing requested vs. actual
# spatial coverage, preventing silent under-sized measurement regions from being
# presented as full 1.0 cm² physical inspections.

from typing import Tuple, Dict, Any, Optional
from PIL import Image
from src.fabric_analysis.calibration import PhysicalCalibration


def extract_metric_roi(img_pil: Image.Image,
                       calibration: PhysicalCalibration,
                       target_roi_cm: Tuple[float, float] = (1.0, 1.0),
                       custom_roi_px: Optional[Tuple[int, int, int, int]] = None) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    The mechanistic justification for this step is: map target metric dimensions
    (target_roi_cm) to integer pixel boundaries using axis-specific calibration
    scales, reporting exact physical coverage and bounding coordinates.
    """
    orig_w, orig_h = img_pil.size
    sx = calibration.pixels_per_cm_x
    sy = calibration.pixels_per_cm_y

    target_w_cm, target_h_cm = target_roi_cm

    if custom_roi_px and len(custom_roi_px) == 4:
        rx, ry, rw, rh = custom_roi_px
        rx = max(0, min(orig_w - 4, int(rx)))
        ry = max(0, min(orig_h - 4, int(ry)))
        rw = max(4, min(orig_w - rx, int(rw)))
        rh = max(4, min(orig_h - ry, int(rh)))
        roi_box = (rx, ry, rx + rw, ry + rh)
        actual_w_cm = rw / sx
        actual_h_cm = rh / sy
        fully_available = (actual_w_cm >= target_w_cm * 0.99) and (actual_h_cm >= target_h_cm * 0.99)
    else:
        req_w_px = int(round(target_w_cm * sx))
        req_h_px = int(round(target_h_cm * sy))

        if req_w_px <= orig_w and req_h_px <= orig_h:
            fully_available = True
            crop_w = req_w_px
            crop_h = req_h_px
        else:
            fully_available = False
            crop_w = min(orig_w, req_w_px)
            crop_h = min(orig_h, req_h_px)

        cx, cy = orig_w // 2, orig_h // 2
        roi_box = (
            cx - crop_w // 2,
            cy - crop_h // 2,
            cx - crop_w // 2 + crop_w,
            cy - crop_h // 2 + crop_h
        )
        actual_w_cm = crop_w / sx
        actual_h_cm = crop_h / sy

    roi_pil = img_pil.crop(roi_box)
    roi_w_px, roi_h_px = roi_pil.size

    warning = None
    if not fully_available:
        warning = (f"Requested metric ROI ({target_w_cm:.2f} x {target_h_cm:.2f} cm) exceeds available image "
                   f"resolution ({orig_w}x{orig_h} px). Measured region is {actual_w_cm:.3f} x {actual_h_cm:.3f} cm.")

    metadata = {
        "requested_roi_cm": [float(target_w_cm), float(target_h_cm)],
        "actual_roi_cm": [round(float(actual_w_cm), 4), round(float(actual_h_cm), 4)],
        "requested_roi_fully_available": bool(fully_available),
        "roi_box_px": list(roi_box),
        "roi_dimensions_px": [int(roi_w_px), int(roi_h_px)],
        "coverage_ratio_x": round(float(actual_w_cm / max(target_w_cm, 1e-5)), 4),
        "coverage_ratio_y": round(float(actual_h_cm / max(target_h_cm, 1e-5)), 4),
        "warning": warning
    }

    return roi_pil, metadata
