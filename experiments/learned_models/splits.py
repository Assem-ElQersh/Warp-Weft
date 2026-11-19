# The mechanistic justification for this step is: enforce strict specimen-level disjoint partitioning to eliminate data leakage across training, validation, and test splits, ensuring no fabric specimen or augmented crop from the same sample appears in multiple sets.

import json
import os
import random
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from experiments.learned_models.dataset_adapters import SampleRecord


def create_specimen_splits(
    records: List[SampleRecord],
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    seed: int = 42,
    stratify_by: Optional[str] = "weave_pattern",
) -> Dict[str, List[str]]:
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Split ratios must sum to 1.0"

    rng = random.Random(seed)

    # Group records by unique specimen_id
    specimens: Dict[str, List[SampleRecord]] = defaultdict(list)
    for r in records:
        spec_id = r.specimen_id or r.sample_id
        specimens[spec_id].append(r)

    # If stratification is requested
    groups: Dict[str, List[str]] = defaultdict(list)
    for spec_id, sample_list in specimens.items():
        if stratify_by:
            strat_val = getattr(sample_list[0], stratify_by, "default") or "default"
        else:
            strat_val = "default"
        groups[strat_val].append(spec_id)

    train_ids: List[str] = []
    val_ids: List[str] = []
    test_ids: List[str] = []

    for strat_val, spec_ids in groups.items():
        rng.shuffle(spec_ids)
        n = len(spec_ids)
        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))
        # Ensure at least 1 in test if n >= 3
        if n >= 3 and (n - n_train - n_val) < 1:
            n_train -= 1

        t_spec = spec_ids[:n_train]
        v_spec = spec_ids[n_train : n_train + n_val]
        te_spec = spec_ids[n_train + n_val :]

        for s in t_spec:
            train_ids.extend([rec.sample_id for rec in specimens[s]])
        for s in v_spec:
            val_ids.extend([rec.sample_id for rec in specimens[s]])
        for s in te_spec:
            test_ids.extend([rec.sample_id for rec in specimens[s]])

    splits = {
        "train": sorted(train_ids),
        "validation": sorted(val_ids),
        "test": sorted(test_ids),
    }

    ok, msg = verify_no_data_leakage(splits, records)
    if not ok:
        raise ValueError(f"Split verification failed: {msg}")

    return splits


def verify_no_data_leakage(
    splits: Dict[str, List[str]], records: Optional[List[SampleRecord]] = None
) -> Tuple[bool, str]:
    train_set = set(splits.get("train", []))
    val_set = set(splits.get("validation", []))
    test_set = set(splits.get("test", []))

    # Check sample-level overlap
    tv = train_set.intersection(val_set)
    tt = train_set.intersection(test_set)
    vt = val_set.intersection(test_set)

    if tv:
        return False, f"Sample leakage between train and validation: {len(tv)} common samples"
    if tt:
        return False, f"Sample leakage between train and test: {len(tt)} common samples"
    if vt:
        return False, f"Sample leakage between validation and test: {len(vt)} common samples"

    # If records provided, check specimen-level overlap
    if records:
        id_to_spec = {r.sample_id: (r.specimen_id or r.sample_id) for r in records}
        train_specs = {id_to_spec[sid] for sid in train_set if sid in id_to_spec}
        val_specs = {id_to_spec[sid] for sid in val_set if sid in id_to_spec}
        test_specs = {id_to_spec[sid] for sid in test_set if sid in id_to_spec}

        if train_specs.intersection(val_specs):
            return False, "Specimen leakage between train and val"
        if train_specs.intersection(test_specs):
            return False, "Specimen leakage between train and test"
        if val_specs.intersection(test_specs):
            return False, "Specimen leakage between val and test"

    return True, "No leakage detected. Partitions are strictly disjoint."


def save_splits_manifest(splits: Dict[str, List[str]], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)


def load_splits_manifest(filepath: str) -> Dict[str, List[str]]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
