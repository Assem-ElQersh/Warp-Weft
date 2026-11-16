# First vs. Second Remediation — 130-Sample Reproduction

## Executive conclusion

Both deterministic-engine revisions were rerun from their own source revisions against the same 130 FabricNET images, the same FabricNet_parameters.xlsx labels, and the same nominal 5 × 4 mm FOV calibration (1280 × 1200 px/cm). Both reruns reproduced their own committed 130-sample benchmark exactly.

The second remediation did not improve all-image candidate-estimate MAE. It made its decision/acceptance policy substantially more conservative and achieved lower errors on the subset it accepted, at the cost of rejecting most image axes. This is a coverage–accuracy tradeoff, not an unqualified accuracy improvement.

## Execution provenance

| Item | First remediation | Second remediation |
|---|---|---|
| Source revision | 7b9b55fdcd6e7e08d9b591b6b55d862a116f4c0e | 8f55927d910197d6778b2d56217092973bf9cc56 |
| GitHub Actions run | [43909157336](https://github.com/Assem-ElQersh/Warp-Weft/actions/runs/43909157336) | [43909157336](https://github.com/Assem-ElQersh/Warp-Weft/actions/runs/43909157336) |
| Execution | Detached worktree at historical first-remediation revision | Current authoritative package |
| Samples processed | 130 / 130 | 130 / 130 |
| Artifact | ID 14245419730 | ID 14246274329 |
| Artifact SHA-256 | 102587abbcb91d5fa8dc24a86e3ef8670d061dc44d3baa2710176e660328340e | 48681d36ea1ebadf878b79131aeff245da9ec9037f15814c31d00ac98fe977872a |

The first revision was executed in a detached Git worktree at its source commit, so imports resolve to the historical package, not the later package. Both executions were in one CI workflow. That workflow passed 54 Python tests and inline JavaScript syntax validation.

## Reproduction against each revision's own saved benchmark

| Revision | Compared fields | Changed records | Maximum numeric delta |
|---|---|---:|---:|
| First remediation | pred_warp, pred_weft, decision_status | 0 / 130 for every field | 0 |
| Second remediation | candidate Warp/Weft, accepted Warp/Weft, decision_status | 0 / 130 for every field | 0 |

This confirms deterministic reproducibility under each revision's own source/configuration. It does not prove that either engine is physically accurate on the client's smartphone/factory acquisition domain.

## Like-for-like direct-axis candidate-estimate comparison

Both versions produce one numeric output per axis for each of the 130 images. For v2, the candidate is the accepted fused density where available and otherwise the FFT candidate. These are candidate estimates, not accepted-output coverage.

| Metric | First remediation | Second remediation candidate estimates | Change |
|---|---:|---:|---:|
| Warp MAE (ends/cm) | 11.7385 | 13.4318 | +1.6933 (+14.43%) |
| Weft MAE (picks/cm) | 10.3000 | 11.2490 | +0.9490 (+9.21%) |
| Warp RMSE | 16.2405 | 18.6760 | +2.4355 |
| Weft RMSE | 14.9443 | 15.9129 | +0.9687 |
| Warp median absolute error | 9.0 | 10.0 | +1.0 |
| Weft median absolute error | 6.0 | 7.0 | +1.0 |
| Warp mean signed bias | -8.5385 | -12.8250 | more negative |
| Weft mean signed bias | -9.1769 | -10.3068 | more negative |
| Warp within ±2 | 28.46% | 26.92% | -1.54 percentage points |
| Weft within ±2 | 33.08% | 27.69% | -5.39 percentage points |

The v2 candidate output is worse under these full-population direct-axis metrics. Its more negative signed bias also indicates stronger underestimation. The method semantics changed between revisions, so this is a reproducible comparison of each released engine revision's outputs under the same dataset and target-axis convention, not a controlled single-variable algorithm experiment.

## Second-remediation accepted-output tradeoff

| Accepted-output metric | Warp | Weft |
|---|---:|---:|
| Accepted outputs | 25 / 130 | 32 / 130 |
| Coverage | 19.23% | 24.62% |
| Rejection rate | 80.77% | 75.38% |
| Accepted-only MAE | 2.48 | 2.375 |
| Accepted-only RMSE | 3.8678 | 3.1125 |
| Accepted-only median absolute error | 2.0 | 2.0 |
| Accepted-only mean signed bias | -0.96 | -1.5625 |
| Accepted within ±2 | 80.00% | 62.50% |
| 95% group-bootstrap CI for MAE | [1.44, 3.601] | [1.71875, 3.0625] |

The accepted-only MAE describes a small subset, not all images. It cannot be compared directly with first-remediation all-image MAE as if denominators were identical.

## Decision-status changes

| Status | First remediation | Second remediation |
|---|---:|---:|
| VALIDATED | 0 | 15 |
| CONSISTENT_WITH_WARNING | 80 | 27 |
| NEEDS_REVIEW | 50 | 88 |

87 of 130 per-sample decision-status labels changed. This reflects the changed v2 acceptance and evidence arbitration policy. It does not mean 87 images became physically different or that v2 has 87 more accurate counts.

## Per-weave accepted-output results in v2

| Weave | Samples | Warp coverage / MAE | Weft coverage / MAE |
|---|---:|---|---|
| Plain | 50 | 40.00% / 2.65 | 36.00% / 2.50 |
| Twill | 39 | 0.00% / N/A | 20.51% / 3.125 |
| Satin | 41 | 12.20% / 1.80 | 14.63% / 1.00 |

Satin tolerance rates are based on only five accepted Warp and six accepted Weft outputs; they are not strong evidence of generalization. Twill Warp has no accepted measurements, so accepted-output accuracy for that axis is undefined.

## Interpretation and next scientific action

1. Keep v2's refusal to present a rejected estimate as validated. That is an integrity improvement even though all-image candidate MAE increased.
2. Do not describe v2 as more accurate overall. Its candidate MAE worsened on both axes.
3. Investigate why the new acceptance policy rejects 80.8% of Warp axes and 75.4% of Weft axes. Improve coverage only when accepted measurement remains supported by physical evidence.
4. Evaluate on the client's own acquisition domain using five matched 1 cm regions per specimen. FabricNET is not a substitute for those local smartphone/factory samples.
5. Train learned perception separately; compare all-sample candidate performance and accepted-output accuracy/coverage under the client's ±2 tolerance.

This comparison closes the first-vs-second saved-benchmark reproduction task. It does not close learned-model validation or client-domain field validation.
