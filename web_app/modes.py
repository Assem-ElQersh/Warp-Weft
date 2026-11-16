"""Honest availability description for the webpage's analysis-mode selector."""
import json
import os
from typing import Any, Dict, Optional


def get_analysis_modes(repository_root: Optional[str] = None) -> Dict[str, Any]:
    """Describe modes without pretending uncommitted/unvalidated weights exist.

    Artifact presence is reported separately. The mode remains unavailable until
    the HTTP server has an explicit, validated learned inference dispatcher.
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
    artifacts_present = checkpoint_ready and os.path.isfile(adapter)

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
                "available": False,
                "artifacts_present": bool(artifacts_present),
                "production_ready": False,
                "description": "Supervised yarn perception/regression using a versioned model artifact.",
                "reason": (
                    "A learned checkpoint and adapter may be present, but this server has no validated learned inference dispatcher. "
                    "The mode remains disabled to prevent silently returning classical results."
                ),
            },
            {
                "id": "hybrid",
                "label": "Hybrid learned perception + physical measurement",
                "available": False,
                "artifacts_present": bool(artifacts_present),
                "production_ready": False,
                "description": "Learned perception proposes yarn evidence; calibrated physical measurement computes density.",
                "reason": (
                    "Hybrid inference has no validated learned inference dispatcher in this server. "
                    "No neural prediction will be substituted for a physical measurement."
                ),
            },
        ],
    }
