# WARP & WEFT AI — FINAL SCIENTIFIC INTEGRITY REMEDIATION REPORT

## 1. Executive Summary & Provenance Verification

- **Repository:** `Assem-ElQersh/Warp-Weft`
- **Active Branch:** `research/scientific-integrity-remediation`
- **Remote Tracking:** `origin/research/scientific-integrity-remediation`
- **Main Branch Status:** `main` untouched (HEAD at `8f0e7ce`); zero force pushes; zero branch merges into main.
- **Pre-Remediation Verified External Backup:**
  - Path: `/home/assem-elqersh/Desktop/Warp-Weft-Pre-Remediation-Backup-20261119-224015/project-working-tree.tar.gz`
  - Size: 5,548,220,123 bytes (5.2 GB)
  - Integrity: `gzip -t` exit code 0 (zero CRC/decompression errors).
- **Automated Test Suite Status:**
  - Collected Tests: 96 tests across 23 test modules.
  - Passing Tests: 96 / 96 (100% pass rate in 4.81s).
  - Regressions: 0.

---

## 2. Immutable Git Commit Sequence

The remediation was structured into 5 logical, atomic, and fully justified commits on branch `research/scientific-integrity-remediation`:

1. **Commit `1e478a4`:**
   *Message:* `The mechanistic justification for this step is: integrate research infrastructure, dataset and model registries, modular metrology engine, and comprehensive scientific audit reports into the remediation branch.`
   *Content:* 74 files changed, 17,223 insertions. Adds modular research CLI tools, dataset and model registries, data manifests, and 26 comprehensive scientific audit reports.

2. **Commit `f58f443`:**
   *Message:* `The mechanistic justification for this step is: align documentation, Provenance Ledger, and user interface scientific terminology with physical metrology standards and single-specimen spatial uniformity protocol.`
   *Content:* 2 files changed, 35 insertions. Qualifies ASTM D3775 roll certification vs single-specimen digital spatial uniformity; sets weave hint options to metadata-only hints; records scientific remediation entry in the README Provenance Ledger.

3. **Commit `f7e3292`:**
   *Message:* `The mechanistic justification for this step is: enforce strict axis isolation in two-point ruler calibration, suppress physical density estimates for uncalibrated images, prevent averaging rejected candidate estimates into certified specimen means, and block false factory PASS decisions.`
   *Content:* 5 files changed, 167 insertions. Resolves calibration axis isolation, uncalibrated density suppression, and specimen consensus gating in `src/fabric_analysis/` and `web_app/`.

4. **Commit `6e2e0de`:**
   *Message:* `The mechanistic justification for this step is: expand the automated test suite with scientific remediation regressions and metrology checks, and preserve exact deterministic FabricNET benchmark reproduction artifacts.`
   *Content:* 9 files changed, 5,309 insertions. Adds 5 regression test suites (`test_scientific_remediation.py`, `test_calibration_uncertainty.py`, `test_data_engine.py`, `test_metrology_metrics.py`, `test_model_registry.py`) and commits exact deterministic benchmark reproduction files.

5. **Commit `6a180d0`:**
   *Message:* `The mechanistic justification for this step is: add end-to-end HTTP integration test verifying that uploaded uncalibrated images receive UNCALIBRATED decision status and suppress physical density outputs.`
   *Content:* 1 file changed, 22 insertions. Locks down end-to-end HTTP endpoint behavior for uncalibrated image payloads.

---

## 3. Systematic Resolution of Scientific & Metrological Defects

| Defect # | Component | Original Defective Behavior | Remediated Invariant & Mechanistic Fix | Verification Script / Test |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | `pipeline.py` & `server.py` | Images without calibration parameters silently defaulted to `400.0 px/cm`, producing false physical densities (ends/cm, picks/cm) on arbitrary images. | An uncalibrated image explicitly sets `is_uncalibrated=True`. Physical densities evaluate to `None`, `total_thread_density=None`, `candidate_measurements={}`, and `decision_status="UNCALIBRATED"`. | `tests/test_scientific_remediation.py::test_uncalibrated_image_does_not_produce_accepted_physical_density`<br>`tests/test_web_server_integration.py::test_uncalibrated_image_analysis_returns_uncalibrated_status` |
| **D2** | `specimen_workflow.py` | When regions failed consensus validation (`accepted_warp=None`), fallback logic substituted unvalidated raw candidate estimates (`cand_warp`) into certified specimen averaging, yielding false `specimen_pass=True` and `decision_status="PASS"` when 0/5 regions were validated. | Only regions with `is_val=True` and positive finite accepted densities are accumulated. Certified means strictly require all 5 regions to pass consensus (`all_regions_validated`). If any region fails, means evaluate to `None` with `decision_status="NEEDS_REVIEW"`. If 5 pass but calibration is unverified, `specimen_pass=False` with `decision_status="UNVERIFIED_CALIBRATION"`. | `tests/test_scientific_remediation.py::test_specimen_workflow_rejects_averaging_rejected_candidates_into_pass`<br>`tests/test_scientific_remediation.py::test_specimen_workflow_rejects_pass_when_calibration_unverified` |
| **D3** | `calibration_profile.py` | Horizontal ruler measurements ($dx$) and vertical measurements ($dy$) silently assigned the measured 1D scale to both orthogonal axes without user notice. | `calibrate_from_two_points` defaults `assume_square_pixels=False`. Horizontal ruler returns `(sx, None)` and vertical returns `(None, sy)`. `calibrate_anisotropic_from_two_rulers` computes true independent $S_x$ and $S_y$. | `tests/test_scientific_remediation.py::test_horizontal_ruler_only_calibrates_horizontal_scale`<br>`tests/test_scientific_remediation.py::test_vertical_ruler_only_calibrates_vertical_scale` |
| **D4** | `calibration_profile.py` | `smartphone_macro_stand_v1` profile falsely claimed `is_verified=True` and `calibration_source="factory_ruler_1cm_optical_graticule"`. | Profile updated to `is_verified=False` and `calibration_source="back_calculated_client_specimen_reference"` with explicit documentation of empirical yarn pitch back-calculation. | `tests/test_scientific_remediation.py::test_smartphone_macro_stand_profile_does_not_claim_unverified_graticule` |
| **D5** | `web_app/index.html` & `server.py` | Tab 6 was labeled "Client 5-Region Specimen Protocol (ASTM D3775)", conflating digital quadrant crops from a single smartphone capture with full ASTM roll certification. | Tab renamed to "5-Region Spatial Uniformity". Clear qualification added citing ASTM D3775-17(2023) multi-location roll sampling requirements vs single-specimen digital spatial uniformity. `/api/analyze/specimen` rejects uncalibrated requests with HTTP 400. | `tests/test_web_ui_contract.py`<br>`tests/test_web_server_integration.py::test_specimen_analysis_endpoint_rejects_missing_calibration` |
| **D6** | `web_app/index.html` | Weave dropdown claimed "Consensus Dominant" and "2D FFT Dominant", implying active algorithmic branching that does not exist in the code. | Dropdown options neutrally relabeled to metadata hints: `Plain Weave (Metadata hint)`, `Twill Weave (Metadata hint)`, `Satin Weave (Metadata hint)`. SQI clarified as heuristic index, not metrological probability. | `tests/test_web_ui_contract.py` |
| **D7** | `results/` | Narrative discrepancy regarding FabricNET 130-image benchmark performance metrics. | Rerun executed across all 130 FabricNET images confirming exact 0.0 delta from committed baseline: Raw candidate MAE: 13.43 warp / 11.25 weft; Consensus accepted subset MAE: 2.48 warp / 2.38 weft; Accepted coverage: 19.2% warp / 24.6% weft; 88 `NEEDS_REVIEW`, 27 `CONSISTENT_WITH_WARNING`, 15 `VALIDATED`. | `results/fabricnet_benchmark_rerun/fabricnet_benchmark_rerun.json`<br>`tests/test_benchmark_integrity.py` |

---

## 4. Protected Asset & Repository Safety Audit

- **Client Private Image (`data/samples/test.png`):**
  - Stored: `data/samples/test.png` (2,595,080 bytes).
  - Git Tracked: `False` (`git ls-files data/samples/test.png` returns empty).
  - Git Ignored: Verified via `.gitignore:132:data/samples/*`.
  - Modification Timestamp: Untouched (2026-11-16 12:24:58).
- **Raw Datasets (4.9 GB):**
  - Directories `data/aitex_database/`, `data/fabric_defects_benchmark/`, `data/multiclass_defects/`, `data/ten_fabrics/`, `data/textile_weaving_tabular/`, `data/textile_knitting_tabular/` are strictly ignored by `.gitignore` lines 121-126.
  - Zero raw image files outside of the 130 public FabricNET samples are tracked.
- **Deep Learning Model Checkpoints & Binaries:**
  - `experiments/models/checkpoints/segformer_b0/model.safetensors` (14.34 MB) is ignored by `.gitignore:99:*.safetensors`.
  - `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth` (84.20 MB) is ignored by `.gitignore:93:*.pth`.
  - Zero heavy binary checkpoints were staged or pushed.
- **Literature PDFs:**
  - `docs/Papers/*.pdf` is ignored by `.gitignore:103:docs/Papers/*.pdf`.
  - Zero PDF binary assets were staged or pushed.

---

## 5. End-to-End Test Suite Execution Matrix

```
============================= test session starts ==============================
platform linux -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: /home/assem-elqersh/Desktop/Warp Weft Project
plugins: anyio-4.10.0, cov-7.0.0, jaxtyping-0.3.10
collected 96 items

tests/test_benchmark_artifact_integrity.py ..                            [  2%]
tests/test_benchmark_integrity.py ....                                   [  6%]
tests/test_calibration.py ......                                         [ 12%]
tests/test_calibration_uncertainty.py ...                                [ 15%]
tests/test_client_image_failure_regression.py ..                         [ 17%]
tests/test_data_engine.py ......                                         [ 23%]
tests/test_fusion.py ....                                                [ 28%]
tests/test_ground_truth_protocol.py .......                              [ 35%]
tests/test_grouped_splits.py ...                                         [ 38%]
tests/test_metrology_metrics.py ....                                     [ 42%]
tests/test_model_registry.py ....                                        [ 46%]
tests/test_notebook_integrity.py ..                                      [ 48%]
tests/test_orientation.py ..                                             [ 51%]
tests/test_roi.py ...                                                    [ 54%]
tests/test_scientific_remediation.py .......                             [ 61%]
tests/test_smartphone_regression.py .                                    [ 62%]
tests/test_spatial.py ..                                                 [ 64%]
tests/test_specimen_workflow.py ....                                     [ 68%]
tests/test_spectral.py ..                                                [ 70%]
tests/test_validation_metrics.py .......                                 [ 78%]
tests/test_web_modes.py ....                                             [ 82%]
tests/test_web_server_integration.py ............                        [ 94%]
tests/test_web_ui_contract.py .....                                      [100%]

============================== 96 passed in 4.81s ==============================
```

---

## 6. Architectural Conclusion

The repository `Assem-ElQersh/Warp-Weft` on dedicated branch `research/scientific-integrity-remediation` has been systematically reconciled. Metrological claims are now strictly grounded:
1. Physical densities require validated, explicit physical scale calibration.
2. Certified factory tolerance compliance strictly requires verified calibration and multi-region consensus validation.
3. Ruler tools isolate orthogonal axes without unstated assumptions.
4. Scientific terminology accurately distinguishes roll-level standard sampling from single-specimen spatial uniformity.
5. All 96 regression tests pass cleanly, and the working tree is clean with all commits pushed to remote tracking.

---

## 7. Second-Pass Scientific Audit & Targeted Remediation Addendum

### 7.1. Operational Context & Starting State
- **Audit Branch:** `research/scientific-integrity-remediation`
- **Starting Commit SHA:** `c2238c6`
- **Objective:** Targeted remediation of residual scientific integrity gaps without weakening metrological criteria, rewriting working code, or touching the main branch.
- **Mandatory Skills Applied:**
  * **`andrej-karpathy-skills`:**
    - *Think Before Coding:* Surfaced tradeoffs between nominal benchmark evaluation and production calibration gating; decoupled nominal benchmark evaluation in `scripts/run_fabricnet_benchmark.py` (`is_verified=True`) from production calibration gating (`is_verified=False` by default).
    - *Simplicity First:* Implemented minimal surgical code changes without introducing speculative abstractions, redundant wrapper classes, or unnecessary configuration layers.
    - *Surgical Changes:* Inspected all callers of modified functions (`calibrate_from_two_points`, `PhysicalCalibration.from_fov`, `analyze_fabric`, and `evaluate_five_region_specimen`) across `src/`, `tests/`, `web_app/`, and `scripts/`.
    - *Goal-Driven Execution:* Authored failing regression tests reproducing all identified defects before altering production code, confirming that 4 tests failed on the unremediated codebase and 12 passed after surgical fixes.
  * **`ponytail`:**
    - *Before You Write:* Verified every caller of `calibrate_from_two_points` and `from_fov` across the entire codebase.
    - *Smallest Complete Change:* Added strict axis and square-pixel validation in `calibrate_from_two_points` (10 lines), default `is_verified=False` in `from_fov` (1 line), and unverified calibration gating in `pipeline.py` (33 lines).
    - *Verify Edge Cases:* Explicitly tested unsupported axis strings, diagonal distance with and without square pixel assumptions, diverged vs concordant unverified inputs, and missing calibration rejections.

---

### 7.2. Confirmed Defects, Root Causes & Surgical Resolutions

| Defect ID | Component & File | Root Cause Mechanism | Remediated Invariant & Surgical Fix | Regression Verification |
| :--- | :--- | :--- | :--- | :--- |
| **SP-01** | `src/fabric_analysis/pipeline.py:241-296` | `pipeline.py` checked only `is_uncalibrated` (when calibration object was omitted entirely), allowing unverified calibration objects (`is_verified=False`, such as `smartphone_macro_stand_v1` or default `PhysicalCalibration.from_scales()`) to produce accepted physical density outputs (`accepted_warp_density_ends_per_cm`) and misleading `VALIDATED` status when estimators were concordant. | Added explicit `elif not calibration.is_verified:` branch. When calibration is unverified: accepted physical densities are strictly set to `None`, `is_validated=False`, `decision_status="UNVERIFIED_CALIBRATION"` (if concordant) or `"NEEDS_REVIEW"` (if diverged). Candidate measurements (`warp_fft`, `warp_proj`, `unverified_warp_consensus`) are preserved exclusively as unverified diagnostics for engineering review. | `tests/test_scientific_remediation.py::test_unverified_calibration_object_cannot_produce_accepted_density`<br>`tests/test_scientific_remediation.py::test_smartphone_macro_stand_profile_cannot_produce_accepted_density` |
| **SP-02** | `src/fabric_analysis/calibration_profile.py:84-117` | `calibrate_from_two_points` silently computed Euclidean distance and returned isotropic `(scale, scale)` when `axis in ("both", "diagonal")` regardless of `assume_square_pixels`, and fell into Euclidean calculation for arbitrary invalid axis strings. | Added strict axis validation: `axis` must be in `("horizontal", "vertical", "both", "diagonal")`, raising `ValueError` otherwise. When `axis in ("both", "diagonal")`, `not assume_square_pixels` raises `ValueError("Diagonal/2D distance cannot calibrate independent X and Y scales without assume_square_pixels=True")`. | `tests/test_scientific_remediation.py::test_diagonal_ruler_rejects_without_square_pixel_assumption`<br>`tests/test_scientific_remediation.py::test_ruler_rejects_invalid_axis` |
| **SP-03** | `src/fabric_analysis/calibration.py:60-88` | `PhysicalCalibration.from_fov()` defaulted to `is_verified=True`, granting ungrounded analytical authority to hardware field-of-view specifications without in-scene calibration verification. | Changed parameter default to `is_verified: bool = False`. Hardware FOV calibrations remain unverified unless verified by an explicit calibration target or stage micrometer (`is_verified=True`). | `tests/test_scientific_remediation.py::test_from_fov_defaults_to_unverified` |
| **SP-04** | `tests/test_scientific_remediation.py:125-176` | `test_specimen_workflow_rejects_pass_when_calibration_unverified` used blank gray images that failed consensus validation, causing regions to be rejected on divergence (`validated_regions_count=0`) rather than isolating the effect of unverified calibration on validated regions. | Replaced with deterministic test patching `analyze_fabric` to return 5 mock validated regions (`is_validated=True`, `decision_status="VALIDATED"`, target densities matching factory spec). Verified that `result.validated_regions_count == 5`, `result.specimen_pass is False`, `result.decision_status == "UNVERIFIED_CALIBRATION"`, and `"UNVERIFIED calibration" in result.decision_summary`. | `tests/test_scientific_remediation.py::test_specimen_workflow_rejects_pass_when_calibration_unverified` |
| **SP-05** | `scripts/run_fabricnet_benchmark.py:195-203` | Rerun script previously passed `PhysicalCalibration.from_scales(sx, sy, source="fabricnet_5x4mm_fov_nominal_unverified")` without explicit `is_verified=True`, which would have triggered production calibration suppression during benchmark validation. | Updated to pass `is_verified=True` with explicit documentation that this evaluates multi-estimator algorithmic consensus under the nominal microscope scale, while preserving `"calibration_verified_with_stage_micrometer": False` in the benchmark configuration metadata. | `scripts/run_fabricnet_benchmark.py`<br>`results/fabricnet_benchmark_rerun/fabricnet_benchmark_rerun.json` |

---

### 7.3. Independent Code & Scientific Metrology Audit Findings
An independent subagent review (`research` subagent, Conversation ID `f4b028ab-d4d9-4838-93e0-299371d3c7c0`) was executed to inspect the complete uncommitted git diff and repository state.
- **Audit Findings:**
  1. *Unverified Calibration Suppression:* Confirmed in `src/fabric_analysis/pipeline.py:263-296`. Synthetic periodic fabric yields `accepted_warp=None`, `accepted_weft=None`, `is_validated=False`, `decision_status="UNVERIFIED_CALIBRATION"`. Divergent input yields `NEEDS_REVIEW`. Diagnostic candidate dictionary is preserved intact.
  2. *Diagonal Ruler Isolation:* Confirmed in `src/fabric_analysis/calibration_profile.py:89-117`. Diagonal without `assume_square_pixels` raises `ValueError`; invalid axis strings raise `ValueError`; diagonal with `assume_square_pixels=True` returns isotropic `(scale, scale)`.
  3. *Default Verification State:* Confirmed in `src/fabric_analysis/calibration.py:67`. `PhysicalCalibration.from_fov()` defaults to `is_verified=False`.
  4. *Deterministic 5-Region Specimen Test:* Confirmed in `tests/test_scientific_remediation.py:125-176`. Proves `specimen_pass=False` and status `UNVERIFIED_CALIBRATION` when 5/5 regions achieve validation.
  5. *Test Suite Execution:* Confirmed 101/101 tests pass cleanly in 4.20s on Python 3.13.9.
  6. *Asset Protection Boundary:* Confirmed zero private assets tracked. `data/samples/test.png`, `*.safetensors`, `*.pth`, `docs/Papers/*.pdf`, and all 6 external raw datasets are strictly ignored by `.gitignore`.

---

### 7.4. Complete Test Suite Execution Matrix (Second Pass)
```
============================= test session starts ==============================
platform linux -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: /home/assem-elqersh/Desktop/Warp Weft Project
plugins: anyio-4.10.0, cov-7.0.0, jaxtyping-0.3.10
collected 101 items

tests/test_benchmark_artifact_integrity.py ..                            [  1%]
tests/test_benchmark_integrity.py ....                                   [  5%]
tests/test_calibration.py ......                                         [ 11%]
tests/test_calibration_uncertainty.py ...                                [ 14%]
tests/test_client_image_failure_regression.py ..                         [ 16%]
tests/test_data_engine.py ......                                         [ 22%]
tests/test_fusion.py ....                                                [ 26%]
tests/test_ground_truth_protocol.py .......                              [ 33%]
tests/test_grouped_splits.py ...                                         [ 36%]
tests/test_metrology_metrics.py ....                                     [ 40%]
tests/test_model_registry.py ....                                        [ 44%]
tests/test_notebook_integrity.py ..                                      [ 46%]
tests/test_orientation.py ..                                             [ 48%]
tests/test_roi.py ...                                                    [ 51%]
tests/test_scientific_remediation.py ............                        [ 63%]
tests/test_smartphone_regression.py .                                    [ 64%]
tests/test_spatial.py ..                                                 [ 66%]
tests/test_specimen_workflow.py ....                                     [ 70%]
tests/test_spectral.py ..                                                [ 72%]
tests/test_validation_metrics.py .......                                 [ 79%]
tests/test_web_modes.py ....                                             [ 83%]
tests/test_web_server_integration.py ............                        [ 95%]
tests/test_web_ui_contract.py .....                                      [100%]

============================= 101 passed in 5.01s ==============================
```

---

### 7.5. FabricNET 130-Image Benchmark Rerun Verification
The authoritative deterministic engine was re-executed across all 130 FabricNET microscope images:
- **Total Samples:** 130
- **Candidate MAE:** Warp = 13.43 ends/cm, Weft = 11.25 picks/cm
- **Accepted Subset MAE:** Warp = 2.48 ends/cm (25 accepted), Weft = 2.38 picks/cm (32 accepted)
- **Within ±2.0 threads/cm:** Warp = 80.0% of accepted (20/25), Weft = 62.5% of accepted (20/32)
- **Decision Status Breakdown:** `NEEDS_REVIEW`: 88, `CONSISTENT_WITH_WARNING`: 27, `VALIDATED`: 15
- **Comparison to Committed Benchmark:**
  * Common samples: 130 / 130
  * Changed sample field counts across `pred_warp`, `pred_weft`, `accepted_warp`, `accepted_weft`, `decision_status`: **0**
  * Max absolute numeric delta: **0.0**
  * Exact deterministic reproducibility: Confirmed.

---

### 7.6. Residual Limitations & Boundary Conditions
1. **Smartphone Macro Stand Profile (`smartphone_macro_stand_v1`):** Scale factors ($S_x=263.5, S_y=208.4\text{ px/cm}$) remain empirical back-calculations from client reference fabric; they cannot provide verified factory certification without physical in-scene calibration targets.
2. **5-Region Spatial Uniformity vs Roll Certification:** Multi-region crops from a single smartphone capture evaluate local specimen uniformity. Factory acceptance per ASTM D3775-17(2023) requires physical test specimens extracted from across the entire fabric roll length and width.

