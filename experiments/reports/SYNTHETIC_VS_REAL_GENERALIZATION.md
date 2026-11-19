# SYNTHETIC VS. REAL GENERALIZATION & DOMAIN GAP REPORT
**Document Reference:** `experiments/reports/SYNTHETIC_VS_REAL_GENERALIZATION.md`  
**Execution Phase:** Phase 5 — Synthetic-to-Real Generalization Diagnostics  
**Execution Context:** Repository Canonical Branch `main`  
**Date:** 2026-11-19  

---

## 1. Executive Summary

This report investigates the domain transfer gap between neural segmentation models trained on procedurally generated synthetic textile swatches and their real-world metrological accuracy when evaluated on:
1. Synthetic microscopy swatches (`sample_plain_32x28.png`).
2. Real optical transmission microscopy (FabricNET $N=130$).
3. Real factory smartphone photography (`client_specimen_2_crop.png`).

The empirical results reveal a severe, catastrophic failure mode: despite achieving $97.82\%$ pixel accuracy and $0.9181$ mIoU on synthetic test data, `WarpWeftUNet` experiences a $\sim 4\times$ density undercount on real smartphone fabric (predicting $8.50\text{ ends/cm}$ vs. ground truth $31.0\text{ ends/cm}$, error $-22.50\text{ ends/cm}$).

---

## 2. Quantitative Empirical Benchmark

The end-to-end hybrid metrology pipeline (`HybridMetrologyRunner`: U-Net segmentation $\to$ morphological skeletonization $\to$ 1D projection pitch extraction $\to$ scale division) was benchmarked across domains:

| Specimen Identifier | Domain / Source | True Warp (ends/cm) | Pred Warp (ends/cm) | Warp Error | True Weft (picks/cm) | Pred Weft (picks/cm) | Weft Error | Decision Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `sample_plain_32x28.png` | Synthetic Microscopy | 32.0 | 15.00 | **-17.00** | 28.0 | 34.29 | **+6.29** | `ACCEPTED` |
| `client_specimen_2_crop.png` | Real Smartphone Macro | 31.0 | 8.50 | **-22.50** | 27.0 | 6.32 | **-20.68** | `ACCEPTED` (Invalid) |
| `client_specimen_2_crop.png` | **Deterministic (Calibrated)** | 31.0 | **32.74** | **+1.74** | 27.0 | **28.47** | **+1.47** | **`ACCEPTED` (Valid)** |

---

## 3. Mathematical & Morphological Failure Diagnosis

### 3.1 The Filament Clumping Phenomenon
When synthetic segmentation masks are compared against real smartphone imagery, the root cause of the $-22.50\text{ ends/cm}$ error becomes mathematically transparent:
1. **The Ground Truth Geometry:**
   - Physical scale: $S_x = 263.5\text{ px/cm}$, $S_y = 208.4\text{ px/cm}$.
   - True physical pitch in image coordinates:
     $$p_{\text{warp, true}} = \frac{S_x}{D_{\text{warp}}} = \frac{263.5}{31.0} \approx 8.50\text{ pixels}$$
     $$p_{\text{weft, true}} = \frac{S_y}{D_{\text{weft}}} = \frac{208.4}{27.0} \approx 7.72\text{ pixels}$$
2. **The Empirical Neural Output:**
   - Observed segmented yarn spacing:
     $$\Delta x_{\text{unet}} = 31.0\text{ pixels}, \quad \Delta y_{\text{unet}} = 33.0\text{ pixels}$$
   - Resulting measured density:
     $$\hat{D}_{\text{warp}} = \frac{263.5}{31.0} = 8.50\text{ ends/cm}$$
     $$\hat{D}_{\text{weft}} = \frac{208.4}{33.0} = 6.32\text{ picks/cm}$$
3. **The Multi-Yarn Clumping Ratio:**
   $$\text{Ratio}_{\text{warp}} = \frac{31.0\text{ px}}{8.50\text{ px}} = 3.65 \approx 4\text{ yarns per segment}$$
   $$\text{Ratio}_{\text{weft}} = \frac{33.0\text{ px}}{7.72\text{ px}} = 4.27 \approx 4\text{ yarns per segment}$$

The synthetic-trained network does not separate adjacent individual yarn filaments. Instead, it segments macroscopic bundles of **3 to 4 yarns** as single unified entities.

### 3.2 Visual & Physical Domain Mismatch Vectors
The failure stems from four distinct physical differences between procedural synthetic renderings and real textile captures:

1. **Fiber Fuzz (Hairy Yarns):**
   - In synthetic rendering, yarns have smooth, analytically defined circular cross-sections with sharp interstice voids.
   - Real spun staple yarns (e.g. combed cotton) exhibit protruding surface micro-fibers (fuzz) that bridge adjacent yarns across the interstice, visually merging them into continuous bands.
2. **Dynamic Range & Shadow Non-Linearity:**
   - Real oblique smartphone lighting creates cast shadows on one side of each yarn crown while illuminating the other.
   - The U-Net mistakes the dark shadow between 4-yarn repeat groups for the only true interstice, ignoring the shallower intra-group valleys.
3. **Harmonic Aliasing in Synthetic Benchmarks:**
   - Even on `sample_plain_32x28.png`, the detected warp spacing was $32.0\text{ px}$ instead of the true $16.0\text{ px}$, indicating that the peak prominence threshold ($0.1$) skipped every alternating yarn peak due to subtle even/odd float illumination differences.

---

## 4. Why the Deterministic Engine Generalizes Across Domains

The classical deterministic engine achieves $+1.74\text{ ends/cm}$ and $+1.47\text{ picks/cm}$ accuracy on the exact same smartphone swatch because of fundamental mathematical differences:

| Property | Deep Segmentation (U-Net) | Deterministic Dual-Engine (2D FFT / Autocorr) |
| :--- | :--- | :--- |
| **Field of View Integration** | Local receptive field ($3 \times 3$ convs, effective RF $\sim 64\text{ px}$) | Global spectral integration across $1024 \times 1024$ pixels ($10^6$ pixels) |
| **Sensitivity to Fiber Fuzz** | **High:** Fuzz bridges individual pixel boundaries, erasing inter-yarn void class | **Extremely Low:** Random micro-fibers act as high-frequency diffuse noise, while the fundamental periodic carrier frequency remains dominant in Fourier space |
| **Dependence on Training Data** | **Total:** Fails if real texture distribution differs from synthetic generator | **Zero:** Operates strictly on physical spatial periodicity and harmonic invariance |
| **Scale Coupling** | Implicit unless explicitly calibrated downstream | Directly coupled to physical scale via $D = f_0 \cdot S$ |

---

## 5. Engineering Invariants & Future Mitigation Pathways

1. **Synthetic Models Prohibited from Autonomous Production Gating:**
   Under no circumstances may a synthetic-pretrained neural network autonomously output accepted density figures for real client imagery without deterministic consensus gating.
2. **Domain Adaptation Requirements:**
   To make learned segmentation viable on real fabrics, future iterations must:
   - Introduce Perlin-noise fiber fuzz and directional micro-shading into `experiments/learned_models/synthetic_generator.py`.
   - Apply weak-supervision pseudo-labeling using the gated deterministic engine on high-confidence real swatches (`decision_status == "ACCEPTED"`).
   - Use contrastive domain alignment (e.g., DINOv2 self-supervised patch tokens) to align synthetic and real feature manifolds before mask decoding.
