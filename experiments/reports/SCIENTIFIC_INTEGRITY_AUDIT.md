# SECOND-PASS SCIENTIFIC INTEGRITY AUDIT & METROLOGY RECONCILIATION
**Repository:** Warp & Weft AI (`/home/assem-elqersh/Desktop/Warp Weft Project/`)  
**Canonical Branch:** `main` (Commit base: `8f0e7ce`)  
**Audit Timestamp:** 2026-11-19T15:31:00+02:00  
**Scope:** Forensic interrogation of FabricNET benchmark discrepancies, Bland-Altman agreement limits, client calibration provenance, physical vs digital multi-region supervision, and repository branch consolidation.

---

## 1. Executive Statement: Software Infrastructure vs Physical Metrology Certification

A rigorous scientific distinction must be maintained:
* **The Software Infrastructure is Verified:** The modular code engine (16 Python modules under `experiments/learned_models/`), the master registries (`registry.json`), the executed research notebooks (01–07), the test suite (**87 of 87 tests passing in 4.50s**), and the production web application are verified, well-typed, and backward-compatible.
* **The Physical Metrology System is NOT Yet Certified for Uncalibrated Smartphone Photography:** Measuring real-world fabric thread density from arbitrary smartphone photographs without an in-scene physical scale target or prior camera calibration remains an unsolved optical metrology problem. Any claim that the system provides automatic, calibration-free physical measurement within $\pm 2.0\text{ threads/cm}$ is scientifically invalid.

---

## 2. Forensic Reconciliation of the FabricNET Benchmark

### 2.1. The Empirical Discrepancy & Erroneous Narrative Retraction
In an earlier pre-commit audit draft, Section 4.2 claimed:
> *"fabricnet_test_benchmark.json: Demonstrates deterministic dual-engine achieving Warp MAE 1.15 threads/cm (90.8% within factory +/- 2.0) and Weft MAE 1.02 threads/cm (92.3% within factory +/- 2.0)."*

**This claim was factually incorrect and is formally retracted.** The actual contents of `experiments/learned_models/results/fabricnet_test_benchmark.json` and `results/fabricnet_benchmark.json` have been independently reproduced across all 130 FabricNET microscope specimens ($S_x=1280.0, S_y=1200.0\text{ px/cm}$):

| Evaluation Mode | Sample Size ($N$) | Warp MAE (ends/cm) | Weft MAE (picks/cm) | Warp $\% \le \pm 2.0$ | Weft $\% \le \pm 2.0$ | Joint $\% \le \pm 2.0$ | Mean Bias (Warp / Weft) | 95% Limits of Agreement (Warp) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Unfiltered Candidates** (`fabricnet_test_benchmark.json`) | 130 | **13.43** | **11.26** | **26.15%** | **27.69%** | **6.15%** | $-12.82\text{ / }-10.32$ | $[-39.53, +13.89]$ |
| **Historical Candidate Estimates** (`results/fabricnet_benchmark.json`) | 130 | **13.43** | **11.25** | **26.90%** | **27.70%** | **6.90%** | $-12.82\text{ / }-10.32$ | $[-39.53, +13.89]$ |
| **Consensus-Gated Accepted Measurements** (`results/fabricnet_benchmark.json`) | Warp: 25<br>Weft: 32 | **2.48** | **2.38** | **80.00%** | **62.50%** | N/A | $-0.96\text{ / }-1.56$ | $[-8.55, +6.63]$ |

### 2.2. Algorithmic Root-Cause of Raw Candidate Error
The underlying benchmark calculation did not change between runs. The large raw error (MAE $13.43$ warp, $11.26$ weft) across the 130 specimens stems from structural weave physics:
1. **Plain Weave ($N=50$):** Warp MAE $= 7.73$, Weft MAE $= 4.93$, with $42\%$ within $\pm 2.0$. Spatial projection and 2D FFT align relatively well with yarn pitch.
2. **Satin Weave ($N=41$):** Warp MAE $= 12.18$, Weft MAE $= 21.93$, with only $12.2\%$ of weft within $\pm 2.0$. Long yarn floats suppress periodic fundamental frequencies, causing the spectral engine to latch onto harmonic sub-multiples.
3. **Twill Weave ($N=39$):** Warp MAE $= 22.05$, Weft MAE $= 8.12$, with only $2.6\%$ of warp within $\pm 2.0$. Diagonal float patterns produce dominant diagonal spectral lobes that project falsely onto the orthogonal measurement axes.

### 2.3. Scrutiny of Agreement Statistics (Bland-Altman LoA)
* On raw unfiltered candidates, the Warp Bland-Altman mean bias is **$-12.82\text{ threads/cm}$** ($\text{SD} = 13.63$), yielding a $95\%$ Limits of Agreement span of:
  $$\text{LoA} = [-39.53, +13.89]\text{ threads/cm}$$
* This span ($\Delta = 53.42\text{ threads/cm}$) extends radically beyond the factory acceptance tolerance of $\pm 2.0\text{ threads/cm}$.
* **Metrological Conclusion:** The raw deterministic estimators cannot be trusted blindly on unclassified weave structures. The consensus decision arbiter (`decision_status`) is scientifically mandatory: when estimators diverge by $> 3.0\text{ threads/cm}$, the measurement MUST be flagged as `NEEDS_REVIEW`. On the 130 FabricNET images, the system correctly rejects $88\text{ of }130$ specimens ($67.7\%$) as `NEEDS_REVIEW`, validating only $15$ as `VALIDATED` and $27$ as `CONSISTENT_WITH_WARNING`.

---

## 3. Client Benchmark Audit & Calibration Provenance

### 3.1. Provenance of Calibration Constants ($S_x=263.5, S_y=208.4$)
In `data/client_benchmark_manifest.json` line 22, the calibration source was previously listed as `"factory_optical_graticule_1cm"`.
**This provenance attribution was inaccurate.** As documented in `docs/CLIENT_IMAGE_FAILURE_ANALYSIS.md` lines 71–77, the scale factors were derived analytically from observed pixel periods and client manual counts:
$$\text{Observed Weft Period} = 7.72\text{ px},\quad \text{Manual Weft Count} = 27\text{ picks/cm}\implies S_y = \frac{7.72}{1/27} = 208.44\text{ px/cm}$$
$$\text{Observed Warp Period} = 8.50\text{ px},\quad \text{Manual Warp Count} = 31\text{ ends/cm}\implies S_x = \frac{8.50}{1/31} = 263.50\text{ px/cm}$$

**Scientific Implications of This In-Situ Derivation:**
1. **Circularity:** Setting the scale using the ground-truth counts proves that the spatial/spectral engine accurately identifies the yarn peak periods ($8.50\text{ px}$ and $7.72\text{ px}$). However, it does **not** prove that the system can independently determine the physical scale of an uncalibrated photograph.
2. **Transferability:** If the user uploads another smartphone photo taken at a different distance or focal length, applying $S_x=263.5, S_y=208.4$ will fail immediately (as seen in the original $54 / 9$ failure where the $1280\text{ px/cm}$ microscope preset was applied).
3. **Traceability:** True metrological calibration requires an independent, traceable physical scale in the scene (such as a calibrated $1.0\text{ cm}$ glass graticule or stainless machinist scale), measured using the interactive two-point ruler tool.
4. **Correction Applied:** `data/client_benchmark_manifest.json` has been updated to explicitly label `calibration_source: "back_calculated_from_specimen_yarn_pitch_and_manual_count"` with an explicit calibration caveat.

### 3.2. Five-Region Physical Supervision vs Digital Spatial Cropping
* The client tested physical Specimen 2 using a $1.0\text{ cm}$ optical pick-glass across 5 physical locations, recording:
  - Warp: $[31, 31, 30, 31, 32]\implies \text{Mean} = 31.0\text{ ends/cm}\quad (\sigma = 0.71)$
  - Weft: $[27, 27, 26, 27, 26]\implies \text{Mean} = 26.6\text{ picks/cm}\quad (\sigma = 0.55)$
* The client uploaded **a single macro photograph** (`data/samples/test.png`, $1200\times 1600$, covering $4.55\times 7.68\text{ cm}$).
* The five ROIs evaluated in Tab 6 and in `src/fabric_analysis/specimen_workflow.py` are **digital spatial crops** ($256\times 256\text{ px}$) extracted from the quadrants of this single image.
* **Scientific Distinction:** Evaluating 5 digital crops across a single full-swatch photograph demonstrates spatial uniformity and reduces local yarn crimp noise ($100\%$ pass within factory $\pm 2.0$, yielding Mean Warp $31.86$, Weft $27.60$). However, because separate macro close-ups of each physical pick-glass placement were not provided (`image_path: null`), this constitutes **specimen-level physical supervision evaluated across digital spatial quadrant ROIs**, not true independent multi-image ASTM D3775 physical validation.

---

## 4. Checkpoint Policy & Repository Invariants

### 4.1. Tracked U-Net Checkpoint Audit
* **File:** `experiments/learned_models/checkpoints/unet_yarn_segmentation.pt` ($7.39\text{ MB}$, SHA-256 `d68a7479...`).
* **Origin:** Trained on procedurally generated synthetic micro-swatches in `04_unet_segmentation_training.ipynb`.
* **Empirical Limitation:** Evaluated on real smartphone capture `test.png` in `06_comprehensive_side_by_side_comparison.ipynb`. Predicted Warp $8.50$ and Weft $6.32\text{ threads/cm}$ (severe undercounting due to fiber fuzz bridging adjacent yarns).
* **Repository Decision:** Already tracked in git history on `main` (commit `d68a747`). Preserved strictly as a reference baseline for synthetic experiments. Its production deployment flag in `src/fabric_analysis/pipeline.py` is permanently disabled (`available: false`). Updated `experiments/learned_models/checkpoints/inventory.json` to state this explicitly.

### 4.2. Pretrained Transformer Weights & Dataset Protection
* `.gitignore` was updated with:
  ```gitignore
  *.safetensors
  docs/Papers/
  docs/Papers/*.pdf
  ```
* Verified with `git check-ignore -v`:
  - `experiments/models/checkpoints/segformer_b0/model.safetensors` ($14.34\text{ MB}$) $\implies$ **IGNORED**.
  - `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth` ($84.20\text{ MB}$) $\implies$ **IGNORED**.
  - `experiments/data_acquisition/downloads/NithinAruswamy_TextileResearchDataset.zip` ($20.72\text{ MB}$) $\implies$ **IGNORED**.
  - `experiments/data_acquisition/downloads/harvard_microtexture/` ($42.5\text{ MB}$) $\implies$ **IGNORED**.
  - `docs/Papers/*.pdf` ($8.89\text{ MB}$) $\implies$ **IGNORED**.

---

## 5. Branch Architecture Consolidation

In accordance with user directives, all work is consolidated strictly onto the single canonical branch:
* **Current Branch:** `main` (tracking `origin/main` at `8f0e7ce`).
* **Deleted Feature Branches:** `feat/reconciled-research-validation` and `feat/comprehensive-textile-model-research` (both were identical pointers to `8f0e7ce` and have been deleted).
* **Branch Policy:** Zero multi-branch divergence. All subsequent infrastructure improvements and releases occur directly on `main`.

---

## 6. Scientific Summary & Release Criteria

| Finding / Item | Previous (Unverified) Claim | Verified Scientific Reality | Release Impact |
| :--- | :--- | :--- | :--- |
| **FabricNET Benchmark** | Warp MAE 1.15, Weft MAE 1.02 ($90.8\% \le \pm 2$) | Raw Warp MAE 13.43, Weft MAE 11.26 ($26.1\% \le \pm 2$); Consensus-gated accepted Warp MAE 2.48, Weft MAE 2.38 ($80.0\% \le \pm 2$, $19.2\%$ coverage) | Retracted erroneous claims; published verified paired statistics. |
| **Bland-Altman LoA** | Mean $+0.04$, LoA $[-3.12, +3.20]$ | Raw Mean $-12.82$, LoA $[-39.53, +13.89]$; Consensus-gated Mean $-0.96$, LoA $[-8.55, +6.63]$ | Clarified that unfiltered estimators extend far beyond factory tolerance on complex weaves. |
| **Client Calibration** | "factory_optical_graticule_1cm" | Back-calculated from observed yarn period and manual count | Rectified manifest to state scale is an in-situ derivation, not external graticule. |
| **Client 5-Region Supervision** | Full ASTM D3775 physical 5-region validation | Specimen-level physical supervision evaluated across 5 digital spatial quadrant ROIs | Qualified claims in manifest and reports; marked `supervision_level: specimen_only`. |
| **Tracked U-Net Checkpoint** | Candidate for Mode 3 production | Synthetic-domain reference only (`available: false`); fails on real smartphone captures | Documented synthetic-only boundary in checkpoint inventory and reports. |
| **Repository Branching** | 3 diverged feature branches | 1 single canonical branch (`main`) | Unified workspace on `main`; deleted obsolete feature branches. |
