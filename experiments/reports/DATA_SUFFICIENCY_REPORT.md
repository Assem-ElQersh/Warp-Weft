# Warp & Weft AI — Data Sufficiency & Domain Transfer Audit Report

**Report ID:** `REP-DATA-SUFFICIENCY-2026-11`  
**Authoritative Branch:** `feat/comprehensive-textile-model-research`  
**Evaluation Standard:** ASTM D3775 ($\pm 2.0\text{ threads/cm}$ Factory Acceptance Tolerance)

---

## 1. Executive Summary & Objective

The objective of Warp & Weft AI is to determine physical warp thread density ($N_{\text{warp}}$, ends/cm) and weft thread density ($N_{\text{weft}}$, picks/cm) from digital camera captures. This audit rigorously evaluates the sufficiency, statistical validity, and domain transferability of all available datasets in the repository and external research landscape.

---

## 2. Quantitative Dataset Inventory

The project currently has access to **10 empirical datasets** spanning 5 distinct imaging domains:

| Dataset Identifier | Domain / Hardware | File Count | Disk Size | Physical Scale ($S$) | Explicit Density Ground Truth ($N_{\text{warp}}, N_{\text{weft}}$) | Usability for Direct Density AI |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`fabricnet`** | Optical USB Microscope | 130 JPG | $13.4\text{ MB}$ | $S_x=1280.0, S_y=1200.0\text{ px/cm}$ | **Yes** ($20\text{--}62\text{ ends/cm}, 15\text{--}93\text{ picks/cm}$) | **Valid for Microscopy Only** |
| **`client_reference_specimen`** | Macro Smartphone Rig | 1 ($5$ regions) | $2.59\text{ MB}$ | $S_x=263.5, S_y=208.4\text{ px/cm}$ | **Yes** (Warp $31$, Weft $27\text{ threads/cm}$) | **Locked Test Benchmark Only ($N=1$)** |
| **`harvard_microtexture`** | RPi HQ Camera + 100x Lens | 190 JPG/PNG | $21.7\text{ MB}$ | High-mag optical microtexture | **No** (40+ Haralick/LBP/Wavelet features) | **Feature Extraction Pretraining Only** |
| **`ten_fabrics`** | Calibrated Flatbed Scan | 2,969 PNG | $423.2\text{ MB}$ | $S = 118.11\text{ px/cm}$ ($300\text{ DPI}$) | **No** (Defect block matrices, coarse weave) | **Texture Analysis Only** |
| **`aitex_database`** | Industrial Web Line-Scan | 354 PNG | $168.1\text{ MB}$ | Full loom web ($<40\text{ px/cm}$) | **No** (12 industrial defect classes) | **Defect Isolation Only** |
| **`multiclass_defects`** | Apparel Factory Macro | 3,067 JPG/PNG | $2.17\text{ GB}$ | Uncalibrated optical camera | **No** (Directional defects: horizontal, vertical) | **Directional Defect Robustness** |
| **`fabric_defects_benchmark`** | Multi-Source Factory Defect | 2,739 JPG/PNG | $2.15\text{ GB}$ | Uncalibrated optical capture | **No** (6 industrial anomaly classes) | **Anomaly Rejection Pretraining** |
| **`textile_weaving_tabular`** | Industrial Loom Logs | 121,149 rows | $40.0\text{ MB}$ | N/A (Production parameters) | **Yes** (EPI $50\text{--}180$, PPI $40\text{--}120$) | **Priors on Industrial Density Bounds** |
| **`textile_knitting_tabular`** | Circular Knitting Machines | 12,570 rows | $3.1\text{ MB}$ | N/A (Machine parameters) | **No** (Knitted loops, not woven grids) | **Exclude from Woven Analysis** |
| **`synthetic_yarn_lattices`** | Procedural Physics Generator | 1,000+ PNG | $50.0\text{ MB}$ | $S = 512.0\text{ px/cm}$ | **Yes** (Pixel-exact centerlines, pitch, masks) | **Synthetic Pretraining & Unit Testing** |

---

## 3. The Physical Metrology Invariant & Optical Scale

A fundamental mathematical reality governs automated thread counting: an image sensor captures discrete integer pixel coordinates $(u, v)$. The physical thread density $N$ depends strictly on two terms:
$$N = \frac{S}{\Delta}$$
where:
* $S$ is the optical spatial calibration scale in $\text{pixels/cm}$.
* $\Delta$ is the inter-yarn spacing (pitch) in $\text{pixels}$.

### Why Uncalibrated Deep Learning Fails
An uncalibrated convolutional network or Vision Transformer has **zero knowledge of camera distance, focal length, or sensor pixel pitch**. 
* If a 30 ends/cm fabric is photographed at $5\text{ cm}$ ($S = 400\text{ px/cm}$), $\Delta = 13.3\text{ px}$.
* If the exact same fabric is photographed at $10\text{ cm}$ ($S = 200\text{ px/cm}$), $\Delta = 6.7\text{ px}$.
* Without physical calibration input, a neural network predicting a scalar density number from raw pixel tensors will produce catastrophic errors the instant the camera distance fluctuates by even a fraction of an inch.

---

## 4. Empirical Proof of Microscope-to-Smartphone Domain Collapse

In `experiments/learned_models/results/side_by_side_comparison.json`, we evaluated the exact same trained models across both domains:

### 4.1. Table A: Held-Out Microscopy Test Set (FabricNET, 26 Held-Out Specimens)
* **Classical Deterministic:** $\text{MAE}_{\text{warp}} = 8.12$, $\text{MAE}_{\text{weft}} = 8.77$ ($R^2 = 0.420 / 0.510$).
* **Global 262-d Random Forest:** $\text{MAE}_{\text{warp}} = 4.88$, $\text{MAE}_{\text{weft}} = 5.39$ ($R^2 = 0.690 / 0.787$).
* **Sliding-Window IFV XGBoost:** $\text{MAE}_{\text{warp}} = 6.67$, $\text{MAE}_{\text{weft}} = 6.71$ ($R^2 = 0.479 / 0.686$).

### 4.2. Table B: Zero-Shot Generalization to Client Smartphone (`test.png`)
* **Ground Truth:** Warp = $31.0\text{ ends/cm}$ ($[29, 33]$), Weft = $27.0\text{ picks/cm}$ ($[25, 29]$).
* **Classical Deterministic (Calibrated Stand $S_x=263.5, S_y=208.4$):**
  * **Warp = $32.74\text{ ends/cm}$ ($\Delta = +1.74$) $\implies \mathbf{PASS}$**
  * **Weft = $28.47\text{ picks/cm}$ ($\Delta = +1.47$) $\implies \mathbf{PASS}$**
  * Status: `ACCEPTED` (Dual-engine consensus).
* **FabricNET Global 262-d RF:**
  * **Warp = $52.05\text{ ends/cm}$ ($\Delta = +21.05$) $\implies \mathbf{FAIL}$**
  * **Weft = $68.55\text{ picks/cm}$ ($\Delta = +41.55$) $\implies \mathbf{FAIL}$**
* **Hybrid WarpWeftUNet (Synthetic Pretraining):**
  * **Warp = $8.50\text{ ends/cm}$, Weft = $6.32\text{ picks/cm} \implies \mathbf{FAIL}$**
  * *Root Cause:* High surface fiber fuzz on real spun cotton causes adjacent yarns to merge into 3-yarn macro bundles under low magnification, suppressing segmented peak counts by $75\%$.

### 4.3. Analytical Diagnosis of the Domain Gap
1. **$4.86\times$ Spatial Magnification Disparity:** In FabricNET ($S_x=1280\text{ px/cm}$), a $30\text{ ends/cm}$ yarn occupies $\sim 42.7\text{ pixels}$. In the client smartphone rig ($S_x=263.5\text{ px/cm}$), the same yarn occupies only $\sim 8.8\text{ pixels}$. Spatial frequency kernels (Gabor filters, GLCM displacement vectors) trained on 42-pixel yarns extract noise when applied to 8-pixel yarns.
2. **Surface Reflection vs. Inter-Yarn Shadow:** Microscopic USB illumination uses a circular LED ring directly illuminating yarn interstices. Smartphone cameras under ambient or oblique top lighting produce shadow gradients and specular highlights that mask interlacing points.

---

## 5. Statistical Proof of Data Insufficiency for Smartphone Deep Learning

The client smartphone dataset currently consists of **$N = 1$ physical fabric swatch** (`data/samples/test.png`, Specimen 2). 

1. **Degrees of Freedom & Overfitting:** An end-to-end convolutional network or Vision Transformer contains between $1.9\text{M}$ (`WarpWeftUNet`) and $3.7\text{M}$ (`SegFormer-B0`) trainable parameters. Optimizing $10^6$ parameters on $N=1$ specimen is mathematically unconstrained. The model will memorize the color, stripe spacing, and fiber fuzz of Specimen 2 and fail completely on any new fabric style.
2. **Specimen-Clustered Dependency Violation:** While 5 spatial crops can be extracted from Specimen 2 ($R_1$ to $R_5$), these crops are **not statistically independent samples**. They share the exact same yarn spinning lot, dye batch, weave tension, and loom settings. Training on $R_1\text{--}R_4$ and testing on $R_5$ causes severe data leakage.

---

## 6. Required Data Acquisition Roadmap for Production AI

To train a robust, generalizable deep learning model for the client factory smartphone workflow:

1. **Minimum Specimen Volume:** Collect **50 to 100 distinct physical fabric specimens** across varied weave architectures (Plain, Twill $2/1$, Twill $2/2$, Satin, Stripe patterns).
2. **Fixed In-Plane Calibration Protocol:** Photograph each swatch using the calibrated factory macro stand ($S_x=263.5, S_y=208.4\text{ px/cm}$) or with a $10\times$ linen tester pick-glass aperture ($S=420.0\text{ px/cm}$).
3. **ASTM D3775 Ground Truth:** For each swatch, record manual counting graticule measurements across 5 physically distinct regions ($5 \times 100 = 500$ verified region labels).
4. **Intermediate Bridge:** In the absence of 100 physical smartphone swatches, the **classical deterministic engine remains the only mathematically valid and certified production system**.
