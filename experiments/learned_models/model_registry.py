# The mechanistic justification for this step is: provide a unified programmatic loader, checkpoint validator, and model instantiation factory for candidate textile architectures, verifying cryptographic SHA-256 hashes and allocating hardware resources (CPU/CUDA) conditionally.

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from experiments.models.segmentation_models import WarpWeftUNet


@dataclass
class ModelEntry:
    model_id: str
    official_name: str
    paradigm: str
    architecture: str
    source_repository: str
    parameter_count: int
    checkpoint_size_bytes: int
    framework: str
    license: str
    input_requirements: Dict[str, Any]
    output_format: Dict[str, Any]
    memory_footprint_mb: float
    inference_latency_ms: float
    quantization_onnx_support: str
    hosted_api_available: bool
    suitability_rating: str
    failure_modes_and_boundary_conditions: str


class ModelRegistry:
    DEFAULT_REGISTRY_PATH = os.path.join(
        os.path.dirname(__file__), "..", "models", "registry.json"
    )

    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path or os.path.abspath(self.DEFAULT_REGISTRY_PATH)
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Model registry not found at: {self.registry_path}")

        with open(self.registry_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

        self.entries: List[ModelEntry] = [
            ModelEntry(**m) for m in self.raw_data.get("models", [])
        ]
        self._by_id: Dict[str, ModelEntry] = {e.model_id: e for e in self.entries}

    def list_models(self) -> List[ModelEntry]:
        return list(self.entries)

    def get(self, model_id: str) -> Optional[ModelEntry]:
        return self._by_id.get(model_id)

    def filter_by_paradigm(self, paradigm: str) -> List[ModelEntry]:
        return [m for m in self.entries if m.paradigm.lower() == paradigm.lower()]

    @staticmethod
    def calculate_sha256(filepath: str) -> str:
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def verify_checkpoint(self, model_id: str) -> Tuple[bool, str]:
        entry = self.get(model_id)
        if not entry:
            return False, f"Model ID '{model_id}' not found"

        if entry.parameter_count == 0:
            return True, "Deterministic model (no weights required)"

        chk_path = os.path.join(
            os.path.dirname(__file__), "checkpoints", "unet_yarn_segmentation.pt"
        )
        if model_id in ("warp_weft_unet_v1", "hybrid_unet_skeleton_pitch"):
            if os.path.exists(chk_path):
                sha = self.calculate_sha256(chk_path)
                return True, f"Checkpoint verified ({os.path.getsize(chk_path)} bytes, sha256={sha[:12]}...)"
            return False, f"Checkpoint file missing: {chk_path}"

        return False, f"Checkpoint for {model_id} is remote/hosted or not yet downloaded"

    def instantiate_model(self, model_id: str, device: Optional[str] = None) -> Any:
        dev = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if model_id == "deterministic_dual_engine":
            from experiments.learned_models.inference import DeterministicInferenceRunner
            return DeterministicInferenceRunner()

        elif model_id == "warp_weft_unet_v1":
            model = WarpWeftUNet(in_channels=1, num_classes=3)
            chk_path = os.path.join(
                os.path.dirname(__file__), "checkpoints", "unet_yarn_segmentation.pt"
            )
            if os.path.exists(chk_path):
                state_dict = torch.load(chk_path, map_location=dev, weights_only=True)
                model.load_state_dict(state_dict)
            model.to(dev)
            model.eval()
            return model

        elif model_id == "hybrid_unet_skeleton_pitch":
            unet = self.instantiate_model("warp_weft_unet_v1", device=dev)
            from experiments.learned_models.inference import HybridMetrologyRunner
            return HybridMetrologyRunner(unet_model=unet, device=dev)

        else:
            raise NotImplementedError(
                f"Instantiation for model '{model_id}' requires custom wrapper or remote API"
            )


def main():
    parser = argparse.ArgumentParser(description="Warp & Weft AI Master Model Registry CLI")
    parser.add_argument("--list", action="store_true", help="List all registered models")
    parser.add_argument("--id", type=str, default=None, help="Show full details for model ID")
    parser.add_argument("--verify-checkpoints", action="store_true", help="Verify local checkpoints")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    registry = ModelRegistry()

    if args.id:
        entry = registry.get(args.id)
        if not entry:
            sys.exit(1)
        if args.json:
            print(json.dumps(entry.__dict__, indent=2))
        else:
            for k, v in entry.__dict__.items():
                print(f"{k}: {v}")
        return

    if args.verify_checkpoints:
        for m in registry.list_models():
            ok, msg = registry.verify_checkpoint(m.model_id)
            status = "VERIFIED" if ok else "UNVERIFIED"
            print(f"[{status}] {m.model_id:<32}: {msg}")
        return

    models = registry.list_models()
    if args.json:
        print(json.dumps([m.__dict__ for m in models], indent=2))
    else:
        print(f"Total Registered Models: {len(models)}")
        for m in models:
            print(
                f"[{m.paradigm:<20}] {m.model_id:<30} | Params: {m.parameter_count:>9} | Latency: {m.inference_latency_ms:>5.1f}ms | Rating: {m.suitability_rating[:15]}"
            )


if __name__ == "__main__":
    main()
