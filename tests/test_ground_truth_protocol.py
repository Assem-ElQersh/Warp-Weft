import json
import os
import unittest

from src.fabric_analysis.ground_truth import GROUND_TRUTH_SCHEMA_VERSION, RegionMeasurement, SpecimenGroundTruth


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
        self.assertEqual(specimen.to_dict()["schema_version"], GROUND_TRUTH_SCHEMA_VERSION)
        self.assertEqual(specimen.warp_mean_ends_per_cm, 31.0)
        self.assertEqual(specimen.weft_mean_picks_per_cm, 27.0)
        self.assertEqual(specimen.region_matched_count, 5)
        self.assertEqual(specimen.specimen_only_count, 0)
        self.assertAlmostEqual(specimen.warp_sample_std_ends_per_cm, 1.0)

    def test_serialized_payload_keys_match_versioned_json_schema(self):
        specimen = SpecimenGroundTruth("fabric-A", tuple(make_region(i, 31, 27) for i in range(1, 6)))
        payload = specimen.to_dict()
        schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", "client_ground_truth.schema.json")
        with open(schema_path, "r", encoding="utf-8") as handle:
            schema = json.load(handle)
        self.assertTrue(set(payload).issubset(set(schema["properties"])))
        self.assertTrue(set(schema["required"]).issubset(set(payload)))
        region_schema = schema["$defs"]["region"]
        for region in payload["regions"]:
            self.assertTrue(set(region).issubset(set(region_schema["properties"])))
            self.assertTrue(set(region_schema["required"]).issubset(set(region)))
        self.assertEqual(payload["expected_regions"], 5)

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

    def test_from_mapping_requires_and_checks_schema_version(self):
        specimen = SpecimenGroundTruth("fabric-A", tuple(make_region(i, 31, 27) for i in range(1, 6)))
        payload = specimen.to_dict()
        self.assertEqual(SpecimenGroundTruth.from_mapping(payload).schema_version, GROUND_TRUTH_SCHEMA_VERSION)
        payload["schema_version"] = "99.0.0"
        with self.assertRaisesRegex(ValueError, "Unsupported ground-truth schema_version"):
            SpecimenGroundTruth.from_mapping(payload)
        del payload["schema_version"]
        with self.assertRaisesRegex(ValueError, "requires schema_version"):
            SpecimenGroundTruth.from_mapping(payload)

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
