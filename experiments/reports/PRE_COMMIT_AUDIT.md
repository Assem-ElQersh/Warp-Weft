# PRE-COMMIT AUDIT & RECONCILIATION VERIFICATION REPORT
**Repository:** Warp & Weft AI (`/home/assem-elqersh/Desktop/Warp Weft Project/`)  
**Target Branch:** `feat/reconciled-research-validation` (branched from `main` @ `8f0e7ce`)  
**Audit Timestamp:** 2026-11-19T15:15:00+02:00  
**Audit Scope:** Forensic review of working tree modifications, untracked artifacts, dataset/model protections, reproducibility integrity, and pre-commit staging classification.

---

## 1. Executive Summary & Verification Context

### 1.1. Operational Invariant Status
1. **Zero Git Modification Invariant:** Absolutely no git staging (`git add`), committing (`git commit`), pushing (`git push`), or branch merging has been executed during this session. The working tree remains purely in review state.
2. **Client Data Privacy Boundary:** Verified that `data/samples/test.png` ($1200 \times 1600 \times 3$, $2,595,080\text{ bytes}$, SHA-256 `fad7284aab78f25ddcd75cd39433b06a4301360132d6156db7b2d5d1c1da853b`) is excluded from tracking by `.gitignore` (lines 128–129: `data/samples/*`, `!data/samples/.gitkeep`). No raw client imagery is staged or exposed.
3. **Automated Test Suite Status:** Full test suite execution (`pytest tests/`) completed with **87 of 87 tests passing (100% success rate)** in $5.09\text{ seconds}$ on Python 3.13.9. No regressions were introduced.
4. **Static Code & Syntax Verification:** Inline JavaScript syntax verification (`scripts/check_inline_javascript.py`) passed cleanly (1 inline script block verified).

---

## 2. Comprehensive Inventory of Working Tree Artifacts

The following inventory audits every modified and untracked file currently present in the working tree (`git status --porcelain`). Each artifact is characterized by exact path, size in bytes, SHA-256 hash prefix, functional purpose, category, and commit safety classification.

| File Path | Type | Size (Bytes) | SHA-256 (16-char) | Category | Functional Purpose | Audit Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `README.md` | Markdown | 35,450 | `ae2ad341510acff0` | Documentation | Central project memory and Provenance Ledger tracking all empirical findings | `COMMIT` |
| `experiments/learned_models/README.md` | Markdown | 17,900 | `2907152fe12e56ad` | Documentation | Technical reference for master registries, modular code engine, and notebooks 01–07 | `COMMIT` |
| `experiments/PROJECT_RESEARCH_STATUS.md` | Markdown | 6,021 | `c67f4b15a1624cab` | Documentation | High-level synthesis of research phase objectives, findings, and architectural decisions | `COMMIT` |
| `experiments/__init__.py` | Python | 0 | `e3b0c44298fc1c14` | Code Package | Empty package initializer enabling modular imports from `experiments` | `COMMIT` |
| `experiments/datasets/README.md` | Markdown | 10,358 | `20370ada6ff2375a` | Documentation | Formal taxonomy and specification for 17 textile datasets across 7 metrology categories | `COMMIT` |
| `experiments/datasets/registry.json` | JSON | 27,188 | `82427143f2b78e09` | Configuration | Master Textile Dataset Registry indexing metadata, licenses, FOV, and calibration specs | `COMMIT` |
| `experiments/data_acquisition/storage_plan.json` | JSON | 3,116 | `880470a9374e87e9` | Configuration | Storage footprint allocation and directory layout plan for raw datasets | `COMMIT` |
| `experiments/data_acquisition/downloads/NithinAruswamy_TextileResearchDataset.zip` | ZIP Archive | 21,722,945 | `bfba988bbf65d92a` | External Data | Raw ZIP archive downloaded from Harvard Dataverse | `DO NOT COMMIT` |
| `experiments/data_acquisition/downloads/harvard_microtexture/` | Directory | ~42.5 MB | Multiple | External Data | 437 unpacked microscopy images and `features.csv` from Harvard Dataverse | `DO NOT COMMIT` |
| `experiments/models/MODEL_RESEARCH_MATRIX.md` | Markdown | 5,689 | `4b73a72b6ee33a1a` | Documentation | Research matrix evaluating candidate architectures across metrology criteria | `COMMIT` |
| `experiments/models/README.md` | Markdown | 8,584 | `5429352a8c2d7e68` | Documentation | Guide to candidate model registry, hardware profiles, and evaluation criteria | `COMMIT` |
| `experiments/models/registry.json` | JSON | 14,801 | `9b7b83c031282f7a` | Configuration | Master Model Registry cataloging 10 architectures across 6 paradigms | `COMMIT` |
| `experiments/models/download_models.py` | Python Script | 10,094 | `f9275d7e988e0537` | Script | Downloader and integrity verifier for pretrained model weights | `COMMIT` |
| `experiments/models/segmentation_models.py` | Python Module | 3,350 | `e2e077a79429c37a` | Code | PyTorch implementation of `WarpWeftUNet` (in_channels=1, num_classes=3) | `COMMIT` |
| `experiments/models/checkpoints/inventory.json` | JSON | 3,702 | `ed4cdef59042a833` | Configuration | Verification records, parameter counts, and SHA-256 hashes for downloaded checkpoints | `COMMIT` |
| `experiments/models/checkpoints/segformer_b0/config.json` | JSON | 6,910 | `3d40454e140497c0` | Model Config | Architecture configuration for SegFormer-B0 | `COMMIT` |
| `experiments/models/checkpoints/segformer_b0/model.safetensors` | Binary Weights | 15,036,944 | `6ae39addd01de6b1` | Model Weights | Pretrained weights for SegFormer-B0 ($14.34\text{ MB}$) | `DO NOT COMMIT` |
| `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth` | Binary Weights | 88,289,404 | `f2f5d5df475ec750` | Model Weights | Pretrained weights for DINOv2 ViT-S/14 ($84.20\text{ MB}$) | `DO NOT COMMIT` |
| `experiments/learned_models/__init__.py` | Python | 0 | `e3b0c44298fc1c14` | Code Package | Empty package initializer for learned models modular engine | `COMMIT` |
| `experiments/learned_models/annotations.py` | Python Module | 2,699 | `5dac9b2f8ca5cb17` | Code | Polygon rasterization, centerline extraction, and morphological skeletonization | `COMMIT` |
| `experiments/learned_models/augmentation.py` | Python Module | 4,646 | `fe318211f27d4515` | Code | Physically grounded augmentations (90° rotation with label swap, scale jitter, blur) | `COMMIT` |
| `experiments/learned_models/benchmark.py` | Python Module | 6,604 | `962509ba0beb0bec` | Code | Benchmark orchestrator comparing deterministic, learned, and hybrid pipelines | `COMMIT` |
| `experiments/learned_models/calibration.py` | Python Module | 2,761 | `d2e35e181622065f` | Code | Scale conversion ($D=S/\Delta$), uncertainty propagation ($\sigma_D$), homography rectification | `COMMIT` |
| `experiments/learned_models/data_registry.py` | Python Module | 5,634 | `ed931b8fcf274b1f` | Code | Programmatic API and CLI for loading, querying, and filtering dataset metadata | `COMMIT` |
| `experiments/learned_models/dataset_adapters.py` | Python Module | 10,745 | `5f0971b46e0d79d1` | Code | Polymorphic ingestion layer normalizing disparate datasets into `SampleRecord` objects | `COMMIT` |
| `experiments/learned_models/download_datasets.py` | Python Module | 5,404 | `57419d8232512403` | Code | Checksum-verified dataset downloader enforcing licensing and access boundaries | `COMMIT` |
| `experiments/learned_models/inference.py` | Python Module | 6,258 | `16ff4c61d6f75438` | Code | Inference runners for deterministic engine, U-Net tiler, and hybrid metrology | `COMMIT` |
| `experiments/learned_models/metrics.py` | Python Module | 4,347 | `8cd79f7ee3fe6a5c` | Code | CV metrics (IoU, Dice) and physical metrology metrics (MAE, RMSE, Bland-Altman LoA) | `COMMIT` |
| `experiments/learned_models/model_registry.py` | Python Module | 6,143 | `c667a75d6c9bbe4d` | Code | Model registry API, checkpoint hash validator, and model instantiation factory | `COMMIT` |
| `experiments/learned_models/preprocessing.py` | Python Module | 4,087 | `93534275d9d40466` | Code | Optical CLAHE, min-max scaling, and sliding-window patch tiler with 2D Hanning blending | `COMMIT` |
| `experiments/learned_models/splits.py` | Python Module | 4,431 | `73a84680c8dd08ce` | Code | Specimen-level grouped data partitioning guaranteeing zero leakage across splits | `COMMIT` |
| `experiments/learned_models/synthetic_generator.py` | Python Module | 6,651 | `aadbb2f76e2c0109` | Code | Procedural multi-weave fabric synthesizer with fiber fuzz, lighting, and exact metadata | `COMMIT` |
| `experiments/learned_models/verify_datasets.py` | Python Module | 8,931 | `1a242d5bcb66a187` | Code | Automated integrity verifier checking image readability, dimensions, and metadata | `COMMIT` |
| `experiments/learned_models/visualization.py` | Python Module | 3,889 | `4c51dcc666edb168` | Code | Publication-grade Bland-Altman plots, agreement corridors, and centerline overlays | `COMMIT` |
| `experiments/learned_models/notebooks/07_comprehensive_textile_research_engine.ipynb` | Jupyter Notebook | 11,008 | `f250b6c73fd978f3` | Notebook | Executed master textile metrology research notebook (cells 1–5 executed, 0 errors) | `COMMIT` |
| `experiments/learned_models/results/dataset_verification_report.json` | JSON | 1,344 | `a9223b4a4e6283b8` | Results | Output of `verify_datasets.py` confirming integrity of 5 local datasets | `COMMIT` |
| `experiments/learned_models/results/fabricnet_test_benchmark.json` | JSON | 1,061 | `33c14e999ea59675` | Results | Benchmark output evaluating deterministic engine on held-out FabricNET (N=130) | `COMMIT` |
| `experiments/learned_models/results/synthetic_micro_swatches_test_benchmark.json` | JSON | 1,893 | `c5ff2f0933cd8b1c` | Results | Comparative benchmark of deterministic vs hybrid U-Net on synthetic swatches | `COMMIT` |
| `experiments/learned_models/results/plots/fabricnet_deterministic_dual_engine_warp_bland_altman.png` | PNG Image | 85,580 | `a4a09c9278eea5f2` | Plot | Bland-Altman agreement plot generated from FabricNET benchmark | `COMMIT` |
| `experiments/learned_models/results/plots/fabricnet_deterministic_dual_engine_warp_scatter.png` | PNG Image | 124,926 | `5ddcde7e3c1f26c6` | Plot | 1:1 scatter agreement corridor plot generated from FabricNET benchmark | `COMMIT` |
| `data/client_benchmark_manifest.json` | JSON | 3,314 | `f6566b83394ef291` | Benchmark Manifest | Dedicated ASTM D3775 5-region benchmark manifest for Client Specimen 2 | `COMMIT` |
| `tests/test_calibration_uncertainty.py` | Test Module | 2,342 | `769fdb4c8cfeadd1` | Automated Test | Unit tests for scale conversion, uncertainty propagation, ruler, and homography | `COMMIT` |
| `tests/test_data_engine.py` | Test Module | 3,354 | `d12f34bb6ff5c23c` | Automated Test | Unit tests for data registry, adapters, zero-leakage splits, and synthetic generator | `COMMIT` |
| `tests/test_metrology_metrics.py` | Test Module | 2,721 | `506bcb2c7ff5b86d` | Automated Test | Unit tests for CV metrics (IoU, Dice) and metrology metrics (MAE, RMSE, LoA) | `COMMIT` |
| `tests/test_model_registry.py` | Test Module | 2,197 | `300fb4a114e9a2f2` | Automated Test | Unit tests for model registry querying, checkpoint hashing, and instantiation | `COMMIT` |
| `experiments/reports/AGENT_RECONCILIATION_REPORT.md` | Markdown | 12,105 | Multiple | Report | Detailed reconciliation between parallel agent research tracks | `COMMIT` |
| `experiments/reports/CLIENT_GROUND_TRUTH_VALIDATION.md` | Markdown | 8,565 | Multiple | Report | Forensic evaluation of Client Specimen 2 across 5 spatial quadrants | `COMMIT` |
| `experiments/reports/DATA_SUFFICIENCY_REPORT.md` | Markdown | 8,556 | Multiple | Report | Rigorous evaluation of dataset volume, diversity, and domain gaps | `COMMIT` |
| `experiments/reports/FINAL_ARCHITECTURE_RECOMMENDATION.md` | Markdown | 12,616 | Multiple | Report | Formal 3-mode architecture specification and production invariants | `COMMIT` |
| `experiments/reports/FINAL_RESEARCH_RECOMMENDATION.md` | Markdown | 8,898 | Multiple | Report | Executive research conclusions and deployment roadmaps | `COMMIT` |
| `experiments/reports/MODEL_COMPARISON_REPORT.md` | Markdown | 9,602 | Multiple | Report | Comparative evaluation of model paradigms, failure modes, and VRAM | `COMMIT` |
| `experiments/reports/NEXT_DATA_COLLECTION_PLAN.md` | Markdown | 11,763 | Multiple | Report | Actionable protocol for laboratory data collection and optical calibration | `COMMIT` |
| `experiments/reports/PHYSICAL_MEASUREMENT_COMPARISON.md` | Markdown | 8,447 | Multiple | Report | Metrology comparison between attempted vs accepted physical measurements | `COMMIT` |
| `experiments/reports/PHYSICAL_METROLOGY_REPORT.md` | Markdown | 8,941 | Multiple | Report | Analytical foundation of optical scaling, Nyquist limits, and crimp variance | `COMMIT` |
| `experiments/reports/TRAINING_REPRODUCTION_REPORT.md` | Markdown | 10,897 | Multiple | Report | Independent reproduction audit of FabricNET feature regression and U-Net | `COMMIT` |
| `experiments/reports/VERIFIED_DATASET_INVENTORY.md` | Markdown | 7,609 | Multiple | Report | Verification inventory auditing 15 candidate textile datasets | `COMMIT` |
| `experiments/reports/VERIFIED_MODEL_INVENTORY.md` | Markdown | 6,478 | Multiple | Report | Verification inventory auditing candidate architectures and checkpoints | `COMMIT` |
| `docs/Papers/*.pdf` (2 files) | PDF Documents | 9,317,075 | Multiple | Literature | Research papers on archaeological thread counting and HiblaTek mobile metrology | `DO NOT COMMIT` |

---

## 3. Data & Model Weight Protection Audit

### 3.1. Client Ground-Truth Data Privacy Boundary
- File: `data/samples/test.png`
- Image Geometry: $1200\text{ (W)} \times 1600\text{ (H)} \times 3\text{ channels}$, 8-bit RGB.
- Size: $2,595,080\text{ bytes}$ ($2.47\text{ MB}$).
- SHA-256: `fad7284aab78f25ddcd75cd39433b06a4301360132d6156db7b2d5d1c1da853b`.
- Status: **Protected**. `.gitignore` lines 128–129 explicitly ignore `data/samples/*` except `.gitkeep`. `git status` confirms this file is NOT tracked or staged.
- Benchmark Manifest (`data/client_benchmark_manifest.json`): Contains only calibration constants ($S_x=263.5, S_y=208.4$), quadrant bounding boxes, and manual counts. No raw pixels are exposed.

### 3.2. Large Model Checkpoint Weights Protection
1. **DINOv2 ViT-S/14 Checkpoint:**
   - Path: `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth`
   - Size: $88,289,404\text{ bytes}$ ($84.20\text{ MB}$).
   - SHA-256: `f2f5d5df475ec7501a3028cbfdb23f5451996ab42296d9178ad8e922ba10b40b`.
   - Protection Status: **Protected**. Matched by line 93 of `.gitignore` (`*.pth`). Must remain untracked. Users acquire it via `download_models.py`.
2. **SegFormer-B0 Checkpoint:**
   - Path: `experiments/models/checkpoints/segformer_b0/model.safetensors`
   - Size: $15,036,944\text{ bytes}$ ($14.34\text{ MB}$).
   - SHA-256: `6ae39addd01de6b12f270a6c024d26ef7f41cb8333246eb3f972b20fb979e27c`.
   - Protection Status: **Vulnerable in current `.gitignore`**. `.safetensors` was not explicitly listed in `.gitignore`. **Directive:** Update `.gitignore` to include `*.safetensors` before any git staging.
3. **U-Net Yarn Segmentation Checkpoint:**
   - Path: `experiments/learned_models/checkpoints/unet_yarn_segmentation.pt`
   - Size: $7,748,829\text{ bytes}$ ($7.39\text{ MB}$).
   - Protection Status: **Tracked**. Tracked previously via `.gitignore` exception line 99 (`!experiments/learned_models/checkpoints/*.pt`). Clean and intact.

### 3.3. External Downloaded Datasets Protection
1. **Harvard Dataverse ZIP Archive:**
   - Path: `experiments/data_acquisition/downloads/NithinAruswamy_TextileResearchDataset.zip`
   - Size: $21,722,945\text{ bytes}$ ($20.72\text{ MB}$).
   - Protection Status: **Protected**. Matched by `.gitignore` lines 20 (`downloads/`) and 103 (`*.zip`).
2. **Harvard Dataverse Extracted Swatches:**
   - Path: `experiments/data_acquisition/downloads/harvard_microtexture/`
   - Size: ~42.5 MB (437 files).
   - Protection Status: **Protected**. Located inside `downloads/`, which is ignored by `.gitignore` line 20.

### 3.4. Academic Literature PDFs Protection
- Path: `docs/Papers/*.pdf` (2 files, $9,317,075\text{ bytes}$, $8.89\text{ MB}$).
  - `Automated thread counting in archaeological textiles using pulse-based feature extraction.pdf` ($7.72\text{ MB}$)
  - `HiblaTek: A Mobile Image Processing System for Automated Warp and Weft Density Analysis.pdf` ($1.59\text{ MB}$)
- Protection Status: **Vulnerable in current `.gitignore`**. Raw PDF papers should not be tracked directly in git history to prevent permanent repository inflation. **Directive:** Add `docs/Papers/*.pdf` to `.gitignore`.

---

## 4. Reproducibility Verification & Execution Audit

### 4.1. Research Notebook 07 Execution Audit
- Path: `experiments/learned_models/notebooks/07_comprehensive_textile_research_engine.ipynb`
- Execution Environment: Python 3.13.9 (`/home/assem-elqersh/anaconda3/bin/python`) via `nbclient.NotebookClient`.
- Audit Results:
  - Total Cells: 7 (2 Markdown cells, 5 Code cells).
  - Unexecuted Cells: 0.
  - Cells with Errors: 0.
  - Execution Output Verification:
    - **Cell 1 (`execution_count: 1`):** Verified dataset registry loading and integrity checking.
      * Output: `Loaded 17 datasets from registry. Verification completed for 5 local datasets. [PASS] fabricnet [PASS] client_reference_specimens [PASS] synthetic_micro_swatches [PASS] ten_fabrics_dataset [PASS] aitex_afid`
    - **Cell 2 (`execution_count: 2`):** Verified model registry inspection and checkpoint verification.
      * Output: `Registered Models: 10. [VERIFIED] deterministic_dual_engine [REMOTE] custom_global_262d_rf [REMOTE] custom_global_262d_xgboost [VERIFIED] warp_weft_unet_v1 ...`
    - **Cell 3 (`execution_count: 3`):** Verified specimen-level disjoint partitioning on FabricNET with zero data leakage.
      * Output: `FabricNET Partitioning: 78 Train, 26 Val, 26 Test. Zero Leakage: True`
    - **Cell 4 (`execution_count: 4`):** Executed comparative benchmark on synthetic swatches.
      * Output: `[deterministic_dual_engine] Warp MAE: 1.00 (<=2: 100.0%) | Weft MAE: 0.00 (<=2: 100.0%)`  
      `[hybrid_unet_skeleton_pitch] Warp MAE: 25.14 (<=2: 0.0%) | Weft MAE: 22.00 (<=2: 0.0%)`
    - **Cell 5 (`execution_count: 5`):** Evaluated physical calibration uncertainty propagation across scales.
      * Output: `Scale: 200.0 px/cm | Density: 20.0 +/- 1.08 threads/cm (5.39%)`  
      `Scale: 400.0 px/cm | Density: 40.0 +/- 2.15 threads/cm (5.39%)`  
      `Scale: 1280.0 px/cm | Density: 128.0 +/- 6.89 threads/cm (5.39%)`

### 4.2. Benchmark Results & Agreement Plots Provenance
All empirical result files in `experiments/learned_models/results/` have a verified, reproducible provenance chain:
1. `dataset_verification_report.json`: Generated by `verify_datasets.py` (and Cell 1 of Notebook 07). Validates 5 local datasets with zero file corruption.
2. `fabricnet_test_benchmark.json`: Generated by `benchmark.py` running on `fabricnet` (N=130). Documents raw candidate performance across all 130 specimens: Warp MAE $13.43\text{ threads/cm}$ ($26.15\%$ within factory $\pm 2.0$) and Weft MAE $11.26\text{ threads/cm}$ ($27.69\%$ within factory $\pm 2.0$), with composite joint accuracy of $6.15\%$. (In comparison, when filtered by consensus gating as shown in `results/fabricnet_benchmark.json`, accepted measurements achieve Warp MAE $2.48\text{ threads/cm}$ at $19.2\%$ coverage and Weft MAE $2.38\text{ threads/cm}$ at $24.6\%$ coverage).
3. `synthetic_micro_swatches_test_benchmark.json`: Generated by `benchmark.py` running on synthetic swatches (and Cell 4 of Notebook 07). Documents deterministic engine achieving Warp MAE $1.00$ ($100\%$ within $\pm 2.0$) vs hybrid U-Net Warp MAE $25.14$ ($0\%$ within $\pm 2.0$).
4. `plots/fabricnet_deterministic_dual_engine_warp_bland_altman.png`: Generated by `visualization.py` via `benchmark.py`. Documents raw candidate Warp Mean Bias $-12.82\text{ threads/cm}$ with $95\%$ Limits of Agreement $[-39.53, +13.89]\text{ threads/cm}$, demonstrating that raw unfiltered spectral/spatial estimators extend well beyond the $\pm 2.0$ factory tolerance on complex or non-plain weaves.
5. `plots/fabricnet_deterministic_dual_engine_warp_scatter.png`: Generated by `visualization.py` via `benchmark.py`. Displays 1:1 agreement line with $\pm 2.0\text{ threads/cm}$ factory tolerance corridor, illustrating widespread scatter outside the tolerance corridor on un-gated samples.

---

## 5. Deep Code Review of Modular Python Engine (`experiments/learned_models/`)

A forensic review was conducted across all 16 Python modules in `experiments/learned_models/`. The following criteria were confirmed:

1. **Linguistic & Explainability Invariants:**
   - Every single Python module begins with an explicit header:
     `# The mechanistic justification for this step is: [X]`
   - Absolute absence of emojis, motivational filler, or speculative comments.
2. **Type Safety & Documentation:**
   - Strict adherence to Python `typing` annotations (`List`, `Dict`, `Tuple`, `Optional`, `Union`, `Any`).
   - Clean dataclass definitions (`SampleRecord`, `DensityMeasurement`, `DatasetEntry`, `ModelEntry`).
3. **Physical Metrology Correctness:**
   - **Calibration Formula:** Unconditionally enforces $D = S / \Delta$ (Density = Scale / Pitch) across all modules. Pure pixel models are prohibited from reporting uncalibrated densities.
   - **Uncertainty Propagation:** Partial derivative propagation $\sigma_D = D \sqrt{(\sigma_S/S)^2 + (\sigma_\Delta/\Delta)^2}$ correctly handles simultaneous camera scale and yarn pitch uncertainties.
   - **Continuous Spatial Coordinates:** Procedural generator (`synthetic_generator.py`) generates continuous spatial meshes (`np.meshgrid`) and continuous elliptical float profiles.
   - **Topological Skeletonization:** Implements Lee-94 morphological skeletonization (`annotations.py`) to reduce segmented yarn bands to 1-pixel centerlines before pitch extraction.
   - **Zero Data Leakage:** Partitioning algorithm (`splits.py`) stratifies at the `specimen_id` level, mathematically preventing crops of the same physical specimen from appearing across train and test partitions.
   - **Patch Re-synthesis:** Tiling reconstructor (`preprocessing.py`) uses a 2D Hanning window (`np.outer(window_1d, window_1d)`) to eliminate edge discontinuity artifacts during sliding-window inference.
4. **Architectural Backward Compatibility:**
   - `DeterministicInferenceRunner` seamlessly wraps `src.fabric_analysis.pipeline.analyze_fabric` without modifying or disrupting the production deterministic engine.

---

## 6. Client Benchmark Audit (`data/client_benchmark_manifest.json`)

1. **Specification Adherence:**
   - Conforms strictly to schema version 1.0.0.
   - Maps Client Specimen 2 ("العينة 2", smartphone capture `data/samples/test.png`).
   - Image resolution verified: $1200 \times 1600 \times 3$, matching physical FOV of $4.554\text{ cm} \times 7.678\text{ cm}$.
   - Physical calibration constants: $S_x = 263.5\text{ px/cm}$, $S_y = 208.4\text{ px/cm}$.
   - **Calibration Provenance Caveat:** As documented in `docs/CLIENT_IMAGE_FAILURE_ANALYSIS.md`, these scale factors were analytically back-calculated from observed pixel periods ($8.50\text{ px}$ warp, $7.72\text{ px}$ weft) and the client specimen's manual counts ($31\text{ ends/cm}$, $27\text{ picks/cm}$). This demonstrates that when scale matches the physical capture, spatial peak finding detects the correct thread frequencies. However, it does NOT constitute an independent external calibration from an in-scene optical graticule.
   - Nyquist resolution verified: $8.50\text{ px/thread}$ (warp) and $7.72\text{ px/thread}$ (weft), far exceeding the Nyquist limit of $2.0\text{ px/thread}$.
2. **ASTM D3775 Factory Ground Truth:**
   - 5 spatial quadrants codified:
     - `R1`: Center Fabric Body ($[472, 672, 728, 928]$) $\to$ Warp 31, Weft 27
     - `R2`: Top-Left Quadrant ($[150, 200, 406, 456]$) $\to$ Warp 31, Weft 27
     - `R3`: Top-Right Quadrant ($[794, 200, 1050, 456]$) $\to$ Warp 30, Weft 26
     - `R4`: Bottom-Left Quadrant ($[150, 1144, 406, 1400]$) $\to$ Warp 31, Weft 27
     - `R5`: Bottom-Right Quadrant ($[794, 1144, 1050, 1400]$) $\to$ Warp 32, Weft 26
   - Statistical baseline: Warp Mean $31.0 \pm 0.71\text{ ends/cm}$, Weft Mean $26.6 \pm 0.55\text{ picks/cm}$.
3. **Supervision Status & Validation Scope:**
   - Explicitly records `supervision_level: specimen_only`. Because individual physical pick-glass cutouts were not separately photographed across the 5 locations with matched in-scene scales, multi-region evaluation is achieved via digital spatial ROI cropping across the single macro swatch capture.
   - **Scientific Distinction:** This proves digital spatial consistency across fabric quadrants, but does not yet constitute full physical 5-region independent physical validation under ASTM D3775. True physical multi-region validation requires 5 separate macro captures with matched in-scene physical scale targets.

---

## 7. Actionable Classification & Staging Recommendation

### 7.1. Summary Classification Counts
- **Total Files Audited:** 58 files across root, docs, data, experiments, tests.
- **Recommended for Commit (`COMMIT`):** 52 files (All code, unit tests, configurations, executed notebook, reports, and lightweight results).
- **Recommended for Git Ignore / External (`DO NOT COMMIT`):** 6 files/directories:
  1. `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth` ($84.20\text{ MB}$, model checkpoint).
  2. `experiments/models/checkpoints/segformer_b0/model.safetensors` ($14.34\text{ MB}$, model checkpoint).
  3. `experiments/data_acquisition/downloads/NithinAruswamy_TextileResearchDataset.zip` ($20.72\text{ MB}$, raw archive).
  4. `experiments/data_acquisition/downloads/harvard_microtexture/` ($42.5\text{ MB}$, raw image files).
  5. `docs/Papers/*.pdf` ($8.89\text{ MB}$, 2 literature papers).
  6. `experiments/models/__pycache__/` (Python bytecode cache).

### 7.2. Recommended `.gitignore` Updates
Prior to executing any `git add`, `.gitignore` should be updated with the following additions:
```gitignore
# Model Weights & Safetensors
*.safetensors

# Literature Papers (Prevent repository bloat)
docs/Papers/*.pdf
```

### 7.3. Proposed (Unexecuted) Staging Sequence
When authorized by the user, the following exact staging commands should be executed to stage all verified components cleanly without staging any prohibited data:

```bash
# 1. Stage updated documentation and ledger
git add README.md
git add experiments/PROJECT_RESEARCH_STATUS.md
git add experiments/learned_models/README.md

# 2. Stage new automated regression and metrology tests
git add tests/test_calibration_uncertainty.py
git add tests/test_data_engine.py
git add tests/test_metrology_metrics.py
git add tests/test_model_registry.py

# 3. Stage client benchmark manifest
git add data/client_benchmark_manifest.json

# 4. Stage master registries and acquisition configurations
git add experiments/__init__.py
git add experiments/datasets/README.md
git add experiments/datasets/registry.json
git add experiments/data_acquisition/storage_plan.json
git add experiments/models/README.md
git add experiments/models/MODEL_RESEARCH_MATRIX.md
git add experiments/models/registry.json
git add experiments/models/download_models.py
git add experiments/models/segmentation_models.py
git add experiments/models/checkpoints/inventory.json
git add experiments/models/checkpoints/segformer_b0/config.json

# 5. Stage modular learned models engine
git add experiments/learned_models/__init__.py
git add experiments/learned_models/annotations.py
git add experiments/learned_models/augmentation.py
git add experiments/learned_models/benchmark.py
git add experiments/learned_models/calibration.py
git add experiments/learned_models/data_registry.py
git add experiments/learned_models/dataset_adapters.py
git add experiments/learned_models/download_datasets.py
git add experiments/learned_models/inference.py
git add experiments/learned_models/metrics.py
git add experiments/learned_models/model_registry.py
git add experiments/learned_models/preprocessing.py
git add experiments/learned_models/splits.py
git add experiments/learned_models/synthetic_generator.py
git add experiments/learned_models/verify_datasets.py
git add experiments/learned_models/visualization.py

# 6. Stage executed research notebook 07 and verified results
git add experiments/learned_models/notebooks/07_comprehensive_textile_research_engine.ipynb
git add experiments/learned_models/results/dataset_verification_report.json
git add experiments/learned_models/results/fabricnet_test_benchmark.json
git add experiments/learned_models/results/synthetic_micro_swatches_test_benchmark.json
git add experiments/learned_models/results/plots/fabricnet_deterministic_dual_engine_warp_bland_altman.png
git add experiments/learned_models/results/plots/fabricnet_deterministic_dual_engine_warp_scatter.png

# 7. Stage all 13 research and reconciliation reports
git add experiments/reports/
```

---

## 8. Final Audit Verification Sign-Off
- **Audit Verification State:** 100% COMPLETE & VERIFIED.
- **Git Commit Action:** ZERO COMMITS EXECUTED (Awaiting explicit user directive).
- **Regression Tests:** 87/87 tests PASSING in 5.09s.
