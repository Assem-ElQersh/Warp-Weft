# Verified Master Textile Dataset Inventory & Ground-Truth Ledger

**The mechanistic justification for this step is: establish an immutable, cryptographically verified catalog of all local, remote, and external textile datasets, resolve conflicting file counts and dimensional discrepancies, and enforce the categorical boundary between physical thread metrology and non-macro defect inspection.**

---

## 1. Categorical Metrology Taxonomy

Datasets are strictly partitioned into 7 functional classes:
* **Category A:** Direct Physical Density Supervision (Warp ends/cm, Weft picks/cm with calibrated FOV).
* **Category B:** Yarn-Level Structural Annotations (Individual warp/weft float masks, centerlines, bounding boxes).
* **Category C:** Calibrated Weave Texture & Surface Scans (Known metric DPI / pixel pitch, complex weaves).
* **Category D:** Textile Defect & Anomaly Inspection (Line-scan web inspection, binary defect masks, non-metric).
* **Category E:** High-Magnification Optical Microscopy (Fiber-level features, Haralick/LBP descriptors).
* **Category F:** Procedural Synthetic Datasets (Exact mathematical ground-truth masks, zero annotation noise).
* **Category G:** Industrial Loom Production & Tabular Records (EPI/PPI manufacturing logs, operational time series).

---

## 2. Comprehensive Dataset Inventory

| Dataset Identifier | Cat. | Storage Location | Files On Disk | Disk Size | Native Resolution | Optical Scale / FOV | Ground-Truth Attributes | License & Attribution | Access Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`fabricnet_microscopy`** | A | `data/fabricnet/` | 131 files | 13.36 MB | $640\times 480\text{ px}$ | $S_x=1280.0, S_y=1200.0\text{ px/cm}$ ($\text{FOV } 5\times 4\text{ mm}$) | Warp: 20–62 ends/cm, Weft: 15–93 picks/cm, Weave: plain/twill/satin | CC BY 4.0 / Seckin et al. (MDPI Sustainability 2023) | **DOWNLOADED_VERIFIED** |
| **`client_specimen_2`** | A | `data/samples/test.png` | 1 file | 2.47 MB | $1200\times 1600\text{ px}$ | $S_x=263.5, S_y=208.4\text{ px/cm}$ ($\text{FOV } 4.55\times 7.68\text{ cm}$) | 5-region manual pick-glass count: Warp 31 ends/cm, Weft 27 picks/cm | Confidential Client IP / Warp & Weft Project | **DOWNLOADED_VERIFIED** |
| **`synthetic_micro_swatches`** | F | `data/synthetic/` | 3 files | 0.67 MB | $400\times 400\text{ px}$ | $S_x=480.0, S_y=480.0\text{ px/cm}$ ($\text{FOV } 8.33\times 8.33\text{ mm}$) | Exact procedural masks: Warp 32 ends/cm, Weft 28 picks/cm | Proprietary Procedural Generator / MIT | **DOWNLOADED_VERIFIED** |
| **`harvard_microtexture`** | E | `experiments/data_acquisition/downloads/harvard_microtexture/` | 438 files | 21.26 MB | $512\times 512\text{ px}$ | 100x optical lens (no metric scale) | 190 images, 40+ Haralick, LBP, and wavelet texture features in `features.csv` | CC0 1.0 Public Domain / Nithin Aruswamy (Harvard Dataverse 2025) | **DOWNLOADED_VERIFIED** |
| **`aitex_database`** | D | `data/aitex_database/` | 354 files | 168.05 MB | $4096\times 256\text{ px}$ | Industrial line-scan ($<1\text{ px/yarn}$) | 245 base images (140 clean, 105 defect) + 109 binary defect masks | Academic Open / Silvestre-Blanes et al. (AITEX 2019) | **DOWNLOADED_VERIFIED** |
| **`ten_fabrics`** | D | `data/ten_fabrics/` | 5,939 files | 423.22 MB | Varied macro | Uncalibrated consumer cameras | 10 surface texture classes (wool, cotton, denim, silk, etc.) | CC BY 4.0 / Sahar Shakir (Kaggle 2021) | **DOWNLOADED_VERIFIED** |
| **`multiclass_defects`** | D | `data/multiclass_defects/` | 3,067 files | 2,172.34 MB | $1280\times 720\text{ px}$ | Surface inspection rig | 9 directional defect categories (horizontal/vertical mispicks, holes) | CC BY 4.0 / Ziya (Kaggle 2023) | **DOWNLOADED_VERIFIED** |
| **`fabric_defects_benchmark`** | D | `data/fabric_defects_benchmark/` | 2,739 files | 2,151.29 MB | $4096\times 256$ & $1920\times 1080$ | Multi-resolution web scan | Pixel segmentation masks for industrial defect detection | CC BY 4.0 / Nexuswho (Kaggle 2022) | **DOWNLOADED_VERIFIED** |
| **`textile_weaving_tabular`** | G | `data/textile_weaving_tabular/` | 7 files | 40.04 MB | Tabular CSV | Machine logs | 121,148 production records: loom RPM, stops, breaks, linear density | CC BY 4.0 / Azmine Toushik Wasi (Mendeley/Kaggle 2023) | **DOWNLOADED_VERIFIED** |
| **`textile_knitting_tabular`** | G | `data/textile_knitting_tabular/` | 1 file | 3.07 MB | Tabular CSV | Machine logs | 12,569 knitting records: loop length, GSM, yarn count, machine gauge | CC BY 4.0 / Toufique (Kaggle 2023) | **DOWNLOADED_VERIFIED** |
| **`roboflow_warp_weft_prod`** | B | Remote Hosted | 52 base (274 aug) | Remote API | $875\times 879\text{ px}$ | Uncalibrated consumer macro | Bounding boxes for longitudinal warp and weft yarn strands | CC BY 4.0 / Ayushi IT (`ayushiit/warp-weft-new-prod`) | **REMOTELY_INDEXED** |
| **`roboflow_fabric_lby7e`** | B | Remote Hosted | 74 base (308 aug) | Remote API | $1792\times 1184\text{ px}$ | Dedicated `measure` bounding box | Polygon masks for interlacing surface yarn floats | CC BY 4.0 / Cheomseongdae (`cheomseongdae/fabric-lby7e`) | **REMOTELY_INDEXED** |
| **`zenodo_cdatp_textiles`** | C | Remote Zenodo | 406 scans | ~15.0 GB | $3840\times 3840\text{ px}$ | 605 DPI ($S = 238.19\text{ px/cm}$) | Calibrated photometric stereo PBR surface maps (Base, Normal, Roughness) | CC BY-SA 4.0 / Kunzelmann et al. (`10.5281/zenodo.21872364`) | **PARTIAL_DOWNLOAD_REQUIRED** |
| **`mendeley_raw_fabrid`** | D | Remote Mendeley | 709 images | 450 MB | $1792\times 1024\text{ px}$ | 4 px/mm ($S = 40.0\text{ px/cm}$) | Industrial line-scan Basler camera; 204 binary defect masks | CC BY 4.0 / Perez-Llorens et al. (`10.17632/db6g85xsyg.1`) | **INACCESSIBLE (reCAPTCHA v3)** |
| **`mendeley_fabrid`** | D | Remote Mendeley | 2,407 images | 350 MB | Varied RGB | Uncalibrated apparel | Missing yarn, needle marks, holes, stains, defect-free | CC BY 4.0 / Ahmed et al. (`10.17632/vncdwps24r.3`) | **INACCESSIBLE (reCAPTCHA v3)** |

---

## 3. Discrepancy Resolution & Audit Log

1. **Client Specimen Image Resolution ($1200\times 1600$ vs $2448\times 3264$):**
   * *Observed Discrepancy:* Early text references in `dataset_registry.json` indicated a resolution of $2448\times 3264$.
   * *Physical Audit:* Reading `data/samples/test.png` with OpenCV returns exactly `(1600, 1200, 3)`. File size is $2,595,080\text{ bytes}$ with SHA-256 `fad7284aab78f25ddcd75cd39433b06a4301360132d6156db7b2d5d1c1da853b`.
   * *Resolution:* All optical calculations for Specimen 2 are strictly based on the real $1200\times 1600$ array.
2. **FabricNET File Count ($130$ vs $131$):**
   * *Observed Discrepancy:* Benchmark scripts reference 130 specimens, but directory contains 131 files.
   * *Physical Audit:* Directory contains 130 JPEG images (`W001.jpg` through `W130.jpg`) plus 1 metadata spreadsheet `FabricNET_database.xlsx`.
   * *Resolution:* Image count is 130; file count is 131.
3. **AITEX Database Structure ($245$ vs $354$):**
   * *Observed Discrepancy:* Paper states 245 images, directory has 354 files.
   * *Physical Audit:* 245 raw fabric scans (140 defect-free in `data/aitex_database/NODefect_images/`, 105 defective in `Defect_images/`) plus 109 pixel binary defect masks (`_mask.png`).
   * *Resolution:* Base image count is 245; total file count including masks is 354.
4. **Harvard Dataverse Extraction ($437$ vs $438$):**
   * *Physical Audit:* ZIP archive contains 437 files ($42.5\text{ MB}$ uncompressed); adding `manifest.json` generated during automated extraction results in 438 files ($21.26\text{ MB}$ on disk).
