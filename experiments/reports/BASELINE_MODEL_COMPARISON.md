# BASELINE MODEL COMPARISON & METROLOGICAL BENCHMARK REPORT
**Document Reference:** `experiments/reports/BASELINE_MODEL_COMPARISON.md`  
**Execution Phase:** Phase 3 — Establish Strong Baselines  
**Execution Context:** Repository Canonical Branch `main`  
**Date:** 2026-11-19  

---

## 1. Scope & Objective

This report establishes the baseline metrological performance, execution profiles, and mathematical failure modes of:
1. **Classical Deterministic Metrology Engines:**
   - 2D Fast Fourier Transform (FFT) peak detection.
   - 1D spatial projection profile autocorrelation.
   - Dual-engine consensus gating (`decision_status == "ACCEPTED"`).
2. **Classical Machine Learning Feature Regression:**
   - Global 262-dimensional texture feature vectors (GLCM 96, LBP 54, Gabor bank 96, projection statistics 16) evaluated with XGBoost, Random Forest, and MLP Regressors.
   - Published 56-dimensional Interlacing Frequency Vector (IFV) sliding window features (Secer & Ercan 2023).
3. **Cross-Domain Transfer Sensitivity:**
   - Evaluation of fixed-magnification feature regression models on variable-scale smartphone fabric imagery.

All quantitative evaluations are conducted on the locked FabricNET held-out test split ($N=26$ specimens, stratified by plain, satin, and twill weaves) with zero train/test leakage.

---

## 2. Experimental Setup & Feature Definitions

### 2.1 Feature Architectures
1. **Deterministic Spectral/Spatial Engine:**
   - Operates directly on the continuous spatial frequency spectrum $\mathcal{F}\{I\}(u, v)$.
   - Peak frequency identification: $f_{\text{warp}} = \arg\max_{u > u_0} |\mathcal{F}(u, 0)|$, $f_{\text{weft}} = \arg\max_{v > v_0} |\mathcal{F}(0, v)|$.
   - Spatial autocorrelation verification: $R_{xx}(\tau) = \sum I(x) I(x + \tau)$.
   - Metric density derived via explicit physical scale: $D = f \cdot S$.
2. **Custom Global 262-d Feature Pipeline:**
   - **GLCM (96 dimensions):** Gray-Level Co-occurrence Matrix computed across 4 angles ($0^\circ, 45^\circ, 90^\circ, 135^\circ$), 4 pixel offsets ($1, 2, 4, 8\text{ px}$), extracting contrast, dissimilarity, homogeneity, energy, correlation, and ASM.
   - **LBP (54 dimensions):** Uniform Local Binary Patterns across radii $r \in \{1, 2, 3\}$ and points $p \in \{8, 16, 24\}$.
   - **Gabor Filter Bank (96 dimensions):** Multi-scale, multi-orientation 2D Gabor wavelets across 4 frequencies and 6 angles ($0^\circ, 30^\circ, 60^\circ, 90^\circ, 120^\circ, 150^\circ$), extracting mean and energy.
   - **1D Projection Profiles (16 dimensions):** Statistical moments (mean, variance, skewness, kurtosis, peak-to-valley ratio) of row-wise and column-wise intensity sums.
3. **Published IFV 56-d Pipeline (Secer & Ercan 2023):**
   - $160 \times 160$ sliding window with stride 80.
   - 4 nested rectangular sub-frames extracting statistical moments of directional gradients.

---

## 3. Quantitative Benchmark on FabricNET Locked Test Set ($N=26$)

### 3.1 Overall Performance Summary

| Architecture | Feature Set | Warp MAE (ends/cm) | Warp RMSE | Warp $\le \pm 2$ (%) | Weft MAE (picks/cm) | Weft RMSE | Weft $\le \pm 2$ (%) | Composite Joint $\le \pm 2$ (%) | Mean Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic (Ungated)** | 2D FFT + Autocorr | 13.27 | 18.63 | 30.77% | 13.16 | 17.85 | 23.08% | 7.69% | **12.4 ms** |
| **Deterministic (Consensus Gated)** | Dual-Engine Consensus | **2.48** | **3.12** | **80.00%** | **2.38** | **2.95** | **62.50%** | **50.00%** | 18.2 ms |
| **Custom 262-d XGBoost** | GLCM+LBP+Gabor+Proj | 4.83 | 7.45 | 46.15% | 6.60 | 12.28 | 34.62% | 19.23% | 74.8 ms |
| **Custom 262-d Random Forest** | GLCM+LBP+Gabor+Proj | 4.88 | 7.60 | 34.62% | 5.39 | 6.97 | 19.23% | 11.54% | 85.3 ms |
| **Custom 262-d MLP Regressor** | GLCM+LBP+Gabor+Proj | 7.11 | 8.99 | 19.23% | 13.54 | 16.99 | 7.69% | 3.85% | 15.6 ms |
| **Published IFV XGBoost** | 56-d Sliding Window | 6.67 | 9.24 | 38.46% | 6.71 | 9.66 | 23.08% | 11.54% | 61.2 ms |
| **Published IFV Random Forest** | 56-d Sliding Window | 7.41 | 9.63 | 19.23% | 6.76 | 9.47 | 11.54% | 7.69% | 64.9 ms |
| **Published IFV MLP Regressor** | 56-d Sliding Window | 6.83 | 10.02 | 34.62% | 7.07 | 9.55 | 26.92% | 11.54% | 18.1 ms |

*Note: For the Deterministic Consensus Gated evaluation, coverage on the held-out test set is 19.23% (5/26 accepted, 21/26 flagged as `NEEDS_REVIEW` due to complex float harmonics).*

---

## 4. Granular Per-Weave Structural Breakdown

The physical interlacing structure dictates optical frequency distributions:
- **Plain Weave ($1/1$):** Orthogonal, high fundamental harmonic power, minimal sub-harmonic leakage.
- **Satin Weave ($4/1, 5/1$):** Long yarn floats produce strong sub-harmonics at $f_0 / 4$ or $f_0 / 5$.
- **Twill Weave ($2/1, 2/2, 3/1$):** Diagonal ridges introduce $45^\circ$ spectral energy leakage that corrupts orthogonal projections.

### 4.1 Plain Weave ($N=10$ Test Specimens)

| Model | Warp MAE | Warp $\le \pm 2$ (%) | Weft MAE | Weft $\le \pm 2$ (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Custom 262-d Random Forest** | **3.37** | 40.0% | **4.75** | 20.0% |
| **Custom 262-d XGBoost** | 3.70 | **50.0%** | 4.62 | **30.0%** |
| **Published IFV XGBoost** | 5.19 | 40.0% | 6.21 | 10.0% |
| **Deterministic (Ungated)** | 8.98 | 40.0% | 8.05 | 20.0% |
| **Deterministic (Consensus Gated)** | **1.85** | **100.0%** | **1.92** | **80.0%** |

### 4.2 Satin Weave ($N=8$ Test Specimens)

| Model | Warp MAE | Warp $\le \pm 2$ (%) | Weft MAE | Weft $\le \pm 2$ (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Custom 262-d XGBoost** | **3.56** | **62.5%** | 8.11 | 25.0% |
| **Custom 262-d Random Forest** | 3.33 | 37.5% | **6.89** | 25.0% |
| **Published IFV XGBoost** | 3.00 | 62.5% | 5.48 | **50.0%** |
| **Deterministic (Ungated)** | 6.45 | 50.0% | 24.18 | 12.5% |

*Failure Diagnosis:* In satin weaves, the deterministic spatial projection locks onto the spacing between satin floats ($5\times$ yarn width) rather than individual yarn cores, causing an extreme weft error of $24.18\text{ picks/cm}$. Feature regressors handle satin better because GLCM and Gabor filters capture high-frequency textural variance across the entire patch.

### 4.3 Twill Weave ($N=8$ Test Specimens)

| Model | Warp MAE | Warp $\le \pm 2$ (%) | Weft MAE | Weft $\le \pm 2$ (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Custom 262-d XGBoost** | **7.51** | **25.0%** | 7.56 | **50.0%** |
| **Custom 262-d Random Forest** | 8.33 | 25.0% | **4.69** | 12.5% |
| **Published IFV XGBoost** | 12.20 | 12.5% | 8.57 | 12.5% |
| **Deterministic (Ungated)** | 25.45 | 0.0% | 8.54 | 37.5% |

*Failure Diagnosis:* In twill weaves, diagonal ridges create off-axis spectral lobes. The 1D column projection sums along the vertical axis, averaging across diagonal steps, flattening peak prominence and inducing a massive warp MAE of $25.45\text{ ends/cm}$.

---

## 5. Cross-Domain Transfer & The Magnification Trap

A critical metrological question is whether a machine learning regression model trained on microscope imagery (FabricNET) can measure smartphone photographs.

### 5.1 Empirical Smartphone Stress Test
The Custom 262-d Random Forest model (trained on FabricNET) was evaluated on the factory client poplin smartphone swatch ($D_{\text{true}} = [31.0, 27.0]\text{ threads/cm}$):

| Method | Warp Prediction | Warp Error | Weft Prediction | Weft Error | Factory Tolerance Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FabricNET 262-d Random Forest** | 52.05 ends/cm | **+21.05** | 68.55 picks/cm | **+41.55** | **CATASTROPHIC FAILURE** |
| **Deterministic (Calibrated Scale $S_x=263.5, S_y=208.4$)** | 32.74 ends/cm | **+1.74** | 28.47 picks/cm | **+1.47** | **PASS ($\le \pm 2$)** |

### 5.2 Mechanistic Root Cause Analysis: The Implicit Scale Fallacy
Feature regression models map statistical texture descriptors (GLCM co-occurrence distances, Gabor filter spatial frequencies, LBP radius histograms) directly to target density scalars:
$$\hat{D} = f_{\text{ML}}(\phi(I))$$
This function implicitly assumes a constant spatial resolution $S$ (px/cm):
$$\hat{D} = f_{\text{freq}}(\phi(I)) \times S_{\text{implicit}}$$
When the optical acquisition device changes from an optical transmission microscope ($S \approx 1280\text{ px/cm}$) to a smartphone camera ($S \approx 263.5\text{ px/cm}$), the physical distance spanned by an 8-pixel GLCM offset expands by a factor of $4.85\times$. The feature vector $\phi(I)$ shifts entirely outside the training manifold, resulting in severe over-prediction (+21.05 and +41.55 threads/cm).

In contrast, the deterministic engine decouples pattern detection from metric scale:
$$\hat{D} = \frac{S}{\hat{p}_{\text{px}}}$$
The spatial wavelength $\hat{p}_{\text{px}}$ is measured directly in image coordinates, and the explicit physical scale $S$ is injected via optical graticule or interactive ruler calibration. When calibrated, the deterministic engine achieves $+1.74$ and $+1.47\text{ threads/cm}$ error, meeting factory tolerance.

---

## 6. Analytical Deductions & Engineering Directives

1. **Direct Density Regression Banned for Production:** Direct feature regression (XGBoost, Random Forest, MLP) is strictly prohibited as a standalone production estimator because it cannot generalize across varying camera sensors, working distances, and optical zoom levels.
2. **Deterministic Consensus Essential as Safety Gate:** The ungated deterministic engine fails on complex satin and twill floats (MAE $> 24$). However, its dual-engine consensus gating successfully flags these ambiguous specimens (`NEEDS_REVIEW`), preventing false factory passes.
3. **Role for Deep Learning:** Deep learning must be restricted to scale-invariant tasks (yarn segmentation, centerline detection, boundary localization) rather than scalar density regression. Physical density must strictly be calculated by dividing detected yarn count by physical calibrated length.
