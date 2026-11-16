"""Evaluation metrics for client-aligned physical thread-density validation.

Rejected predictions remain in coverage denominators. Region-level confidence
intervals use specimen-cluster bootstrap when specimen IDs are supplied.
Specimen-level metrics require all five regional predictions, matching the
client's five-location manual averaging protocol.
"""
import math
import random
from collections import defaultdict
from statistics import mean, median
from typing import Any, Dict, List, Mapping, Optional, Sequence


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _percentile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("Cannot calculate a percentile from an empty sequence")
    position = (len(sorted_values) - 1) * probability
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(sorted_values[lower])
    fraction = position - lower
    return float(sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction)


def axis_metrics(
    targets: Sequence[float],
    predictions: Sequence[Optional[float]],
    runtimes_ms: Optional[Sequence[Optional[float]]] = None,
    tolerance: float = 2.0,
    bootstrap_samples: int = 1000,
    seed: int = 42,
    groups: Optional[Sequence[Any]] = None,
) -> Dict[str, Any]:
    """Compute errors, ±1/±2 accuracy, coverage, rejection and runtime.

    When groups are supplied, MAE confidence intervals resample independent
    groups (normally fabric_id) with replacement, retaining all rows from a
    specimen. Without groups, the legacy row bootstrap is retained.
    """
    if len(targets) != len(predictions):
        raise ValueError("targets and predictions must have the same length")
    if runtimes_ms is not None and len(runtimes_ms) != len(targets):
        raise ValueError("runtimes_ms must match targets length")
    if groups is not None and len(groups) != len(targets):
        raise ValueError("groups must match targets length")
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
    accepted_groups: List[Any] = []

    for index, (target, prediction) in enumerate(zip(targets, predictions)):
        if not _finite_number(target):
            raise ValueError(f"Target at index {index} is not a finite non-boolean number")
        if prediction is not None and not _finite_number(prediction):
            prediction = None
        if prediction is not None:
            signed = float(prediction) - float(target)
            signed_errors.append(signed)
            errors.append(abs(signed))
            if groups is not None:
                accepted_groups.append(groups[index])
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
        "within_tolerance_pct": None,
        "runtime_mean_ms": round(sum(accepted_runtimes) / len(accepted_runtimes), 3) if accepted_runtimes else None,
        "runtime_median_ms": round(median(accepted_runtimes), 3) if accepted_runtimes else None,
        "runtime_observations": len(accepted_runtimes),
        "runtime_all_mean_ms": round(sum(all_runtimes) / len(all_runtimes), 3) if all_runtimes else None,
        "mae_bootstrap_95_ci": None,
    }
    if predicted == 0:
        return result

    result.update({
        "mae": round(sum(errors) / predicted, 6),
        "rmse": round(math.sqrt(sum(error * error for error in errors) / predicted), 6),
        "median_absolute_error": round(median(errors), 6),
        "mean_signed_bias": round(sum(signed_errors) / predicted, 6),
        "within_1_pct": round(sum(error <= 1.0 for error in errors) / predicted * 100.0, 2),
        "within_2_pct": round(sum(error <= 2.0 for error in errors) / predicted * 100.0, 2),
        "within_tolerance_pct": round(sum(error <= tol for error in errors) / predicted * 100.0, 2),
    })

    if bootstrap_samples:
        rng = random.Random(seed)
        bootstrap_mae: List[float] = []
        if groups is None:
            for _ in range(bootstrap_samples):
                draw = [errors[rng.randrange(predicted)] for _ in range(predicted)]
                bootstrap_mae.append(sum(draw) / predicted)
            bootstrap_unit = "prediction"
            bootstrap_group_count = None
        else:
            grouped_errors: Dict[Any, List[float]] = defaultdict(list)
            for group, error in zip(accepted_groups, errors):
                grouped_errors[group].append(error)
            group_names = list(grouped_errors)
            for _ in range(bootstrap_samples):
                draw: List[float] = []
                for _ in range(len(group_names)):
                    selected = group_names[rng.randrange(len(group_names))]
                    draw.extend(grouped_errors[selected])
                if draw:
                    bootstrap_mae.append(sum(draw) / len(draw))
            bootstrap_unit = "group"
            bootstrap_group_count = len(group_names)

        if bootstrap_mae:
            bootstrap_mae.sort()
            result["mae_bootstrap_95_ci"] = {
                "lower": round(_percentile(bootstrap_mae, 0.025), 6),
                "upper": round(_percentile(bootstrap_mae, 0.975), 6),
                "samples": len(bootstrap_mae),
                "seed": seed,
                "unit": bootstrap_unit,
                "group_count": bootstrap_group_count,
            }
    return result


def evaluate_prediction_records(
    records: Sequence[Mapping[str, Any]],
    tolerance: float = 2.0,
    bootstrap_samples: int = 1000,
    seed: int = 42,
    regions_per_specimen: int = 5,
) -> Dict[str, Any]:
    """Evaluate local and client-protocol specimen-mean predictions.

    Required local record keys: fabric_id, weave_type, warp_manual_density,
    weft_manual_density, warp_predicted_density, weft_predicted_density.
    Each specimen must contain exactly five regional records. A specimen-axis
    prediction is accepted only when all five model predictions exist.
    """
    if len(records) == 0:
        raise ValueError("records cannot be empty")
    if regions_per_specimen < 1:
        raise ValueError("regions_per_specimen must be positive")

    def one_axis(
        items: Sequence[Mapping[str, Any]],
        axis: str,
        include_groups: bool = True,
        samples: int = bootstrap_samples,
    ) -> Dict[str, Any]:
        return axis_metrics(
            [item[f"{axis}_manual_density"] for item in items],
            [item.get(f"{axis}_predicted_density") for item in items],
            [item.get("runtime_ms") for item in items],
            tolerance=tolerance,
            bootstrap_samples=samples,
            seed=seed,
            groups=[item["fabric_id"] for item in items] if include_groups else None,
        )

    by_weave: Dict[str, list] = defaultdict(list)
    by_specimen: Dict[str, list] = defaultdict(list)
    for item in records:
        fabric_id = item.get("fabric_id")
        if not isinstance(fabric_id, str) or not fabric_id.strip():
            raise ValueError("Every prediction record must contain a non-empty fabric_id")
        by_weave[str(item.get("weave_type") or "unknown")].append(item)
        by_specimen[fabric_id].append(item)

    for fabric_id, items in by_specimen.items():
        if len(items) != regions_per_specimen:
            raise ValueError(
                f"Specimen {fabric_id} must have exactly {regions_per_specimen} region records; got {len(items)}"
            )

    result: Dict[str, Any] = {
        "n_regions": len(records),
        "n_specimens": len(by_specimen),
        "warp": one_axis(records, "warp"),
        "weft": one_axis(records, "weft"),
        "per_weave": {},
        "per_specimen": {},
        "specimen_aggregate": {},
    }

    for key, items in sorted(by_weave.items()):
        result["per_weave"][key] = {
            "n_regions": len(items),
            "n_specimens": len({item["fabric_id"] for item in items}),
            "warp": one_axis(items, "warp"),
            "weft": one_axis(items, "weft"),
        }

    specimen_rows: List[Dict[str, Any]] = []
    for fabric_id, items in sorted(by_specimen.items()):
        specimen_rows.append({
            "fabric_id": fabric_id,
            "weave_type": str(items[0].get("weave_type") or "unknown"),
            "warp_manual_density": mean(float(item["warp_manual_density"]) for item in items),
            "weft_manual_density": mean(float(item["weft_manual_density"]) for item in items),
            "warp_predicted_density": (
                mean(float(item["warp_predicted_density"]) for item in items)
                if all(_finite_number(item.get("warp_predicted_density")) for item in items)
                else None
            ),
            "weft_predicted_density": (
                mean(float(item["weft_predicted_density"]) for item in items)
                if all(_finite_number(item.get("weft_predicted_density")) for item in items)
                else None
            ),
            "runtime_ms": (
                sum(float(item["runtime_ms"]) for item in items)
                if all(_finite_number(item.get("runtime_ms")) for item in items)
                else None
            ),
            "warp_regions_predicted": sum(_finite_number(item.get("warp_predicted_density")) for item in items),
            "weft_regions_predicted": sum(_finite_number(item.get("weft_predicted_density")) for item in items),
        })

    result["specimen_aggregate"] = {
        "protocol_regions_per_specimen": regions_per_specimen,
        "n_specimens": len(specimen_rows),
        "warp": axis_metrics(
            [item["warp_manual_density"] for item in specimen_rows],
            [item["warp_predicted_density"] for item in specimen_rows],
            [item["runtime_ms"] for item in specimen_rows],
            tolerance=tolerance,
            bootstrap_samples=bootstrap_samples,
            seed=seed,
            groups=[item["fabric_id"] for item in specimen_rows],
        ),
        "weft": axis_metrics(
            [item["weft_manual_density"] for item in specimen_rows],
            [item["weft_predicted_density"] for item in specimen_rows],
            [item["runtime_ms"] for item in specimen_rows],
            tolerance=tolerance,
            bootstrap_samples=bootstrap_samples,
            seed=seed,
            groups=[item["fabric_id"] for item in specimen_rows],
        ),
        "specimens": specimen_rows,
    }

    for fabric_id, items in sorted(by_specimen.items()):
        result["per_specimen"][fabric_id] = {
            "n_regions": len(items),
            "warp": one_axis(items, "warp", include_groups=False, samples=0),
            "weft": one_axis(items, "weft", include_groups=False, samples=0),
        }
    return result
