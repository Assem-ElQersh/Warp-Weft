# The mechanistic justification for this step is: document complete model research matrix, dataset and annotation audits, checkpoint provenance, and empirical comparison results in experiments/learned_models/README.md.

# Warp & Weft AI: Trained Models vs. Deterministic Measurement Research Phase

## 1. Executive Summary
This document records the empirical results, architectural audits, and comparative benchmarks for the research phase evaluating **Trained Machine Learning Models vs. Classical Deterministic Measurement** for fabric thread density estimation (ends/cm and picks/cm).

The overarching objective is to prepare the engineering foundations for three user-selectable operational modes in the web application:
1. **Classical Deterministic Analysis**: High-speed, zero-training frequency-domain (2D FFT) and spatial projection analysis calibrated via physical pixel scale ($S_x, S_y$ in px/cm).
2. **Learned-Model Analysis**: Direct feature-based machine learning regression mapping spatial texture descriptors (GLCM, LBP, Gabor, IFV) to thread density.
3. **Hybrid Analysis**: Learned deep semantic segmentation (PyTorch U-Net) isolating yarn core filaments, coupled with calibrated morphological skeletonization and center-to-center pitch measurement.

---

## 2. Model Research Matrix

| Paradigm / Model | Underlying Architecture | Input Tensor & Resolution | Output Format | Spatial Calibration Required ($S_x, S_y$) | Training / Tuning Cost | Inference Latency | Primary Failure Modes & Boundary Conditions |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Engine** (`src/fabric_analysis`) | 2D FFT + 1D Spatial Autocorrelation & Peak Filtering | Grayscale / RGB $(H, W)$ arbitrary resolution | Direct thread density ($T_x, T_y$ in ends/cm) | **Mandatory** ($S_x, S_y$ px/cm) | Zero (Pure mathematical inference) | ~12 ms (CPU) | Harmonic ambiguity on twill/satin long yarn floats; low optical contrast; non-periodic patterns. |
| **Custom Global 262-d Regression (Random Forest)** | GLCM (96) + LBP (54) + Gabor (96) + Proj (16) $\to$ Regressor | Single 2D Grayscale $(480, 640)$ | Direct density ($T_x, T_y$ in ends/cm) | **Implicit** (Nominal $5\times 4\text{ mm}$ FOV: $S_x=1280.0, S_y=1200.0\text{ px/cm}$) | Low (~80s CPU feature extraction, ~2s training) | ~85 ms (CPU) | Magnification shift; camera sensor distance changes; out-of-distribution weave architectures. |
| **Custom Global 262-d Regression (XGBoost)** | 262-d structural texture vector $\to$ Gradient Boosted Trees | Single 2D Grayscale $(480, 640)$ | Direct density ($T_x, T_y$ in ends/cm) | **Implicit** (Nominal $5\times 4\text{ mm}$ FOV: $S_x=1280.0, S_y=1200.0\text{ px/cm}$) | Low (~80s feature extraction, ~1s training) | ~75 ms (CPU) | Severe sensitivity to high-frequency sensor noise and out-of-distribution optical blur. |
| **Published IFV Sliding Window (Random Forest)** | Secer & Ercan 2023 ($160\times 160$ sliding window, 4 nested frames, 56-d vector) | Single 2D Grayscale $(480, 640)$ | Direct density ($T_x, T_y$ in ends/cm) | **Implicit** (Nominal $5\times 4\text{ mm}$ FOV) | Low (~7s CPU feature extraction, ~2s training) | ~65 ms (CPU) | Magnification shift; cannot transfer across sensor resolutions. |
| **Published IFV Sliding Window (XGBoost)** | 56-d sliding window frame vector $\to$ Gradient Boosted Trees | Single 2D Grayscale $(480, 640)$ | Direct density ($T_x, T_y$ in ends/cm) | **Implicit** (Nominal $5\times 4\text{ mm}$ FOV) | Low (~7s feature extraction, ~1s training) | ~60 ms (CPU) | Overfitting on small-N dataset; fails on variable magnification. |
| **Roboflow Yarn Detector (`ayushiit/warp-weft-new-prod`)** | YOLOv8-based Object Detection (Roboflow 3.0 Fast) | 3-channel RGB $(640, 640)$ stretched | Discrete bounding boxes (`warp`, `weft`) | **Absent** (Predicts uncalibrated box counts in pixel crop) | Cloud hosted / proprietary | ~35 ms (Cloud API / GPU) | NMS suppresses 30-50% of adjacent parallel yarns; box count does not equal threads/cm without FOV scale. |
| **Roboflow Float Segmenter (`cheomseongdae/fabric-lby7e`)** | Roboflow 2.0 Base Semantic Segmentation | 1-channel Grayscale $(1184, 1184)$ | Pixel masks (`warp`, `weft`, `measure`) | **Optional** (Detects physical ruler polygon) | Cloud hosted / proprietary | ~60 ms (Cloud API / GPU) | Low mIoU (35.7%) yields severe mask fragmentation; requires heuristic graph tracking to link floats into yarns. |
| **TextileDefectDetection FCN (`weningerleon`)** | Modified U-Net (14 Conv2D + BatchNorm + LeakyReLU) | 6-channel tensor: Paired front-lit + back-lit RGB | 3-class float-point probability map | **Absent** (Requires downstream tracking + scale) | Pretrained (`net.h5`, 93.7 MB, Python 3.6 / TF 1.11) | ~40 ms (GPU) | Incompatible with standard single-exposure microscopy; plain-weave float tracking heuristic fails on twill/satin. |
| **Hybrid Analysis (WarpWeftUNet + Spacing)** | PyTorch U-Net (1.93M params) + Morphological Skeletonization | 1-channel Grayscale $(256, 256)$ native patch tiling | Segmentation masks $\to$ Centerlines $\to$ Spacing | **Mandatory** ($S_x, S_y$ px/cm) | Moderate (15 epochs on synthetic swatches) | ~35 ms (GPU) / ~120 ms (CPU) | Extreme fiber fuzz bridging adjacent yarns; computational overhead on low-end edge CPUs. |

---

## 3. Dataset and Annotation Audit

### A. FabricNET Parameters & Image Corpus
- **Volume & Modality**: 130 microscope swatches ($480 \times 640$ pixels, RGB).
- **Physical Optical Invariant**: Field of view is nominally $5.0 \times 4.0\text{ mm}$ ($0.5 \times 0.4\text{ cm}$) across $640 \times 480$ px ($S_x = 1280.0\text{ px/cm}, S_y = 1200.0\text{ px/cm}$; unverified against external stage micrometer).
- **Weave Distribution**: 50 Plain, 41 Satin, 39 Twill.
- **Ground Truth Target**: `Warp` (20 to 62 ends/cm, mean 35.7), `Weft` (15 to 93 picks/cm, mean 34.9).
- **Partitioning Protocol**: Strict specimen-level disjoint partitioning (`experiments/learned_models/results/fabricnet_splits.json`). 78 Train / 26 Validation / 26 Held-out Test specimens stratified by weave type. Zero image or augmented patch overlap across partitions.

### B. Roboflow `ayushiit/warp-weft-new-prod`
- **Volume**: 52 base images; Version 1: 274 images; Version 2: 200 images (augmented 5x with flips, crops, grayscale, noise).
- **Annotation Type**: Longitudinal bounding boxes covering visible spans of warp and weft yarns.
- **Classes**: `warp`, `weft` (2 classes).
- **Defects & Limitations**:
  1. **NMS Degradation**: When yarn spacing is dense (e.g. 20-30 pixels apart), adjacent bounding boxes exhibit mutual IoU overlap exceeding standard suppression thresholds ($\text{IoU} \ge 0.45$). Greedy NMS suppresses legitimate parallel yarn detections.
  2. **Uncalibrated Metric Output**: Outputs integer detection counts in a stretched 640x640 window. Yields no direct correlation to threads per centimeter without calibrated optical scale.

### C. Roboflow `cheomseongdae/fabric-lby7e`
- **Volume**: 74 base images; Version 6: 308 images ($1184 \times 1184$ grayscale).
- **Annotation Type**: Multi-point fine polygons on surface float points + bounding box on physical ruler (`measure`).
- **Classes**: `warp`, `weft`, `measure` (3 classes).
- **Defects & Limitations**:
  1. Low reported benchmark mIoU (35.7%) reflects extreme boundary ambiguity between adjacent fibers.
  2. Segmenting float points alone does not identify continuous yarns; it requires graph-based path tracking.

### D. Synthetic Microscope Ground Truth Corpus
- **Volume**: 120 synthesized micro-swatches ($256 \times 256$) with known yarn counts (12-24 warp, 10-22 weft), controlled blur (Gaussian PSF $\sigma=1.2$), sensor Gaussian noise ($\sigma=0.08$), and exact pixel-level masks.
- **Splits**: 80 Train / 20 Validation / 20 Held-out Test.
- **Classes**: 0: Interstice void, 1: Longitudinal warp yarn core, 2: Transverse weft yarn core.

---

## 4. Downloaded Checkpoint Inventory

The checkpoint inventory is formally maintained in `experiments/learned_models/checkpoints/inventory.json`.

```json
{
  "checkpoints": [
    {
      "checkpoint_id": "textile_defect_detection_fcn_v1",
      "filename": "net.h5",
      "filepath": "experiments/reference_repos/TextileDefectDetection/example/net.h5",
      "sha256": "d2439b2fd7c94154950ec2805b99ece91472150f53b7ad1760d7645b894944b7",
      "size_bytes": 93740448,
      "framework": "TensorFlow/Keras 1.11 (Python 3.6)",
      "architecture": "Modified U-Net (14 Conv2D + BatchNorm + LeakyReLU + Softmax)",
      "input_shape": [null, null, 6],
      "input_channels": 6,
      "output_classes": 3,
      "class_labels": ["background", "warp_float", "weft_float"],
      "dual_illumination_required": true,
      "weave_compatibility": ["plain"],
      "direct_density_prediction": false,
      "integration_recommendation": "Preserve as reference model; unsuitable for general single-image density analysis."
    },
    {
      "checkpoint_id": "unet_yarn_segmentation_v1",
      "filename": "unet_yarn_segmentation.pt",
      "filepath": "experiments/learned_models/checkpoints/unet_yarn_segmentation.pt",
      "sha256": "3ef9b96ebc0c7ba07e8ef8c40ff497b7b134812845c47854e7d58fbb2fc134b2",
      "size_bytes": 7718915,
      "framework": "PyTorch 2.13.0+cu130",
      "architecture": "WarpWeftUNet (DoubleConv encoder-decoder with skip connections)",
      "input_shape": [null, 1, 256, 256],
      "input_channels": 1,
      "output_classes": 3,
      "class_labels": ["background_interstice", "warp_yarn_core", "weft_yarn_core"],
      "best_val_miou": 0.9258,
      "test_pixel_accuracy": 0.9782,
      "test_miou": 0.9181,
      "direct_density_prediction": false,
      "integration_recommendation": "Synthetic domain only. Requires manual pixel-level annotations on physical fabrics before production release."
    }
  ]
}
```

---

## 5. Empirical Experimental Findings

### Table A: FabricNET Microscope Domain (26 Held-out Test Specimens)

| Method / Architecture | Feature Set | Warp MAE | Warp $\le \pm 2$ (%) | Weft MAE | Weft $\le \pm 2$ (%) | Latency | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Engine** | 2D FFT + 1D Spatial Autocorrelation | 13.27 | 30.8% | 13.16 | 23.1% | ~12 ms | Twill/satin float harmonics; low optical contrast |
| **Custom Global 262-d (Random Forest)** | GLCM(96) + LBP(54) + Gabor(96) + Proj(16) | 4.88 | 34.6% | 5.39 | 19.2% | ~85 ms | Implicit fixed magnification; cannot transfer to phone |
| **Custom Global 262-d (XGBoost)** | GLCM(96) + LBP(54) + Gabor(96) + Proj(16) | 4.83 | 46.2% | 6.60 | 34.6% | ~75 ms | Sensor noise sensitivity; implicit magnification |
| **Published IFV (Random Forest)** | Secer & Ercan 2023 ($160\times 160$ IFV) | 7.41 | 19.2% | 6.76 | 11.5% | ~65 ms | Out-of-distribution weave textures; implicit scale |
| **Published IFV (XGBoost)** | Secer & Ercan 2023 ($160\times 160$ IFV) | 6.67 | 38.5% | 6.71 | 23.1% | ~60 ms | Overfitting on small-N dataset; implicit scale |

### Table B: Client Smartphone Domain (`data/samples/test.png`, Specimen 2)
Ground Truth: Warp = 31 ends/cm (Acceptance tolerance: 29–33), Weft = 27 picks/cm (Acceptance tolerance: 25–29). Factory Tolerance = $\pm 2.0\text{ threads/cm}$.

| Method / Paradigm | Warp (ends/cm) | Weft (picks/cm) | Decision Status | Factory Tolerance Check | Root Cause / Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic (FabricNET Preset $S_x=1280, S_y=1200$)** | 54.0 (Candidate) | 9.0 (Candidate) | **NEEDS_REVIEW** (Accepted: None) | **REJECTED** (Error +23 / -18) | 5.5x scale inflation ($1280/1200$ vs $263/208\text{ px/cm}$) + macro-stripe harmonic aliasing |
| **Deterministic (Calibrated Phone $S_x=263.5, S_y=208.4$)** | **32.74** | **28.47** | **ACCEPTED** | **PASS** (+1.74 warp $\in [29,33]$, +1.47 weft $\in [25,29]$) | Physically calibrated pitch on uniform ground weave |
| **FabricNET Global 262-d RF Regressor** | 52.05 | 68.55 | UNVALIDATED | **FAIL** (Error +21.05 warp, +41.55 weft) | 5x FOV disparity between microscope optics and phone camera |
| **Hybrid WarpWeftUNet (Patch-tiled)** | 8.50 | 6.32 | UNVALIDATED | **FAIL** (Error -22.50 warp, -20.68 weft) | Synthetic-to-real domain gap; segments fiber clusters |

---

## 6. Synthesis & Final Architectural Recommendation

For the production web application, the three user-selectable operational modes are structured as follows:

1. **Mode 1 — Classical Deterministic Analysis (Default & Active Production Mode)**:
   - **Engine**: Authoritative production engine in `src/fabric_analysis/`.
   - **Status**: **Available** (`available: true`).
   - **Ideal For**: Clean, unprinted plain fabrics with uniform lighting and known spatial calibration scale ($S_x, S_y$).
   - **Characteristics**: Sub-15ms execution latency, zero GPU requirements, fully explainable physics. Exposes explicit `decision_status` (ACCEPTED vs. NEEDS_REVIEW) to protect against unvalidated harmonic guesses.

2. **Mode 2 — Learned-Model Analysis (Macro Feature Mode)**:
   - **Engine**: Feature vector (GLCM + LBP + Gabor + IFV) evaluated via trained Random Forest / XGBoost models.
   - **Status**: **Research Package Committed; Production Flag Disabled** (`available: false`).
   - **Reason**: Requires client-aligned dataset with 5-region smartphone protocol before production release.

3. **Mode 3 — Hybrid Analysis (High-Precision Guided Mode)**:
   - **Engine**: Lightweight PyTorch U-Net (`unet_yarn_segmentation.pt`) coupled with topological skeletonization and calibrated pitch calculation.
   - **Status**: **Research Package Committed; Production Flag Disabled** (`available: false`).
   - **Reason**: Pretrained checkpoint is synthetic-domain; real-domain pixel ground truth is required before production deployment.

---

## 7. Master Registries & Reproducible Research Engine

### 7.1. Master Registries
1. **Master Dataset Registry** (`experiments/datasets/registry.json` & `experiments/datasets/README.md`):
   - Indexes 17 candidate textile datasets across 7 functional metrology categories (A: Physical Density Labels, B: Yarn-Level Segmentation, C: Textile Appearance, D: Defect Disruption, E: Statistical Microtexture, F: Synthetic Simulation, G: Auxiliary Tabular).
   - Codifies physical calibration specifications ($S_x, S_y$), optical field of view, Nyquist-Shannon resolution bounds, and licensing governance.
   - Strictly enforces the rule: defect masks must never be conflated with periodic thread density ground truth.

2. **Master Model Registry** (`experiments/models/registry.json` & `experiments/models/README.md`):
   - Catalogs 10 model candidates across classical deterministic, statistical feature regression, deep semantic segmentation, promptable foundation models, foundation feature backbones, and hybrid metrology.
   - Details exact parameter counts, input/output tensors, memory footprints, and inference latency.
   - Mandates explicit physical scale grounding ($D = S / \Delta$) for physical metrology.

### 7.2. Reproducible Research Code Engine (`experiments/learned_models/`)
The modular Python engine provides dedicated CLI and programmatic entry points:
- `data_registry.py`: CLI and API to query, filter, and validate dataset metadata.
- `download_datasets.py`: Checksum-verified downloader respecting licensing and academic access boundaries.
- `verify_datasets.py`: Automated dataset integrity verifier checking image readability, dimensions, and label coverage.
- `dataset_adapters.py`: Polymorphic data ingestion layer standardizing disparate datasets into `SampleRecord` objects.
- `annotations.py`: Mathematical transformations for polygons, masks, skeletons, and continuous density maps.
- `preprocessing.py`: Optical CLAHE normalization and sliding-window patch tiling with smooth Hanning reconstruction.
- `splits.py`: Specimen-grouped disjoint partitioning guaranteeing zero data leakage across train, val, and test splits.
- `augmentation.py`: Physically grounded textile augmentations (90° orthogonal rotation with axis swap, scale jitter with synchronous calibration update, blur, noise, and shading gradients).
- `calibration.py`: Physical metrology conversions ($D = S / \Delta$), homography rectification, and partial derivative error propagation ($\sigma_D$).
- `metrics.py`: Dual-level evaluation metrics: CV metrics (IoU, Dice, Pixel Accuracy) and metrology metrics (MAE, RMSE, MBE, max error, % within ±1 and ±2 threads/cm, Bland-Altman LoA).
- `model_registry.py`: Model loader, checkpoint SHA-256 verifier, and hardware-aware instantiation factory.
- `inference.py`: Full-frame and patch-based inference runners for deterministic, U-Net, and hybrid pipelines.
- `visualization.py`: Publication-grade Bland-Altman plots, agreement corridors, and centerline overlays.
- `benchmark.py`: Unified comparative benchmarking CLI executing evaluations across held-out splits.

### 7.3. Research Notebook Suite
All experimental workflows are maintained as reproducible `.ipynb` files:
- `01_fabricnet_feature_regression.ipynb`: Global 262-d Random Forest and XGBoost regression.
- `01b_fabricnet_ifv_sliding_window.ipynb`: Concentric IFV sliding-window feature regression.
- `02_roboflow_projects_audit_and_eval.ipynb`: Bounding box NMS suppression and float segmentation audit.
- `03_textile_defect_fcn_inspection.ipynb`: 6-channel dual-illumination FCN inspection.
- `04_unet_segmentation_training.ipynb`: PyTorch WarpWeftUNet training on synthetic swatches.
- `05_hybrid_geometric_measurement.ipynb`: Native patch-tiled hybrid segmentation and pitch measurement.
- `06_comprehensive_side_by_side_comparison.ipynb`: Multi-model side-by-side empirical comparison.
- `07_comprehensive_textile_research_engine.ipynb`: Master research pipeline demonstrating end-to-end dataset registration, verification, calibration uncertainty, and benchmarking.
