# LABEL QUALITY & ANNOTATION PIPELINE REPORT
**Document Reference:** `experiments/reports/LABEL_QUALITY_REPORT.md`  
**Execution Phase:** Phase 2 — Label Quality and Annotation Pipeline  
**Execution Context:** Repository Canonical Branch `main`  
**Date:** 2026-11-19  

---

## 1. Executive Summary

This report establishes the annotation taxonomy, per-dataset coverage, quality grades, conversion pipelines, and weak-supervision strategies across all datasets registered in `experiments/data/unified_manifest.json`.

Supervised computer vision algorithms for textile thread counting require fine-grained spatial supervision (yarn segmentation masks, instance boundaries, centerlines). However, public and commercial textile datasets predominantly offer global specimen-level scalar density labels (ends/cm, picks/cm) or high-level classification tags without spatial coordinate grounding. This discrepancy necessitates a formal annotation taxonomy and mathematical transformation pipelines to bridge global labels, synthetic annotations, and pseudo-labeled real fabric imagery.

---

## 2. Eight-Tier Textile Annotation Taxonomy

To eliminate ambiguity between semantic segmentation, instance segmentation, object detection, and metrological density estimation, the project defines an 8-tier annotation hierarchy:

| Tier | Annotation Level | Mathematical Format | Metrological Purpose | Required For |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Specimen-Level Density** | Scalars $(D_{\text{warp}}, D_{\text{weft}}) \in \mathbb{R}^2$ in threads/cm | Ground-truth reference for macroscopic density evaluation | Global feature regression, benchmark verification |
| **Tier 2** | **ROI-Level Density** | Bounding box $(x_1, y_1, x_2, y_2)$ + local $(D_{\text{warp}}, D_{\text{weft}})$ | Localized validation across crimp and tension variations | Multi-crop spatial variance analysis |
| **Tier 3** | **Yarn Centerlines** | 1D polylines $P_i = \{(x_k, y_k)\}_{k=1}^{K_i}$ per yarn | Direct physical pitch calculation without boundary ambiguity | Skeleton-based pitch extraction, peak tracking |
| **Tier 4** | **Yarn Instance Masks** | Polygonal masks $M_i \in \{0, 1\}^{H \times W}$, label $\in \{\text{warp}, \text{weft}\}$ | Separation of individual interlacing yarns | Mask R-CNN, SOLOv2, instance segmentation |
| **Tier 5** | **Binary Semantic Masks** | Tensor $M \in \{0, 1, 2\}^{H \times W}$ (0: background/gap, 1: warp, 2: weft) | Directional orientation and structural segmentation | U-Net, SegFormer, DeepLabV3+ |
| **Tier 6** | **Yarn Direction Labels** | Dense angle map $\theta(x, y) \in [-\pi/2, \pi/2]$ or vector fields | Local fiber orientation and skew rectification | Radon transform verification, orientation validation |
| **Tier 7** | **Calibration Markers** | Pixel distance $L_{\text{px}}$ between known points + physical length $L_{\text{cm}}$ | Conversion factor $S \in \mathbb{R}^+$ (px/cm) | Physical metrology, density conversion |
| **Tier 8** | **Image Quality Annotations** | Quality vectors: blur (Laplacian variance), contrast (Michelson), SNR | Input reliability gate to reject non-measurable imagery | Decision gating, quality rejection thresholds |

---

## 3. Dataset-by-Dataset Annotation Audit

Every registered dataset in `experiments/data/unified_manifest.json` (328 total records) was audited against this 8-tier hierarchy.

### 3.1 FabricNET (130 Specimens)
- **Source:** Secer & Ercan (2023), Pamukkale University.
- **Image Specifications:** $1280 \times 1200$ pixels, optical transmission microscope, fixed magnification ($S_x = 1280\text{ px/cm}$, $S_y = 1200\text{ px/cm}$).
- **Available Annotation Tiers:**
  - Tier 1 (Specimen-Level Density): Complete (130/130). Warp and weft threads/cm verified against manual counting glass ground truth.
  - Weave Category: Complete (130/130: Plain 61, Twill 36, Satin 33).
- **Missing Annotation Tiers:**
  - Tiers 2, 3, 4, 5, 6, 7, 8: Absent. No pixel coordinates, no yarn boundaries, no centerline vectors.
- **Quality Grade:** **Grade A (Global Physical Ground Truth) / Grade F (Spatial Coordinates)**.
- **Supervision Limitation:** Direct fully-supervised pixel segmentation cannot be trained directly on FabricNET without synthetic pretraining or deterministic pseudo-labeling.

### 3.2 Synthetic Micro Swatches (3 Primary Swatches + Programmatic Generator)
- **Source:** Internal procedural yarn rendering engine (`experiments/learned_models/synthetic_generator.py`).
- **Image Specifications:** $512 \times 512$ pixels, procedural sinusoidal yarn profiles, exact yarn diameters, packing densities, and Gaussian noise.
- **Available Annotation Tiers:**
  - Tier 1 (Specimen-Level Density): Complete and exact.
  - Tier 3 (Yarn Centerlines): Exact integer pixel coordinates generated during procedural rendering.
  - Tier 5 (Binary/Ternary Semantic Masks): Exact ground-truth masks generated pixel-by-pixel (0: gap, 1: warp, 2: weft).
  - Tier 7 (Calibration Markers): Mathematically known pixel pitch.
- **Missing Annotation Tiers:**
  - Real fiber fuzz, smartphone camera sensor noise, non-planar fabric wrinkles, variable illumination shading.
- **Quality Grade:** **Grade A+ (Synthetic Ground Truth) / Domain Gap: High**.

### 3.3 Client Reference Specimens (5 Crops, 1 Physical Sample)
- **Source:** Real factory client smartphone photograph of dyed cotton poplin.
- **Image Specifications:** $4000 \times 3000$ macro capture, segmented into 5 spatial ROI crops ($1024 \times 1024$).
- **Available Annotation Tiers:**
  - Tier 1 (Specimen-Level Density): 31.0 ends/cm (warp), 27.0 picks/cm (weft) from factory count glass.
  - Tier 2 (ROI-Level Density): 5 spatial quadrant crops (specimen-only supervision; localized crimp variance unmeasured).
  - Tier 7 (Calibration Markers): Back-calculated calibration ($S_x = 263.5\text{ px/cm}$, $S_y = 208.4\text{ px/cm}$) from physical count and empirical pitch.
- **Missing Annotation Tiers:**
  - Tiers 3, 4, 5, 6: Absent. No manually annotated yarn centerlines or segmentation boundaries.
- **Quality Grade:** **Grade B (Specimen-Level Ground Truth) / Caveat: Back-Calculated Scale**.

### 3.4 Harvard Microtexture Dataset (190 Images)
- **Source:** Harvard Dataverse texture classification repository.
- **Image Specifications:** $512 \times 512$ variable textile scans.
- **Available Annotation Tiers:**
  - Texture Category Labels: Complete (190/190).
- **Missing Annotation Tiers:**
  - Tiers 1 through 8: Entirely absent. No thread count, no physical scale, no yarn boundaries.
- **Quality Grade:** **Grade D (Metrologically Unusable)**.
- **Supervision Decision:** Excluded from quantitative density benchmarking; usable only for self-supervised pretraining (DINOv2 feature validation) or general texture classification.

---

## 4. Annotation Conversion Pipeline

To convert spatial annotations into standard formats suitable for training and evaluation, `experiments/learned_models/annotations.py` implements mathematical transformation functions:

### 4.1 Polygon Vector to Raster Semantic Mask
For datasets with polygonal vector annotations (COCO format):
$$\text{Mask}(y, x) = \begin{cases} 1 & \text{if } (x, y) \in \mathcal{P}_{\text{warp}} \\ 2 & \text{if } (x, y) \in \mathcal{P}_{\text{weft}} \\ 0 & \text{otherwise} \end{cases}$$
Implemented using `cv2.fillPoly` with anti-aliasing disabled to preserve crisp boundary coordinates.

### 4.2 Morphological Skeletonization for Centerline Extraction
Centerlines are extracted from binary yarn masks using iterative morphological thinning:
$$S_k = (M \ominus k B) \setminus ((M \ominus k B) \circ B)$$
$$S(M) = \bigcup_{k=0}^{K} S_k$$
where $B$ is a $3 \times 3$ cross structuring element, $\ominus$ denotes erosion, and $\circ$ denotes morphological opening. This guarantees single-pixel-wide topological medial axes without disconnecting yarn segments.

### 4.3 1D Centerline Projection and Pitch Derivation
To derive physical pitch $\hat{p}$ from the skeletonized medial axis:
- For warp yarns (vertical orientation): Project skeleton along column axis:
  $$P_{\text{warp}}(x) = \sum_{y=0}^{H-1} S(y, x)$$
- For weft yarns (horizontal orientation): Project skeleton along row axis:
  $$P_{\text{weft}}(y) = \sum_{x=0}^{W-1} S(y, x)$$
- Identify local maxima $x_1, x_2, \dots, x_N$ using prominence-based peak detection (`scipy.signal.find_peaks` with prominence $\ge 0.1 \cdot \max(P)$).
- Calculate spacing vector $\Delta x_i = x_{i+1} - x_i$.
- Compute median spatial pitch:
  $$\hat{p} = \text{median}(\{\Delta x_i\}_{i=1}^{N-1})$$
- Density in threads/cm is:
  $$D = \frac{S}{\hat{p}}$$
  where $S$ is physical scale in px/cm.

### 4.4 Bounding Box to Gaussian Density Map
For object detection annotations where bounding boxes are provided per yarn:
$$D_{\text{map}}(x, y) = \sum_{i=1}^{M} \frac{1}{2\pi \sigma^2} \exp\left(-\frac{(x - c_{x,i})^2 + (y - c_{y,i})^2}{2\sigma^2}\right)$$
where $(c_{x,i}, c_{y,i})$ is the bounding box centroid and $\sigma = 4.0\text{ px}$.

---

## 5. Weak Supervision & Pseudo-Labeling Strategy

To overcome the lack of ground-truth yarn segmentations in real fabric imagery (FabricNET and client captures), a deterministic-to-neural weak supervision pipeline is established:

```
[Real Microscope / Smartphone Fabric Image]
                     │
                     ▼
  [Deterministic Consensus Dual-Engine]
  - 2D FFT Spectral Peak Tracking
  - 1D Autocorrelation & Spatial Projections
  - Gabor Directional Filtering
                     │
                     ├──────── Consensus Check Failed ───────► [REJECT / MANUAL ANNOTATION]
                     │         (|D_spectral - D_spatial| > 2.0)
                     ▼
        Consensus Accepted (|ΔD| ≤ 2.0)
                     │
                     ▼
  [Spatial Bandpass Phase-Congruency Filtering]
  - Extract dominant frequency band: [f0 - Δf, f0 + Δf]
  - Compute localized oriented Hilbert analytic signal
  - Trace zero-crossings / peak ridge lines
                     │
                     ▼
  [Morphological Candidate Centerlines & Masks]
  - Medial axis centerline estimation
  - Dilation by estimated yarn radius r = p / 2
                     │
                     ▼
  [Confidence-Weighted Pseudo-Label]
  - Assign sample loss weight w = 1.0 - (|D_spectral - D_spatial| / 2.0)
  - Train segmentation model with soft-boundary loss
```

### 5.1 Gating Criterion for Pseudo-Labels
A sample is accepted for pseudo-label generation if and only if:
1. Deterministic status is `ACCEPTED` (`decision_status == "ACCEPTED"`).
2. Spectral vs spatial density discrepancy satisfies $|\hat{D}_{\text{spectral}} - \hat{D}_{\text{spatial}}| \le 1.5\text{ threads/cm}$.
3. Spectral peak prominence ratio satisfies $P_{\text{prominence}} \ge 3.0$ over local noise floor.
4. Blur metric (Laplacian variance) exceeds 100.0.

On the 130-image FabricNET dataset, this gating criterion accepts 25 high-confidence plain weave specimens for high-purity pseudo-labeling, rejecting satin and twill specimens whose harmonic float interference would corrupt neural training targets.

---

## 6. Synthetic Data Augmentation Strategy to Bridge Real Gaps

Given that real manual pixel annotations for thousands of yarns are economically prohibitive, procedural synthetic generation (`experiments/learned_models/synthetic_generator.py`) serves as the foundational pretraining engine:

1. **Procedural Weave Generation:**
   - Plain $1/1$, Twill $2/1$, Twill $2/2$, Satin $4/1$, Satin $5/1$.
   - Randomized yarn densities: Warp $15 - 65\text{ ends/cm}$, Weft $12 - 55\text{ picks/cm}$.
   - Randomized yarn diameters: $d = \frac{p}{\text{packing\_factor}}$, with packing factor $\in [0.70, 0.95]$.
2. **Photometric Realism Layer:**
   - Fiber Fuzz: Perlin noise texture blended along yarn boundaries.
   - Non-uniform lighting: 2D quadratic shading gradient simulating smartphone flash/ambient vignetting.
   - Micro-twist: Helical brightness modulation along yarn longitudinal axis simulating multi-filament yarn twist.
3. **Sensor Simulation:**
   - Gaussian sensor readout noise ($\sigma_n \in [0.01, 0.05]$).
   - Defocus blur (Gaussian kernel $\sigma_b \in [0.5, 2.0]$).
   - JPEG compression artifacts ($Q \in [70, 95]$).

---

## 7. Conclusions and Mandatory Downstream Constraints

1. **No Spatial Claims on FabricNET:** FabricNET must strictly be treated as a Tier 1 (specimen-level) dataset. It cannot validate pixel-level segmentation accuracy.
2. **Synthetic Pretraining Mandate:** Deep segmentation networks (U-Net, SegFormer) must be pretrained on procedurally generated synthetic swatches where ground-truth masks are mathematically exact.
3. **Decoupled Architecture:** Segmentation networks must never output a direct density scalar. They must strictly output yarn centerlines or segmentation masks. Density must be computed downstream via deterministic physical pitch extraction divided by calibrated physical scale ($D = S / \hat{p}$).
