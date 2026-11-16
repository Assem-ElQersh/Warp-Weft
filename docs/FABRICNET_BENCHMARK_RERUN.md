# FabricNET deterministic benchmark reproduction

## Reproduction provenance

- Repository: Assem-ElQersh/Warp-Weft
- Runner: scripts/run_fabricnet_benchmark.py
- Source commit: 663a1656d8f5e2e50157bb903436ac89e8c3fdeb
- GitHub Actions run: https://github.com/Assem-ElQersh/Warp-Weft/actions/runs/43904962934
- Uploaded artifact: fabricnet-benchmark-rerun (artifact ID 14246080718)
- Artifact SHA-256: b7f18527ea8fa5f08d868750f5a877369664028b1dee4ea8784ad369018aa10a
- Artifact expiry reported by GitHub: 2027-02-14
- Artifact files: fabricnet_benchmark_rerun.json and fabricnet_benchmark_rerun.csv
- Dataset: all 130 FabricNET images and the committed FabricNet_parameters.xlsx workbook.

The workflow completed all 130 images and uploaded both result files. It also ran the 51-test Python suite and the inline JavaScript syntax check successfully.

The later validation of the hardened latest branch head also passed 54 Python tests and reran all 130 images successfully: [GitHub Actions run 43907041685](https://github.com/Assem-ElQersh/Warp-Weft/actions/runs/43907041685). Its artifact (ID 14246042495) has SHA-256 e6579398ea1ebadf878b79131a74c7bfcf7a24f111411c94a776c6ebc83fbdfd. The newer artifact has the same sample predictions, accepted results, and status counts.

## Acquisition and calibration configuration

| Setting | Value |
|---|---:|
| Image resolution | 640 × 480 px |
| Field of view | 5 × 4 mm |
| Nominal X scale | 1280 px/cm |
| Nominal Y scale | 1200 px/cm |
| Stage-micrometer verification | Not performed |
| Skew rectification | Enabled |
| Weave hint | FabricNET Texture metadata |
| Spatial prominence | 0.04 |
| Bootstrap | 1000 replicates, seed 42 |

The FOV-derived calibration is nominal and remains physically unverified. It must not be transferred to smartphone images.

## Reproduction result

The rerun was compared row by row against the committed results/fabricnet_benchmark.json artifact.

| Comparison field | Changed samples | Maximum numeric delta |
|---|---:|---:|
| Candidate Warp | 0 / 130 | 0 |
| Candidate Weft | 0 / 130 | 0 |
| Accepted Warp | 0 / 130 | 0 |
| Accepted Weft | 0 / 130 | 0 |
| Decision status | 0 / 130 | Exact match |

This establishes deterministic reproduction of the currently committed benchmark under the runner configuration. It does not establish measurement accuracy against the client's five-region physical protocol, because FabricNET is a different microscopy dataset with a different ground-truth acquisition procedure.

## Overall candidate estimates

Candidate estimates use the accepted fusion result when available and otherwise retain the FFT candidate as an explicitly unvalidated candidate. They are not accepted production measurements.

| Metric | Warp | Weft |
|---|---:|---:|
| MAE | 13.4318 | 11.2490 |
| RMSE | 18.6760 | 15.9129 |
| Median absolute error | 10.00 | 7.00 |
| Mean signed bias | -12.8250 | -10.3068 |
| Within ±1 | 16.15% | 17.69% |
| Within ±2 | 26.92% | 27.69% |
| Candidate coverage | 100% | 100% |
| 95% group-bootstrap CI for MAE | [11.1882, 15.5893] | [9.3845, 13.1390] |

The negative bias indicates systematic underestimation. Candidate figures remain poor and are retained for diagnosis, not presented as factory-accepted output.

## Accepted measurements

Rejected axes remain null. Error statistics use accepted predictions only; coverage and rejection use all 130 FabricNET samples as the denominator.

| Metric | Warp | Weft |
|---|---:|---:|
| Accepted | 25 / 130 | 32 / 130 |
| Coverage | 19.23% | 24.62% |
| Rejected | 105 | 98 |
| Rejection rate | 80.77% | 75.38% |
| MAE | 2.48 | 2.375 |
| RMSE | 3.8678 | 3.1125 |
| Median absolute error | 2.00 | 2.00 |
| Mean signed bias | -0.96 | -1.5625 |
| Within ±1 | 48.00% | 40.62% |
| Within ±2 | 80.00% | 62.50% |
| 95% group-bootstrap CI for MAE | [1.44, 3.601] | [1.7188, 3.0625] |

These metrics are selective: they describe a small accepted subset, not all images. Low coverage is an important system outcome and must not be hidden by accepted-only MAE.

## Accepted measurements by weave

| Weave | Samples | Warp accepted | Warp coverage | Warp MAE | Warp within ±2 | Weft accepted | Weft coverage | Weft MAE | Weft within ±2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Plain | 50 | 20 | 40.00% | 2.65 | 75.00% | 18 | 36.00% | 2.50 | 61.11% |
| Twill | 39 | 0 | 0.00% | N/A | N/A | 8 | 20.51% | 3.125 | 50.00% |
| Satin | 41 | 5 | 12.20% | 1.80 | 100.00% | 6 | 14.63% | 1.00 | 83.33% |

The satin tolerance rates are based on only five accepted Warp outputs and six accepted Weft outputs. They are not robust evidence of general satin performance. Twill Warp has no accepted result, so no accepted-output accuracy claim can be made for that axis.

## Decision status

- VALIDATED: 15
- CONSISTENT_WITH_WARNING: 27
- NEEDS_REVIEW: 88

These are sample-level decisions. Per-axis accepted coverage differs because one axis can be accepted while the other is rejected.

## Orientation-invariant metric caveat

The benchmark paired/orientation-invariant diagnostic chooses whether to swap the image axes by comparing both possibilities against known ground-truth labels. It is ground-truth-assisted and strictly an offline diagnostic. It cannot be used by the production application to infer warp/weft orientation when labels are unknown.

## Interpretation

The rerun proves that the saved benchmark is reproducible from the committed source, dataset and configuration. It does not prove the existing deterministic engine meets the client's tolerance in field use. It also does not validate any learned model. The client protocol requires five manually counted 1 cm regions per physical specimen, ideally with each region photograph matched to its own manual counts. That data is not present in FabricNET and must be collected separately.
