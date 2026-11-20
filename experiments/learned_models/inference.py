# The mechanistic justification for this step is: provide production-grade, memory-efficient inference execution across CPU and CUDA backends, supporting single full-frame analysis, overlapping patch-tiling for multi-megapixel swatches, and hybrid centerline-pitch extraction.

from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import torch

# The mechanistic justification for this step is: defer research-specific imports
# (morphological skeletonization, patch tiler, and GUM uncertainty calculators) to
# their specific runner methods, ensuring DeterministicInferenceRunner executes with zero
# dependency on SciPy or auxiliary annotation processing modules.


class DeterministicInferenceRunner:
    def __call__(
        self,
        image: np.ndarray,
        scale_x: float,
        scale_y: float,
        weave_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        from PIL import Image
        from src.fabric_analysis.pipeline import analyze_fabric

        if image.dtype != np.uint8:
            img_u8 = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        else:
            img_u8 = image.copy()

        pil_img = Image.fromarray(img_u8)
        res = analyze_fabric(
            img_pil=pil_img,
            pixels_per_cm=scale_x,
            pixels_per_cm_y=scale_y,
            weave_hint=weave_type or "auto",
        )
        results = res.get("results", {})
        audit = res.get("audit", {})

        warp_val = results.get("accepted_warp_density_ends_per_cm")
        if warp_val is None:
            warp_val = audit.get("fft_warp", 0.0)

        weft_val = results.get("accepted_weft_density_picks_per_cm")
        if weft_val is None:
            weft_val = audit.get("fft_weft", 0.0)

        return {
            "model_id": "deterministic_dual_engine",
            "warp_density": float(warp_val) if warp_val is not None else 0.0,
            "weft_density": float(weft_val) if weft_val is not None else 0.0,
            "decision_status": results.get("decision_status", "NEEDS_REVIEW"),
            "confidence": float(results.get("confidence_score", 0.0)),
            "skew_angle": float(results.get("detected_skew_deg", 0.0)),
        }


class UNetInferenceRunner:
    def __init__(
        self,
        unet_model: torch.nn.Module,
        patch_size: int = 256,
        stride: int = 128,
        device: Optional[str] = None,
    ):
        from experiments.learned_models.preprocessing import PatchTiler
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = unet_model.to(self.device)
        self.model.eval()
        self.tiler = PatchTiler(patch_size=patch_size, stride=stride)

    def predict_mask(self, image: np.ndarray) -> np.ndarray:
        from experiments.learned_models.preprocessing import normalize_minmax
        # Preprocessing: convert to grayscale float32 [0, 1]
        if image.ndim == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        elif image.dtype == np.uint8:
            gray = image.astype(np.float32) / 255.0
        else:
            gray = image.astype(np.float32)

        gray = normalize_minmax(gray)
        patches, coords, orig_shape = self.tiler.extract_patches(gray)

        # Batch forward pass through PyTorch U-Net
        batch_size = 8
        n_patches = len(patches)
        all_prob_patches = []

        with torch.no_grad():
            for i in range(0, n_patches, batch_size):
                p_batch = patches[i : i + batch_size]
                t_batch = (
                    torch.from_numpy(p_batch)
                    .unsqueeze(1)
                    .to(self.device, dtype=torch.float32)
                )
                logits = self.model(t_batch)
                probs = torch.softmax(logits, dim=1).cpu().numpy()
                all_prob_patches.extend([probs[j] for j in range(len(probs))])

        all_prob_patches = np.array(all_prob_patches)  # [N, 3, 256, 256]
        all_prob_patches = np.transpose(all_prob_patches, (0, 2, 3, 1))  # [N, 256, 256, 3]

        reconstructed_probs = self.tiler.reconstruct_from_patches(
            all_prob_patches, coords, orig_shape
        )
        return np.argmax(reconstructed_probs, axis=-1).astype(np.uint8)


class HybridMetrologyRunner:
    def __init__(self, unet_model: torch.nn.Module, device: Optional[str] = None):
        self.seg_runner = UNetInferenceRunner(unet_model=unet_model, device=device)

    def __call__(
        self,
        image: np.ndarray,
        scale_x: float,
        scale_y: float,
        min_prominence: float = 0.05,
    ) -> Dict[str, Any]:
        from experiments.learned_models.annotations import (
            extract_pitch_from_centerlines,
            morphological_skeleton,
        )
        from experiments.learned_models.calibration import calculate_density_with_uncertainty

        mask = self.seg_runner.predict_mask(image)
        warp_mask = (mask == 1).astype(np.uint8)
        weft_mask = (mask == 2).astype(np.uint8)

        # Topological centerline extraction via Lee-94 morphological skeletonization
        warp_skel = morphological_skeleton(warp_mask)
        weft_skel = morphological_skeleton(weft_mask)

        # Spacing measurement:
        # Warp threads run vertically; pitch is measured horizontally (axis=0 sums columns)
        warp_pitch, warp_spacings = extract_pitch_from_centerlines(
            warp_skel, axis=0, min_prominence=min_prominence
        )
        # Weft threads run horizontally; pitch is measured vertically (axis=1 sums rows)
        weft_pitch, weft_spacings = extract_pitch_from_centerlines(
            weft_skel, axis=1, min_prominence=min_prominence
        )

        warp_meas = calculate_density_with_uncertainty(
            pitch_px=warp_pitch, scale_px_per_cm=scale_x
        )
        weft_meas = calculate_density_with_uncertainty(
            pitch_px=weft_pitch, scale_px_per_cm=scale_y
        )

        return {
            "model_id": "hybrid_unet_skeleton_pitch",
            "warp_density": round(warp_meas.density, 2),
            "weft_density": round(weft_meas.density, 2),
            "warp_uncertainty": round(warp_meas.uncertainty, 2),
            "weft_uncertainty": round(weft_meas.uncertainty, 2),
            "warp_pitch_px": round(warp_pitch, 2),
            "weft_pitch_px": round(weft_pitch, 2),
            "warp_spacings_count": len(warp_spacings),
            "weft_spacings_count": len(weft_spacings),
            "decision_status": "ACCEPTED" if (warp_pitch > 0 and weft_pitch > 0) else "NEEDS_REVIEW",
        }
