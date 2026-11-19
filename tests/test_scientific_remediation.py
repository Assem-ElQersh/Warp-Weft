# ==============================================================================
# Unit Regression Test Suite: Scientific Remediation & Integrity Policy
# ==============================================================================
# The mechanistic justification for this step is: provide rigorous regression
# tests for confirmed scientific metrology defects: preventing silent default scale
# substitution (400 px/cm), enforcing rejection of unvalidated candidate averaging
# in 5-region specimen evaluation, verifying directional ruler axis isolation,
# and guaranteeing that unverified calibrations cannot produce false PASS statuses.

import math
import os
import sys
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.calibration_profile import (
    CalibrationProfile,
    calibrate_from_two_points,
    get_calibration_profile,
    STANDARD_PROFILES,
)
from src.fabric_analysis.pipeline import analyze_fabric
from src.fabric_analysis.specimen_workflow import (
    evaluate_five_region_specimen,
    RegionResult,
    SpecimenEvaluationResult,
    REQUIRED_REGIONS_COUNT,
)


class TestScientificRemediation(unittest.TestCase):
    """Regression test suite for scientific integrity and physical validity."""

    def test_uncalibrated_image_does_not_produce_accepted_physical_density(self):
        """
        Mechanistic Test: An uncalibrated image (no calibration passed) must NEVER
        silently default to 400 px/cm and must NEVER produce an accepted physical
        density in ends/cm or picks/cm.
        """
        # Create a synthetic periodic image of 300x300 pixels
        img = Image.new("RGB", (300, 300), color=(200, 200, 200))
        res = analyze_fabric(img_pil=img, calibration=None, pixels_per_cm=None)

        results = res["results"]
        # Must not produce accepted physical densities
        self.assertIsNone(
            results.get("accepted_warp_density_ends_per_cm"),
            "Uncalibrated image must not produce accepted warp density",
        )
        self.assertIsNone(
            results.get("accepted_weft_density_picks_per_cm"),
            "Uncalibrated image must not produce accepted weft density",
        )
        self.assertIn(
            results.get("decision_status"),
            ["UNCALIBRATED", "NEEDS_REVIEW"],
            "Uncalibrated image must have UNCALIBRATED or NEEDS_REVIEW status",
        )
        cal = res["calibration"]
        self.assertFalse(
            cal.get("is_verified", True),
            "Uncalibrated image must not have is_verified=True",
        )
        self.assertNotEqual(
            cal.get("calibration_source"),
            "factory_ruler_1cm_optical_graticule",
            "Must not claim an in-scene optical graticule when uncalibrated",
        )

    def test_specimen_workflow_rejects_averaging_rejected_candidates_into_pass(self):
        """
        Mechanistic Test: If any of the required 5 regions fails validation,
        the specimen workflow must NOT average unvalidated candidate values
        into a certified mean to declare specimen_pass=True.
        """
        from unittest.mock import patch

        mock_rejected_result = {
            "results": {
                "accepted_warp_density_ends_per_cm": None,
                "accepted_weft_density_picks_per_cm": None,
                "decision_status": "NEEDS_REVIEW",
                "is_validated": False,
                "signal_quality_index": 25.0,
                "decision_rationale": "Spectral and spatial estimators diverged.",
                "candidate_measurements": {"warp_fft": 31.0, "weft_fft": 27.0},
            },
            "audit": {"proj_warp": 31.0, "proj_weft": 27.0},
            "calibration": {"is_verified": True},
        }

        test_images = [Image.new("RGB", (200, 200), color=(128, 128, 128)) for _ in range(5)]
        cal = PhysicalCalibration.from_scales(263.5, 208.4, is_verified=True)

        with patch("src.fabric_analysis.specimen_workflow.analyze_fabric", return_value=mock_rejected_result):
            result = evaluate_five_region_specimen(
                fabric_id="mock_unvalidated_specimen",
                images=test_images,
                calibration=cal,
                target_warp=31.0,
                target_weft=27.0,
                tolerance=2.0,
            )

        # None of the regions are validated
        self.assertEqual(result.validated_regions_count, 0)
        # Specimen MUST NOT be marked PASS when 0/5 regions are validated!
        self.assertFalse(
            result.specimen_pass is True,
            "Specimen must NOT pass when regions are unvalidated/rejected",
        )
        self.assertEqual(
            result.decision_status,
            "NEEDS_REVIEW",
            "Decision status must be NEEDS_REVIEW when regions fail consensus",
        )
        self.assertIsNone(
            result.warp_mean_ends_per_cm,
            "Certified warp mean must be None when required regions fail validation",
        )

    def test_specimen_workflow_rejects_pass_when_calibration_unverified(self):
        """
        Mechanistic Test: If calibration is unverified, the specimen evaluation
        must not declare an ungrounded certified factory PASS.
        """
        test_images = [Image.new("RGB", (200, 200), color=(128, 128, 128)) for _ in range(5)]
        unverified_cal = PhysicalCalibration.from_scales(263.5, 208.4, is_verified=False)

        result = evaluate_five_region_specimen(
            fabric_id="unverified_cal_specimen",
            images=test_images,
            calibration=unverified_cal,
            target_warp=31.0,
            target_weft=27.0,
            tolerance=2.0,
        )
        self.assertFalse(result.specimen_pass is True)

    def test_horizontal_ruler_only_calibrates_horizontal_scale(self):
        """
        Mechanistic Test: A horizontal ruler measurement (dx) establishes
        horizontal scale (Sx) only. It must NOT silently assign Sx to Sy
        unless square pixels are explicitly declared.
        """
        # Horizontal points: dx = 200 px, dy = 0 px across 1.0 cm
        sx, sy = calibrate_from_two_points(
            pt1=(100, 100),
            pt2=(300, 100),
            known_distance_cm=1.0,
            axis="horizontal",
            assume_square_pixels=False,
        )
        self.assertEqual(sx, 200.0)
        self.assertIsNone(sy, "Horizontal ruler must not calibrate vertical axis without assume_square_pixels")

    def test_vertical_ruler_only_calibrates_vertical_scale(self):
        """
        Mechanistic Test: A vertical ruler measurement (dy) establishes
        vertical scale (Sy) only. It must NOT silently assign Sy to Sx.
        """
        # Vertical points: dx = 0 px, dy = 300 px across 1.5 cm
        sx, sy = calibrate_from_two_points(
            pt1=(100, 100),
            pt2=(100, 400),
            known_distance_cm=1.5,
            axis="vertical",
            assume_square_pixels=False,
        )
        self.assertIsNone(sx, "Vertical ruler must not calibrate horizontal axis without assume_square_pixels")
        self.assertEqual(sy, 200.0)

    def test_ruler_diagonal_is_isotropic_only(self):
        """
        Mechanistic Test: A diagonal ruler measurement yields an isotropic
        Euclidean scale, and must not be claimed as independent X and Y calibration.
        """
        # Diagonal: dx = 300, dy = 400 -> dist = 500 px across 2.5 cm -> 200 px/cm
        sx, sy = calibrate_from_two_points(
            pt1=(0, 0),
            pt2=(300, 400),
            known_distance_cm=2.5,
            axis="both",
            assume_square_pixels=True,
        )
        self.assertEqual(sx, 200.0)
        self.assertEqual(sy, 200.0)

    def test_smartphone_macro_stand_profile_does_not_claim_unverified_graticule(self):
        """
        Mechanistic Test: The smartphone_macro_stand_v1 profile must not claim
        is_verified=True with an optical graticule when its scales were back-calculated.
        """
        profile = get_calibration_profile("smartphone_macro_stand_v1")
        self.assertIsNotNone(profile)
        self.assertIn(
            "back_calculated",
            profile.calibration_source.lower(),
            "Calibration source must state back_calculated, not optical graticule",
        )
        self.assertFalse(
            profile.is_verified,
            "Back-calculated smartphone scale must not be marked is_verified=True",
        )


if __name__ == "__main__":
    unittest.main()
