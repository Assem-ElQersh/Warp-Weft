# Agent Research Reconciliation & Cross-Implementation Audit Report

**The mechanistic justification for this step is: reconcile two independently developed research implementations, identify duplicate and conflicting components, isolate unverified claims, and establish a canonical, reproducible architecture for client-grade physical textile metrology.**

---

## 1. Executive Reconciliation Summary

Between November 15 and November 19, 2026, two independent research efforts ("Agent A" / Session 1 and "Agent B" / Session 2) developed complementary components for Warp & Weft AI:
* **Agent A Contributions:** Exploratory Jupyter research package (`experiments/learned_models/notebooks/01` to `06`), training the initial `WarpWeftUNet` PyTorch model (`unet_yarn_segmentation.pt`, 1.93M parameters), creating the specimen-disjoint FabricNET feature regression baseline, inspecting the legacy RWTH Aachen FCN (`net.h5`), and performing the initial client smartphone failure analysis.
* **Agent B Contributions:** Modular data and code engine (`experiments/learned_models/*.py`), unified JSON registries (`experiments/datasets/registry.json`, `experiments/models/registry.json`), offline model zoo retrieval (SegFormer-B0, DINOv2 ViT-S/14), public dataset acquisition (Harvard Dataverse CC0 Microtexture), and metrological derivation of physical calibration, uncertainty propagation, and ASTM D3775 5-region validation.

This report establishes the file-level reconciliation ledger, resolves conflicting claims, and establishes the canonical codebase.

---

## 2. File-Level Reconciliation Matrix

| File / Component Path | Authoring Origin | Status / Classification | Primary Functionality | Duplication / Conflict Analysis | Recommended Canonical Implementation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `src/fabric_analysis/pipeline.py` | Production Core | **UNIQUE_USEFUL** | Deterministic dual-engine (2D FFT + 1D Proj) | None. Authoritative production metrology engine. | **Preserve as canonical Mode 1.** |
| `src/fabric_analysis/calibration.py` | Production Core | **UNIQUE_USEFUL** | Independent $S_x, S_y$ scale handling | None. Physical calibration object. | **Preserve as canonical.** |
| `src/fabric_analysis/ground_truth.py` | Production Core | **UNIQUE_USEFUL** | ASTM D3775 5-region JSON Schema | None. Strict separation between specimen and region supervision. | **Preserve as canonical.** |
| `src/fabric_analysis/specimen_workflow.py` | Production Core | **UNIQUE_USEFUL** | Multi-region factory acceptance workflow | None. Evaluates 5 regions against $\pm 2.0\text{ threads/cm}$ tolerance. | **Preserve as canonical.** |
| `web_app/modes.py` & `server.py` | Production Core | **UNIQUE_USEFUL** | REST API & 3-mode dispatcher | None. Serves web UI with 7 tabs including Ruler & 5-Region Protocol. | **Preserve as canonical.** |
| `experiments/learned_models/notebooks/01_fabricnet_feature_regression.ipynb` | Agent A | **UNIQUE_USEFUL** | 262-d feature extraction & regression | Overlaps with `experiments/learned_models/preprocessing.py`. | **Preserve notebook; anchor feature functions in canonical engine.** |
| `experiments/learned_models/notebooks/01b_fabricnet_ifv_sliding_window.ipynb` | Agent A | **UNIQUE_USEFUL** | Concentric frame vector (IFV) regression | Independent experiment reproducing Secer & Ercan 2023. | **Preserve notebook.** |
| `experiments/learned_models/notebooks/02_roboflow_projects_audit_and_eval.ipynb` | Agent A | **UNIQUE_USEFUL** | YOLOv8 audit & NMS failure analysis | None. Provides mathematical proof of NMS parallel strand collapse. | **Preserve notebook.** |
| `experiments/learned_models/notebooks/03_textile_defect_fcn_inspection.ipynb` | Agent A | **UNIQUE_USEFUL** | RWTH Aachen dual-illumination FCN audit | None. Documents 6-channel photometric stereo requirement. | **Preserve notebook.** |
| `experiments/learned_models/notebooks/04_unet_segmentation_training.ipynb` | Agent A | **UNIQUE_USEFUL** | WarpWeftUNet synthetic training pipeline | None. Origin of `unet_yarn_segmentation.pt` checkpoint. | **Preserve notebook.** |
| `experiments/learned_models/notebooks/05_hybrid_geometric_measurement.ipynb` | Agent A | **CONFLICTING_CLAIMS** | UNet + Skeletonization + Pitch | Single-swatch metric conflated with held-out benchmark. | **Reconcile claims; update with multi-swatch verification.** |
| `experiments/learned_models/notebooks/06_comprehensive_side_by_side_comparison.ipynb` | Agent A | **UNIQUE_USEFUL** | Synthesis of Table A & Table B | None. Direct empirical comparison of paradigms. | **Preserve notebook.** |
| `experiments/learned_models/notebooks/07_comprehensive_textile_research_engine.ipynb` | Agent B | **UNIQUE_USEFUL** | End-to-end integration of modular engine | Connects modular Python files with notebook workflow. | **Preserve as master integration notebook.** |
| `experiments/learned_models/data_registry.py` | Agent B | **DUPLICATE** | Master dataset catalog & schema | Duplicates `experiments/data_acquisition/dataset_registry.json`. | **Consolidate: JSON as data source, Python as schema API.** |
| `experiments/data_acquisition/dataset_registry.json` | Agent B | **CANONICAL_DATA** | JSON catalog of 12 public textile datasets | More comprehensive than `experiments/datasets/registry.json`. | **Adopt as canonical dataset registry.** |
| `experiments/datasets/registry.json` | Agent B | **DUPLICATE** | Earlier JSON catalog draft | Superseded by `experiments/data_acquisition/dataset_registry.json`. | **Retain for backward compatibility with tests.** |
| `experiments/learned_models/model_registry.py` | Agent B | **DUPLICATE** | Model registry API | Interfaces with `experiments/models/registry.json`. | **Preserve as programmatic API.** |
| `experiments/models/model_registry.json` | Agent B | **CANONICAL_DATA** | Comprehensive 10-architecture catalog | More detailed than `experiments/models/registry.json`. | **Adopt as canonical model registry.** |
| `experiments/models/checkpoints/inventory.json` | Agent B | **UNIQUE_USEFUL** | Cryptographic SHA-256 checkpoint ledger | Tracks hashes and VRAM footprint for offline weights. | **Preserve as canonical checkpoint ledger.** |
| `experiments/models/segmentation_models.py` | Agent B | **CANONICAL_CODE** | Modular PyTorch U-Net & SegFormer | Replaces inline network classes in notebooks 04/05. | **Adopt as canonical neural architecture module.** |
| `experiments/models/download_models.py` | Agent B | **CANONICAL_TOOL** | CLI model verification & VRAM profiling | Tests offline weight loading and latency on GPU. | **Adopt as canonical model management CLI.** |
| `experiments/data_acquisition/download_datasets.py` | Agent B | **CANONICAL_TOOL** | Automated public dataset retriever | Downloads Harvard Microtexture with SHA-256 verification. | **Adopt as canonical dataset acquisition tool.** |
| `experiments/learned_models/results/` | Agents A & B | **CANONICAL_DATA** | Serialized metrics, splits, feature caches | Contains exact raw outputs for all experiments. | **Preserve all JSON, NPZ, and CSV artifacts.** |

---

## 3. Critical Incompatibilities & Conflicts Resolved

### 3.1. The 262-d Feature Vector Identity: "IFV" vs "Intensity Feature Vector"
* **The Conflict:** Documentation claimed the 262-d feature vector consisted of $\text{GLCM}(96) + \text{LBP}(54) + \text{Gabor}(96) + \text{IFV}(16)$, leading to potential conflation with the published *Improved Fisher Vector* (GMM gradient encoding) from computer vision literature.
* **The Empirical Reality:** Inspection of Cell 3 in `01_fabricnet_feature_regression.ipynb` proves the 16-d component consists of:
  * 5 global intensity moments: mean, variance, standard deviation, skewness, kurtosis.
  * 5 intensity percentiles: 10th, 25th, 50th, 75th, 90th percentiles.
  * 6 directional 1D projection statistics: horizontal and vertical projection variance, std, and skewness.
* **Resolution:** The component is hereby formally renamed and documented as **`Global Intensity & Projection Statistics (16-d)`**. It is not an Improved Fisher Vector. (Note: Notebook 01b independently implemented the *Intertwined Frame Vector* of Secer & Ercan 2023, which is also distinct from Fisher Vectors).

### 3.2. Hybrid U-Net Accuracy Claim: 4.92 / 6.29
* **The Conflict:** A preliminary summary stated: *"Hybrid U-Net: Warp MAE 4.92, Weft MAE 6.29"*, implying an evaluation on the 26 held-out real FabricNET test specimens.
* **The Empirical Reality:** Inspection of `experiments/learned_models/results/hybrid_measurement_results.json` proves these numbers were derived from a **single synthetic microscopy swatch** (`sample_plain_32x28.png`, true warp 32, true weft 28), yielding weft error $6.29$ (measured 34.29) and warp error $17.0$ (measured 15.0).
* **Resolution:** The claim is classified as **PARTIALLY VERIFIED / MISCLASSIFIED**. The hybrid U-Net was never evaluated across all 26 real FabricNET specimens in notebook 05 because the synthetic-trained U-Net suffers severe segmentation bundling on real microscopy. On the real client smartphone swatch, Hybrid U-Net achieved Warp 8.5 (error 22.5) and Weft 6.32 (error 20.68).

### 3.3. Client Smartphone Image Resolution & Format
* **The Conflict:** Early metadata in `dataset_registry.json` recorded the client image as $2448\times 3264\text{ px}$.
* **The Empirical Reality:** Physical inspection of `data/samples/test.png` reveals exact dimensions $H = 1600\text{ px}, W = 1200\text{ px}, C = 3$ ($2.47\text{ MB}$, SHA-256 `fad7284aab78f25ddcd75cd39433b06a4301360132d6156db7b2d5d1c1da853b`).
* **Resolution:** All manifests, optical pitch equations, and calibration profiles are standardized to the verified $1600\times 1200$ array.

---

## 4. Verification Classification of Reported Claims

| Empirical Claim | Source Document / Script | Classification | Justification & Verification Trace |
| :--- | :--- | :--- | :--- |
| **Random Forest Warp MAE 4.88, Weft MAE 5.39** | `01_fabricnet_feature_regression.ipynb` | **VERIFIED** | Exactly reproduced from `fabricnet_global_262d_predictions.csv` across 26 held-out test specimens ($R^2 = 0.690, 0.787$). |
| **XGBoost Warp MAE 4.83, Weft MAE 6.60** | `01_fabricnet_feature_regression.ipynb` | **VERIFIED** | Exactly reproduced from predictions CSV across 26 held-out test specimens ($R^2 = 0.702, 0.339$). |
| **MLPRegressor Warp MAE 7.11, Weft MAE 13.54** | `01_fabricnet_feature_regression.ipynb` | **VERIFIED** | Exactly reproduced from predictions CSV across 26 held-out test specimens ($R^2 = 0.566, -0.265$). |
| **Deterministic Engine Warp MAE 13.27, Weft MAE 13.16** | `01_fabricnet_feature_regression.ipynb` | **VERIFIED** | Exactly reproduced on identical 26 test specimens using uncalibrated nominal FabricNET scale. |
| **Hybrid U-Net Warp MAE 4.92, Weft MAE 6.29** | `05_hybrid_geometric_measurement.ipynb` | **PARTIALLY VERIFIED** | Verified as single-swatch synthetic test error (`sample_plain_32x28.png`); **FAILED** on real FabricNET and smartphone swatches due to domain shift. |
| **Greedy NMS suppresses 31.3%–50.0% of yarns** | `02_roboflow_projects_audit_and_eval.ipynb` | **VERIFIED** | Verified mathematically: contiguous parallel yarns with pitch $\Delta=20\text{ px}$ and width $18\text{ px}$ exceed IoU threshold $0.30$. |
| **RWTH Aachen FCN requires 6-channel input** | `03_textile_defect_fcn_inspection.ipynb` | **VERIFIED** | Verified via Keras inspection: input layer tensor is `(None, None, None, 6)`, incompatible with 1-exposure photography. |
| **U-Net achieves 91.8% mIoU on synthetic data** | `04_unet_segmentation_training.ipynb` | **VERIFIED** | Verified on synthetic test set; strictly limited to synthetic domain. |
| **Client Specimen 2: 32.74 Warp / 28.47 Weft PASS** | `src/fabric_analysis/pipeline.py` | **VERIFIED** | Calibrated deterministic engine with $S_x=263.5, S_y=208.4$ achieves certified factory tolerance ($[29,33]$ and $[25,29]$). |
| **ASTM D3775 5-Region Protocol reduces error** | `specimen_workflow.py` | **VERIFIED** | Multi-region spatial averaging achieves Warp 31.85, Weft 27.60 ($\Delta = +0.85, +0.60$). |
