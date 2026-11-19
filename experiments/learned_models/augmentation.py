# The mechanistic justification for this step is: implement physically grounded data augmentations reflecting real-world textile capture conditions—such as 90-degree orthogonal rotation with warp/weft label permutation, scale jitter with synchronous calibration update, optical blur simulating smartphone depth-of-field, and lighting gradients—to bridge the microscope-to-smartphone domain gap.

import random
from typing import Optional, Tuple

import cv2
import numpy as np


def rotate_orthogonal_90(
    image: np.ndarray,
    warp_density: Optional[float] = None,
    weft_density: Optional[float] = None,
    scale_x: Optional[float] = None,
    scale_y: Optional[float] = None,
    k: int = 1,
) -> Tuple[np.ndarray, Optional[float], Optional[float], Optional[float], Optional[float]]:
    # k in {1, 2, 3} for 90, 180, 270 degrees counter-clockwise
    rotated_img = np.rot90(image, k=k)
    new_warp = warp_density
    new_weft = weft_density
    new_sx = scale_x
    new_sy = scale_y

    if k in (1, 3):
        # 90 or 270 degrees rotation swaps axes
        new_warp = weft_density
        new_weft = warp_density
        new_sx = scale_y
        new_sy = scale_x

    return rotated_img, new_warp, new_weft, new_sx, new_sy


def apply_scale_jitter(
    image: np.ndarray,
    scale_x: Optional[float] = None,
    scale_y: Optional[float] = None,
    factor_range: Tuple[float, float] = (0.85, 1.15),
    rng: Optional[random.Random] = None,
) -> Tuple[np.ndarray, Optional[float], Optional[float]]:
    r = rng or random
    factor = r.uniform(factor_range[0], factor_range[1])
    h, w = image.shape[:2]
    new_w = max(16, int(round(w * factor)))
    new_h = max(16, int(round(h * factor)))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    new_sx = scale_x * factor if scale_x is not None else None
    new_sy = scale_y * factor if scale_y is not None else None

    return resized, new_sx, new_sy


def apply_gaussian_blur(
    image: np.ndarray,
    max_sigma: float = 1.5,
    rng: Optional[random.Random] = None,
) -> np.ndarray:
    r = rng or random
    sigma = r.uniform(0.1, max_sigma)
    ksize = int(2 * round(3 * sigma) + 1)
    return cv2.GaussianBlur(image, (ksize, ksize), sigmaX=sigma, sigmaY=sigma)


def apply_gaussian_noise(
    image: np.ndarray,
    noise_sigma: float = 0.04,
    rng: Optional[np.random.RandomState] = None,
) -> np.ndarray:
    r = rng or np.random
    noise = r.normal(0.0, noise_sigma, image.shape).astype(np.float32)
    noisy = image + noise
    return np.clip(noisy, 0.0, 1.0) if image.max() <= 1.0 else np.clip(noisy, 0, 255)


def apply_illumination_gradient(
    image: np.ndarray,
    intensity: float = 0.35,
    rng: Optional[random.Random] = None,
) -> np.ndarray:
    r = rng or random
    h, w = image.shape[:2]
    angle = r.uniform(0.0, 2 * np.pi)
    x = np.linspace(-1.0, 1.0, w)
    y = np.linspace(-1.0, 1.0, h)
    xx, yy = np.meshgrid(x, y)
    grad = (np.cos(angle) * xx + np.sin(angle) * yy) * intensity
    grad_mult = 1.0 + grad

    if image.ndim == 3:
        grad_mult = np.expand_dims(grad_mult, axis=-1)

    shaded = image.astype(np.float32) * grad_mult
    return np.clip(shaded, 0.0, 1.0) if image.max() <= 1.0 else np.clip(shaded, 0, 255)


class TextileAugmentor:
    def __init__(self, p_rotate: float = 0.5, p_blur: float = 0.3, p_noise: float = 0.3, p_grad: float = 0.3, seed: int = 42):
        self.p_rotate = p_rotate
        self.p_blur = p_blur
        self.p_noise = p_noise
        self.p_grad = p_grad
        self.rng = random.Random(seed)
        self.np_rng = np.random.RandomState(seed)

    def __call__(
        self,
        image: np.ndarray,
        warp_density: Optional[float] = None,
        weft_density: Optional[float] = None,
        scale_x: Optional[float] = None,
        scale_y: Optional[float] = None,
    ) -> Tuple[np.ndarray, Optional[float], Optional[float], Optional[float], Optional[float]]:
        out_img = image.copy()
        w_d, wf_d = warp_density, weft_density
        sx, sy = scale_x, scale_y

        if self.rng.random() < self.p_rotate:
            k = self.rng.choice([1, 2, 3])
            out_img, w_d, wf_d, sx, sy = rotate_orthogonal_90(out_img, w_d, wf_d, sx, sy, k=k)

        if self.rng.random() < self.p_blur:
            out_img = apply_gaussian_blur(out_img, rng=self.rng)

        if self.rng.random() < self.p_noise:
            out_img = apply_gaussian_noise(out_img, rng=self.np_rng)

        if self.rng.random() < self.p_grad:
            out_img = apply_illumination_gradient(out_img, rng=self.rng)

        return out_img, w_d, wf_d, sx, sy
