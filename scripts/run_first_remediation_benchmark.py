#!/usr/bin/env python3
"""Re-run the first remediation engine in the source revision that produced it.

This script is copied into a temporary git worktree at commit
7b9b55fdcd6e7e08d9b591b6b55d862a116f4c0e and run there. Therefore its imports
resolve to the historical src.fabric_analysis package, not the current engine.
It applies the same direct-axis metrics to all 130 sample outputs and verifies
them against that revision's committed benchmark JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List, Mapping, Sequence

from openpyxl import load_workbook
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.pipeline import analyze_fabric

EXPECTED_COMMIT = "7b9b55fdcd6e7e08d9b591b6b55d862a116f4c0e"
EXPECTED_SAMPLES = 130
PROMINENCE = 0.04
SCALE_X = 1280.0
SCALE_Y = 1200.0


def finite(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_metadata(path: Path) -> List[Dict[str, Any]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        iterator = workbook.active.iter_rows(values_only=True)
        try:
            header_row = next(iterator)
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
            raise ValueError(f"Missing workbook columns: {', '.join(missing)}")
        records = []
        for row_number, row in enumerate(iterator, start=2):
            if not row or all(value is None for value in row):
                continue
            sample_id = int(row[headers["Image id"]])
            warp = row[headers["Warp"]]
            weft = row[headers["Weft"]]
            texture = row[headers["Texture"]]
            gsm = row[headers["Specific Mass"]] if "Specific Mass" in headers else None
            if not finite(warp) or not finite(weft):
                raise ValueError(f"Invalid ground truth in workbook row {row_number}")
            if texture is None or not str(texture).strip():
                raise ValueError(f"Missing weave label for W{sample_id:03d}")
            records.append({
                "sample_num": sample_id,
                "image_id": f"W{sample_id:03d}.jpg",
                "gt_warp": float(warp),
                "gt_weft": float(weft),
                "texture": str(texture).strip().lower(),
                "gsm": float(gsm) if finite(gsm) else None,
            })
        return records
    finally:
        workbook.close()


def summarize(rows: Sequence[Mapping[str, Any]], pred_key: str, gt_key: str) -> Dict[str, Any]:
    errors = [float(row[pred_key]) - float(row[gt_key]) for row in rows]
    absolute = [abs(error) for error in errors]
    if not errors:
        raise ValueError("Cannot summarize an empty prediction set")
    return {
        "n": len(errors),
        "mae": round(mean(absolute), 6),
        "rmse": round(math.sqrt(mean(error * error for error in errors)), 6),
        "median_absolute_error": round(median(absolute), 6),
        "mean_signed_bias": round(mean(errors), 6),
        "within_1_pct": round(sum(error <= 1.0 for error in absolute) / len(errors) * 100.0, 2),
        "within_2_pct": round(sum(error <= 2.0 for error in absolute) / len(errors) * 100.0, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "fabricnet")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "first_remediation_rerun")
    parser.add_argument("--expected-samples", type=int, default=EXPECTED_SAMPLES)
    args = parser.parse_args()

    workbook_path = args.data_dir / "FabricNet_parameters.xlsx"
    if not workbook_path.is_file():
        raise FileNotFoundError(workbook_path)
    metadata = load_metadata(workbook_path)
    if len(metadata) != args.expected_samples:
        raise ValueError(f"Expected {args.expected_samples} samples; found {len(metadata)}")
    missing = [row["image_id"] for row in metadata if not (args.data_dir / row["image_id"]).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing FabricNET images: {missing[:10]}")

    calibration = PhysicalCalibration.from_scales(
        sx=SCALE_X,
        sy=SCALE_Y,
        source="fabricnet_optical_microscopy",
    )
    started = datetime.now(timezone.utc)
    records: List[Dict[str, Any]] = []
    statuses: Counter = Counter()

    for index, row in enumerate(metadata, start=1):
        with Image.open(args.data_dir / row["image_id"]) as image_file:
            image = image_file.convert("RGB")
            result = analyze_fabric(
                img_pil=image,
                calibration=calibration,
                auto_skew=True,
                weave_hint=row["texture"],
                prominence=PROMINENCE,
            )
        values = result["results"]
        audit = result["audit"]
        pred_warp = float(values["warp_ends_per_cm"])
        pred_weft = float(values["weft_picks_per_cm"])
        status = str(values["decision_status"])
        statuses[status] += 1

        direct_warp_error = abs(pred_warp - row["gt_warp"])
        direct_weft_error = abs(pred_weft - row["gt_weft"])
        swapped = (
            abs(pred_warp - row["gt_weft"]) + abs(pred_weft - row["gt_warp"])
            < direct_warp_error + direct_weft_error
        )
        paired_warp_error = abs(pred_warp - (row["gt_weft"] if swapped else row["gt_warp"]))
        paired_weft_error = abs(pred_weft - (row["gt_warp"] if swapped else row["gt_weft"]))

        records.append({
            **row,
            "pred_warp": pred_warp,
            "pred_weft": pred_weft,
            "decision_status": status,
            "sqi": values["signal_quality_index"],
            "skew_deg": values["detected_skew_deg"],
            "fft_warp": audit["fft_warp"],
            "fft_weft": audit["fft_weft"],
            "proj_warp": audit["proj_warp"],
            "proj_weft": audit["proj_weft"],
            "err_warp_direct": direct_warp_error,
            "err_weft_direct": direct_weft_error,
            "swapped_orientation": swapped,
            "paired_warp_error": paired_warp_error,
            "paired_weft_error": paired_weft_error,
            "latency_ms": result["latency_ms"],
        })
        if index % 10 == 0 or index == len(metadata):
            print(f"First-remediation revision processed {index}/{len(metadata)} images", flush=True)

    warp_summary = summarize(records, "pred_warp", "gt_warp")
    weft_summary = summarize(records, "pred_weft", "gt_weft")
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[row["texture"]].append(row)

    per_weave = {}
    for weave, weave_rows in sorted(grouped.items()):
        per_weave[weave] = {
            "n": len(weave_rows),
            "warp": summarize(weave_rows, "pred_warp", "gt_warp"),
            "weft": summarize(weave_rows, "pred_weft", "gt_weft"),
        }

    reference_path = ROOT / "results" / "fabricnet_benchmark.json"
    if not reference_path.is_file():
        raise FileNotFoundError(f"Historical committed benchmark missing: {reference_path}")
    with reference_path.open("r", encoding="utf-8") as handle:
        reference = json.load(handle)
    reference_rows = {item["image_id"]: item for item in reference.get("samples", [])}
    if len(reference_rows) != EXPECTED_SAMPLES:
        raise ValueError(f"Historical reference has {len(reference_rows)} samples, expected 130")

    mismatches = {"pred_warp": 0, "pred_weft": 0, "decision_status": 0}
    max_delta = {"pred_warp": 0.0, "pred_weft": 0.0}
    for row in records:
        old = reference_rows.get(row["image_id"])
        if old is None:
            raise ValueError(f"Historical reference missing {row['image_id']}")
        for field in ("pred_warp", "pred_weft"):
            delta = abs(float(row[field]) - float(old[field]))
            max_delta[field] = max(max_delta[field], delta)
            if delta > 1e-8:
                mismatches[field] += 1
        if row["decision_status"] != old["decision_status"]:
            mismatches["decision_status"] += 1

    paired_warp = [row["paired_warp_error"] for row in records]
    paired_weft = [row["paired_weft_error"] for row in records]
    output = {
        "schema_version": "1.0.0",
        "source_revision": EXPECTED_COMMIT,
        "rerun_started_at_utc": started.isoformat(),
        "rerun_completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "acseckn/fabricnet",
        "total_samples": len(records),
        "configuration": {
            "image_resolution_px": [640, 480],
            "field_of_view_mm": [5.0, 4.0],
            "pixels_per_cm_x": SCALE_X,
            "pixels_per_cm_y": SCALE_Y,
            "calibration_verified_with_stage_micrometer": False,
            "auto_skew": True,
            "prominence": PROMINENCE,
            "weave_hint_source": "FabricNET Texture label",
        },
        "metric_semantics": {
            "prediction": "First-remediation fusion output from warp_ends_per_cm and weft_picks_per_cm for every sample, including NEEDS_REVIEW status.",
            "evaluation": "Direct-axis MAE/RMSE/median/bias/within ±1/±2 across all 130 samples.",
            "orientation_invariant": "Ground-truth-assisted axis swap; offline diagnostic only.",
            "accepted_coverage": "Not separately represented by first-remediation engine output contract; do not infer acceptance from status.",
        },
        "aggregate_metrics": {
            "direct_axis": {"warp": warp_summary, "weft": weft_summary},
            "orientation_invariant_paired": {
                "warp_mae": round(mean(paired_warp), 6),
                "weft_mae": round(mean(paired_weft), 6),
            },
            "per_weave": per_weave,
            "decision_status_breakdown": dict(statuses),
        },
        "comparison_to_committed_first_remediation_benchmark": {
            "reference_samples": len(reference_rows),
            "rerun_samples": len(records),
            "changed_sample_field_counts": mismatches,
            "max_absolute_numeric_delta": max_delta,
        },
        "samples": records,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "first_remediation_fabricnet_rerun.json"
    csv_path = args.output_dir / "first_remediation_fabricnet_rerun.csv"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, allow_nan=False)
        handle.write("\n")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print("=== FIRST REMEDIATION 130-IMAGE RE-RUN ===")
    print(json.dumps({
        "source_revision": EXPECTED_COMMIT,
        "total_samples": len(records),
        "warp_mae": warp_summary["mae"],
        "weft_mae": weft_summary["mae"],
        "within_2_pct": {
            "warp": warp_summary["within_2_pct"],
            "weft": weft_summary["within_2_pct"],
        },
        "status_breakdown": dict(statuses),
        "reference_comparison": output["comparison_to_committed_first_remediation_benchmark"],
        "json_artifact": str(json_path),
        "csv_artifact": str(csv_path),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
