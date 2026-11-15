# Data Repository: Textile Fabric Datasets & Physical Specifications

## 1. Directory Architecture & Taxonomy

The `data/` directory houses the multi-modal empirical foundations for automated warp and weft thread density counting, skew rectification, texture classification, and textile structural defect analysis. The repository contains 9 distinct subdirectories totaling **~5.07 GB** across **12,238 files**, structured across physical microscopy, industrial web scans, flatbed captures, synthetic mathematical testbeds, and production tabular records:

```
data/
├── fabricnet/                  # Microscopic Ground-Truth Thread Density (130 RGB images + Excel metadata)
├── aitex_database/             # High-Aspect-Ratio Web Scan Inspection (354 images + binary masks)
├── ten_fabrics/                # Calibrated 300 DPI Flatbed Scanner Crops (2,969 PNGs + 2,970 block TXT masks)
├── multiclass_defects/         # Directional & Structural Fabric Defects (3,067 images across 9 classes)
├── fabric_defects_benchmark/   # Aggregated 6-Class Defect Benchmark (2,739 images, 2.15 GB)
├── textile_weaving_tabular/    # Industrial Loom Production Time-Series (121,149 records with EPI/PPI specs)
├── textile_knitting_tabular/   # Circular Knitting Physical Parameters (12,570 records, 38 columns)
├── synthetic/                  # Ground-Truth Calibrated Mathematical Swatches (3 physics-simulated PNGs)
└── samples/                    # User Ingestion Buffer (.gitkeep for real-time sample testing)
```

---

## 2. Master Cross-Dataset Specifications Matrix

| Dataset Identifier | Primary Modality & Domain | File Count & Disk Footprint | Native Spatial Resolution | Optical Field of View (FOV) | Calibration Scale ($S$) | Target Labels / Ground Truth Annotations | Primary Architectural Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`fabricnet`** | Optical Handheld Microscopy | 130 JPG + 1 XLSX<br>($13.36\text{ MB}$) | $640 \times 480\text{ px}$<br>(24-bit RGB) | $5.0\text{ mm} \times 4.0\text{ mm}$<br>($0.5 \times 0.4\text{ cm}$) | $S_x = 1280.0\text{ px/cm}$<br>$S_y = 1200.0\text{ px/cm}$ | Exact Warp ($20\text{--}62\text{ ends/cm}$), Weft ($15\text{--}93\text{ picks/cm}$), GSM, Pattern | **Gold-Standard Ground Truth** for direct optical thread counting |
| **`aitex_database`** | Industrial Web-Scan Inspection | 354 PNG<br>($168.05\text{ MB}$) | $4096 \times 256\text{ px}$<br>(8-bit Grayscale) | Full loom fabric web width ($1.0\text{--}1.5\text{ m}$) | Variable ($< 40\text{ px/cm}$) | 12 industrial defect classes (broken end, broken pick, etc.) + pixel masks | Macro web inspection; validation of missing warp/weft disruptions |
| **`ten_fabrics`** | Calibrated Flatbed Color Scan | 2,969 PNG + 2,970 TXT<br>($423.22\text{ MB}$) | $256 \times 256\text{ px}$<br>(24-bit RGB, 10% overlap) | $21.67\text{ mm} \times 21.67\text{ mm}$<br>($2.167 \times 2.167\text{ cm}$) | $S = 118.11\text{ px/cm}$<br>($300\text{ DPI}$ fixed) | 10 fabric types, 27 defect types, $16 \times 16$ block grid binary matrices | Scanner calibration baseline; coarse weave texture analysis |
| **`multiclass_defects`** | Industrial Apparel Production | 3,067 JPG/PNG<br>($2.17\text{ GB}$) | $640 \times 360\text{ px}$<br>(RGB & Grayscale) | Standard macro factory camera frame | Uncalibrated optical capture | 9 categories: `horizontal` (weft), `Vertical` (warp), `hole`, `lines`, `stain`, etc. | Directional yarn defect isolation along orthogonal axes |
| **`fabric_defects_benchmark`** | Multi-Source Defect Benchmark | 2,739 JPG/PNG<br>($2.15\text{ GB}$) | $640 \times 360\text{ px}$<br>(RGB & Grayscale) | Standard macro camera frame | Uncalibrated optical capture | 6 categories: 1,666 clean, 1,073 defected (stain, hole, lines, horizontal, vertical) | Directional yarn defect localization baseline |
| **`textile_weaving_tabular`** | Loom Manufacturing Logs | 3 CSV + 1 XLSX + 2 IPYNB<br>($40.04\text{ MB}$) | 121,149 tabular rows<br>(18--19 columns) | Industrial manufacturing run | N/A (Physical metrics) | Warp Count, Weft Count, EPI ($50\text{--}180$), PPI ($40\text{--}120$), Crimp%, Shrink% | Ground-truth statistical distribution of industrial EPI/PPI |
| **`textile_knitting_tabular`** | Circular Knitting Machine Specs | 1 CSV<br>($3.07\text{ MB}$) | 12,570 tabular rows<br>(38 columns) | Circular knitting machine | N/A (Machine parameters) | Machine Gauge ($14\text{--}32\text{ needles/in}$), Dia, Stitch Length, Tex, GSM | Structural contrast: knitted loops (courses/wales) vs. woven grids |
| **`synthetic`** | Mathematical Waveform Simulation | 3 PNG<br>($0.67\text{ MB}$) | $400 \times 400\text{ px}$ & $800 \times 800\text{ px}$ | $1.0 \times 1.0\text{ cm}$ & $2.0 \times 2.0\text{ cm}$ | $S = 400.0\text{ px/cm}$<br>($\Delta x = 25.0\,\mu\text{m/px}$) | Exact Warp (32, 36), Weft (28, 30), Tilt ($0.0^\circ, +12.0^\circ, +15.0^\circ$) | Absolute unit testbed with zero measurement uncertainty |
| **`samples`** | User Ingestion Working Directory | Dynamic (.gitkeep) | User-defined | User-defined | Configurable via Web App | User test imagery | Local upload directory for ad-hoc fabric verification |

---

## 3. Dataset-Specific Engineering & Physical Specifications

### 3.1. FabricNET: Microscopic Ground-Truth Thread Density (`data/fabricnet/`)

#### Provenance & Academic Reference
* **Authors:** Ali Can Seçkin, et al.
* **Publication:** *"FabricNET: A Dataset for Basic Weaving Fabric Texture Recognition and Mass Prediction"*, *Sustainability* (MDPI), 2023, 15(21), 15197.
* **Source Repository:** Kaggle (`acseckn/fabricnet`) / MDPI Open Access.

#### Physical Capture Hardware & Optical Setup
* **Microscope Sensor:** Handheld digital USB optical microscope with built-in adjustable circular white-LED illumination ring.
* **Optical Magnification:** High-magnification macro zoom focusing on an active physical area of **$5.0\text{ mm} \times 4.0\text{ mm}$** ($0.50\text{ cm} \times 0.40\text{ cm}$).
* **Sensor Resolution:** $640 \times 480\text{ pixels}$ (aspect ratio 4:3), 24-bit RGB color depth, JPEG format.

#### Metric Calibration Invariant
From the physical field of view ($5.0\text{ mm} \times 4.0\text{ mm}$) and pixel grid ($640 \times 480\text{ px}$), the horizontal and vertical scale factors are analytically fixed:
$$S_x = \frac{640\text{ pixels}}{0.50\text{ cm}} = \mathbf{1280.0\text{ pixels/cm}} \quad \implies \quad \Delta x = \frac{10,000\,\mu\text{m}}{1280} = \mathbf{7.8125\,\mu\text{m/pixel}}$$
$$S_y = \frac{480\text{ pixels}}{0.40\text{ cm}} = \mathbf{1200.0\text{ pixels/cm}} \quad \implies \quad \Delta y = \frac{10,000\,\mu\text{m}}{1200} = \mathbf{8.3333\,\mu\text{m/pixel}}$$

#### Dataset Composition & Schema (`FabricNet_parameters.xlsx`)
The dataset comprises **130 photographic samples** (`W001.jpg` to `W130.jpg`) paired with verified laboratory measurements across 5 attributes:
1. `Image id`: Integer identifier ($1$ to $130$).
2. `Specific Mass`: Fabric surface weight (GSM) ranging from **$85.0\text{ g/m}^2$ to $250.0\text{ g/m}^2$** (mean: $148.73\text{ g/m}^2$).
3. `Warp`: Ground-truth warp thread density ranging from **$20.0\text{ to }62.0\text{ ends/cm}$** (mean: $35.72\text{ ends/cm}$).
4. `Weft`: Ground-truth weft thread density ranging from **$15.0\text{ to }93.0\text{ picks/cm}$** (mean: $34.92\text{ picks/cm}$).
5. `Texture`: Fundamental weaving pattern classification:
   * **Plain Weave (`plain`):** 50 samples (1/1 balanced alternating interlacement).
   * **Twill Weave (`twill`):** 39 samples (diagonal floating ridges, e.g. 2/1, 2/2, 3/1).
   * **Satin Weave (`satin`):** 41 samples (extended surface floats with minimized interlacing points).

#### Warp & Weft Algorithmic Usability
FabricNET is the **primary physical benchmark** for the project. Because individual yarn crowns and inter-yarn shadows are distinctly imaged at $\sim 8\,\mu\text{m/pixel}$, it satisfies the Nyquist-Shannon criterion ($> 15\text{ pixels per yarn period}$ for densities up to $60\text{ threads/cm}$). It directly validated the dual-engine consensus on `W012.jpg` (Warp $38.0\text{ ends/cm}$, $\Delta=0.0$; Weft $32.5\text{ picks/cm}$, $\Delta=0.5$).

---

### 3.2. AITEX Fabric Image Database — AFID (`data/aitex_database/`)

#### Provenance & Academic Reference
* **Authors:** J. Silvestre-Blanes, T. Albero-Albero, I. Miralles, R. Pérez-Llorens, and J. Moreno.
* **Publication:** *"AFID: A Public Fabric Image Database for Defect Detection"*, *AUTEX Research Journal*, 2019, 19(4), pp. 363–370.
* **Source Organization:** Textile Research Institute (AITEX), Alcoy, Alicante, Spain.

#### Physical Capture Hardware & Optical Setup
* **Acquisition System:** Industrial high-speed web inspection line equipped with synchronized line-scan cameras.
* **Illumination Architecture:** Uniform backlighting and top frontlighting configured to expose structural weaving defects across continuous moving fabric webs ($1.0\text{--}1.5\text{ m}$ roll width).
* **Native Resolution:** **$4096 \times 256\text{ pixels}$** (extreme aspect ratio 16:1), 8-bit Grayscale (modes `L` and `LA`), lossless PNG format.

#### Dataset Structure & Naming Conventions
The database contains **354 images** organized into three subdirectories:
1. **`Defect_images/` (106 images):** Real industrial defect samples named `nnnn_ddd_ff.png`:
   * `nnnn`: Serial image acquisition index.
   * `ddd`: 3-digit defect classification code.
   * `ff`: Fabric style index ($00$ to $06$).
2. **`Mask_images/` (107 images):** Pixel-level binary segmentation masks named `nnnn_ddd_ff_mask.png` where white pixels ($255$) denote the localized flaw and black pixels ($0$) denote clean ground texture.
3. **`NODefect_images/` (141 images):** Pristine defect-free fabric textures partitioned across 7 industrial fabric styles:
   * `2608691-202020u`: 21 samples
   * `2311517-195063u`: 20 samples
   * `2306881-210020u`: 20 samples
   * `2306894-210033u`: 20 samples
   * `2311980-185026u`: 20 samples
   * `2311694-1930c7u`: 20 samples
   * `2311694-2040n7u`: 20 samples

#### Defect Code Taxonomy

| Defect Code (`ddd`) | Defect Designation | Textile Mechanism & Warp/Weft Relationship |
| :---: | :--- | :--- |
| **`002`** | Broken End | Warp yarn rupture during shedding; causes vertical gap along loom axis |
| **`006`** | Broken Yarn | Localized filament breakage across yarn body |
| **`010`** | Broken Pick | Weft insertion failure during rapier/air-jet cycle; causes horizontal void |
| **`016`** | Weft Curling | Snarl or tension loop forming along horizontal fill yarn |
| **`019`** | Fuzzyball / Slub | Entangled fiber cluster attached to yarn surface |
| **`022`** | Cut Selvage | Mechanical shearing of the outer fabric boundary edge |
| **`023`** | Crease | Longitudinal folding deformation induced during roll take-up |
| **`025`** | Warp Ball | Accumulation of loose fibers around warp ends behind the reed |
| **`027`** | Knots | Manual or automatic yarn tying joints exceeding normal yarn diameter |
| **`029`** | Contamination | Oil, grease, or foreign colored fiber deposits |
| **`030`** | Nep | Small knot of entangled fibers created during carding/spinning |
| **`036`** | Weft Crack | Thin horizontal spacing band due to uneven beat-up density |

#### Warp & Weft Algorithmic Usability
AITEX images cover wide web spans ($> 1\text{ meter}$) at relatively low optical resolution ($< 40\text{ px/cm}$), meaning individual yarn boundaries span only $1\text{--}2\text{ pixels}$. While insufficient for direct 1 cm thread counting without microscope optics, AITEX is the **ideal benchmark for validating missing yarn disruptions** (broken ends vs. broken picks) and testing sub-patch slicing algorithms (e.g. $256 \times 256$ crops).

---

### 3.3. Ten Fabrics Dataset — TFD (`data/ten_fabrics/`)

#### Provenance & Specifications
* **Authors:** Sahar Shakir, et al.
* **Source:** Industrial textile weaving mill via Kaggle (`saharshakir/ten-fabrics-dataset-tfd`).
* **Volume:** 5,939 files ($423.22\text{ MB}$), comprising 2,969 PNG images and 2,970 TXT ground-truth block annotations.

#### Acquisition Hardware & Optical Calibration
* **Scanner Hardware:** Commercial flatbed optical color scanner.
* **Scan Resolution:** Fixed **$300\text{ DPI}$** ($118.11\text{ pixels/cm}$).
* **Spatial Period:** $\Delta x = \Delta y = \frac{25,400\,\mu\text{m}}{300} = \mathbf{84.67\,\mu\text{m/pixel}}$.
* **Patch Cropping Geometry:** Continuous fabric scans partitioned into **$256 \times 256\text{ pixel}$** crops with **10% spatial overlap** ($25.6\text{ px}$) to prevent border truncation of defects.
* **Physical Crop Area:** Each patch spans exactly **$21.67\text{ mm} \times 21.67\text{ mm}$** ($2.167\text{ cm} \times 2.167\text{ cm}$).

#### Dataset Composition & Annotation Protocol
* **Fabric Classes:** 10 structural categories (folders `001` through `010`).
* **Sample Count:** 3,000 total image patches:
  * Clean / Defect-Free: **2,257 patches (75.2%)**
  * Defective: **743 patches (24.8%)** encompassing 27 distinct defect types (~90% natural factory flaws, ~10% introduced holes/stains).
* **Ground Truth Format:** Every PNG image is accompanied by a `.txt` file containing a **$16 \times 16$ binary matrix** (256 elements). Each binary integer maps to an exact **$16 \times 16\text{ pixel}$ spatial block** ($1.355\text{ mm} \times 1.355\text{ mm}$ physical tile):
  * `0`: Clean, normal fabric texture.
  * `1`: Defected texture containing flaw structure.

#### Warp & Weft Algorithmic Usability
Because TFD provides an exact flatbed scanner calibration ($S = 118.11\text{ px/cm}$), it allows testing metric projection profiling on coarse fabrics ($N \le 20\text{ threads/cm}$). For fine fabrics ($N > 35\text{ threads/cm}$), $300\text{ DPI}$ approaches the Nyquist limit ($< 3\text{ pixels/thread}$), demonstrating the necessity of $\ge 600\text{--}1200\text{ DPI}$ scanners or optical microscopes.

---

### 3.4. Multi-Class Fabric Defect Detection Dataset (`data/multiclass_defects/`)

#### Provenance & Specifications
* **Curator:** Ziya07, Kaggle / Industrial Apparel Production Assembly Lines.
* **Volume:** 3,067 images ($2.17\text{ GB}$), consisting of 2,917 JPG and 150 PNG files.
* **Resolution:** Standard widescreen **$640 \times 360\text{ pixels}$** (16:9 aspect ratio) with subsets up to $1280 \times 720\text{ px}$, 24-bit RGB and 8-bit Grayscale.

#### Class Distribution & Textile Fault Mapping

| Subdirectory Category | Image Count | Physical Fault Description | Directional Axis |
| :--- | :---: | :--- | :---: |
| **`defect free`** | 1,666 | Normal woven fabric surface with uniform yarn interlacing | Baseline |
| **`stain`** | 398 | Localized chemical, oil, dye, or grease discolouration | Surface |
| **`hole`** | 281 | Complete physical puncture severing both warp and weft yarns | Bi-directional |
| **`lines`** | 157 | Drawing-in faults, reed marks, or longitudinal tension streaks | Longitudinal |
| **`horizontal`** | 136 | **Weft-direction yarn defects:** missing picks, coarse picks, broken fill | **Weft ($y$-axis)** |
| **`Broken stitch`** | 112 | Severed sewing thread in garment seaming or hem stitching | Stitching |
| **`Pinched fabric`** | 108 | Feed-dog or presser-foot mechanical bunching during sewing assembly | Handling |
| **`Needle mark`** | 108 | Puncture perforation along seam lines from blunt sewing needles | Mechanical |
| **`Vertical`** | 101 | **Warp-direction yarn defects:** broken ends, misdraws, warp streaks | **Warp ($x$-axis)** |

#### Warp & Weft Algorithmic Usability
This dataset explicitly isolates **directional yarn defects along orthogonal axes**:
* `horizontal` faults disrupt weft periodicity without corrupting warp continuity.
* `Vertical` faults disrupt warp periodicity without corrupting weft continuity.
This decoupling makes it a benchmark for testing directional 1D marginal projection profile robustness against localized single-axis yarn breaks.

---

### 3.5. Fabric Defects Benchmark Dataset (`data/fabric_defects_benchmark/`)

#### Provenance & Specifications
* **Curator:** nexuswho / Moratuwa Textile Defect Collection.
* **Volume:** 2,739 images ($2.15\text{ GB}$), consisting of 2,589 JPG and 150 PNG files.
* **Resolution:** Standardized to **$640 \times 360\text{ pixels}$**.
* **Class Architecture:** Standardized 6-class subset of industrial defects:
  1. `defect free`: 1,666 images
  2. `stain`: 398 images
  3. `hole`: 281 images
  4. `lines`: 157 images
  5. `horizontal`: 136 images
  6. `Vertical`: 101 images

---

### 3.6. Industrial Weaving Loom Production Dataset (`data/textile_weaving_tabular/`)

#### Provenance & Academic Reference
* **Authors:** Azmine Toushik Wasi, et al.
* **Source:** Mendeley Data (`nxb4shgs9h/1`) & Zenodo (`7498062`).
* **Volume:** 40.04 MB. Contains:
  * `full_weaving_dataset.csv`: 121,149 rows, 18 columns.
  * `weaving_dataset_full.csv`: 121,149 rows, 19 columns.
  * `weaving_rejection_dataset.csv`: 22,011 rows, 14 columns.
  * `raw_data_all.xlsx`: 8.2 MB raw manufacturing production sheets.
  * ETL Notebooks: `code_to_clean_the_raw_data.ipynb`, `weaving_dataset_full_code.ipynb`.

#### Schema & Column Definitions

| Column Name | Data Type | Physical Interpretation & Engineering Units |
| :--- | :--- | :--- |
| `ID` | Integer | Unique identifier for manufacturing production order |
| `Month` | Categorical | Production month of the weaving run |
| `Construction` | String | Standard textile notation: $\frac{\text{Warp Count} \times \text{Weft Count}}{\text{EPI} \times \text{PPI}}$ (e.g. `40x40/133x72`) |
| `warp_count` | Float | English cotton count ($N_e$) of the warp yarn |
| `weft_count` | Float | English cotton count ($N_e$) of the weft yarn |
| `epi` | Float | **Ends Per Inch** (Target warp thread density on loom) |
| `ppi` | Float | **Picks Per Inch** (Target weft thread density on loom) |
| `Req_Finish_Fabrics` | Float | Required finished fabric quantity (yards) |
| `Fabric_Allowance` | Float | Percentage manufacturing overage allowance |
| `Rec_Beam_length(yds)` | Float | Received warp beam yarn length |
| `Shrink_allow` | Float | Dimensional shrinkage allowance percentage |
| `act_shrink%` | Float | Actual empirically measured fabric shrinkage (%) |
| `assump_crimp%` | Float | Assumed yarn crimp percentage (take-up during interlacing) |
| `act_crimp%` | Float | Empirically verified yarn crimp percentage |
| `Req_grey_fabric` | Float | Required loom-state (greige) fabric yardage |
| `Total_pdn_m/c` | Float | Cumulative production output from weaving loom (yards) |
| `Rej_and_cut_Piece` | Float | Rejection yardage due to weaving flaws and cut remnants |
| `Rejection` | Float | Target rejection classification/volume in rejection model |

#### Warp & Weft Density Metric Bridge
Industrial loom specifications are recorded in Ends Per Inch (EPI) and Picks Per Inch (PPI). The mathematical bridge between tabular specifications and our metric computer vision pipeline ($N_{\text{warp}}, N_{\text{weft}}$ in $\text{threads/cm}$) is:
$$N_{\text{warp}} = \frac{\text{EPI}}{2.54} \approx 0.3937 \times \text{EPI}$$
$$N_{\text{weft}} = \frac{\text{PPI}}{2.54} \approx 0.3937 \times \text{PPI}$$

For standard industrial shirting construction `40x40/133x72`:
* Warp Density: $N_{\text{warp}} = \frac{133}{2.54} = \mathbf{52.36\text{ ends/cm}}$ (mean pitch $P_x = 191.0\,\mu\text{m}$).
* Weft Density: $N_{\text{weft}} = \frac{72}{2.54} = \mathbf{28.35\text{ picks/cm}}$ (mean pitch $P_y = 352.8\,\mu\text{m}$).

---

### 3.7. Circular Knitting Machine Dataset (`data/textile_knitting_tabular/`)

#### Provenance & Specifications
* **Author:** Toufique33, Kaggle (`toufique33/textile-knitting-dataset`).
* **Volume:** 1 CSV file (`knitting_dataset.csv`), 3.07 MB.
* **Shape:** 12,570 rows $\times$ 38 columns.

#### Physical Parameters & Machine Specifications
Captures industrial circular knitting production records across 38 variables including:
* Machine Specifications: `M/C Brand` (Fukuhara, Mayer & Cie, Terrot), `m/c_dia` (inches, e.g. 30", 34", 52"), `m/c_gauge` (needles/inch, e.g. 14G, 20G, 24G, 28G).
* Loop Parameters: `stitch` (loop length in mm, e.g. $2.6\text{--}4.8\text{ mm}$), `tightness_factor` ($TF = \frac{\sqrt{\text{Tex}}}{l}$).
* Yarn Counts: `Yarn_Count` ($N_e$, e.g. 24/1, 30/1, 34/1), `yarn_count_tex_1` (Linear density in Tex).
* Fabric Physicals: `GSM` ($100\text{ to }750\text{ g/m}^2$), `composition` (100% Cotton, CVC, TC), `construction` (Single Jersey, 1x1 Rib, Interlock, Terry Fleece).

#### Architectural Contrast
Serves as an essential structural baseline contrasting **knitted loop geometries (courses and wales)** against **woven orthogonal grids (warp and weft)**.

---

### 3.8. Synthetic Benchmark Swatches (`data/synthetic/`)

#### Formulation & Physics-Based Synthesis
To evaluate the mathematical precision of the computer vision engine under conditions with zero ground-truth uncertainty, three synthetic swatches were generated using physics-based 2D optical modeling:
$$I_{\text{clean}}(x, y) = I_0 + A_x \cos\left(\frac{2\pi x}{P_x}\right) + A_y \cos\left(\frac{2\pi y}{P_y}\right) + C_{xy} \cos\left(\frac{2\pi x}{P_x}\right)\cos\left(\frac{2\pi y}{P_y}\right)$$
$$I_{\text{noisy}}(x, y) = \text{Rot}_\theta\Big[I_{\text{clean}}(x, y) \cdot G_{\text{illum}}(x, y) + \mathcal{N}(0, \sigma_{\text{fiber}}^2)\Big]$$

#### Swatch Specifications

| File Name | Dimensions | Calibration Scale | True Density Specs | Applied Angular Tilt | Simulated Physical Artifacts |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **`macro_swatch_skewed_12deg.png`** | $800 \times 800\text{ px}$ | $400.0\text{ px/cm}$ | **Warp: 36 ends/cm** ($P_x = 277.8\,\mu\text{m}$)<br>**Weft: 30 picks/cm** ($P_y = 333.3\,\mu\text{m}$) | **$+12.00^\circ$** | Gaussian yarn crowns, inter-yarn shadow valleys, fiber hairiness ($\sigma=8.5$), bilinear illumination gradient ($0.85\text{--}1.15$) |
| **`sample_plain_32x28.png`** | $400 \times 400\text{ px}$ | $400.0\text{ px/cm}$ | **Warp: 32 ends/cm** ($P_x = 312.5\,\mu\text{m}$)<br>**Weft: 28 picks/cm** ($P_y = 357.1\,\mu\text{m}$) | **$0.00^\circ$** | Perfect orthogonal alignment, balanced 1/1 plain weave profile |
| **`sample_skewed_15deg.png`** | $400 \times 400\text{ px}$ | $400.0\text{ px/cm}$ | **Warp: 32 ends/cm** ($P_x = 312.5\,\mu\text{m}$)<br>**Weft: 28 picks/cm** ($P_y = 357.1\,\mu\text{m}$) | **$+15.00^\circ$** | Synthetic counter-clockwise rotation demonstrating profile collapse and Radon peak recovery |

---

### 3.9. User Ingestion Buffer (`data/samples/`)

The `data/samples/` directory is tracked in git via `.gitkeep` and serves as the local ingest buffer for user-uploaded smartphone captures, pick-glass photographs, and external test images.

---

## 4. Optical Physics, Spatial Resolution & Nyquist Sampling Criteria

To accurately detect individual yarn crowns and resolve warp/weft thread density per centimeter, the imaging system must satisfy the **Nyquist-Shannon sampling theorem**:

$$f_{\text{sampling}} > 2 f_{\max} \quad \implies \quad \Delta x < \frac{P_{\min}}{2}$$

In practical textile microscopy, yarn hairiness, optical blurring, and shadow variations demand at least **$8\text{ to }12\text{ pixels per yarn period}$** ($K \ge 8$):

$$\Delta x \le \frac{10,000\,\mu\text{m}}{N_{\text{threads/cm}} \times K}$$

### Minimum Resolution Requirements by Fabric Category

| Fabric Classification | Density Range ($N_{\text{threads/cm}}$) | Yarn Period ($P$ in $\mu\text{m}$) | Required Optical Resolution ($\Delta x$) | Minimum Scale ($S$ in $\text{px/cm}$) | Recommended Acquisition Hardware |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Coarse (Canvas, Burlap, Medical Gauze)** | $8\text{--}18\text{ threads/cm}$ | $555\text{--}1250\,\mu\text{m}$ | $\Delta x \le 55.0\,\mu\text{m/px}$ | $S \ge 180\text{ px/cm}$ | Smartphone macro, $600\text{ DPI}$ Flatbed Scanner |
| **Medium (Denim, Oxford Shirting, Twill)** | $20\text{--}40\text{ threads/cm}$ | $250\text{--}500\,\mu\text{m}$ | $\Delta x \le 25.0\,\mu\text{m/px}$ | $S \ge 400\text{ px/cm}$ | Smartphone with 10x Pick-Glass, $1200\text{ DPI}$ Scanner |
| **Fine (Poplin, Percale, Satin, Microfiber)** | $45\text{--}95\text{ threads/cm}$ | $105\text{--}222\,\mu\text{m}$ | $\Delta x \le 10.5\,\mu\text{m/px}$ | $S \ge 950\text{ px/cm}$ | **USB Digital Microscope ($1200\text{--}1280\text{ px/cm}$)** |

---

## 5. Storage Policy, Bandwidth Management & Git Invariants

To avoid overloading the Git repository with multi-gigabyte binary assets, strict tracking invariants are enforced via [`.gitignore`](../.gitignore):

* **Tracked Assets (Committed to Repository):**
  * `data/README.md`: This comprehensive data taxonomy and physical specifications reference.
  * `data/fabricnet/FabricNet_parameters.xlsx`: Ground-truth tabular parameters (131 rows, 13.3 KB).
  * `data/synthetic/*`: High-precision synthetic testbed PNGs (696 KB total).
  * `data/samples/.gitkeep`: Empty ingestion buffer anchor.
* **Ignored Large Datasets (Preserved Locally on Disk):**
  * `data/fabricnet/*.jpg`: 130 microscope captures (13.3 MB).
  * `data/aitex_database/`: 354 line-scan PNGs (168 MB).
  * `data/ten_fabrics/`: 5,939 scanner files (440 MB).
  * `data/multiclass_defects/`: 3,067 images (2.17 GB).
  * `data/fabric_defects_benchmark/`: 2,739 images (2.15 GB).
  * `data/textile_weaving_tabular/`: Industrial production logs (41 MB).
  * `data/textile_knitting_tabular/`: Knitting production CSV (3.1 MB).
