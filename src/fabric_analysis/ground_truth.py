"""Client-aligned manual ground-truth protocol for five-region fabric specimens.

A region label is valid for local image supervision only when its own photograph
is linked through image_path. Specimen averages are never copied back onto
individual regions.
"""
from dataclasses import asdict, dataclass
from datetime import date
from math import isfinite
from statistics import mean, stdev
from typing import Any, Dict, Mapping, Optional, Sequence

EXPECTED_REGIONS_PER_SPECIMEN = 5


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_positive_float(value: Any, field: str) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite positive number or null")
    result = float(value)
    if not isfinite(result) or result <= 0:
        raise ValueError(f"{field} must be a finite positive number or null")
    return result


@dataclass(frozen=True)
class RegionMeasurement:
    """One manual measurement at one physical region of a fabric specimen.

    Counts are raw counts over measurement_length_cm; per-centimeter densities
    are derived properties. image_path may be null when no photograph of this
    exact measured region exists.
    """

    fabric_id: str
    region_id: str
    image_path: Optional[str]
    warp_manual_count: int
    weft_manual_count: int
    measurement_length_cm: float
    camera_id: Optional[str]
    pixels_per_cm_x: Optional[float]
    pixels_per_cm_y: Optional[float]
    calibration_source: Optional[str]
    weave_type: str
    lighting_type: Optional[str]
    focus_quality: Optional[str]
    measurement_date: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "fabric_id", _required_text(self.fabric_id, "fabric_id"))
        object.__setattr__(self, "region_id", _required_text(self.region_id, "region_id"))
        if self.image_path is not None:
            object.__setattr__(self, "image_path", _required_text(self.image_path, "image_path"))
        for field in ("warp_manual_count", "weft_manual_count"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field} must be a non-negative integer")
        if isinstance(self.measurement_length_cm, bool) or not isinstance(self.measurement_length_cm, (int, float)):
            raise ValueError("measurement_length_cm must be a finite positive number")
        length = float(self.measurement_length_cm)
        if not isfinite(length) or length <= 0:
            raise ValueError("measurement_length_cm must be finite and positive")
        object.__setattr__(self, "measurement_length_cm", length)

        sx = _optional_positive_float(self.pixels_per_cm_x, "pixels_per_cm_x")
        sy = _optional_positive_float(self.pixels_per_cm_y, "pixels_per_cm_y")
        if (sx is None) != (sy is None):
            raise ValueError("pixels_per_cm_x and pixels_per_cm_y must both be supplied or both be null")
        object.__setattr__(self, "pixels_per_cm_x", sx)
        object.__setattr__(self, "pixels_per_cm_y", sy)

        for field in ("camera_id", "calibration_source", "lighting_type", "focus_quality"):
            value = getattr(self, field)
            if value is not None:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{field} must be a non-empty string or null")
                object.__setattr__(self, field, value.strip())

        object.__setattr__(self, "weave_type", _required_text(self.weave_type, "weave_type").lower())
        try:
            date.fromisoformat(_required_text(self.measurement_date, "measurement_date"))
        except ValueError as exc:
            raise ValueError("measurement_date must be an ISO-8601 date (YYYY-MM-DD)") from exc

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RegionMeasurement":
        if not isinstance(value, Mapping):
            raise ValueError("Each region measurement must be an object")
        required = {
            "fabric_id", "region_id", "image_path", "warp_manual_count",
            "weft_manual_count", "measurement_length_cm", "camera_id",
            "pixels_per_cm_x", "pixels_per_cm_y", "calibration_source",
            "weave_type", "lighting_type", "focus_quality", "measurement_date",
        }
        missing = sorted(required - set(value.keys()))
        if missing:
            raise ValueError(f"Missing region fields: {', '.join(missing)}")
        return cls(**{key: value[key] for key in required})

    @property
    def warp_ends_per_cm(self) -> float:
        return self.warp_manual_count / self.measurement_length_cm

    @property
    def weft_picks_per_cm(self) -> float:
        return self.weft_manual_count / self.measurement_length_cm

    @property
    def supervision_level(self) -> str:
        return "region_matched" if self.image_path else "specimen_only"

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["warp_ends_per_cm"] = self.warp_ends_per_cm
        result["weft_picks_per_cm"] = self.weft_picks_per_cm
        result["supervision_level"] = self.supervision_level
        return result


@dataclass(frozen=True)
class SpecimenGroundTruth:
    """Five independent, region-level observations for one physical specimen."""

    fabric_id: str
    regions: tuple

    def __post_init__(self) -> None:
        object.__setattr__(self, "fabric_id", _required_text(self.fabric_id, "fabric_id"))
        regions = tuple(self.regions)
        if len(regions) != EXPECTED_REGIONS_PER_SPECIMEN:
            raise ValueError(
                f"Exactly {EXPECTED_REGIONS_PER_SPECIMEN} measured regions are required; got {len(regions)}"
            )
        if any(not isinstance(region, RegionMeasurement) for region in regions):
            raise ValueError("regions must contain RegionMeasurement instances")
        if any(region.fabric_id != self.fabric_id for region in regions):
            raise ValueError("Every region must belong to the specimen fabric_id")
        ids = [region.region_id for region in regions]
        if len(set(ids)) != len(ids):
            raise ValueError("region_id values must be unique within a specimen")
        object.__setattr__(self, "regions", regions)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SpecimenGroundTruth":
        if not isinstance(value, Mapping):
            raise ValueError("Specimen ground truth must be an object")
        if "fabric_id" not in value or "regions" not in value:
            raise ValueError("Specimen record requires fabric_id and regions")
        regions_value = value["regions"]
        if not isinstance(regions_value, Sequence) or isinstance(regions_value, (str, bytes)):
            raise ValueError("regions must be an array")
        return cls(
            fabric_id=value["fabric_id"],
            regions=tuple(RegionMeasurement.from_mapping(item) for item in regions_value),
        )

    @property
    def warp_region_densities(self) -> tuple:
        return tuple(region.warp_ends_per_cm for region in self.regions)

    @property
    def weft_region_densities(self) -> tuple:
        return tuple(region.weft_picks_per_cm for region in self.regions)

    @property
    def warp_mean_ends_per_cm(self) -> float:
        return mean(self.warp_region_densities)

    @property
    def weft_mean_picks_per_cm(self) -> float:
        return mean(self.weft_region_densities)

    @property
    def warp_sample_std_ends_per_cm(self) -> float:
        return stdev(self.warp_region_densities)

    @property
    def weft_sample_std_picks_per_cm(self) -> float:
        return stdev(self.weft_region_densities)

    @property
    def region_matched_count(self) -> int:
        return sum(region.image_path is not None for region in self.regions)

    @property
    def specimen_only_count(self) -> int:
        return EXPECTED_REGIONS_PER_SPECIMEN - self.region_matched_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fabric_id": self.fabric_id,
            "expected_regions": EXPECTED_REGIONS_PER_SPECIMEN,
            "regions": [region.to_dict() for region in self.regions],
            "specimen_summary": {
                "warp_mean_ends_per_cm": self.warp_mean_ends_per_cm,
                "weft_mean_picks_per_cm": self.weft_mean_picks_per_cm,
                "warp_sample_std_ends_per_cm": self.warp_sample_std_ends_per_cm,
                "weft_sample_std_picks_per_cm": self.weft_sample_std_picks_per_cm,
            },
            "region_matched_count": self.region_matched_count,
            "specimen_only_count": self.specimen_only_count,
        }
