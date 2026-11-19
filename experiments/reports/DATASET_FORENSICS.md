# DATASET FORENSICS & UNIFIED METADATA REPORT — PHASE 1
**Repository:** Warp & Weft AI (`/home/assem-elqersh/Desktop/Warp Weft Project/`)  
**Canonical Manifests:** `experiments/data/unified_manifest.json` and `experiments/data/split_manifest.json`  
**Audit Timestamp:** 2026-11-19T21:56:00+02:00  
**Authorship / Role:** Principal ML Engineer, Textile Metrology Lead  

---

## 1. Executive Summary & Forensic Scope

Phase 1 establishes an immutable, unified metadata schema and data ingestion engine for textile density metrology. DISPARATE textile datasets have historically conflated surface defect masks or texture classification with physical yarn density. This forensic audit separates datasets with physically verified thread counts from auxiliary datasets, verifies pixel byte integrity, performs perceptual duplicate detection, and enforces strict specimen-level disjoint partitioning with zero data leakage.

---

## 2. Unified Metadata Schema Specification

Every sample across all audited datasets is mapped to an immutable record conforming to the following standardized schema:

| Schema Field | Data Type | Nullable | Functional Purpose & Metrological Constraint |
| :--- | :--- | :--- | :--- |
| `sample_id` | `string` | No | Unique sample identifier (e.g. `fabricnet_W10`, `client_specimen_002_R1`) |
| `specimen_id` | `string` | No | Physical specimen identifier ensuring zero-leakage group partitioning |
| `image_id` | `string` | No | Base filename of the raw capture tensor |
| `dataset_id` | `string` | No | Originating dataset (`fabricnet`, `synthetic_micro_swatches`, etc.) |
| `image_path` | `string` | No | Workspace relative path to the image file |
| `warp_density` | `float` | Yes | Physical warp yarn count in threads/cm ($D_x$); `null` if unmeasured |
| `weft_density` | `float` | Yes | Physical weft yarn count in threads/cm ($D_y$); `null` if unmeasured |
| `density_units` | `string` | Yes | Standard physical units: `"threads/cm"` |
| `weave_type` | `string` | Yes | Architectural weave pattern: `"plain"`, `"twill"`, `"satin"`, etc. |
| `calibration_type` | `string` | No | `"nominal_microscope"`, `"in_situ_back_calculated"`, `"synthetic_exact"`, `"uncalibrated_microscopy"` |
| `px_per_cm_x` | `float` | Yes | Independent horizontal optical scale factor ($S_x$ in px/cm) |
| `px_per_cm_y` | `float` | Yes | Independent vertical optical scale factor ($S_y$ in px/cm) |
| `physical_reference_method` | `string` | Yes | Method of ground truth acquisition (`"manual_pick_glass_astm_d3775"`, `"synthetic_exact"`, etc.) |
| `roi_id` | `string` | No | `"full_frame"`, or specific regional crop ID (`"R1"`, `"R2"`, etc.) |
| `split` | `string` | No | Partition assignment: `"train"`, `"validation"`, `"test"`, `"locked_client_test"`, `"auxiliary"` |
| `label_quality` | `string` | No | `"ground_truth_physical"`, `"synthetic_exact"`, `"texture_class_only"` |
| `license` | `string` | No | IP governance (`"CC-BY-4.0"`, `"CC0-1.0"`, `"MIT"`, `"Proprietary_Client_Data"`) |
| `sha256` | `string` | No | 64-character SHA-256 cryptographic hash of image bytes |
| `dhash` | `integer` | Yes | 64-bit perceptual difference hash for duplicate/near-duplicate detection |
| `image_width` | `integer` | No | Pixel width ($W$) |
| `image_height` | `integer` | No | Pixel height ($H$) |
| `channels` | `integer` | No | Color channel count ($C \in \{1, 3\}$) |

---

## 3. Audited Dataset Inventory & Metrological Characterization

### 3.1. Primary Metrology Datasets (With Ground-Truth Physical Density)

#### 1. FabricNET (`data/fabricnet/`)
* **Specimen Count:** 130 physical fabric specimens (1 image per specimen).
* **Native Resolution:** $640 \times 480$ pixels (RGB).
* **Optical Modality:** USB digital optical microscope with nominal fixed magnification ($S_x = 1280.0\text{ px/cm}, S_y = 1200.0\text{ px/cm}$).
* **Physical Reference:** Manual counts performed under microscope magnification, documented in `FabricNet_parameters.xlsx` (Secer & Ercan 2023).
* **Weave Distribution:** Plain ($N=50$), Satin ($N=41$), Twill ($N=39$).
* **Density Range:** Warp: $16.0\text{ to }74.0\text{ ends/cm}$, Weft: $12.0\text{ to }48.0\text{ picks/cm}$.
* **Licensing:** CC-BY-4.0 (Open Access for research and commercial benchmarking).
* **Integrity Audit:** 130 of 130 files valid, 0 corruptions, 0 exact dHash duplicates, 0 near-duplicates (Hamming distance $\le 2$).

#### 2. Client Reference Specimen 2 (`data/samples/test.png`)
* **Specimen Count:** 1 physical cotton-blend shirting swatch ("العينة 2").
* **Native Resolution:** $1200 \times 1600$ pixels (RGB).
* **Optical Modality:** Macro smartphone photography on copy-stand.
* **Physical Reference:** ASTM D3775 manual pick-glass count across 5 physical locations (Warp: $31.0 \pm 0.71\text{ ends/cm}$, Weft: $26.6 \pm 0.55\text{ picks/cm}$).
* **Calibration Provenance:** $S_x = 263.5, S_y = 208.4\text{ px/cm}$ (analytically back-calculated from observed yarn period and manual count).
* **Supervision Level:** `specimen_only`. The 5 ROIs represent digital spatial quadrant crops ($256\times 256\text{ px}$) across the macroscopic capture.
* **Licensing:** Proprietary Client Confidential (Raw pixels excluded from git tracking via `.gitignore`).

#### 3. Synthetic Micro-Swatches (`data/synthetic/`)
* **Specimen Count:** 3 procedural micro-swatches (`synthetic_swatch_32_28.png`, etc.).
* **Native Resolution:** $400 \times 400$ and $800 \times 800$ pixels (Grayscale).
* **Optical Modality:** Procedural raster synthesis.
* **Physical Reference:** Exact mathematical parameterization ($D_x = 32.0, D_y = 28.0\text{ threads/cm}$ at $S = 400.0\text{ px/cm}$).
* **Licensing:** MIT License (Generated internally).

---

### 3.2. Auxiliary & Defect Datasets (No Physical Thread Density)

#### 4. Harvard Textile Microtexture Dataset (`experiments/data_acquisition/downloads/harvard_microtexture/`)
* **Image Count:** 190 optical microscopy captures ($512\times 512$ and $640\times 480$).
* **Labels:** 40+ quantitative Haralick, LBP, and wavelet texture features in `features.csv`.
* **Metrological Limitation:** NO warp or weft density labels. Useful solely as a visual representation benchmark for texture classification.
* **Licensing:** CC0-1.0 (Public Domain).

#### 5. Ten Fabrics Dataset (`data/ten_fabrics/`)
* **Image Count:** 2,969 PNG images ($256\times 256$).
* **Labels:** 10 structural weave classes + defect bounding polygons.
* **Metrological Limitation:** NO yarn count or physical scale metadata.

#### 6. AITEX Industrial Loom Dataset (`data/aitex_database/`)
* **Image Count:** 354 industrial line-scan captures ($4096\times 256$).
* **Labels:** Binary structural defect masks.
* **Metrological Limitation:** NO thread density ground truth.

---

## 4. Perceptual Hashing & Duplicate Detection Audit

A 64-bit difference hash (dHash) was calculated across all 130 FabricNET images:
* **Exact Duplicate Test:** Max collision count = 0.
* **Near-Duplicate Test (Hamming Distance $\le 2$):** 0 near-duplicate pairs detected.
* **Conclusion:** FabricNET consists of 130 genuinely distinct fabric swatches with zero duplicate contamination.

---

## 5. Specimen-Grouped Disjoint Split Partitioning

To satisfy the non-negotiable **No Data Leakage Invariant**, FabricNET was partitioned into immutable specimen-disjoint sets using stratified sampling by weave pattern (`seed=42`):

```text
Total FabricNET Specimens: 130
├── Train Split:      78 specimens (60.0%) [Plain: 30, Satin: 25, Twill: 23]
├── Validation Split: 26 specimens (20.0%) [Plain: 10, Satin:  8, Twill:  8]
└── Test Split:       26 specimens (20.0%) [Plain: 10, Satin:  8, Twill:  8]
```

### Zero-Leakage Mathematical Verification:
$$\text{Train} \cap \text{Validation} = \emptyset \quad (0\text{ common samples})$$
$$\text{Train} \cap \text{Test} = \emptyset \quad (0\text{ common samples})$$
$$\text{Validation} \cap \text{Test} = \emptyset \quad (0\text{ common samples})$$

Client Specimen 2 is partitioned strictly into `locked_client_test` and is never exposed to model training or hyperparameter tuning.
