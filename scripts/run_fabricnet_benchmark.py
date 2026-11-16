#!/usr/bin/env python3
"""Re-run the authoritative deterministic engine across all 130 FabricNET images.

This runner preserves the committed benchmark and emits a separately versioned
rerun artifact. Candidate estimates and accepted measurements are evaluated
separately. Orientation-invariant pairing is explicitly ground-truth-assisted
and is retained only as an offline diagnostic.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from openpyxl import load_workbook
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.pipeline import analyze_fabric
from src.fabric_analysis.validation_metrics import axis_metrics


EXPECTED_SAMPLES = 130
FOV_WIDTH_MM = 5.0
FOV_HEIGHT_MM = 4.0
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
PROMINENCE = 0.04


def finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def as_float(value: Any, field: str, sample_id: int) -> float:
    if not finite_number(value):
        raise ValueError(f"Sample W{sample_id:03d} has invalid {field}: {value!r}")
    return float(value)


def load_metadata(workbook_path: Path) -> List[Dict[str, Any]]:
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        try:
            header_row = next(rows)
        except StopIteration as exc:
            raise ValueError("FabricNET workbook is empty") from exc
        headers = {
            str(value).strip(): index
            for index, value in enumerate(header_row)
            if value is not None and str(value).strip()
        }
        required = {"Image id", "Warp", "Weft", "Texture"}
        missing = sorted(required - set(headers))
        if missing:
            raise ValueError(f"FabricNET workbook is missing columns: {', '.join(missing)}")

        records: List[Dict[str, Any]] = []
        for row_number, row in enumerate(rows, start=2):
            if not row or all(value is None for value in row):
                continue
            raw_id = row[headers["Image id"]]
            if raw_id is None:
                continue
            try:
                sample_id = int(raw_id)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid Image id at workbook row {row_number}: {raw_id!r}") from exc

            texture = row[headers["Texture"]]
            if texture is None or not str(texture).strip():
                raise ValueError(f"Sample W{sample_id:03d} has no Texture label")
            gsm = row[headers["Specific Mass"]] if "Specific Mass" in headers else None
            records.append({
                "sample_num": sample_id,
                "image_id": f"W{sample_id:03d}.jpg",
                "gt_warp": as_float(row[headers["Warp"]], "Warp", sample_id),
                "gt_weft": as_float(row[headers["Weft"]], "Weft", sample_id),
                "texture": str(texture).strip().lower(),
                "gsm": float(gsm) if finite_number(gsm) else None,
            })
        return records
    finally:
        workbook.close()


def metric_summary(
    records: Sequence[Mapping[str, Any]],
    prediction_key: str,
    target_key: str,
    runtime_key: str = "latency_ms",
) -> Dict[str, Any]:
    groups = [record["image_id"] for record in records]
    return axis_metrics(
        [record[target_key] for record in records],
        [record.get(prediction_key) for record in records],
        [record.get(runtime_key) for record in records],
        tolerance=2.0,
        bootstrap_samples=1000,
        seed=42,
        groups=groups,
    )


def compare_to_committed(
    rerun_records: Sequence[Mapping[str, Any]],
    committed_path: Path,
) -> Dict[str, Any]:
    if not committed_path.exists():
        return {"available": False, "reason": "No committed benchmark JSON exists."}
    try:
        with committed_path.open("r", encoding="utf-8") as handle:
            committed = json.load(handle, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (OSError, ValueError) as exc:
        return {"available": False, "reason": f"Committed benchmark is not strict JSON: {exc}"}

    old_by_id = {row.get("image_id"): row for row in committed.get("samples", [])}
    common = [row for row in rerun_records if row["image_id"] in old_by_id]
    fields = ("pred_warp", "pred_weft", "accepted_warp", "accepted_weft", "decision_status")
    differences: Dict[str, int] = {field: 0 for field in fields}
    max_abs_delta: Dict[str, Optional[float]] = {
        field: 0.0 for field in fields if field != "decision_status"
    }
    for new in common:
        old = old_by_id[new["image_id"]]
        for field in fields:
            left, right = new.get(field), old.get(field)
            if field == "decision_status":
                if left != right:
                    differences[field] += 1
            elif finite_number(left) and finite_number(right):
                delta = abs(float(left) - float(right))
                if delta > 1e-8:
                    differences[field] += 1
                current = max_abs_delta[field]
                max_abs_delta[field] = max(float(current or 0.0), delta)
            elif left != right:
                differences[field] += 1
    return {
        "available": True,
        "committed_samples": len(old_by_id),
        "rerun_samples": len(rerun_records),
        "common_samples": len(common),
        "changed_sample_field_counts": differences,
        "max_absolute_numeric_delta": max_abs_delta,
        "not_compared_fields": ["accepted_warp_continuous", "accepted_weft_continuous"],
        "interpretation": (
            "Exact deterministic reproduction compares all fields preserved by the historical benchmark. "
            "Continuous accepted consensus values are newly emitted by this runner and were not stored in the historical artifact."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "fabricnet")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "fabricnet_benchmark_rerun")
    parser.add_argument("--expected-samples", type=int, default=EXPECTED_SAMPLES)
    args = parser.parse_args()

    images_dir = args.data_dir
    workbook_path = images_dir / "FabricNet_parameters.xlsx"
    if not workbook_path.is_file():
        raise FileNotFoundError(f"FabricNET metadata workbook not found: {workbook_path}")

    metadata = load_metadata(workbook_path)
    if len(metadata) != args.expected_samples:
        raise ValueError(
            f"Expected {args.expected_samples} metadata rows; found {len(metadata)}. "
            "Do not silently benchmark a partial dataset."
        )

    missing_images = [row["image_id"] for row in metadata if not (images_dir / row["image_id"]).is_file()]
    if missing_images:
        raise FileNotFoundError(f"Missing {len(missing_images)} FabricNET images: {', '.join(missing_images[:10])}")

    sx = IMAGE_WIDTH / (FOV_WIDTH_MM / 10.0)
    sy = IMAGE_HEIGHT / (FOV_HEIGHT_MM / 10.0)
    calibration = PhysicalCalibration.from_scales(
        sx=sx,
        sy=sy,
        source="fabricnet_5x4mm_fov_nominal_unverified",
    )

    started = datetime.now(timezone.utc)
    records: List[Dict[str, Any]] = []
    status_counts: Counter = Counter()
    for index, metadata_row in enumerate(metadata, start=1):
        image_path = images_dir / metadata_row["image_id"]
        with Image.open(image_path) as image_file:
            image = image_file.convert("RGB")
            result = analyze_fabric(
                img_pil=image,
                calibration=calibration,
                auto_skew=True,
                weave_hint=metadata_row["texture"],
                prominence=PROMINENCE,
            )

        values = result["results"]
        candidates = values.get("candidate_measurements") or {}
        accepted_warp = values.get("accepted_warp_density_ends_per_cm")
        accepted_weft = values.get("accepted_weft_density_picks_per_cm")
        fft_warp = candidates.get("warp_fft")
        fft_weft = candidates.get("weft_fft")
        candidate_warp = accepted_warp if accepted_warp is not None else fft_warp
        candidate_weft = accepted_weft if accepted_weft is not None else fft_weft

        direct_total = (
            abs(float(candidate_warp) - metadata_row["gt_warp"]) +
            abs(float(candidate_weft) - metadata_row["gt_weft"])
            if finite_number(candidate_warp) and finite_number(candidate_weft) else None
        )
        swapped_total = (
            abs(float(candidate_warp) - metadata_row["gt_weft"]) +
            abs(float(candidate_weft) - metadata_row["gt_warp"])
            if finite_number(candidate_warp) and finite_number(candidate_weft) else None
        )
        swapped = bool(swapped_total is not None and direct_total is not None and swapped_total < direct_total)

        def err(prediction: Any, target: float) -> Optional[float]:
            return abs(float(prediction) - target) if finite_number(prediction) else None

        status = str(values.get("decision_status", "UNKNOWN"))
        status_counts[status] += 1
        records.append({
            **metadata_row,
            "pred_warp": float(candidate_warp) if finite_number(candidate_warp) else None,
            "pred_weft": float(candidate_weft) if finite_number(candidate_weft) else None,
            "accepted_warp": int(accepted_warp) if finite_number(accepted_warp) else None,
            "accepted_weft": int(accepted_weft) if finite_number(accepted_weft) else None,
            "accepted_warp_continuous": (
                float(values["warp_density_continuous"])
                if finite_number(accepted_warp) and finite_number(values.get("warp_density_continuous")) else None
            ),
            "accepted_weft_continuous": (
                float(values["weft_density_continuous"])
                if finite_number(accepted_weft) and finite_number(values.get("weft_density_continuous")) else None
            ),
            "pred_warp_source": "accepted_fusion" if accepted_warp is not None else "fft_candidate_unvalidated",
            "pred_weft_source": "accepted_fusion" if accepted_weft is not None else "fft_candidate_unvalidated",
            "fft_warp": values.get("candidate_measurements", {}).get("warp_fft"),
            "fft_weft": values.get("candidate_measurements", {}).get("weft_fft"),
            "proj_warp": result.get("audit", {}).get("proj_warp"),
            "proj_weft": result.get("audit", {}).get("proj_weft"),
            "swapped_orientation": swapped,
            "paired_warp_error": err(candidate_warp, metadata_row["gt_weft"] if swapped else metadata_row["gt_warp"]),
            "paired_weft_error": err(candidate_weft, metadata_row["gt_warp"] if swapped else metadata_row["gt_weft"]),
            "err_warp_candidate": err(candidate_warp, metadata_row["gt_warp"]),
            "err_weft_candidate": err(candidate_weft, metadata_row["gt_weft"]),
            "err_warp_accepted": err(accepted_warp, metadata_row["gt_warp"]),
            "err_weft_accepted": err(accepted_weft, metadata_row["gt_weft"]),
            "decision_status": status,
            "is_validated": bool(values.get("is_validated", False)),
            "signal_quality_index": values.get("signal_quality_index"),
            "skew_deg": values.get("detected_skew_deg"),
            "latency_ms": result.get("latency_ms"),
        })
        if index % 10 == 0 or index == len(metadata):
            print(f"Processed {index}/{len(metadata)} FabricNET images", flush=True)

    candidate_warp = metric_summary(records, "pred_warp", "gt_warp")
    candidate_weft = metric_summary(records, "pred_weft", "gt_weft")
    accepted_warp = metric_summary(records, "accepted_warp", "gt_warp")
    accepted_weft = metric_summary(records, "accepted_weft", "gt_weft")

    weave_metrics: Dict[str, Any] = {}
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[row["texture"]].append(row)
    for weave, weave_records in sorted(grouped.items()):
        weave_metrics[weave] = {
            "n_samples": len(weave_records),
            "candidate_estimates": {
                "warp": metric_summary(weave_records, "pred_warp", "gt_warp"),
                "weft": metric_summary(weave_records, "pred_weft", "gt_weft"),
            },
            "accepted_measurements": {
                "warp": metric_summary(weave_records, "accepted_warp", "gt_warp"),
                "weft": metric_summary(weave_records, "accepted_weft", "gt_weft"),
            },
        }

    paired_warp_errors = [row["paired_warp_error"] for row in records if row["paired_warp_error"] is not None]
    paired_weft_errors = [row["paired_weft_error"] for row in records if row["paired_weft_error"] is not None]
    paired_summary = {
        "n_samples": len(paired_warp_errors),
        "warp_mae": round(mean(paired_warp_errors), 6) if paired_warp_errors else None,
        "weft_mae": round(mean(paired_weft_errors), 6) if paired_weft_errors else None,
        "policy": "Ground-truth-assisted axis swap; offline diagnostic only, never production inference.",
    }

    comparison = compare_to_committed(records, ROOT / "results" / "fabricnet_benchmark.json")
    output = {
        "schema_version": "2.2.0",
        "created_at_utc": started.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "acseckn/fabricnet",
        "total_samples": len(records),
        "benchmark_configuration": {
            "image_resolution_px": [IMAGE_WIDTH, IMAGE_HEIGHT],
            "field_of_view_mm": [FOV_WIDTH_MM, FOV_HEIGHT_MM],
            "pixels_per_cm_x": sx,
            "pixels_per_cm_y": sy,
            "calibration_verified_with_stage_micrometer": False,
            "calibration_uncertainty_pct": calibration.uncertainty_pct,
            "calibration_uncertainty_interpretation": "Configured relative scale envelope, not a statistical confidence interval or measured per-camera uncertainty.",
            "auto_skew": True,
            "prominence": PROMINENCE,
            "weave_hint_source": "FabricNET Texture label",
        },
        "metric_semantics": {
            "candidate_estimates": "Accepted fused density when available, otherwise the unvalidated FFT candidate.",
            "accepted_measurements": "Non-null accepted fusion outputs only. accepted_warp/accepted_weft are rounded integers; accepted_*_continuous preserve the pre-rounding one-decimal consensus. Rejected outputs count against coverage.",
            "orientation_invariant_paired": paired_summary["policy"],
            "bootstrap": "1000-seed-42 specimen-level clusters (one FabricNET image per sample).",
        },
        "aggregate_metrics": {
            "candidate_estimates": {"warp": candidate_warp, "weft": candidate_weft},
            "accepted_measurements": {"warp": accepted_warp, "weft": accepted_weft},
            "orientation_invariant_paired": paired_summary,
            "decision_status_breakdown": dict(status_counts),
            "per_weave": weave_metrics,
        },
        "comparison_to_committed_benchmark": comparison,
        "samples": records,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "fabricnet_benchmark_rerun.json"
    csv_path = args.output_dir / "fabricnet_benchmark_rerun.csv"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, allow_nan=False)
        handle.write("\n")

    csv_fields = list(records[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print("=== FABRICNET 130-IMAGE RE-RUN ===")
    print(json.dumps({
        "total_samples": len(records),
        "candidate_warp_mae": candidate_warp["mae"],
        "candidate_weft_mae": candidate_weft["mae"],
        "accepted_warp_coverage_pct": accepted_warp["coverage_pct"],
        "accepted_weft_coverage_pct": accepted_weft["coverage_pct"],
        "accepted_warp_mae": accepted_warp["mae"],
        "accepted_weft_mae": accepted_weft["mae"],
        "decision_status_breakdown": dict(status_counts),
        "comparison_to_committed_benchmark": comparison,
        "json_artifact": str(json_path),
        "csv_artifact": str(csv_path),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
