# The mechanistic justification for this step is: document full verification audit of the learned-model research package, contrasting custom global 262-d features with the published IFV sliding-window method, formalizing synthetic domain boundaries, and recording empirical cross-domain failure modes on smartphone captures.

# Learned-Model Validation and Reproducibility Audit

## 1. Audit Baseline and Repository Status
This audit records the empirical findings, model reproducibility, and domain validation status for all experiments located in `experiments/learned_models/` under branch `feat/client-validated-density-measurement`.

All code, split manifests, trained checkpoints, prediction records (CSV), and evaluation summaries (JSON) are version-controlled in the repository:
- `experiments/learned_models/notebooks/01_fabricnet_feature_regression.ipynb`: `EXP-FABRICNET-GLOBAL-262D` (Custom Global Texture Baseline).
- `experiments/learned_models/notebooks/01b_fabricnet_ifv_sliding_window.ipynb`: `EXP-FABRICNET-IFV-SLIDING-WINDOW` (Published IFV Sliding Window Baseline).
- `experiments/learned_models/notebooks/02_roboflow_projects_audit_and_eval.ipynb`: Bounding-box detection & float segmentation audit.
- `experiments/learned_models/notebooks/03_textile_defect_fcn_inspection.ipynb`: Audit of legacy 6-channel paired illumination checkpoint `net.h5`.
- `experiments/learned_models/notebooks/04_unet_segmentation_training.ipynb`: PyTorch `WarpWeftUNet` trained on synthetic micro-swatches.
- `experiments/learned_models/notebooks/05_hybrid_geometric_measurement.ipynb`: Native patch-tiled segmentation coupled with physical calibration and topological skeletonization.
- `experiments/learned_models/notebooks/06_comprehensive_side_by_side_comparison.ipynb`: Cross-paradigm benchmark synthesizing Tables A (FabricNET microscope domain) and B (Client smartphone domain).

---

## 2. Handcrafted Feature Sets: Custom Global 262-d vs. Published IFV Sliding Window

### A. Custom Global Texture Baseline (`EXP-FABRICNET-GLOBAL-262D`)
- **Composition (262 Dimensions)**:
  - GLCM (96): 6 properties (`contrast`, `dissimilarity`, `homogeneity`, `energy`, `correlation`, `ASM`) across 4 pixel distances ($1, 2, 4, 8$) and 4 angles ($0^\circ, 45^\circ, 90^\circ, 135^\circ$).
  - LBP (54): Multi-scale uniform histograms across $(P=8, R=1), (P=16, R=2), (P=24, R=3)$.
  - Gabor Filter Bank (96): 4 radial frequencies ($0.05, 0.1, 0.2, 0.35$) across 8 orientations $\times$ 3 statistics (mean, std, mean-square energy).
  - Global Projections (16): Intensity moments (mean, var, std, skew, kurtosis, percentiles 10, 25, 50, 75, 90) and 1D horizontal/vertical projection statistics.
- **Empirical Results (26 Held-out Test Specimens, Split `fabricnet_splits.json`)**:
  - Random Forest: Warp MAE = 4.88, Weft MAE = 5.39 ($R^2 = 0.690 / 0.787$); 34.6% warp / 19.2% weft within factory tolerance ($\pm 2\text{ threads/cm}$).
  - XGBoost: Warp MAE = 4.83, Weft MAE = 6.60 ($R^2 = 0.702 / 0.339$); 46.2% warp / 34.6% weft within $\pm 2\text{ threads/cm}$.
  - MLP: Warp MAE = 7.11, Weft MAE = 13.54 ($R^2 = 0.566 / -0.265$).
  - Per-sample predictions serialized to: `experiments/learned_models/results/fabricnet_global_262d_predictions.csv`.

### B. Published IFV Sliding Window Baseline (`EXP-FABRICNET-IFV-SLIDING-WINDOW`)
- **Citation**: Secer & Ercan (2022/2023, MDPI Sustainability 15(21), 15197, `doi:10.3390/su152115197`).
- **Algorithm**:
  - $160 \times 160$ sliding window with stride 80 across $480 \times 640$ image ($5 \times 7 = 35$ windows per specimen).
  - 4 concentric rectangular frames of thickness 20 px per window.
  - Features per window (28): frame intensity centroids $(\bar{x}_k, \bar{y}_k)$ offset from center $(80, 80)$, radial distance $dr_k$, frame mean/std, and 1D projection variances.
  - Aggregation across 35 windows: mean and std ($28 \times 2 = 56$ features).
- **Empirical Results (Exact Same 26 Held-out Test Specimens)**:
  - Random Forest (IFV): Warp MAE = 7.41, Weft MAE = 6.76 ($R^2 = 0.449 / 0.704$); 19.2% warp / 11.5% weft within $\pm 2\text{ threads/cm}$.
  - XGBoost (IFV): Warp MAE = 6.67, Weft MAE = 6.71 ($R^2 = 0.479 / 0.686$); 38.5% warp / 23.1% weft within $\pm 2\text{ threads/cm}$.
  - MLP (IFV): Warp MAE = 8.65, Weft MAE = 11.02 ($R^2 = 0.320 / 0.165$).
  - Per-sample predictions serialized to: `experiments/learned_models/results/fabricnet_ifv_sliding_window_predictions.csv`.

### Analytical Deduction
While the published IFV representation captures local frame centroid offsets, the multi-scale global texture baseline (`EXP-FABRICNET-GLOBAL-262D`) achieves higher fidelity on FabricNET (Warp MAE 4.83 vs 6.67) because Gabor filter banks and multi-radius LBP directly capture fine harmonic periodicities across a broader spatial frequency spectrum. However, both feature sets implicitly assume a fixed optical magnification and fail under field-of-view changes.

---

## 3. Deep Segmentation & Hybrid Measurement: Synthetic Domain Boundary

### A. Synthetic Training Evaluation (`04_unet_segmentation_training.ipynb`)
- **Architecture**: `WarpWeftUNet` (1.93M parameters, 3-class segmentation: void, warp core, weft core).
- **Dataset**: 120 synthetic micro-swatches ($256 \times 256$) with exact pixel masks, Gaussian PSF blur ($\sigma=1.2$), and sensor noise ($\sigma=0.08$).
- **Held-out Test Performance**: Pixel Accuracy = 97.82%, Mean IoU = 91.81% (Warp core IoU = 96.80%, Weft core IoU = 97.48%).
- **Domain Limitation**: This checkpoint (`experiments/learned_models/checkpoints/unet_yarn_segmentation.pt`) is strictly **synthetic-domain only**. Real fabric swatches exhibit fiber hairiness, yarn twisting, specular reflections, and twill floats that are absent in synthetic swatches.

### B. Native Patch-Tiled Hybrid Pipeline (`05_hybrid_geometric_measurement.ipynb`)
- To prevent destructive downsampling artifacts, the hybrid pipeline slides $256 \times 256$ patches across the native resolution image (stride 128), accumulates class logits, takes argmax, skeletonizes yarn masks, and measures center-to-center pitch.
- **On Synthetic Swatch (`sample_plain_32x28.png`, GT: 32 warp, 28 weft)**:
  - Weft pitch $\Delta_y = 14.0\text{ px} \to T_y = 480 / 14 = 34.29\text{ picks/cm}$ (Error = 6.29).
  - Warp pitch $\Delta_x = 32.0\text{ px} \to T_x = 480 / 32 = 15.00\text{ ends/cm}$ (Float interstice ambiguity).
- **On Client Photograph (`data/samples/test.png`, Specimen 2, GT: 31 warp, 27 weft, $S_x=263.5, S_y=208.4$)**:
  - Predicted Warp: $8.50\text{ ends/cm}$ ($\Delta_x = 31.0\text{ px}$, true yarn pitch $\approx 8.5\text{ px}$).
  - Predicted Weft: $6.32\text{ picks/cm}$ ($\Delta_y = 33.0\text{ px}$, true yarn pitch $\approx 7.7\text{ px}$).
  - **Mechanistic Cause of Domain Failure**: The synthetic U-Net groups bundles of 3–4 adjacent real yarns into single core masks because real fiber hairiness bridges the interstices. Consequently, peak spacing is 4x too wide, yielding densities 4x too low ($8.5$ vs $31$, $6.3$ vs $27$).

---

## 4. Cross-Domain Transfer: Client Smartphone Benchmark (Table B)

When evaluated on the client's smartphone photograph (`data/samples/test.png`, Specimen 2 Ground Truth: Warp 31 ends/cm, Weft 27 picks/cm, factory acceptance tolerance $\pm 2.0\text{ threads/cm}$):

| Paradigm / Model | Warp Density | Weft Density | Decision Status | Factory Tolerance ($\pm 2.0$) | Root Cause / Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic (Uncalibrated FabricNET Preset)** | 54.0 ends/cm | 9.0 picks/cm | **NEEDS_REVIEW** (Accepted: None) | **REJECTED** (Warp +23, Weft -18) | 5.5x scale inflation ($1280/1200$ vs $263/208\text{ px/cm}$) + macro-stripe harmonic aliasing |
| **Deterministic (Calibrated Phone Scale)** | **32.74 ends/cm** | **28.47 picks/cm** | **ACCEPTED** | **PASS** (+1.74 warp in [29,33], +1.47 weft in [25,29]) | Calibrated spatial scale ($S_x=263.5, S_y=208.4$) on uniform ground weave |
| **FabricNET Global 262-d RF Regressor** | 52.05 ends/cm | 68.55 picks/cm | UNVALIDATED | **FAIL** (Warp +21.05, Weft +41.55) | 5x FOV disparity between microscope optics and phone camera |
| **FabricNET Published IFV RF Regressor** | 58.30 ends/cm | 64.10 picks/cm | UNVALIDATED | **FAIL** (Warp +27.30, Weft +37.10) | Severe magnification shift; invalidates fixed-window geometry |
| **Hybrid WarpWeftUNet (Patch-tiled)** | 8.50 ends/cm | 6.32 picks/cm | UNVALIDATED | **FAIL** (Warp -22.50, Weft -20.68) | Synthetic-to-real domain gap; segments fiber clusters |

---

## 5. Web Application Integration & Mode Availability Policy

The production server (`web_app/modes.py` and `web_app/server.py`) enforces strict isolation:
1. **Mode 1 (Classical Deterministic)**: **Active Production Mode (`available: true`)**.
   - Requires physical spatial calibration ($S_x, S_y$).
   - Returns explicit `decision_status` (`ACCEPTED` vs `NEEDS_REVIEW`). On divergence or low contrast, `accepted_warp_density_ends_per_cm` is set to `None`, strictly preventing false estimates from being presented as truth.
2. **Mode 2 (Learned Feature Regression)**: **Disabled in Production (`available: false`)**.
   - Justification: Feature regressors trained on FabricNET cannot transfer across optical magnifications. Enabling this mode on smartphone captures would deliver invalid numbers without warning.
3. **Mode 3 (Hybrid Segmentation)**: **Disabled in Production (`available: false`)**.
   - Justification: Synthetic-domain U-Net suffers severe segmentation failure on real smartphone fabric images. Real-domain pixel-level ground truth annotation is required prior to activation.
