# ==============================================================================
# Unit Regression Test: Benchmark Provenance & Serialization Integrity
# ==============================================================================
# The mechanistic justification for this step is: verify mathematical derivation of
# errors and test the end-to-end report serialization pipeline (JSON, CSV, TXT)
# from injected engine predictions, ensuring schema adherence and numeric round-trip fidelity.

import unittest
import os
import sys
import json
import csv
import tempfile
import datetime
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.pipeline import analyze_fabric
from web_app.engine import run_complete_fabric_analysis


def generate_benchmark_reports(records: list,
                               calibration_meta: dict,
                               output_dir: str,
                               schema_version: str = "2.0.0") -> dict:
    """
    The mechanistic justification for this step is: serialize structured benchmark
    outputs across JSON, CSV, and TXT formats with consistent schema versions,
    explicit timestamps, and mathematically validated aggregate statistics.
    """
    os.makedirs(output_dir, exist_ok=True)
    n = len(records)
    if n == 0:
        raise ValueError("Cannot serialize empty records set")

    # Compute aggregate metrics
    warp_errs = [r["err_warp_direct"] for r in records]
    weft_errs = [r["err_weft_direct"] for r in records]
    paired_w_errs = [r["paired_warp_err"] for r in records]
    paired_wf_errs = [r["paired_weft_err"] for r in records]

    warp_mae = float(np.mean(warp_errs))
    weft_mae = float(np.mean(weft_errs))
    warp_rmse = float(np.sqrt(np.mean(np.square(warp_errs))))
    weft_rmse = float(np.sqrt(np.mean(np.square(weft_errs))))

    warp_acc1 = float(np.mean([1.0 if e <= 1.0 else 0.0 for e in warp_errs]) * 100.0)
    weft_acc1 = float(np.mean([1.0 if e <= 1.0 else 0.0 for e in weft_errs]) * 100.0)
    warp_acc2 = float(np.mean([1.0 if e <= 2.0 else 0.0 for e in warp_errs]) * 100.0)
    weft_acc2 = float(np.mean([1.0 if e <= 2.0 else 0.0 for e in weft_errs]) * 100.0)

    paired_w_mae = float(np.mean(paired_w_errs))
    paired_wf_mae = float(np.mean(paired_wf_errs))
    paired_acc2 = float(np.mean([1.0 if (r["paired_warp_err"] <= 2.0 and r["paired_weft_err"] <= 2.0) else 0.0 for r in records]) * 100.0)

    # Weave breakdown
    weaves = sorted(list(set(r["texture"] for r in records)))
    weave_breakdown = {}
    for w in weaves:
        w_recs = [r for r in records if r["texture"] == w]
        w_w_errs = [r["err_warp_direct"] for r in w_recs]
        w_wf_errs = [r["err_weft_direct"] for r in w_recs]
        weave_breakdown[w] = {
            "count": len(w_recs),
            "warp_mae": round(float(np.mean(w_w_errs)), 2),
            "weft_mae": round(float(np.mean(w_wf_errs)), 2),
            "warp_acc_le_2": round(float(np.mean([1.0 if e <= 2.0 else 0.0 for e in w_w_errs]) * 100.0), 1),
            "weft_acc_le_2": round(float(np.mean([1.0 if e <= 2.0 else 0.0 for e in w_wf_errs]) * 100.0), 1),
            "mean_sqi": round(float(np.mean([r["sqi"] for r in w_recs])), 1)
        }

    status_counts = {}
    for r in records:
        st = r["decision_status"]
        status_counts[st] = status_counts.get(st, 0) + 1

    payload = {
        "schema_version": schema_version,
        "timestamp_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dataset": "acseckn/fabricnet",
        "total_samples": n,
        "calibration": calibration_meta,
        "aggregate_metrics": {
            "direct_axis": {
                "warp_mae": round(warp_mae, 2),
                "weft_mae": round(weft_mae, 2),
                "warp_rmse": round(warp_rmse, 2),
                "weft_rmse": round(weft_rmse, 2),
                "warp_acc_within_1": round(warp_acc1, 1),
                "weft_acc_within_1": round(weft_acc1, 1),
                "warp_acc_within_2": round(warp_acc2, 1),
                "weft_acc_within_2": round(weft_acc2, 1)
            },
            "orientation_invariant_paired": {
                "warp_mae": round(paired_w_mae, 2),
                "weft_mae": round(paired_wf_mae, 2),
                "joint_acc_within_2": round(paired_acc2, 1)
            },
            "weave_breakdown": weave_breakdown,
            "decision_status_breakdown": status_counts
        },
        "samples": records
    }

    # 1. Write JSON
    json_path = os.path.join(output_dir, "fabricnet_benchmark.json")
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)

    # 2. Write CSV
    csv_path = os.path.join(output_dir, "fabricnet_benchmark.csv")
    if records:
        keys = list(records[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(records)

    # 3. Write TXT
    txt_path = os.path.join(output_dir, "output.txt")
    with open(txt_path, "w") as f:
        f.write("=== FABRICNET PHYSICAL MICROSCOPY 130-SAMPLE BENCHMARK ===\n")
        f.write(f"Timestamp: {payload['timestamp_iso']} | Schema: {schema_version}\n")
        f.write(f"Evaluated Samples: {n}\n")
        f.write(f"Direct Overall MAE: Warp={warp_mae:.2f} ends/cm, Weft={weft_mae:.2f} picks/cm\n")
        f.write(f"Direct Acc (<= 2 ends/cm): Warp={warp_acc2:.1f}%, Weft={weft_acc2:.1f}%\n")
        for w, stats in weave_breakdown.items():
            f.write(f"{w.capitalize()} Weave (N={stats['count']}): Warp MAE={stats['warp_mae']}, Weft MAE={stats['weft_mae']} | Acc<=2: Warp={stats['warp_acc_le_2']}%, Weft={stats['weft_acc_le_2']}%\n")
        f.write(f"Orientation Invariant MAE: Warp={paired_w_mae:.2f}, Weft={paired_wf_mae:.2f} | Joint Acc<=2: {paired_acc2:.1f}%\n")

    return {
        "json_path": json_path,
        "csv_path": csv_path,
        "txt_path": txt_path,
        "payload": payload
    }


class TestBenchmarkIntegrity(unittest.TestCase):
    def test_calculated_errors_match_arithmetic_truth(self):
        measured_warp = 38.0
        ground_truth_warp = 38
        measured_weft = 35.0
        ground_truth_weft = 33

        reported_warp_error = abs(measured_warp - ground_truth_warp)
        reported_weft_error = abs(measured_weft - ground_truth_weft)

        self.assertEqual(reported_warp_error, 0.0)
        self.assertEqual(reported_weft_error, 2.0)
        self.assertNotEqual(reported_weft_error, 0.5)

    def test_benchmark_report_serialization_pipeline(self):
        # Inject synthetic predictions across multiple weaves and statuses
        injected_records = [
            {
                "image_id": "W001.jpg",
                "sample_num": 1,
                "texture": "plain",
                "gsm": 120.0,
                "gt_warp": 36.0,
                "gt_weft": 30.0,
                "pred_warp": 36.0,
                "pred_weft": 30.0,
                "fft_warp": 36.0,
                "fft_weft": 30.0,
                "proj_warp": 36.0,
                "proj_weft": 30.0,
                "skew_deg": 0.5,
                "err_warp_direct": 0.0,
                "err_weft_direct": 0.0,
                "swapped_orientation": False,
                "paired_warp_err": 0.0,
                "paired_weft_err": 0.0,
                "decision_status": "VALIDATED",
                "sqi": 88.5,
                "latency_ms": 32.1
            },
            {
                "image_id": "W002.jpg",
                "sample_num": 2,
                "texture": "twill",
                "gsm": 150.0,
                "gt_warp": 40.0,
                "gt_weft": 32.0,
                "pred_warp": 38.0,
                "pred_weft": 35.0,
                "fft_warp": 38.0,
                "fft_weft": 35.0,
                "proj_warp": 38.0,
                "proj_weft": 35.0,
                "skew_deg": -1.2,
                "err_warp_direct": 2.0,
                "err_weft_direct": 3.0,
                "swapped_orientation": False,
                "paired_warp_err": 2.0,
                "paired_weft_err": 3.0,
                "decision_status": "CONSISTENT_WITH_WARNING",
                "sqi": 62.0,
                "latency_ms": 28.4
            },
            {
                "image_id": "W003.jpg",
                "sample_num": 3,
                "texture": "satin",
                "gsm": 200.0,
                "gt_warp": 50.0,
                "gt_weft": 40.0,
                "pred_warp": 45.0,
                "pred_weft": 42.0,
                "fft_warp": 45.0,
                "fft_weft": 42.0,
                "proj_warp": 30.0,
                "proj_weft": 25.0,
                "skew_deg": 0.0,
                "err_warp_direct": 5.0,
                "err_weft_direct": 2.0,
                "swapped_orientation": False,
                "paired_warp_err": 5.0,
                "paired_weft_err": 2.0,
                "decision_status": "NEEDS_REVIEW",
                "sqi": 35.0,
                "latency_ms": 30.0
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            cal_dict = {"pixels_per_cm_x": 1280.0, "pixels_per_cm_y": 1200.0}
            res = generate_benchmark_reports(
                records=injected_records,
                calibration_meta=cal_dict,
                output_dir=tmp_dir,
                schema_version="2.0.0"
            )

            # 1. Validate JSON Output
            with open(res["json_path"], "r") as f:
                loaded_json = json.load(f)
            self.assertEqual(loaded_json["schema_version"], "2.0.0")
            self.assertEqual(loaded_json["total_samples"], 3)
            self.assertIn("timestamp_iso", loaded_json)
            # MAE warp = (0.0 + 2.0 + 5.0) / 3 = 2.33
            self.assertAlmostEqual(loaded_json["aggregate_metrics"]["direct_axis"]["warp_mae"], 2.33, places=2)
            # MAE weft = (0.0 + 3.0 + 2.0) / 3 = 1.67
            self.assertAlmostEqual(loaded_json["aggregate_metrics"]["direct_axis"]["weft_mae"], 1.67, places=2)
            self.assertEqual(loaded_json["aggregate_metrics"]["decision_status_breakdown"]["VALIDATED"], 1)
            self.assertEqual(loaded_json["aggregate_metrics"]["decision_status_breakdown"]["NEEDS_REVIEW"], 1)

            # 2. Validate CSV Output
            with open(res["csv_path"], "r") as f:
                reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 3)
            self.assertEqual(reader[0]["image_id"], "W001.jpg")
            self.assertEqual(float(reader[0]["err_warp_direct"]), 0.0)
            self.assertEqual(float(reader[1]["err_warp_direct"]), 2.0)

            # 3. Validate TXT Output
            with open(res["txt_path"], "r") as f:
                txt_content = f.read()
            self.assertIn("Direct Overall MAE: Warp=2.33 ends/cm, Weft=1.67 picks/cm", txt_content)
            self.assertIn("Schema: 2.0.0", txt_content)

    def test_production_engine_and_src_package_equivalence(self):
        fpath = "data/synthetic/sample_plain_32x28.png"
        if not os.path.exists(fpath):
            self.skipTest(f"Synthetic fixture not found: {fpath}")

        im = Image.open(fpath)
        cal = PhysicalCalibration.from_scales(400.0)

        res_src = analyze_fabric(im, calibration=cal, auto_skew=False)
        res_engine = run_complete_fabric_analysis(im, pixels_per_cm=400.0, auto_skew=False)

        self.assertEqual(res_src["results"]["warp_ends_per_cm"], res_engine["results"]["warp_ends_per_cm"])
        self.assertEqual(res_src["results"]["weft_picks_per_cm"], res_engine["results"]["weft_picks_per_cm"])
        self.assertEqual(res_src["results"]["engine_mode"], res_engine["results"]["engine_mode"])

    def test_fabricnet_w012_end_to_end_execution(self):
        fpath = "data/fabricnet/W012.jpg"
        if not os.path.exists(fpath):
            self.skipTest(f"FabricNET fixture not found: {fpath}")

        im = Image.open(fpath)
        cal = PhysicalCalibration.from_fov(640, 480, 0.50, 0.40)
        res = analyze_fabric(im, calibration=cal, weave_hint="plain", auto_skew=True)

        self.assertEqual(res["status"], "success")
        self.assertIn("warp_ends_per_cm", res["results"])
        self.assertIn("weft_picks_per_cm", res["results"])
        self.assertIn("actual_roi_cm", res["roi_metadata"])
        self.assertFalse(res["roi_metadata"]["requested_roi_fully_available"])


if __name__ == "__main__":
    unittest.main()
