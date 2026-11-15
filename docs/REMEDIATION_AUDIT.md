# Warp & Weft AI — Engineering Remediation Audit & Root-Cause Analysis

## 1. Executive Summary
This audit provides a comprehensive investigation of the codebase, notebooks, web application, physical dataset benchmarks, and documentation of the Warp & Weft AI project. Every defect listed in the Master Engineering Remediation Prompt has been verified directly against source code and raw data files.

---

## 2. Repository Inventory & Inspection Manifest

### 2.1. Complete Repository File Inventory

| Path | File Type | Size | Status | Primary Purpose / Role |
| :--- | :--- | :--- | :--- | :--- |
| `README.md` | Markdown | 45.8 KB | Inspected (100%) | Central project memory, Provenance Ledger, architecture specs |
| `data/README.md` | Markdown | 38.1 KB | Inspected (100%) | Multi-modal dataset specifications, calibration matrix, taxonomy |
| `web_app/engine.py` | Python | 19.3 KB | Inspected (100%) | Production dual-engine core (2D FFT, 1D projection, skew, fusion) |
| `web_app/server.py` | Python | 10.8 KB | Inspected (100%) | Standalone HTTP server, REST API endpoints, preset router |
| `web_app/index.html` | HTML/JS/CSS | 63.7 KB | Inspected (100%) | Web frontend UI, dual-language EN/AR, mobile layout, help toggles |
| `notebooks/01_optical_and_spectral_sandbox.ipynb` | Jupyter Notebook | 18.2 KB | Inspected (100%) | Synthetic 2D FFT & 1D projection sandbox (10 cells) |
| `notebooks/02_skew_rectification_engine.ipynb` | Jupyter Notebook | 24.5 KB | Inspected (100%) | Polar Radon skew detection & affine rectification (9 cells) |
| `notebooks/03_end_to_end_thread_counter.ipynb` | Jupyter Notebook | 32.1 KB | Inspected (100%) | End-to-end synthetic pipeline for 1.0 cm² analysis (11 cells) |
| `notebooks/04_real_fabric_benchmark.ipynb` | Jupyter Notebook | 28.7 KB | Inspected (100%) | Real physical microscopy benchmark on FabricNET (8 cells) |
| `notebooks/05_web_app_interface.ipynb` | Jupyter Notebook | 14.9 KB | Inspected (100%) | Web application verification & test suite (11 cells) |
| `data/fabricnet/FabricNet_parameters.xlsx` | Excel Spreadsheet | 13.4 KB | Inspected (100%) | Ground-truth metadata for 130 samples (Warp, Weft, GSM, Texture) |
| `data/fabricnet/W001.jpg` - `W130.jpg` | 130 JPEG images | ~13.3 MB | Inspected (100%) | Physical microscopy images ($640 \times 480$ px, $5 \times 4$ mm FOV) |
| `data/synthetic/macro_swatch_skewed_12deg.png` | PNG image | 453.6 KB | Inspected (100%) | Synthetic test swatch ($800 \times 800$ px, $+12^\circ$ tilt) |
| `data/synthetic/sample_plain_32x28.png` | PNG image | 132.7 KB | Inspected (100%) | Synthetic test swatch ($400 \times 400$ px, $0^\circ$ tilt) |
| `data/synthetic/sample_skewed_15deg.png` | PNG image | 116.7 KB | Inspected (100%) | Synthetic test swatch ($400 \times 400$ px, $+15^\circ$ tilt) |
| `results/fabricnet_benchmark.json` | JSON | 1.4 KB | Inspected (100%) | Recorded benchmark output for W012, W017, W001, W067 |
| `results/output.json` | JSON | 1.1 KB | Inspected (100%) | Recorded end-to-end production verification metrics |
| `results/output.txt` | Text | 767 B | Inspected (100%) | Raw benchmark execution log |
| `results/output_skew.json` | JSON | 477 B | Inspected (100%) | Skew engine metrics |
| `results/output_skew.txt` | Text | 238 B | Inspected (100%) | Skew engine text log |
| `results/web_app_verification.json` | JSON | 4.7 KB | Inspected (100%) | Web app test verification records |
| `reports/warp_weft_report_en.tex` | LaTeX Source | 18.5 KB | Inspected (100%) | English 7-page technical demo report source |
| `reports/warp_weft_report_en.pdf` | PDF Document | 20.1 MB | Inspected (100%) | Compiled English technical report |
| `reports/warp_weft_report_ar.tex` | LaTeX Source | 26.0 KB | Inspected (100%) | Arabic 8-page technical demo report source |
| `reports/warp_weft_report_ar.fodt` | Flat XML ODF | 50.6 KB | Inspected (100%) | Arabic technical report LibreOffice source |
| `reports/warp_weft_report_ar.pdf` | PDF Document | 1.86 MB | Inspected (100%) | Compiled Arabic technical report |
| `.gitignore` | Git Config | 1.85 KB | Inspected (100%) | Tracking rules, asset exclusion boundaries |

### 2.2. Dependency Inventory
* **Standard Python Runtime (`/usr/bin/python3`):**
  * `numpy`: 2.5.2 (Available)
  * `pillow`: 10.2.0 (Available)
  * `requests`: 2.31.0 (Available)
* **Full Scientific Anaconda Runtime (`/home/assem-elqersh/anaconda3/bin/python`):**
  * `torch`: 2.6.0+cu126 (Available)
  * `torchvision`: 0.21.0+cu126 (Available)
  * `cv2` (opencv-python): 4.11.0 (Available)
  * `scipy`: 1.15.2 (Available)
  * `matplotlib`: 3.10.1 (Available)
  * `pandas`: 2.2.3 (Available)
  * `openpyxl`: 3.1.5 (Available)
  * `tabulate`: 0.9.0 (Available)
* **Web Serving & Architecture:**
  * Zero external framework requirement: pure standard library (`http.server`, `socketserver`, `json`, `base64`, `urllib`).

### 2.3. Test Inventory
* **Existing Automated Tests:** Zero standalone test files exist (`tests/` directory did not exist; `.gitignore` was set to ignore `test_*.py`).
* **Existing Verification Scripts:** Embedded inside Jupyter notebooks (`notebooks/05_web_app_interface.ipynb`), which executed ad-hoc HTTP requests against local port 8080.
* **Finding:** Complete absence of automated regression unit tests.

### 2.4. Missing Asset Inventory
* All 130 FabricNET images (`W001.jpg` to `W130.jpg`) exist locally in `data/fabricnet/`.
* The `.gitignore` file contains `data/fabricnet/*.jpg`, which prevented these images from being committed to GitHub. This explains why an external git clone lacked the image files.
* Ground-truth Excel `FabricNet_parameters.xlsx` is tracked (`!data/fabricnet/FabricNet_parameters.xlsx`).
* User Smartphone Image: Documented as $1200 \times 1600$ px with reproduced metrics (54.3169 Warp / 8.5803 Weft) in the prompt. While the test metrics and behavior are fully documented, the raw source photo was not permanently saved to disk. A synthetic fixture matching this exact failure mode (strong surface fuzz / illumination gradients confusing FFT harmonic detection) must be constructed for regression verification.

---

## 3. Confirmed Implementation Defect Register

### Defect 2.1 — FabricNET Benchmark Contains Hardcoded Validation Values
* **Severity:** Critical
* **Affected Files:** `notebooks/04_real_fabric_benchmark.ipynb` (Cell 7), `results/fabricnet_benchmark.json`, `results/output.txt`, `README.md` (Table 8.5).
* **Root Cause:**
  In Cell 4 of Notebook 04, the projection engine computed:
  ```python
  proj_nx = float(round(len(warp_peaks) / fov_w_cm, 1))  # 38.0
  proj_ny = float(round(len(weft_peaks) / fov_h_cm, 1))  # 35.0
  ```
  Ground truth for W012 is Warp=38, Weft=33. The true measurement error was $\Delta_{\text{warp}} = 0.0, \Delta_{\text{weft}} = 2.0$.
  However, in Cell 7, the code persisted:
  ```python
  "validated_warp": 38,
  "delta_warp": 0.0,
  "validated_weft": 33,
  "delta_weft": 0.5
  ```
  And in `results/output.txt`: `Sample W012 (Plain): GT Warp=38, Weft=33 | Measured Warp=38.0, Weft=32.5 | Exact Delta=0.0 ends/cm`.
  The values 38, 33, 0.0, 0.5, and 32.5 were hardcoded literals not derived from the algorithmic execution.
* **Impact:** Manufactured validation results; corrupted benchmark integrity; impossible to measure actual algorithmic progress.

### Defect 2.2 — Anisotropic Pixel Scale Ignored (Square Pixel Assumption)
* **Severity:** Critical
* **Affected Files:** `web_app/engine.py` (`run_complete_fabric_analysis()`, `compute_1d_projection_density()`), `web_app/server.py`, `notebooks/04_real_fabric_benchmark.ipynb`.
* **Root Cause:**
  The engine accepted a single scalar `pixels_per_cm=400.0` or `1280.0` and computed:
  ```python
  crop_w_cm = cW_px / pixels_per_cm
  crop_h_cm = cH_px / pixels_per_cm
  ```
  FabricNET images are $640 \times 480$ px covering $5.0 \times 4.0$ mm.
  $S_x = 640 / 0.5 = 1280.0\text{ px/cm}$, but $S_y = 480 / 0.4 = 1200.0\text{ px/cm}$ ($6.67\%$ difference).
  Applying $1280.0\text{ px/cm}$ to the vertical axis scaled vertical dimensions to $0.4 / (1200/1280) = 0.375\text{ cm}$, introducing a systematic $6.67\%$ error in weft density calculations. Furthermore, affine rotation in pixel coordinates on anisotropic pixels causes physical angular distortion.
* **Impact:** Inaccurate physical FOV, distorted density conversions, and non-metric rotation.

### Defect 2.3 — ROI Selection Silently Accepts Insufficient Physical Coverage
* **Severity:** High
* **Affected Files:** `web_app/engine.py` (lines 368-382).
* **Root Cause:**
  ```python
  roi_side_px = int(pixels_per_cm * 1.0)
  crop_w = min(orig_w, roi_side_px)
  crop_h = min(orig_h, roi_side_px)
  ```
  For an image smaller than $1.0\text{ cm}$ (e.g. FabricNET $640 \times 480$ px at $1280 \times 1200$ px/cm, where $1.0\text{ cm}$ requires $1280 \times 1200$ px), the crop takes the entire image ($640 \times 480$ px, which is only $0.5 \times 0.4$ cm) and proceeds without alerting the user that the requested $1.0\text{ cm}^2$ ROI was physically unavailable.
* **Impact:** User is led to believe $1.0\text{ cm}$ was analyzed when only a sub-centimeter fragment was measured, inflating the effect of boundary quantization.

### Defect 2.4 — Skew Detected but Never Rectified in Real Benchmark
* **Severity:** Critical
* **Affected Files:** `notebooks/04_real_fabric_benchmark.ipynb` (Cell 3).
* **Root Cause:**
  Cell 3 computes:
  ```python
  detected_skew = float(angles[np.argmax(energies)])
  ```
  However, it never rotates `enhanced` by `-detected_skew` before proceeding to 2D FFT and 1D projections. Projections and 2D FFT were computed on the tilted raw image.
* **Impact:** Tilted yarns wash out projection contrast and shift spectral peaks away from the Fourier axes.

### Defect 2.5 — 2D FFT Assumes Strongest Axial Peak is Yarn Fundamental
* **Severity:** Critical
* **Affected Files:** `web_app/engine.py` (`compute_2d_fft_density()`, `parabolic_sub_bin_interpolation()`), `notebooks/04_real_fabric_benchmark.ipynb`.
* **Root Cause:**
  ```python
  slice_x = mag_crop[ccrow, :]
  k_x, spnr_x = parabolic_sub_bin_interpolation(slice_x, cccol, search_offset=4)
  ```
  The algorithm takes a 1D slice along the center row/column and calls `argmax` beyond bin 4. It does not perform 2D peak-pair verification, harmonic grouping, low-frequency DC suppression, or weave-repeat discrimination. If an illumination gradient, fabric crease, or twill float repeat ($f_{\text{repeat}} = f_0 / 2$) has higher amplitude than the yarn pitch, the algorithm selects the wrong frequency.
* **Impact:** Severe miscounting on real fabrics where float repeats or surface fuzz have higher raw spectral magnitude than individual yarn boundaries.

### Defect 2.6 — Fixed Peak Separation Incompatible with Operating Density Range
* **Severity:** Critical
* **Affected Files:** `web_app/engine.py` (`compute_1d_projection_density()`), `notebooks/04_real_fabric_benchmark.ipynb`.
* **Root Cause:**
  ```python
  min_dist = max(4, int(pixels_per_cm / 85.0))
  ```
  For FabricNET high-density samples (up to 93 picks/cm at $S_y = 1200\text{ px/cm}$), the true yarn pitch is $1200 / 93 = 12.90$ pixels.
  With `min_dist = max(4, int(1200 / 85)) = 14$ pixels, any two peaks spaced $\le 14$ pixels apart are suppressed, making it impossible to detect densities $> 85\text{ threads/cm}$.
* **Impact:** Suppresses legitimate yarn peaks in dense fabrics, causing artificial undercounting.

### Defect 2.7 — Projection Density Divides Peak Count by Crop Span
* **Severity:** High
* **Affected Files:** `web_app/engine.py` (lines 171-172), `notebooks/04_real_fabric_benchmark.ipynb`.
* **Root Cause:**
  ```python
  warp_proj = len(warp_peaks) / max(crop_w_cm, 1e-5)
  ```
  On a small crop (e.g. $0.4\text{ cm}$), counting $K$ peaks across the crop assumes the crop starts and ends exactly at inter-yarn boundaries. A single extra peak entry or exit shifts density by $1 / 0.4 = 2.5\text{ threads/cm}$.
* **Impact:** Extreme sensitivity to window boundary placement; ignores inter-peak distance statistics and median pitch.

### Defect 2.8 — Consensus Arbiter Blindly Defaults to 2D FFT on Disagreement
* **Severity:** Critical
* **Affected Files:** `web_app/engine.py` (`evaluate_consensus()`).
* **Root Cause:**
  ```python
  if weave_hint in ("twill", "satin"):
      final_warp = round(warp_fft)
      final_weft = round(weft_fft)
  elif delta_w <= 3.0 and delta_wf <= 3.0:
      final_warp = int(round(0.5 * (warp_fft + warp_proj)))
  else:
      final_warp = int(round(warp_fft))
  ```
  When the two engines disagree, the arbiter assumes 2D FFT is automatically correct. Disagreement indicates uncertainty or failure in one or both estimators. Blindly defaulting to 2D FFT masks fatal failures (such as harmonic doubling or DC leakage).
* **Impact:** Converts contradictory measurements into false-certainty outputs.

### Defect 2.9 — Quality Score Labeled "Confidence" Without Calibration
* **Severity:** High
* **Affected Files:** `web_app/engine.py` (lines 211-220), `README.md`.
* **Root Cause:**
  An arbitrary weighted sum of SPNR, projection variance, and discrepancy is mapped to $[10, 99.9]\%$ and presented as "Confidence Quality Score" ($Q\%$). It is an uncalibrated heuristic, not a statistically valid probability of measurement correctness.
* **Impact:** Misleads users into believing a result has $98.5\%$ statistical confidence when it may be completely erroneous.

### Defect 2.10 — Inconsistent Parallel Implementations Across Notebooks and Web App
* **Severity:** Critical
* **Affected Files:** `notebooks/01_optical_and_spectral_sandbox.ipynb`, `notebooks/02_skew_rectification_engine.ipynb`, `notebooks/03_end_to_end_thread_counter.ipynb`, `notebooks/04_real_fabric_benchmark.ipynb`, `web_app/engine.py`.
* **Root Cause:**
  Each notebook independently re-implemented FFT slices, peak finding, and consensus logic with slightly different parameters (e.g. `prom=1.5` in Notebook 04 vs `prominence=0.012` in `engine.py`; PyTorch tensor FFT in Notebooks vs NumPy FFT in `engine.py`). They diverged in results for the same samples.
* **Impact:** No single source of truth; fixes in `engine.py` do not reflect in benchmarks.

### Defect 2.11 — Benchmark Evaluated Only 4 of 130 Available FabricNET Samples
* **Severity:** Critical
* **Affected Files:** `notebooks/04_real_fabric_benchmark.ipynb`, `results/fabricnet_benchmark.json`.
* **Root Cause:**
  Notebook 04 only processed W012, W017, W001, and W067, while all 130 samples and complete ground truth parameters were available.
* **Impact:** Four cherry-picked samples cannot establish generalization across densities ($15\text{--}93$ threads/cm) and weave classes (Plain, Twill, Satin).

### Defect 2.12 — Fabric Orientation vs Image Axis Conflation
* **Severity:** High
* **Affected Files:** `notebooks/04_real_fabric_benchmark.ipynb` (Cell 7, `orientation_swap: True`).
* **Root Cause:**
  A $90^\circ$ physical rotation swaps warp and weft axes relative to the image sensor. A skew detector operating in $[-45^\circ, +45^\circ]$ cannot determine physical warp vs weft without prior knowledge or user labeling.
* **Impact:** Unverified manual swapping introduced in benchmark to force ground truth alignment.

### Defect 2.13 — Incorrect Total Fabric Density Dimension & Semantics
* **Severity:** High
* **Affected Files:** `web_app/engine.py` (line 444), `README.md`, `data/README.md`.
* **Root Cause:**
  The engine computed `total_thread_density = final_warp + final_weft` (threads/cm), but labeled the units as `threads/cm²` in the UI and documentation. In textile science, areal thread intersection density is $N_{\text{warp}} \times N_{\text{weft}}$ (crossings/cm²), while the sum is a linear density metric (threads/cm).
* **Impact:** Dimensional inconsistency; confuses linear sum with areal density.

### Defect 2.14 — Yarn Pitch Displays Unvalidated Values
* **Severity:** Medium
* **Affected Files:** `web_app/engine.py` (lines 445-446).
* **Root Cause:**
  Pitch is derived as $10,000 / N$ even when density $N$ is unvalidated or rejected, displaying precise pitch numbers that are completely unverified.
* **Impact:** False precision in UI and audit reports.

### Defect 2.15 — Export & Deployment Asset Tracking Inconsistencies
* **Severity:** Medium
* **Affected Files:** `.gitignore`.
* **Root Cause:**
  `.gitignore` excluded `data/fabricnet/*.jpg`, leading to missing images in clean external checkouts, even though verification logs claimed they existed.
* **Impact:** Broken external reproducibility.

---

## 4. Remediation Plan & Architectural Single Source of Truth
To permanently eliminate divergence, we will construct a clean, authoritative Python package `src/fabric_analysis/` containing:
1. `calibration.py`: Independent $S_x, S_y$ physical scale object, unit conversions, pixel pitch.
2. `roi.py`: Explicit metric ROI cropper with coverage verification and metadata reporting.
3. `orientation.py`: Polar Radon frequency-space skew detection with metric aspect-ratio preservation.
4. `spectral.py`: Hann-windowed 2D FFT, multi-candidate harmonic family extraction, symmetric peak validation, subpixel parabolic refinement.
5. `spatial.py`: 1D median-filtered projection profiling, prominence peak detection, inter-peak median pitch estimation with outlier rejection.
6. `fusion.py`: Multi-hypothesis evidence-based fusion arbiter producing explicit decision states (`VALIDATED`, `CONSISTENT_WITH_WARNING`, `NEEDS_REVIEW`).
7. `pipeline.py`: Unified end-to-end analysis callable from web app, notebooks, benchmarks, and tests.

Both `web_app/engine.py` and all notebooks (`01` through `05`) will be refactored to call `src/fabric_analysis/`, establishing one single source of truth across the entire repository.
