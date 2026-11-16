"""Deterministic specimen-grouped data splitting without image/patch leakage."""
import random
from collections import defaultdict
from typing import Any, Dict, List, Mapping, Sequence


def grouped_kfold_indices(
    records: Sequence[Mapping[str, Any]],
    n_splits: int = 5,
    group_key: str = "fabric_id",
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Return grouped K-fold indices; all rows for a specimen stay in one fold."""
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")
    groups: Dict[str, List[int]] = defaultdict(list)
    for index, record in enumerate(records):
        if group_key not in record or record[group_key] is None:
            raise ValueError(f"Every record must contain {group_key}")
        groups[str(record[group_key])].append(index)
    if len(groups) < n_splits:
        raise ValueError(f"Need at least {n_splits} unique groups, found {len(groups)}")

    names = list(groups)
    random.Random(seed).shuffle(names)
    names.sort(key=lambda name: len(groups[name]), reverse=True)
    folds: List[List[str]] = [[] for _ in range(n_splits)]
    fold_sizes = [0] * n_splits
    for name in names:
        target_fold = min(range(n_splits), key=lambda fold: (fold_sizes[fold], fold))
        folds[target_fold].append(name)
        fold_sizes[target_fold] += len(groups[name])

    all_indices = set(range(len(records)))
    output = []
    for fold_index, test_groups in enumerate(folds):
        test_set = set(test_groups)
        test_indices = sorted(index for name in test_groups for index in groups[name])
        train_indices = sorted(all_indices - set(test_indices))
        output.append({
            "fold": fold_index,
            "train_indices": train_indices,
            "test_indices": test_indices,
            "train_groups": sorted(set(groups) - test_set),
            "test_groups": sorted(test_set),
        })
    return output


def grouped_train_validation_test_split(
    records: Sequence[Mapping[str, Any]],
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    group_key: str = "fabric_id",
    seed: int = 42,
) -> Dict[str, Any]:
    """Split by specimen IDs; fractions apply approximately to row counts."""
    if not records:
        raise ValueError("records cannot be empty")
    if train_fraction <= 0 or validation_fraction <= 0 or train_fraction + validation_fraction >= 1:
        raise ValueError("train/validation fractions must be positive and leave a positive test fraction")

    groups: Dict[str, List[int]] = defaultdict(list)
    for index, record in enumerate(records):
        if group_key not in record or record[group_key] is None:
            raise ValueError(f"Every record must contain {group_key}")
        groups[str(record[group_key])].append(index)
    if len(groups) < 3:
        raise ValueError("At least three unique specimens are required for train/validation/test splitting")

    names = list(groups)
    random.Random(seed).shuffle(names)
    names.sort(key=lambda name: len(groups[name]), reverse=True)
    total_rows = len(records)
    targets = [
        total_rows * train_fraction,
        total_rows * validation_fraction,
        total_rows * (1.0 - train_fraction - validation_fraction),
    ]
    split_names: List[List[str]] = [[], [], []]
    split_sizes = [0, 0, 0]

    for name in names:
        remaining_targets = [targets[i] - split_sizes[i] for i in range(3)]
        selected = max(range(3), key=lambda i: (remaining_targets[i], -i))
        split_names[selected].append(name)
        split_sizes[selected] += len(groups[name])

    if any(not values for values in split_names):
        raise ValueError("Grouping left an empty split; add more independent specimens")

    result = {}
    for name, selected_groups in zip(("train", "validation", "test"), split_names):
        indices = sorted(index for group in selected_groups for index in groups[group])
        result[name] = {
            "indices": indices,
            "groups": sorted(selected_groups),
            "n_rows": len(indices),
        }
    result["seed"] = seed
    result["group_key"] = group_key
    return result
