# ==============================================================================
# Warp & Weft AI — Core Fabric Analysis Package
# ==============================================================================
# The mechanistic justification for this step is: expose the authoritative
# fabric analysis API components from a single top-level package namespace.

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.roi import extract_metric_roi
from src.fabric_analysis.orientation import detect_fabric_skew, rectify_and_crop
from src.fabric_analysis.spectral import compute_spectral_density_multicandidate
from src.fabric_analysis.spatial import compute_spatial_projection_density
from src.fabric_analysis.fusion import evaluate_evidence_fusion
from src.fabric_analysis.pipeline import analyze_fabric, pil_to_base64_data_url
from src.fabric_analysis.calibration_profile import (
    CalibrationProfile,
    get_calibration_profile,
    list_calibration_profiles,
    calibrate_from_two_points,
)
from src.fabric_analysis.specimen_workflow import (
    evaluate_five_region_specimen,
    SpecimenEvaluationResult,
    RegionResult,
)

__all__ = [
    "PhysicalCalibration",
    "extract_metric_roi",
    "detect_fabric_skew",
    "rectify_and_crop",
    "compute_spectral_density_multicandidate",
    "compute_spatial_projection_density",
    "evaluate_evidence_fusion",
    "analyze_fabric",
    "pil_to_base64_data_url",
    "CalibrationProfile",
    "get_calibration_profile",
    "list_calibration_profiles",
    "calibrate_from_two_points",
    "evaluate_five_region_specimen",
    "SpecimenEvaluationResult",
    "RegionResult",
]
