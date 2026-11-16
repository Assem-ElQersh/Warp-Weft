import unittest

from src.fabric_analysis.ground_truth import RegionMeasurement, SpecimenGroundTruth


def make_region(index, warp, weft, image=True):
    return RegionMeasurement(
        fabric_id="fabric-A",
        region_id=f"R{index}",
        image_path=f"images/R{index}.jpg" if image else None,
        warp_manual_count=warp,
        weft_manual_count=weft,
        measurement_length_cm=1.0,
        camera_id="phone-1",
        pixels_per_cm_x=1280.0,
        pixels_per_cm_y=1200.0,
        calibration_source="stage_micrometer",
        weave_type="plain",
        lighting_type="diffuse_front",
        focus_quality="sharp",
        measurement_date="2026-11-16",
    )


class TestClientGroundTruthProtocol(unittest.TestCase):
    def test_five_region_mean_and_sample_std_are_derived_from_raw_counts(self):
        specimen = SpecimenGroundTruth("fabric-A", (
            make_region(1, 30, 26),
            make_region(2, 32, 27),
            make_region(3, 31, 28),
            make_region(4, 30, 27),
            make_region(5, 32, 27),
        ))
        self.assertEqual(specimen.warp_mean_ends_per_cm, 31.0)
        self.assertEqual(specimen.weft_mean_picks_per_cm, 27.0)
        self.assertEqual(specimen.region_matched_count, 5)
        self.assertEqual(specimen.specimen_only_count, 0)
        self.assertAlmostEqual(specimen.warp_sample_std_ends_per_cm, 1.0)

    def test_specimen_average_is_not_written_back_as_region_label(self):
        specimen = SpecimenGroundTruth("fabric-A", (
            make_region(1, 30, 26, image=False),
            make_region(2, 32, 27, image=False),
            make_region(3, 31, 28, image=False),
            make_region(4, 30, 27, image=False),
            make_region(5, 32, 27, image=False),
        ))
        serialized = specimen.to_dict()
        self.assertEqual(serialized["region_matched_count"], 0)
        self.assertTrue(all(item["image_path"] is None for item in serialized["regions"]))
        self.assertTrue(all(item["supervision_level"] == "specimen_only" for item in serialized["regions"]))
        self.assertNotIn("specimen_mean", serialized["regions"][0])

    def test_rejects_wrong_number_of_regions(self):
        with self.assertRaisesRegex(ValueError, "Exactly 5"):
            SpecimenGroundTruth("fabric-A", (make_region(1, 30, 26),))

    def test_rejects_mixed_fabric_ids_and_duplicate_regions(self):
        with self.assertRaisesRegex(ValueError, "belong to"):
            SpecimenGroundTruth("fabric-A", tuple(
                RegionMeasurement(**{**make_region(i, 30, 27).__dict__, "fabric_id": "other" if i == 5 else "fabric-A"})
                for i in range(1, 6)
            ))
        with self.assertRaisesRegex(ValueError, "unique"):
            SpecimenGroundTruth("fabric-A", tuple(
                make_region(1 if i == 5 else i, 30, 27) for i in range(1, 6)
            ))

    def test_rejects_partial_anisotropic_calibration(self):
        values = make_region(1, 30, 27).__dict__.copy()
        values["pixels_per_cm_y"] = None
        with self.assertRaisesRegex(ValueError, "both be supplied"):
            RegionMeasurement(**values)


if __name__ == "__main__":
    unittest.main()
