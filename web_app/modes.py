"""Honest availability description for the webpage's analysis-mode selector."""
import json
import os
from typing import Any, Dict, Optional


def get_analysis_modes(repository_root: Optional[str] = None) -> Dict[str, Any]:
    """Describe modes without pretending uncommitted/unvalidated weights exist.

    A learned mode becomes available only after a model registry that points to
    an existing checkpoint and an inference adapter are all present.
    """
    root = repository_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    learned_dir = os.path.join(root, "experiments", "learned_models")
    registry = os.path.join(learned_dir, "model_registry.json")
    adapter = os.path.join(root, "web_app", "learned_inference.py")
    checkpoint_ready = False
    try:
        with open(registry, "r", encoding="utf-8") as handle:
            registry_data = json.load(handle)
        checkpoint_path = registry_data.get("checkpoint_path")
        checkpoint_ready = bool(
            isinstance(checkpoint_path, str)
            and checkpoint_path
            and os.path.isfile(os.path.join(learned_dir, checkpoint_path))
        )
    except (OSError, ValueError, TypeError):
        checkpoint_ready = False
    artifact_ready = checkpoint_ready and os.path.isfile(adapter)

    return {
        "default_mode": "classical",
        "modes": [
            {
                "id": "classical",
                "label": "Classical deterministic",
                "available": True,
                "production_ready": True,
                "description": "Existing calibrated 2D FFT + 1D spatial projection + evidence arbiter.",
                "reason": None,
            },
            {
                "id": "learned",
                "label": "Learned models",
                "available": bool(artifact_ready),
                "production_ready": False,
                "description": "Supervised yarn perception/regression using a versioned model artifact.",
                "reason": None if artifact_ready else (
                    "No committed model registry referencing an existing checkpoint and inference adapter are available. "
                    "Reported external/local experiment metrics are not reproducible from this checkout."
                ),
            },
            {
                "id": "hybrid",
                "label": "Hybrid learned perception + physical measurement",
                "available": bool(artifact_ready),
                "production_ready": False,
                "description": "Learned perception proposes yarn evidence; calibrated physical measurement computes density.",
                "reason": None if artifact_ready else (
                    "Hybrid inference requires the same missing, versioned learned-model artifacts and adapter. "
                    "No neural prediction will be substituted for a physical measurement."
                ),
            },
        ],
    }
