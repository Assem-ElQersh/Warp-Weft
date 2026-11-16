# ==============================================================================
# Warp & Weft AI — Physical Calibration Module
# ==============================================================================
# The mechanistic justification for this step is: provide an authoritative,
# immutable physical calibration object that supports anisotropic horizontal (X)
# and vertical (Y) optical sensor scaling, preventing systematic metric density
# distortion caused by non-square sensor aspect ratios or rectangular fields of view.

from dataclasses import dataclass, asdict
import math
from typing import Tuple, Dict, Any, Optional


@dataclass(frozen=True)
class PhysicalCalibration:
    """
    Physical spatial calibration specifying sensor pixel density per centimeter.
    """
    pixels_per_cm_x: float
    pixels_per_cm_y: float
    pixel_pitch_um_x: float
    pixel_pitch_um_y: float
    calibration_source: str
    is_verified: bool
    uncertainty_pct: float

    @classmethod
    def from_scales(cls,
                    sx: float,
                    sy: Optional[float] = None,
                    source: str = "user_specified",
                    is_verified: bool = False,
                    uncertainty_pct: float = 5.0) -> "PhysicalCalibration":
        """
        The mechanistic justification for this step is: construct a calibration
        instance from horizontal and vertical pixel scales, defaulting to isotropic
        scaling if vertical scale is omitted.
        """
        sx = float(sx)
        sy = float(sy) if sy is not None else sx
        uncertainty = float(uncertainty_pct)
        if not math.isfinite(sx) or not math.isfinite(sy) or sx <= 0.0 or sy <= 0.0:
            raise ValueError(f"Spatial calibration scales must be finite and positive: sx={sx}, sy={sy}")
        if not math.isfinite(uncertainty) or uncertainty < 0.0 or uncertainty >= 100.0:
            raise ValueError("uncertainty_pct must be finite and in the range [0, 100)")

        pitch_x = 10000.0 / sx
        pitch_y = 10000.0 / sy

        return cls(
            pixels_per_cm_x=round(sx, 4),
            pixels_per_cm_y=round(sy, 4),
            pixel_pitch_um_x=round(pitch_x, 4),
            pixel_pitch_um_y=round(pitch_y, 4),
            calibration_source=str(source),
            is_verified=bool(is_verified),
            uncertainty_pct=uncertainty
        )

    @classmethod
    def from_fov(cls,
                 image_width_px: int,
                 image_height_px: int,
                 fov_width_cm: float,
                 fov_height_cm: float,
                 source: str = "optical_fov_hardware",
                 is_verified: bool = True,
                 uncertainty_pct: float = 1.0) -> "PhysicalCalibration":
        """
        The mechanistic justification for this step is: compute exact anisotropic
        calibration scales from known optical sensor resolution and physical field of view.
        """
        if image_width_px <= 0 or image_height_px <= 0:
            raise ValueError(f"Invalid pixel dimensions: {image_width_px}x{image_height_px}")
        if fov_width_cm <= 0.0 or fov_height_cm <= 0.0:
            raise ValueError(f"Invalid physical FOV: {fov_width_cm}x{fov_height_cm} cm")

        sx = float(image_width_px) / float(fov_width_cm)
        sy = float(image_height_px) / float(fov_height_cm)

        return cls.from_scales(
            sx=sx,
            sy=sy,
            source=source,
            is_verified=is_verified,
            uncertainty_pct=uncertainty_pct
        )

    @classmethod
    def from_dpi(cls,
                 dpi_x: float,
                 dpi_y: Optional[float] = None,
                 source: str = "scanner_hardware_dpi",
                 is_verified: bool = True,
                 uncertainty_pct: float = 0.5) -> "PhysicalCalibration":
        """
        The mechanistic justification for this step is: map scanner dots-per-inch (DPI)
        to metric pixels-per-centimeter using the exact international inch constant (2.54 cm).
        """
        sx = float(dpi_x) / 2.54
        sy = (float(dpi_y) / 2.54) if dpi_y is not None else sx
        return cls.from_scales(
            sx=sx,
            sy=sy,
            source=source,
            is_verified=is_verified,
            uncertainty_pct=uncertainty_pct
        )

    @property
    def is_isotropic(self) -> bool:
        """Check if horizontal and vertical scales match within 0.1% tolerance."""
        return abs(self.pixels_per_cm_x - self.pixels_per_cm_y) / max(self.pixels_per_cm_x, 1e-5) < 0.001

    @property
    def aspect_ratio(self) -> float:
        """Ratio of horizontal pixel size to vertical pixel size (Sx / Sy)."""
        return self.pixels_per_cm_x / self.pixels_per_cm_y

    def density_interval(self, density: Optional[float]) -> Optional[Dict[str, float]]:
        """Return calibration-only bounds; this is not a statistical confidence interval."""
        if density is None:
            return None
        value = float(density)
        if not math.isfinite(value) or value < 0.0:
            raise ValueError("density must be a finite non-negative number or null")
        delta = value * self.uncertainty_pct / 100.0
        return {
            "nominal": round(value, 6),
            "lower": round(max(0.0, value - delta), 6),
            "upper": round(value + delta, 6),
            "absolute_uncertainty": round(delta, 6),
            "relative_uncertainty_pct": self.uncertainty_pct,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize calibration object to JSON-serializable dictionary."""
        d = asdict(self)
        d["is_isotropic"] = self.is_isotropic
        d["aspect_ratio"] = round(self.aspect_ratio, 4)
        return d
