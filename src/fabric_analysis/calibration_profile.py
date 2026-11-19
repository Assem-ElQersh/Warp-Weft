"""Camera-specific physical calibration profiles and interactive in-plane calibration helpers."""
from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, List, Optional, Tuple

from src.fabric_analysis.calibration import PhysicalCalibration


# Minimum pixel scale to satisfy Nyquist criteria (>= 8 px per yarn period for typical 25-45 threads/cm fabric)
MINIMUM_PRACTICAL_DENSITY_SCALE_PX_PER_CM = 150.0


@dataclass(frozen=True)
class CalibrationProfile:
    """A versioned, traceable calibration profile for a specific acquisition setup."""

    profile_id: str
    display_name: str
    camera_model: str
    lens_description: str
    working_distance_cm: float
    pixels_per_cm_x: float
    pixels_per_cm_y: float
    uncertainty_pct: float
    calibration_date: str
    calibration_source: str
    is_verified: bool
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise ValueError("profile_id must be a non-empty string")
        if self.pixels_per_cm_x <= 0.0 or self.pixels_per_cm_y <= 0.0:
            raise ValueError("Pixel scales must be strictly positive")
        if self.uncertainty_pct < 0.0 or self.uncertainty_pct >= 100.0:
            raise ValueError("uncertainty_pct must be in range [0, 100)")
        if self.working_distance_cm <= 0.0:
            raise ValueError("working_distance_cm must be positive")

    def to_physical_calibration(self) -> PhysicalCalibration:
        """Convert profile to authoritative PhysicalCalibration instance."""
        return PhysicalCalibration.from_scales(
            sx=self.pixels_per_cm_x,
            sy=self.pixels_per_cm_y,
            source=f"profile:{self.profile_id}:{self.calibration_source}",
            is_verified=self.is_verified,
            uncertainty_pct=self.uncertainty_pct,
        )

    def is_resolution_sufficient(self, target_max_threads_per_cm: float = 60.0) -> bool:
        """Check if pixel density satisfies Nyquist sampling for target fabric density."""
        required_scale = target_max_threads_per_cm * 8.0  # 8 pixels per thread minimum
        return min(self.pixels_per_cm_x, self.pixels_per_cm_y) >= required_scale

    def to_dict(self) -> Dict[str, Any]:
        """Serialize profile to dictionary."""
        d = asdict(self)
        d["is_resolution_sufficient"] = self.is_resolution_sufficient()
        return d


def calibrate_from_two_points(
    pt1: Tuple[float, float],
    pt2: Tuple[float, float],
    known_distance_cm: float,
    axis: str = "both",
    assume_square_pixels: bool = False,
) -> Tuple[Optional[float], Optional[float]]:
    """Calculate pixels/cm from two pixel coordinates spanning a known physical distance.

    The mechanistic justification for this step is: prevent ungrounded cross-axis scale
    assignment when measuring a 1D ruler, allowing callers to explicitly require or forgo
    an isotropic square-pixel assumption.

    Parameters:
        pt1: (x1, y1) in image pixel coordinates
        pt2: (x2, y2) in image pixel coordinates
        known_distance_cm: physical distance in centimeters (> 0)
        axis: "horizontal" (uses dx), "vertical" (uses dy), or "both" (euclidean distance)
        assume_square_pixels: whether a 1D axis measurement may be applied to both axes
    Returns:
        (pixels_per_cm_x, pixels_per_cm_y)
    """
    if known_distance_cm <= 0.0:
        raise ValueError("known_distance_cm must be positive")
    dx = abs(pt2[0] - pt1[0])
    dy = abs(pt2[1] - pt1[1])

    valid_axes = ("horizontal", "vertical", "both", "diagonal")
    if axis not in valid_axes:
        raise ValueError(f"Unsupported calibration axis: '{axis}'. Supported: 'horizontal', 'vertical', 'both', 'diagonal'")

    if axis == "horizontal":
        if dx < 1.0:
            raise ValueError("Horizontal pixel distance too small for calibration")
        scale = dx / known_distance_cm
        sx = round(scale, 4)
        sy = round(scale, 4) if assume_square_pixels else None
        return (sx, sy)
    elif axis == "vertical":
        if dy < 1.0:
            raise ValueError("Vertical pixel distance too small for calibration")
        scale = dy / known_distance_cm
        sy = round(scale, 4)
        sx = round(scale, 4) if assume_square_pixels else None
        return (sx, sy)
    elif axis in ("both", "diagonal"):
        if not assume_square_pixels:
            raise ValueError(
                "Diagonal/2D distance cannot calibrate independent X and Y scales without assume_square_pixels=True"
            )
        euclidean_dist = math.hypot(dx, dy)
        if euclidean_dist < 1.0:
            raise ValueError("Pixel distance too small for calibration")
        scale = euclidean_dist / known_distance_cm
        return (round(scale, 4), round(scale, 4))


def calibrate_anisotropic_from_two_rulers(
    h_pt1: Tuple[float, float],
    h_pt2: Tuple[float, float],
    h_known_distance_cm: float,
    v_pt1: Tuple[float, float],
    v_pt2: Tuple[float, float],
    v_known_distance_cm: float,
) -> Tuple[float, float]:
    """Calculate anisotropic (Sx, Sy) from independent horizontal and vertical ruler measurements."""
    sx, _ = calibrate_from_two_points(h_pt1, h_pt2, h_known_distance_cm, axis="horizontal", assume_square_pixels=False)
    _, sy = calibrate_from_two_points(v_pt1, v_pt2, v_known_distance_cm, axis="vertical", assume_square_pixels=False)
    if sx is None or sy is None:
        raise ValueError("Failed to calibrate anisotropic scales from two rulers")
    return (sx, sy)


# Authoritative Standard Profile Library
STANDARD_PROFILES: Dict[str, CalibrationProfile] = {
    "smartphone_macro_stand_v1": CalibrationProfile(
        profile_id="smartphone_macro_stand_v1",
        display_name="Smartphone Fixed Macro Stand (10x Optical Attachment, 6 cm)",
        camera_model="Reference Smartphone",
        lens_description="10x Macro Clip Attachment on Primary Sensor",
        working_distance_cm=6.0,
        pixels_per_cm_x=263.5,
        pixels_per_cm_y=208.4,
        uncertainty_pct=3.0,
        calibration_date="2026-11-17",
        calibration_source="back_calculated_client_specimen_reference",
        is_verified=False,
        notes="Scale empirically back-calculated from client specimen reference pitch; not an in-scene certified optical graticule.",
    ),
    "smartphone_pick_glass_v1": CalibrationProfile(
        profile_id="smartphone_pick_glass_v1",
        display_name="Folding Pick-Glass In-Frame Gauge (1.0 cm Aperture)",
        camera_model="Smartphone Primary Sensor",
        lens_description="Native Lens over 10x Linen Tester Aperture",
        working_distance_cm=4.5,
        pixels_per_cm_x=420.0,
        pixels_per_cm_y=420.0,
        uncertainty_pct=2.0,
        calibration_date="2026-11-17",
        calibration_source="in_frame_1cm_pick_glass_aperture",
        is_verified=True,
        notes="Scale verified against standard 10x 1-inch folding textile pick-glass.",
    ),
    "microscope_fabricnet_nominal": CalibrationProfile(
        profile_id="microscope_fabricnet_nominal",
        display_name="Optical Microscope (5x4 mm FOV — FabricNET Dataset Scale)",
        camera_model="Optical Microscope CMOS Sensor",
        lens_description="Microscope Objective Lens",
        working_distance_cm=1.2,
        pixels_per_cm_x=1280.0,
        pixels_per_cm_y=1200.0,
        uncertainty_pct=5.0,
        calibration_date="2026-11-15",
        calibration_source="dataset_paper_nominal_fov",
        is_verified=False,
        notes="Microscopy dataset nominal scale; strictly invalid for smartphone macro captures.",
    ),
}


def get_calibration_profile(profile_id: str) -> Optional[CalibrationProfile]:
    """Retrieve calibration profile by ID."""
    return STANDARD_PROFILES.get(profile_id)


def list_calibration_profiles() -> List[Dict[str, Any]]:
    """List all available calibration profiles as JSON-serializable dictionaries."""
    return [profile.to_dict() for profile in STANDARD_PROFILES.values()]
