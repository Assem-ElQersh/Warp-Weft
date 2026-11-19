"""Client-validated five-region fabric specimen measurement workflow and tolerance evaluation."""
from dataclasses import asdict, dataclass
import math
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Sequence, Tuple
from PIL import Image

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.pipeline import analyze_fabric


CLIENT_TARGET_WARP_ENDS_PER_CM = 31.0
CLIENT_TARGET_WEFT_PICKS_PER_CM = 27.0
CLIENT_FACTORY_TOLERANCE_THREADS_PER_CM = 2.0
REQUIRED_REGIONS_COUNT = 5


@dataclass(frozen=True)
class RegionResult:
    """Analysis result for a single physical measurement region."""

    region_id: str
    crop_box: Optional[Tuple[int, int, int, int]]
    image_identifier: str
    warp_density_ends_per_cm: Optional[float]
    weft_density_picks_per_cm: Optional[float]
    warp_candidate_ends_per_cm: Optional[float]
    weft_candidate_picks_per_cm: Optional[float]
    decision_status: str
    is_validated: bool
    signal_quality_index: float
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpecimenEvaluationResult:
    """Specimen-level evaluation across 5 independent physical regions against factory tolerance."""

    fabric_id: str
    expected_regions: int
    evaluated_regions_count: int
    validated_regions_count: int
    regions: List[RegionResult]
    warp_mean_ends_per_cm: Optional[float]
    weft_mean_picks_per_cm: Optional[float]
    warp_sample_std_ends_per_cm: Optional[float]
    weft_sample_std_picks_per_cm: Optional[float]
    warp_pass: Optional[bool]
    weft_pass: Optional[bool]
    specimen_pass: Optional[bool]
    target_warp_ends_per_cm: float
    target_weft_picks_per_cm: float
    factory_tolerance_threads_per_cm: float
    decision_status: str
    decision_summary: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["regions"] = [r.to_dict() for r in self.regions]
        return d


def evaluate_five_region_specimen(
    fabric_id: str,
    images: Sequence[Image.Image],
    calibration: PhysicalCalibration,
    roi_boxes: Optional[Sequence[Tuple[int, int, int, int]]] = None,
    target_warp: float = CLIENT_TARGET_WARP_ENDS_PER_CM,
    target_weft: float = CLIENT_TARGET_WEFT_PICKS_PER_CM,
    tolerance: float = CLIENT_FACTORY_TOLERANCE_THREADS_PER_CM,
) -> SpecimenEvaluationResult:
    """Execute five-region specimen analysis and test client acceptance tolerance.

    Supports two input patterns:
      1. Single full-specimen image with exactly 5 ROI boxes provided in roi_boxes.
      2. Exactly 5 separate region images (roi_boxes may be None or match image dimensions).
    """
    if len(images) == 1 and roi_boxes is not None and len(roi_boxes) == REQUIRED_REGIONS_COUNT:
        base_img = images[0]
        region_items = []
        for i, box in enumerate(roi_boxes, start=1):
            cropped = base_img.crop(box)
            region_items.append((f"R{i}", cropped, box, f"{fabric_id}_single_img_ROI_{i}"))
    elif len(images) == REQUIRED_REGIONS_COUNT:
        region_items = []
        for i, img in enumerate(images, start=1):
            box = roi_boxes[i - 1] if (roi_boxes and len(roi_boxes) == REQUIRED_REGIONS_COUNT) else None
            region_items.append((f"R{i}", img, box, f"{fabric_id}_region_img_{i}"))
    else:
        raise ValueError(
            f"Expected either 1 image with 5 ROI boxes, or exactly 5 separate region images. Got {len(images)} images."
        )

    region_results: List[RegionResult] = []
    warp_values: List[float] = []
    weft_values: List[float] = []

    for r_id, r_img, r_box, r_ident in region_items:
        res = analyze_fabric(r_img, calibration=calibration)
        results = res["results"]
        audit = res["audit"]
        cands = results["candidate_measurements"]

        accepted_warp = results.get("accepted_warp_density_ends_per_cm")
        accepted_weft = results.get("accepted_weft_density_picks_per_cm")
        cand_warp = cands.get("warp_fft") or audit.get("proj_warp")
        cand_weft = cands.get("weft_fft") or audit.get("proj_weft")
        status = results.get("decision_status", "NEEDS_REVIEW")
        is_val = results.get("is_validated", False)
        sqi = float(results.get("signal_quality_index", 0.0))

        # The mechanistic justification for this step is: ensure only consensus-validated,
        # accepted densities are incorporated into specimen-level statistics, strictly
        # excluding rejected or unvalidated candidate estimates from certified means.
        if is_val and accepted_warp is not None and math.isfinite(accepted_warp) and accepted_warp > 0:
            warp_values.append(float(accepted_warp))
        if is_val and accepted_weft is not None and math.isfinite(accepted_weft) and accepted_weft > 0:
            weft_values.append(float(accepted_weft))

        region_results.append(
            RegionResult(
                region_id=r_id,
                crop_box=r_box,
                image_identifier=r_ident,
                warp_density_ends_per_cm=accepted_warp,
                weft_density_picks_per_cm=accepted_weft,
                warp_candidate_ends_per_cm=cand_warp,
                weft_candidate_picks_per_cm=cand_weft,
                decision_status=status,
                is_validated=is_val,
                signal_quality_index=sqi,
                notes=results.get("decision_rationale", ""),
            )
        )

    validated_count = sum(r.is_validated for r in region_results)

    # A certified specimen mean strictly requires all 5 regions to be validated
    all_regions_validated = (
        validated_count == REQUIRED_REGIONS_COUNT
        and len(warp_values) == REQUIRED_REGIONS_COUNT
        and len(weft_values) == REQUIRED_REGIONS_COUNT
    )
    calibration_verified = bool(calibration and getattr(calibration, "is_verified", False))

    if all_regions_validated:
        warp_mean = mean(warp_values)
        weft_mean = mean(weft_values)
        warp_std = stdev(warp_values) if len(warp_values) >= 2 else 0.0
        weft_std = stdev(weft_values) if len(weft_values) >= 2 else 0.0
    else:
        warp_mean = None
        weft_mean = None
        warp_std = None
        weft_std = None

    warp_pass = None
    weft_pass = None
    specimen_pass = None

    if all_regions_validated and calibration_verified:
        warp_pass = abs(warp_mean - target_warp) <= tolerance
        weft_pass = abs(weft_mean - target_weft) <= tolerance
        specimen_pass = warp_pass and weft_pass
        if specimen_pass:
            decision_status = "PASS"
            decision_summary = (
                f"Specimen {fabric_id} PASSED factory tolerance: "
                f"Warp={warp_mean:.1f} (target {target_warp}±{tolerance}), "
                f"Weft={weft_mean:.1f} (target {target_weft}±{tolerance})."
            )
        else:
            decision_status = "FAIL"
            decision_summary = (
                f"Specimen {fabric_id} FAILED factory tolerance: "
                f"Warp={warp_mean:.1f} ({'PASS' if warp_pass else 'FAIL'}), "
                f"Weft={weft_mean:.1f} ({'PASS' if weft_pass else 'FAIL'})."
            )
    elif all_regions_validated and not calibration_verified:
        warp_pass = abs(warp_mean - target_warp) <= tolerance
        weft_pass = abs(weft_mean - target_weft) <= tolerance
        specimen_pass = False
        decision_status = "UNVERIFIED_CALIBRATION"
        decision_summary = (
            f"Specimen {fabric_id} has {REQUIRED_REGIONS_COUNT} validated regions but UNVERIFIED calibration "
            f"({calibration.calibration_source if calibration else 'none'}). "
            f"Certified factory pass requires verified physical calibration."
        )
    else:
        decision_status = "NEEDS_REVIEW"
        decision_summary = (
            f"Specimen {fabric_id} requires review: {validated_count}/{REQUIRED_REGIONS_COUNT} regions validated. "
            f"Insufficient valid measurements to compute certified 5-region mean."
        )

    return SpecimenEvaluationResult(
        fabric_id=fabric_id,
        expected_regions=REQUIRED_REGIONS_COUNT,
        evaluated_regions_count=len(region_results),
        validated_regions_count=validated_count,
        regions=region_results,
        warp_mean_ends_per_cm=round(warp_mean, 2) if warp_mean is not None else None,
        weft_mean_picks_per_cm=round(weft_mean, 2) if weft_mean is not None else None,
        warp_sample_std_ends_per_cm=round(warp_std, 2) if warp_std is not None else None,
        weft_sample_std_picks_per_cm=round(weft_std, 2) if weft_std is not None else None,
        warp_pass=warp_pass,
        weft_pass=weft_pass,
        specimen_pass=specimen_pass,
        target_warp_ends_per_cm=target_warp,
        target_weft_picks_per_cm=target_weft,
        factory_tolerance_threads_per_cm=tolerance,
        decision_status=decision_status,
        decision_summary=decision_summary,
    )
