"""Evaluation metrics for client-aligned physical thread-density validation.

Rejected/None predictions are not silently dropped from coverage statistics.
Error metrics are computed only over returned predictions and are accompanied
by explicit denominators and rejection rates.
"""
import math
import random
from collections import defaultdict
from statistics import median
from typing import Any, Dict, List, Mapping, Optional, Sequence


def _finite_number(value: Any) -> bool:
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def axis_metrics(
    targets: Sequence[float],
    predictions: Sequence[Optional[float]],
    runtimes_ms: Optional[Sequence[Optional[float]]] = None,
    tolerance: float = 2.0,
    bootstrap_samples: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Compute error, ±1/±2 accuracy, coverage and rejection metrics for one axis."""
    if len(targets) != len(predictions):
        raise ValueError("targets and predictions must have the same length")
    if runtimes_ms is not None and len(runtimes_ms) != len(targets):
        raise ValueError("runtimes_ms must match targets length")
    if len(targets) == 0:
        raise ValueError("At least one target is required")
    tol = float(tolerance)
    if not math.isfinite(tol) or tol < 0:
        raise ValueError("tolerance must be finite and non-negative")
    if bootstrap_samples < 0:
        raise ValueError("bootstrap_samples must be non-negative")

    errors: List[float] = []
    signed_errors: List[float] = []
    accepted_runtimes: List[float] = []
    all_runtimes: List[float] = []

    for index, (target, prediction) in enumerate(zip(targets, predictions)):
        if not _finite_number(target):
            raise ValueError(f"Target at index {index} is not finite")
        if prediction is not None and not _finite_number(prediction):
            prediction = None
        if prediction is not None:
            signed = float(prediction) - float(target)
            signed_errors.append(signed)
            errors.append(abs(signed))
        if runtimes_ms is not None:
            runtime = runtimes_ms[index]
            if runtime is not None and _finite_number(runtime) and float(runtime) >= 0:
                all_runtimes.append(float(runtime))
                if prediction is not None:
                    accepted_runtimes.append(float(runtime))

    total = len(targets)
    predicted = len(errors)
    rejected = total - predicted
    result: Dict[str, Any] = {
        "n_total": total,
        "n_predicted": predicted,
        "n_rejected": rejected,
        "coverage_pct": round(predicted / total * 100.0, 2),
        "rejection_rate_pct": round(rejected / total * 100.0, 2),
        "tolerance": tol,
        "mae": None,
        "rmse": None,
        "median_absolute_error": None,
        "mean_signed_bias": None,
        "within_1_pct": None,
        "within_2_pct": None,
        "runtime_mean_ms": round(sum(accepted_runtimes) / len(accepted_runtimes), 3) if accepted_runtimes else None,
        "runtime_median_ms": round(median(accepted_runtimes), 3) if accepted_runtimes else None,
        "runtime_observations": len(accepted_runtimes),
        "runtime_all_mean_ms": round(sum(all_runtimes) / len(all_runtimes), 3) if all_runtimes else None,
    }
    if predicted == 0:
        result["mae_bootstrap_95_ci"] = None
        return result

    result.update({
        "mae": round(sum(errors) / predicted, 6),
        "rmse": round(math.sqrt(sum(error * error for error in errors) / predicted), 6),
        "median_absolute_error": round(median(errors), 6),
        "mean_signed_bias": round(sum(signed_errors) / predicted, 6),
        "within_1_pct": round(sum(error <= 1.0 for error in errors) / predicted * 100.0, 2),
        "within_2_pct": round(sum(error <= tol for error in errors) / predicted * 100.0, 2),
    })

    if bootstrap_samples:
        rng = random.Random(seed)
        bootstrap_mae = []
        for _ in range(bootstrap_samples):
            draw = [errors[rng.randrange(predicted)] for _ in range(predicted)]
            bootstrap_mae.append(sum(draw) / predicted)
        bootstrap_mae.sort()
        low_index = int(0.025 * (bootstrap_samples - 1))
        high_index = int(0.975 * (bootstrap_samples - 1))
        result["mae_bootstrap_95_ci"] = {
            "lower": round(bootstrap_mae[low_index], 6),
            "upper": round(bootstrap_mae[high_index], 6),
            "samples": bootstrap_samples,
            "seed": seed,
        }
    else:
        result["mae_bootstrap_95_ci"] = None
    return result


def evaluate_prediction_records(
    records: Sequence[Mapping[str, Any]],
    tolerance: float = 2.0,
    bootstrap_samples: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Evaluate local-region predictions with global, per-weave and per-specimen views.

    Required keys per record: fabric_id, weave_type, warp_manual_density,
    weft_manual_density, warp_predicted_density, weft_predicted_density.
    A null prediction is a rejected measurement, not an omitted sample.
    """
    if len(records) == 0:
        raise ValueError("records cannot be empty")

    def one_axis(items: Sequence[Mapping[str, Any]], axis: str) -> Dict[str, Any]:
        return axis_metrics(
            [item[f"{axis}_manual_density"] for item in items],
            [item.get(f"{axis}_predicted_density") for item in items],
            [item.get("runtime_ms") for item in items],
            tolerance=tolerance,
            bootstrap_samples=bootstrap_samples,
            seed=seed,
        )

    result: Dict[str, Any] = {
        "n_regions": len(records),
        "warp": one_axis(records, "warp"),
        "weft": one_axis(records, "weft"),
        "per_weave": {},
        "per_specimen": {},
    }
    by_weave: Dict[str, list] = defaultdict(list)
    by_specimen: Dict[str, list] = defaultdict(list)
    for item in records:
        by_weave[str(item.get("weave_type") or "unknown")].append(item)
        by_specimen[str(item["fabric_id"])].append(item)

    for key, items in sorted(by_weave.items()):
        result["per_weave"][key] = {
            "n_regions": len(items),
            "warp": one_axis(items, "warp"),
            "weft": one_axis(items, "weft"),
        }
    for key, items in sorted(by_specimen.items()):
        result["per_specimen"][key] = {
            "n_regions": len(items),
            "warp": one_axis(items, "warp"),
            "weft": one_axis(items, "weft"),
        }
    return result
