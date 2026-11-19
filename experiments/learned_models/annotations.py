# The mechanistic justification for this step is: provide deterministic mathematical transformations for converting vector annotations (polygons, bounding boxes) into raster masks, extracting 1D centerline profiles, and standardizing multi-class thread labels.

import json
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from scipy import ndimage


def polygon_to_mask(
    polygons: List[np.ndarray], height: int, width: int, dtype: np.dtype = np.uint8
) -> np.ndarray:
    mask = np.zeros((height, width), dtype=dtype)
    for poly in polygons:
        pts = np.asarray(poly, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(mask, [pts], 1)
    return mask


def bboxes_to_density_map(
    bboxes: List[Tuple[float, float, float, float]],
    height: int,
    width: int,
    sigma: float = 4.0,
) -> np.ndarray:
    density = np.zeros((height, width), dtype=np.float32)
    for x1, y1, x2, y2 in bboxes:
        cx = int(round((x1 + x2) / 2.0))
        cy = int(round((y1 + y2) / 2.0))
        if 0 <= cx < width and 0 <= cy < height:
            density[cy, cx] += 1.0

    if np.sum(density) > 0 and sigma > 0:
        density = ndimage.gaussian_filter(density, sigma=sigma, mode="constant")
    return density


def morphological_skeleton(binary_mask: np.ndarray) -> np.ndarray:
    mask_bool = binary_mask > 0
    skel = np.zeros_like(mask_bool, dtype=np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    temp = mask_bool.astype(np.uint8).copy()

    while True:
        eroded = cv2.erode(temp, element)
        temp_open = cv2.dilate(eroded, element)
        sub = cv2.subtract(temp, temp_open)
        skel = cv2.bitwise_or(skel, sub)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            break
    return skel


def extract_pitch_from_centerlines(
    skeleton: np.ndarray, axis: int = 0, min_prominence: float = 0.1
) -> Tuple[float, List[float]]:
    # Project along axis: axis=0 projects vertically (sums columns) to measure horizontal pitch (warp)
    # axis=1 projects horizontally (sums rows) to measure vertical pitch (weft)
    profile = np.sum(skeleton > 0, axis=axis).astype(np.float32)
    if profile.max() > 0:
        profile /= profile.max()

    from scipy.signal import find_peaks
    peaks, _ = find_peaks(profile, distance=5, prominence=min_prominence)
    if len(peaks) < 2:
        return 0.0, []

    spacings = np.diff(peaks).tolist()
    median_pitch = float(np.median(spacings))
    return median_pitch, spacings


def parse_coco_categories(coco_dict: Dict[str, Any]) -> Dict[int, str]:
    return {c["id"]: c["name"] for c in coco_dict.get("categories", [])}
