import unittest

from src.fabric_analysis.grouped_splits import grouped_kfold_indices, grouped_train_validation_test_split


class TestGroupedSplits(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"fabric_id": f"F{i}", "region_id": f"R{j}"}
            for i in range(12) for j in range(5)
        ]

    def test_kfold_never_splits_a_specimen_across_folds(self):
        folds = grouped_kfold_indices(self.records, n_splits=4, seed=13)
        observed = {}
        for fold in folds:
            for group in fold["test_groups"]:
                self.assertNotIn(group, observed)
                observed[group] = fold["fold"]
            self.assertFalse(set(fold["train_groups"]) & set(fold["test_groups"]))
        self.assertEqual(set(observed), {f"F{i}" for i in range(12)})

    def test_holdout_split_has_disjoint_specimen_groups(self):
        split = grouped_train_validation_test_split(self.records, seed=9)
        groups = [set(split[name]["groups"]) for name in ("train", "validation", "test")]
        self.assertFalse(groups[0] & groups[1])
        self.assertFalse(groups[0] & groups[2])
        self.assertFalse(groups[1] & groups[2])
        self.assertEqual(len(set.union(*groups)), 12)

    def test_rejects_missing_group_identifier(self):
        with self.assertRaisesRegex(ValueError, "fabric_id"):
            grouped_kfold_indices([{"region_id":"R1"}], n_splits=2)


if __name__ == "__main__":
    unittest.main()
