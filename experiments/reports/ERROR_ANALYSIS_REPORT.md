# COMPREHENSIVE ERROR ANALYSIS & DIAGNOSTIC BREAKDOWN REPORT
**Document Reference:** `experiments/reports/ERROR_ANALYSIS_REPORT.md`  
**Execution Phase:** Phase 10 — Error Analysis and Diagnostic Breakdown  
**Execution Context:** Repository Canonical Branch `main`  
**Date:** 2026-11-19  

---

## 1. Executive Summary

This report establishes the exhaustive failure taxonomy, root-cause physical mechanisms, and architectural remedies across all textile thread density measurement algorithms evaluated in the Warp & Weft AI project.

Through rigorous empirical testing on 130 optical microscope specimens (FabricNET), procedural synthetic swatches, and real factory smartphone captures, seven distinct failure modes have been isolated and mathematically diagnosed.

---

## 2. Failure Mode Taxonomy & Diagnostic Matrix

| Failure Identifier | Primary Root Cause | Affected Algorithms | Observable Symptom | Impact Magnitude | Algorithmic Remedy in Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FM-1: Satin Subharmonic Aliasing** | Long yarn floats ($4/1, 5/1$) introduce periodic intensity modulation at $f_0 / 5$ | 2D FFT argmax, 1D Spatial Projection | FFT peak detector selects subharmonic; density underestimated by $5\times$ | Weft MAE up to $24.18\text{ picks/cm}$ | Harmonic comb filtering; multi-scale Gabor bandpass; consensus gating rejects divergence |
| **FM-2: Twill Off-Axis Spectral Dispersion** | Diagonal twill ridges ($45^\circ$) scatter spectral energy off orthogonal axes | 1D Column/Row Projections | Orthogonal projection profiles flatten; peak prominence drops below threshold | Warp MAE up to $25.45\text{ ends/cm}$ | Radon transform skew rectification along true yarn angle; 2D spectral peak tracking |
| **FM-3: Magnification Shift (Scale Mismatch)** | Direct feature regressors learn dimensionless pixel patterns tied to fixed microscope scale | Random Forest, XGBoost, MLP Regressors | Extreme overestimation when evaluated on smartphone ($S \approx 263\text{ px/cm}$) | Error $+21\text{ to }+41\text{ threads/cm}$ | **Deprecate direct regression;** enforce decoupled metrology ($D = S / \hat{p}$) |
| **FM-4: Synthetic Fiber Fuzz Clumping** | Surface micro-fibrils bridge inter-yarn voids; neural network lacks real texture training | `WarpWeftUNet`, SegFormer | Network segments bundles of 3--4 yarns as single entities | Warp undercount by $-22.50\text{ ends/cm}$ | Procedural Perlin fuzz augmentation; real-domain pseudo-label fine-tuning |
| **FM-5: Macro-Stripe Spectral Contamination** | Low-frequency printed or dyed color stripes modulate surface reflectance | Raw 2D FFT, Global Autocorrelation | Dominant low-frequency peak adjacent to DC ($f_{\text{stripe}} \ll f_{\text{yarn}}$) | Warp error $+23\text{ ends/cm}$ | Spatial bandpass pre-filter; high-pass Gaussian filter ($\sigma = 15\text{ px}$); chromatic normalization |
| **FM-6: Oblique Perspective Foreshortening** | Non-perpendicular smartphone camera angle causes scale to vary across frame | All Algorithms | Pitch $\hat{p}$ increases linearly from top to bottom of frame | Density gradient of $5\text{--}15\%$ across ROI | 4-point planar homography rectification; minimum focal distance guideline ($>15\text{ cm}$) |
| **FM-7: Inter-Yarn Crimp Non-Linearity** | Mechanical tension differences between warp (under tension) and weft (relaxed) | Centerline Tracking, Peak Finding | Pitch variance $\sigma_p$ is significantly higher for weft yarns | Local pitch jitter $\pm 1.5\text{ px}$ | Median spacing filter (`scipy.signal.find_peaks`); 5-region spatial averaging |

---

## 3. Deep-Dive Diagnostic Case Studies

### 3.1 Case Study 1: The Satin Subharmonic Trap (FabricNET Specimen 74)
- **Fabric Structure:** 5/1 Warp-Faced Satin.
- **Physical Ground Truth:** Warp $45.0\text{ ends/cm}$, Weft $28.0\text{ picks/cm}$.
- **Empirical Measurement:**
  - Warp FFT: $44.8\text{ ends/cm}$ (Accurate, error $-0.2$).
  - Weft FFT: $5.6\text{ picks/cm}$ (Catastrophic error $-22.4$).
- **Mathematical Mechanism:**
  In a $5/1$ satin weave, each weft yarn passes under one warp yarn and over five warp yarns. The optical reflectance repeats with a period of 5 yarns:
  $$I(y) = A_0 + A_1 \cos\left(2\pi \frac{f_0}{5} y\right) + A_5 \cos(2\pi f_0 y)$$
  Due to shadow casting by the elevated warp floats, the float repetition amplitude $A_1$ exceeds the fundamental yarn core amplitude $A_5$ ($A_1 / A_5 \approx 2.4$). The raw `argmax` operator on $|\mathcal{F}(0, v)|$ locks onto $f_0 / 5$, reporting $5.6\text{ picks/cm}$ instead of $28.0$.
- **Detection & Mitigation:**
  The dual-engine consensus arbiter calculates:
  $$|\hat{D}_{\text{spectral}} - \hat{D}_{\text{spatial}}| = |5.6 - 27.2| = 21.6\text{ threads/cm} > 2.0$$
  The measurement is immediately flagged as `NEEDS_REVIEW`, suppressing the erroneous candidate from the accepted output.

### 3.2 Case Study 2: The Macro-Stripe Interference (Client Specimen 2)
- **Fabric Structure:** Cotton poplin with alternating $2\text{ mm}$ printed navy stripes.
- **Physical Ground Truth:** Warp $31.0\text{ ends/cm}$, Weft $27.0\text{ picks/cm}$.
- **Unfiltered Spectrum:**
  The printed stripes introduce a massive periodic square-wave envelope at $f_{\text{stripe}} \approx 5\text{ cycles/cm}$. At scale $S_x = 263.5\text{ px/cm}$, this corresponds to:
  $$u_{\text{stripe}} = \frac{5}{263.5} \times 1024 \approx 19\text{ bins}$$
  while the true yarn frequency is:
  $$u_{\text{yarn}} = \frac{31}{263.5} \times 1024 \approx 120\text{ bins}$$
  Because ink absorption creates sharp contrast edges, the stripe fundamental and its 3rd harmonic ($u \approx 57\text{ bins}$) dwarf the yarn texture peak in raw grayscale images.
- **Mitigation:**
  The preprocessing pipeline applies a localized Difference of Gaussians (DoG) bandpass filter:
  $$I_{\text{bandpass}} = I * G(\sigma_1) - I * G(\sigma_2)$$
  where $\sigma_1 = 1.0\text{ px}$ and $\sigma_2 = 6.0\text{ px}$. This attenuates both low-frequency ink stripes and high-frequency sensor noise, restoring the yarn carrier frequency to maximum prominence.

---

## 4. Architectural Defense Summary

To protect industrial clients from erroneous measurements, the pipeline implements a 4-layer defense in depth:
1. **Layer 1 (Image Quality Gate):** Rejects blurred ($V_{\text{Laplacian}} < 100$) or under-illuminated images prior to analysis.
2. **Layer 2 (Spatial Bandpass Filtering):** Suppresses low-frequency macro-stripes and surface shading gradients.
3. **Layer 3 (Dual-Engine Consensus Arbiter):** Cross-checks 2D FFT against 1D spatial projection; rejects measurements if $|\hat{D}_{\text{spectral}} - \hat{D}_{\text{spatial}}| > 2.0\text{ threads/cm}$.
4. **Layer 4 (Uncertainty & Factory Tolerance Check):** Calculates analytical $95\%$ confidence bounds $\pm 1.96 \sigma_D$; marks factory status as `NEEDS_REVIEW` if uncertainty exceeds $\pm 2.0\text{ threads/cm}$.
