# The mechanistic justification for this step is: provide an automated benchmark orchestrator executing side-by-side comparative evaluations between classical deterministic, learned regression, and hybrid metrology models across held-out dataset splits, outputting structured empirical metrics and persisting results to results/output.json.

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from experiments.learned_models.dataset_adapters import get_dataset_adapter
from experiments.learned_models.metrics import evaluate_dual_axis_predictions
from experiments.learned_models.model_registry import ModelRegistry
from experiments.learned_models.splits import create_specimen_splits, load_splits_manifest
from experiments.learned_models.visualization import plot_bland_altman, plot_scatter_agreement


def run_benchmark(
    dataset_id: str = "fabricnet",
    model_ids: Optional[List[str]] = None,
    split_name: str = "test",
    output_path: Optional[str] = None,
    generate_plots: bool = True,
) -> Dict[str, Any]:
    models = model_ids or ["deterministic_dual_engine", "hybrid_unet_skeleton_pitch"]
    adapter = get_dataset_adapter(dataset_id)

    # Load or generate specimen splits
    splits_file = os.path.join(
        os.path.dirname(__file__), "results", f"{dataset_id}_splits.json"
    )
    if os.path.exists(splits_file):
        splits = load_splits_manifest(splits_file)
    else:
        splits = create_specimen_splits(adapter.samples, seed=42)

    target_sample_ids = splits.get(split_name, [s.sample_id for s in adapter.samples])
    target_samples = [s for s in adapter.samples if s.sample_id in target_sample_ids]

    # Model registry loader
    registry = ModelRegistry()

    benchmark_results: Dict[str, Any] = {
        "dataset_id": dataset_id,
        "split": split_name,
        "n_samples": len(target_samples),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": {},
    }

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    for m_id in models:
        try:
            model_instance = registry.instantiate_model(m_id)
        except Exception as exc:
            benchmark_results["models"][m_id] = {"error": f"Failed to instantiate: {str(exc)}"}
            continue

        true_warp = []
        pred_warp = []
        true_weft = []
        pred_weft = []
        latencies = []

        for sample in target_samples:
            if sample.warp_density is None or sample.weft_density is None:
                continue

            img = adapter.load_image_array(adapter.samples.index(sample), grayscale=False)
            sx = sample.scale_x_px_per_cm or 1280.0
            sy = sample.scale_y_px_per_cm or 1200.0

            t0 = time.time()
            if m_id == "deterministic_dual_engine":
                out = model_instance(
                    image=(img * 255.0).astype(np.uint8),
                    scale_x=sx,
                    scale_y=sy,
                    weave_type=sample.weave_pattern or "plain",
                )
                pw = out["warp_density"]
                pf = out["weft_density"]
            elif m_id == "hybrid_unet_skeleton_pitch":
                res = model_instance(image=img, scale_x=sx, scale_y=sy)
                pw = res["warp_density"]
                pf = res["weft_density"]
            else:
                pw, pf = 0.0, 0.0

            dt = (time.time() - t0) * 1000.0
            latencies.append(dt)

            true_warp.append(sample.warp_density)
            pred_warp.append(float(pw) if pw is not None else 0.0)
            true_weft.append(sample.weft_density)
            pred_weft.append(float(pf) if pf is not None else 0.0)

        metrics = evaluate_dual_axis_predictions(true_warp, pred_warp, true_weft, pred_weft)
        metrics["mean_latency_ms"] = round(float(np.mean(latencies)), 2) if latencies else 0.0

        if generate_plots and len(true_warp) >= 3:
            plot_bland_altman(
                true_warp,
                pred_warp,
                title=f"{m_id} - Warp Density Bland-Altman",
                save_path=os.path.join(plots_dir, f"{dataset_id}_{m_id}_warp_bland_altman.png"),
            )
            plot_scatter_agreement(
                true_warp,
                pred_warp,
                title=f"{m_id} - Warp Density Agreement",
                save_path=os.path.join(plots_dir, f"{dataset_id}_{m_id}_warp_scatter.png"),
            )

        benchmark_results["models"][m_id] = metrics

    out_file = output_path or os.path.join(results_dir, f"{dataset_id}_{split_name}_benchmark.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)

    return benchmark_results


def main():
    parser = argparse.ArgumentParser(description="Warp & Weft AI Benchmark CLI")
    parser.add_argument("--dataset", type=str, default="synthetic_micro_swatches", help="Dataset ID to evaluate")
    parser.add_argument("--models", type=str, default="deterministic_dual_engine,hybrid_unet_skeleton_pitch", help="Comma-separated model IDs")
    parser.add_argument("--split", type=str, default="test", help="Split name (train, validation, test)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    parser.add_argument("--no-plots", action="store_true", help="Disable plot generation")
    args = parser.parse_args()

    model_list = [m.strip() for m in args.models.split(",") if m.strip()]
    results = run_benchmark(
        dataset_id=args.dataset,
        model_ids=model_list,
        split_name=args.split,
        output_path=args.output,
        generate_plots=not args.no_plots,
    )

    print(f"Benchmark Run Complete for Dataset: {results['dataset_id']} (Split: {results['split']}, N={results['n_samples']})")
    for m_id, m_data in results["models"].items():
        if "error" in m_data:
            print(f"[{m_id}] ERROR: {m_data['error']}")
        else:
            warp = m_data.get("warp", {})
            weft = m_data.get("weft", {})
            print(
                f"[{m_id:<30}] Warp MAE: {warp.get('mae'):>5.2f} (<=2: {warp.get('pct_within_2'):>5.1f}%) | Weft MAE: {weft.get('mae'):>5.2f} (<=2: {weft.get('pct_within_2'):>5.1f}%) | Latency: {m_data.get('mean_latency_ms'):>5.1f}ms"
            )


if __name__ == "__main__":
    main()
