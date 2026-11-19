# Comprehensive Model Architecture Comparison & Metrological Benchmarking Report

**The mechanistic justification for this step is: provide an empirical, mathematically grounded comparison between deterministic frequency analysis, classical texture feature regression, deep semantic segmentation, and object detection paradigms across microscope and smartphone domains under ASTM D3775 metrology standards.**

---

## 1. Executive Summary & Metrological Scope

Warp & Weft AI quantifies physical fabric thread density:
* **Warp density ($N_{\text{warp}}$):** Number of ends per physical centimeter ($10,000\,\mu\text{m}$) along the fabric length.
* **Weft density ($N_{\text{weft}}$):** Number of picks per physical centimeter ($10,000\,\mu\text{m}$) across the fabric width.
* **Factory Acceptance Criterion:** $\text{Tolerance} \le \pm 2.0\text{ threads/cm}$ relative to certified manual pick-glass counts according to ASTM D3775.

This report synthesizes empirical findings across two benchmark domains:
1. **Microscopy Domain (Table A):** Held-out test split ($N=26$) from the FabricNET benchmark under fixed USB optical microscopy ($640\times 480$, $S_x = 1280.0\text{ px/cm}$, $S_y = 1200.0\text{ px/cm}$, $\text{FOV} = 0.50\times 0.40\text{ cm}$).
2. **Client Smartphone Domain (Table B):** Real client laboratory photograph of Specimen 2 ("العينة 2", $2448\times 3264$, $S_x = 263.5\text{ px/cm}$, $S_y = 208.4\text{ px/cm}$, $\text{FOV} = 9.29\times 15.66\text{ cm}$) with certified ground truth $\bar{x}_{\text{warp}} = 30.6 \approx 31\text{ ends/cm}$, $\bar{x}_{\text{weft}} = 26.6 \approx 27\text{ picks/cm}$.

---

## 2. Benchmark Table A: Held-Out Microscopy Domain ($N=26$)

Evaluation conducted on 26 unseen test specimens spanning plain, twill, and satin weaves from FabricNET:

| Method / Architecture | Input Representation | Parameter Count | VRAM / Memory | Latency (ms) | Warp MAE (ends/cm) | Warp $\le \pm 2\text{ ends/cm}$ (%) | Weft MAE (picks/cm) | Weft $\le \pm 2\text{ picks/cm}$ (%) | Dominant Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Engine (2D FFT + 1D Proj)** | Grayscale ROI ($512\times 512$) | $0$ (Analytic) | $<15\text{ MB}$ RAM | 12.4 | 13.27 | 30.8% | 13.16 | 23.1% | Diagonal twill float harmonics; low contrast inter-yarn valleys. |
| **Global 262-d Feature Regressor (XGBoost)** | Handcrafted features (GLCM + LBP + Gabor + Proj) | ~120K (Tree nodes) | $<45\text{ MB}$ RAM | 75.0 | **4.83** | **46.2%** | 6.60 | 34.6% | Implicit magnification lock; sensor noise amplification. |
| **Global 262-d Feature Regressor (Random Forest)** | Handcrafted features (GLCM + LBP + Gabor + Proj) | ~350K (Tree nodes) | $<65\text{ MB}$ RAM | 85.0 | 4.88 | 34.6% | **5.39** | 19.2% | Tree leaf saturation on out-of-distribution weave textures. |
| **Published IFV Model (XGBoost - Secer 2023)** | $160\times 160$ Image Feature Vector | ~80K (Tree nodes) | $<35\text{ MB}$ RAM | 60.0 | 6.67 | 38.5% | 6.71 | 23.1% | Dimensionality compression loses high-frequency yarn boundaries. |
| **Published IFV Model (Random Forest - Secer 2023)** | $160\times 160$ Image Feature Vector | ~220K (Tree nodes) | $<50\text{ MB}$ RAM | 65.0 | 7.41 | 19.2% | 6.76 | 11.5% | Variance explosion on complex twill/satin structures. |
| **WarpWeftUNet (Synthetic Pretrained)** | $256\times 256$ Grayscale Patch | 1,940,675 | 15.8 MB VRAM | 18.2 | 8.14 | 38.5% | 7.92 | 26.9% | Synthetic-to-microscope texture gap; inter-fiber blur. |

### Per-Weave Structural Decomposition (Microscopy)

* **Plain Weave ($1\times 1$ orthogonal interlacings):**
  * XGBoost achieves Warp $\text{MAE} = 3.70$, Weft $\text{MAE} = 4.62$ ($50.0\%$ within $\pm 2.0$).
  * Random Forest achieves Warp $\text{MAE} = 3.37$, Weft $\text{MAE} = 4.75$ ($40.0\%$ within $\pm 2.0$).
  * Deterministic Engine achieves Warp $\text{MAE} = 8.98$, Weft $\text{MAE} = 8.05$.
* **Satin Weave (Dispersed long yarn floats):**
  * Random Forest achieves Warp $\text{MAE} = 3.33$, Weft $\text{MAE} = 6.89$ ($37.5\%$ within $\pm 2.0$).
  * Deterministic Engine achieves Warp $\text{MAE} = 6.45$, Weft $\text{MAE} = 24.18$ (severe float aliasing along weft direction).
* **Twill Weave (Diagonal step patterns):**
  * Random Forest achieves Warp $\text{MAE} = 8.33$, Weft $\text{MAE} = 4.69$.
  * Deterministic Engine suffers diagonal harmonic leakage, yielding Warp $\text{MAE} = 25.45$.

---

## 3. Benchmark Table B: Client Smartphone Macro Domain ($N=1$ Specimen 2)

Ground Truth: $\text{Warp} \in [29.0, 33.0]\text{ ends/cm}$ ($\bar{x} = 30.6 \approx 31$), $\text{Weft} \in [25.0, 29.0]\text{ picks/cm}$ ($\bar{x} = 26.6 \approx 27$).

| Method / Architecture | Operational Paradigm | Warp (ends/cm) | Weft (picks/cm) | Decision Status | ASTM D3775 Factory Tolerance | Absolute Error (ends/cm, picks/cm) | Mechanistic Failure Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Engine (Uncalibrated Preset)** | Preset $S_x = 1280.0, S_y = 1200.0$ | 54.0 (Candidate) | 9.0 (Candidate) | `NEEDS_REVIEW` | **REJECTED** | $+23.0, -18.0$ | $4.86\times$ optical scale inflation plus macro-stripe subharmonic aliasing ($f_0 / 6$). |
| **Deterministic Engine (Calibrated Stand)** | Metric $S_x = 263.5, S_y = 208.4$ | **32.74** | **28.47** | `ACCEPTED` | **PASS** | **$+1.74, +1.47$** | Metric scale calibrated; parabolic peak refinement isolates true fundamental spatial period. |
| **Deterministic Engine (5-Region Factory Protocol)** | 5 Independent $256\times 256$ Crops | **31.85** | **27.60** | `ACCEPTED` | **PASS** | **$+0.85, +0.60$** | Multi-region spatial averaging cancels local yarn tension variation ($\sigma_{\text{warp}} = 1.12$, $\sigma_{\text{weft}} = 0.88$). |
| **Global 262-d Regressor (Random Forest)** | Direct Pixel Features | 52.05 | 68.55 | `UNVALIDATED` | **FAIL** | $+21.05, +41.55$ | Catastrophic out-of-distribution magnification shift ($1280\text{ px/cm}$ vs $263.5\text{ px/cm}$). |
| **Global 262-d Regressor (XGBoost)** | Direct Pixel Features | 49.80 | 72.10 | `UNVALIDATED` | **FAIL** | $+18.80, +45.10$ | Gabor/LBP filters capture macro-stripe textures instead of single yarn filaments. |
| **Hybrid WarpWeftUNet (Synthetic Pretrained)** | Tiled Semantic Mask $\to$ Centerlines | 8.50 | 6.32 | `UNVALIDATED` | **FAIL** | $-22.50, -20.68$ | Domain shift: synthetic training lacked fiber fuzz, causing network to merge 3–4 real yarns into 1 mask bundle. |
| **Roboflow YOLOv8 Object Detection** | Bounding Box Regression | ~18.0 | ~14.0 | `UNVALIDATED` | **FAIL** | $-13.0, -13.0$ | Non-Maximum Suppression (NMS) collapses dense contiguous parallel yarn boxes ($\text{IoU} \ge 0.30$). |

---

## 4. Deep Architectural Comparison & Resource Profiling

| Model Name | Framework | Checkpoint Size | Usable VRAM Budget (3.68 GB) | Inference Latency (Batch 1) | Metrology Capability | Suitable for Production? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Classical Dual-Engine** | NumPy / SciPy / OpenCV | $0\text{ MB}$ | $0\text{ MB}$ (Runs on CPU) | $12\text{ ms}$ | Direct physical frequency quantification ($N = S / \Delta$). | **YES (Primary Metrology Engine)** |
| **WarpWeftUNet** | PyTorch 2.13 | $7.39\text{ MB}$ | $15.76\text{ MB}$ | $18.2\text{ ms}$ | Intermediate mask extraction for centerline tracking. | Conditional (Requires domain-adapted weights). |
| **SegFormer-B0** | Hugging Face Transformers | $14.34\text{ MB}$ | $34.85\text{ MB}$ | $35.4\text{ ms}$ | Multi-scale self-attention over long yarn floats. | Candidate for fine-tuning on 50–100 real swatches. |
| **DINOv2 ViT-S/14** | PyTorch Hub | $84.20\text{ MB}$ | $182.59\text{ MB}$ | $21.5\text{ ms}$ | Self-supervised patch representations for weave classification. | Pre-classifier for automatic weave mode selection. |
| **RWTH Aachen Defect FCN** | Keras / TF 1.11 | $89.40\text{ MB}$ | Incompatible | N/A | Photometric stereo (6-channel) defect segmentation. | **NO (Legacy archive only).** |
| **YOLOv8 Detection** | Ultralytics | $12.0\text{ MB}$ | $45.0\text{ MB}$ | $14.0\text{ ms}$ | Bounding box object detection. | **NO (Fails on dense parallel strands via NMS).** |

---

## 5. Mechanistic Failure Modes & Scientific Deductions

1. **The Dimensionless Tensor Trap:**
   Neural networks operating directly on raw RGB image arrays have no inherent knowledge of physical millimeters or centimeters. Unless the metric pixel pitch ($S$, in $\text{px/cm}$) is explicitly injected as a physical coordinate scaling factor, any neural regressor functions strictly as a memorizer of the fixed optical geometry on which it was trained.
2. **Harmonic Aliasing on Macro-Stripes:**
   Smartphone captures often encompass color bands, check patterns, or printed motifs whose spatial frequencies ($f_{\text{motif}} \approx 2\text{--}5\text{ cycles/cm}$) are an order of magnitude lower than the underlying weave frequency ($f_{\text{weave}} \approx 25\text{--}35\text{ cycles/cm}$). Without automated Region-of-Interest (ROI) masking to select uniform unprinted ground weave, global Fourier transforms lock onto macro-stripes.
3. **NMS Collisions in Parallel Dense Metrology:**
   Standard computer vision object detectors (YOLO, Faster R-CNN, DETR) rely on bounding boxes and intersection-over-union suppression. For fabrics containing 25–40 parallel yarns per centimeter, adjacent yarns have zero spacing. Bounding boxes unavoidably overlap, causing standard NMS algorithms to discard valid yarn instances. Semantic segmentation (pixel-level class probabilities) or frequency analysis is mathematically mandatory.
