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
| **FabricNET Feature Regression (Random Forest)** | GLCM (96) + LBP (54) + Gabor (96) + IFV (16) $\to$ 262-d feature vector $\to$ Regressor | Single 2D Grayscale $(480, 640)$ | Direct density ($T_x, T_y$ in ends/cm) | **Implicit** (Nominal $5\times 4\text{ mm}$ FOV: $S_x=1280.0, S_y=1200.0\text{ px/cm}$) | Low (~90s CPU feature extraction, ~2s training) | ~85 ms (CPU) | Magnification shift; camera sensor distance changes; out-of-distribution weave architectures. |
| **FabricNET Feature Regression (XGBoost)** | 262-d structural texture vector $\to$ Gradient Boosted Trees | Single 2D Grayscale $(480, 640)$ | Direct density ($T_x, T_y$ in ends/cm) | **Implicit** (Nominal $5\times 4\text{ mm}$ FOV: $S_x=1280.0, S_y=1200.0\text{ px/cm}$) | Low (~90s feature extraction, ~1s training) | ~75 ms (CPU) | Severe sensitivity to high-frequency sensor noise and out-of-distribution optical blur. |
| **Roboflow Yarn Detector (`ayushiit/warp-weft-new-prod`)** | YOLOv8-based Object Detection (Roboflow 3.0 Fast) | 3-channel RGB $(640, 640)$ stretched | Discrete bounding boxes (`warp`, `weft`) | **Absent** (Predicts uncalibrated box counts in pixel crop) | Cloud hosted / proprietary | ~35 ms (Cloud API / GPU) | NMS suppresses 30-50% of adjacent parallel yarns; box count does not equal threads/cm without FOV scale. |
| **Roboflow Float Segmenter (`cheomseongdae/fabric-lby7e`)** | Roboflow 2.0 Base Semantic Segmentation | 1-channel Grayscale $(1184, 1184)$ | Pixel masks (`warp`, `weft`, `measure`) | **Optional** (Detects physical ruler polygon) | Cloud hosted / proprietary | ~60 ms (Cloud API / GPU) | Low mIoU (35.7%) yields severe mask fragmentation; requires heuristic graph tracking to link floats into yarns. |
| **TextileDefectDetection FCN (`weningerleon`)** | Modified U-Net (14 Conv2D + BatchNorm + LeakyReLU) | 6-channel tensor: Paired front-lit + back-lit RGB | 3-class float-point probability map | **Absent** (Requires downstream tracking + scale) | Pretrained (`net.h5`, 93.7 MB, Python 3.6 / TF 1.11) | ~40 ms (GPU) | Incompatible with standard single-exposure microscopy; plain-weave float tracking heuristic fails on twill/satin. |
| **Hybrid Analysis (WarpWeftUNet + Spacing)** | PyTorch U-Net (1.93M params) + Morphological Skeletonization | 1-channel Grayscale $(256, 256)$ | Segmentation masks $\to$ Centerlines $\to$ Spacing | **Mandatory** ($S_x, S_y$ px/cm) | Moderate (15 epochs on synthetic swatches) | ~35 ms (GPU) / ~120 ms (CPU) | Extreme fiber fuzz bridging adjacent yarns; computational overhead on low-end edge CPUs. |

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
      "integration_recommendation": "Recommended for Mode 3 (Hybrid Analysis): use model output for topological skeletonization followed by calibrated spatial pitch measurement."
    }
  ]
}
```

---

## 5. Empirical Experimental Findings

### Approach A: FabricNET Feature Regression (Notebook 01)
Evaluated across **26 held-out test specimens** (strictly unseen during training):
- **Random Forest**: Warp MAE = 4.88, Weft MAE = 5.39 ($R^2 = 0.690$ warp, $R^2 = 0.787$ weft).
- **XGBoost**: Warp MAE = 4.83, Weft MAE = 6.60 ($R^2 = 0.702$ warp, $R^2 = 0.339$ weft).
- **MLP Regressor**: Warp MAE = 7.11, Weft MAE = 13.54 ($R^2 = 0.566$ warp, $R^2 = -0.265$ weft).
- **Deterministic Baseline (Unvalidated direct candidates on full test split)**: Warp MAE = 13.27, Weft MAE = 13.16.

#### Weave-Specific Empirical Breakdown (MAE in threads/cm):
| Weave Architecture | Random Forest (Warp / Weft) | XGBoost (Warp / Weft) | MLP Regressor (Warp / Weft) | Deterministic Baseline (Warp / Weft) |
| :--- | :--- | :--- | :--- | :--- |
| **Plain** ($N=10$) | **3.37 / 4.75** | 3.70 / 4.62 | 5.87 / 10.67 | 8.98 / 8.05 |
| **Satin** ($N=9$) | **3.33 / 6.89** | 3.56 / 8.11 | 3.89 / 15.09 | 6.45 / 24.18 |
| **Twill** ($N=7$) | 8.33 / **4.69** | 7.51 / 7.56 | 11.89 / 15.58 | 25.45 / 8.54 |

**Key Deduction**:
Feature regression using Random Forest substantially outperforms unvalidated deterministic FFT on Satin weft (MAE 6.89 vs 24.18) and Twill warp (MAE 8.33 vs 25.45). This occurs because Random Forest captures non-linear statistical correlations between texture energy and yarn count, bypassing the harmonic ambiguity that plagues 2D FFT on long yarn floats. However, feature regression implicitly assumes a fixed 1.0 cm field-of-view; it does not generalize if the optical magnification changes.

### Approach B: Roboflow Projects Audit (Notebook 02)
- Mathematical simulation of greedy Non-Maximum Suppression (NMS) on parallel yarns (pitch $\Delta = 20$ px, yarn width $18$ px, $640 \times 640$ window):
  - At standard detector threshold $\text{IoU} = 0.45$: 32 true yarns $\to$ 22 retained (31.3% undercounting).
  - At $\text{IoU} = 0.30$: 32 true yarns $\to$ 16 retained (50.0% undercounting).
- **Deduction**: Discrete bounding-box object detection is mathematically flawed for dense parallel yarn counting unless NMS is replaced by directional 1D non-maximum suppression along the orthogonal axis.

### Approach C: TextileDefectDetection FCN Audit (Notebook 03)
- Checkpoint `net.h5` verified: 14 Conv2D layers, 93.7 MB.
- Input requires 6 channels: channel 0-2 (front-lit / reflected) and channel 3-5 (back-lit / transmitted).
- **Deduction**: Incompatible with standard single-exposure microscopy and FabricNET images. Cannot be deployed for general fabric density counting without dedicated dual-illumination hardware.

### Approach D: Modern Semantic Segmentation Baseline (Notebook 04)
- Trained `WarpWeftUNet` (1.93M parameters) on synthetic micro-swatches with Gaussian blur and noise.
- **Validation mIoU**: 92.58% (synthetic domain).
- **Held-out Test Performance (Synthetic domain)**:
  - Pixel Accuracy: **97.82%**
  - Mean IoU: **91.81%**
  - Background/Void IoU: 81.16%
  - Warp Yarn Core IoU: 96.80%
  - Weft Yarn Core IoU: 97.48%
- **Domain Constraint & Finding**: PyTorch U-Net demonstrates excellent segmentation on synthetic micro-swatches with mathematically ground-truthed masks. However, because real FabricNET and client smartphone swatches lack manual pixel-level yarn masks, this mIoU cannot be claimed as real-world segmentation accuracy. Real-domain deployment requires manual annotation on actual physical swatches.

### Approach E: Hybrid Geometric Measurement (Notebook 05)
- Evaluated on benchmark plain swatch (`sample_plain_32x28.png`, Ground Truth: Warp = 32.0, Weft = 28.0 ends/cm, Scale = 480 px/cm):
  - Predicted Warp Spacing $\Delta_x = 13.0$ px $\to$ Density = 36.92 ends/cm (Error = 4.92 ends/cm).
  - Predicted Weft Spacing $\Delta_y = 14.0$ px $\to$ Density = 34.29 picks/cm (Error = 6.29 picks/cm).
- **Deduction**: The hybrid pipeline decouples semantic pattern recognition from metric scaling. It eliminates harmonic ambiguity by explicitly locating yarn core centerlines, while honoring physical calibration ($S_x, S_y$).

---

## 6. Synthesis & Final Architectural Recommendation

For the production web application, the three user-selectable operational modes are structured as follows:

1. **Mode 1 — Classical Deterministic Analysis (Default & Currently Active Production Mode)**:
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
