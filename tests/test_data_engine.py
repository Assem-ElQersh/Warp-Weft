# The mechanistic justification for this step is: establish automated unit tests for data registry parsing, dataset adapters, verification routines, and specimen-level split isolation, verifying zero data leakage.

import os
import unittest

from experiments.learned_models.data_registry import DataRegistry
from experiments.learned_models.dataset_adapters import (
    FabricNetAdapter,
    SyntheticSwatchesAdapter,
    get_dataset_adapter,
)
from experiments.learned_models.splits import create_specimen_splits, verify_no_data_leakage
from experiments.learned_models.verify_datasets import DatasetVerifier


class TestDataEngine(unittest.TestCase):
    def setUp(self):
        self.registry = DataRegistry()

    def test_registry_contains_required_datasets(self):
        datasets = self.registry.list_datasets()
        self.assertGreaterEqual(len(datasets), 15)
        ids = [d.dataset_id for d in datasets]
        self.assertIn("fabricnet", ids)
        self.assertIn("client_reference_specimens", ids)
        self.assertIn("fiberdefect_ct", ids)
        self.assertIn("synthetic_micro_swatches", ids)
        self.assertIn("cdatp", ids)

    def test_registry_filters(self):
        cat_a = self.registry.filter_by_category("A")
        self.assertGreaterEqual(len(cat_a), 2)
        for d in cat_a:
            self.assertEqual(d.taxonomy_category, "A")

        calibrated = self.registry.filter_by_calibration(True)
        self.assertGreaterEqual(len(calibrated), 5)
        for d in calibrated:
            self.assertTrue(d.physical_calibration_available)

    def test_fabricnet_adapter_loading(self):
        adapter = get_dataset_adapter("fabricnet")
        self.assertEqual(len(adapter), 130)
        first = adapter[0]
        self.assertEqual(first.dataset_id, "fabricnet")
        self.assertEqual(first.image_width, 640)
        self.assertEqual(first.image_height, 480)
        self.assertEqual(first.scale_x_px_per_cm, 1280.0)
        self.assertEqual(first.scale_y_px_per_cm, 1200.0)
        self.assertIsNotNone(first.warp_density)
        self.assertIsNotNone(first.weft_density)

    def test_synthetic_swatches_adapter(self):
        adapter = get_dataset_adapter("synthetic_micro_swatches")
        self.assertGreaterEqual(len(adapter), 3)
        sample = adapter[0]
        self.assertEqual(sample.dataset_id, "synthetic_micro_swatches")
        self.assertEqual(sample.scale_x_px_per_cm, 400.0)
        self.assertIn(sample.warp_density, [32.0, 36.0])

    def test_zero_leakage_splits(self):
        adapter = get_dataset_adapter("fabricnet")
        splits = create_specimen_splits(
            adapter.samples, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=42
        )
        self.assertEqual(len(splits["train"]), 78)
        self.assertEqual(len(splits["validation"]), 26)
        self.assertEqual(len(splits["test"]), 26)
        ok, msg = verify_no_data_leakage(splits, adapter.samples)
        self.assertTrue(ok)

    def test_dataset_verifier(self):
        verifier = DatasetVerifier()
        res_fab = verifier.verify_fabricnet()
        self.assertEqual(res_fab["status"], "PASS")
        self.assertEqual(res_fab["valid_images"], 130)

        res_syn = verifier.verify_synthetic_swatches()
        self.assertEqual(res_syn["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
