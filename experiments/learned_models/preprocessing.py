# The mechanistic justification for this step is: provide standardized optical normalization (CLAHE, min-max scaling), sliding-window patch tiling with boundary padding and overlap, and seamless patch reconstruction to enable deep models with fixed input sizes to process arbitrary multi-megapixel fabric swatches without loss of spatial resolution.

from typing import List, Tuple, Union

import cv2
import numpy as np


def apply_clahe(
    image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)
) -> np.ndarray:
    if image.dtype != np.uint8:
        img_u8 = np.clip(image * 255.0, 0, 255).astype(np.uint8)
    else:
        img_u8 = image.copy()

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    if img_u8.ndim == 2:
        res = clahe.apply(img_u8)
    elif img_u8.ndim == 3 and img_u8.shape[2] == 3:
        lab = cv2.cvtColor(img_u8, cv2.COLOR_RGB2LAB)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        res = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    else:
        res = img_u8

    return res.astype(np.float32) / 255.0


def normalize_minmax(image: np.ndarray) -> np.ndarray:
    img_float = image.astype(np.float32)
    min_val = float(np.min(img_float))
    max_val = float(np.max(img_float))
    if max_val - min_val > 1e-7:
        return (img_float - min_val) / (max_val - min_val)
    return np.zeros_like(img_float)


class PatchTiler:
    def __init__(self, patch_size: int = 256, stride: int = 128):
        self.patch_size = patch_size
        self.stride = stride

    def extract_patches(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]], Tuple[int, int]]:
        h, w = image.shape[:2]
        pad_h = (self.stride - (h - self.patch_size) % self.stride) % self.stride
        pad_w = (self.stride - (w - self.patch_size) % self.stride) % self.stride

        if h < self.patch_size:
            pad_h = self.patch_size - h
        if w < self.patch_size:
            pad_w = self.patch_size - w

        if image.ndim == 2:
            padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode="reflect")
        else:
            padded = np.pad(image, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect")

        pad_h_total, pad_w_total = padded.shape[:2]
        patches = []
        coords = []

        for y in range(0, pad_h_total - self.patch_size + 1, self.stride):
            for x in range(0, pad_w_total - self.patch_size + 1, self.stride):
                patch = padded[y : y + self.patch_size, x : x + self.patch_size]
                patches.append(patch)
                coords.append((y, x, y + self.patch_size, x + self.patch_size))

        return np.array(patches, dtype=np.float32), coords, (h, w)

    def reconstruct_from_patches(
        self,
        patches: np.ndarray,
        coordinates: List[Tuple[int, int, int, int]],
        original_shape: Tuple[int, int],
    ) -> np.ndarray:
        h, w = original_shape
        max_y = max(c[2] for c in coordinates)
        max_x = max(c[3] for c in coordinates)

        channels = patches.shape[-1] if patches.ndim == 4 else None
        if channels:
            canvas = np.zeros((max_y, max_x, channels), dtype=np.float32)
            weight = np.zeros((max_y, max_x, 1), dtype=np.float32)
        else:
            canvas = np.zeros((max_y, max_x), dtype=np.float32)
            weight = np.zeros((max_y, max_x), dtype=np.float32)

        # 2D Hanning window for smooth blending
        window_1d = np.hanning(self.patch_size)
        window_2d = np.outer(window_1d, window_1d).astype(np.float32)
        window_2d = np.maximum(window_2d, 1e-4)
        if channels:
            window_2d_chan = np.expand_dims(window_2d, axis=-1)
        else:
            window_2d_chan = window_2d

        for patch, (y1, x1, y2, x2) in zip(patches, coordinates):
            canvas[y1:y2, x1:x2] += patch * window_2d_chan
            weight[y1:y2, x1:x2] += window_2d_chan

        weight[weight == 0] = 1.0
        reconstructed = canvas / weight
        return reconstructed[:h, :w]
