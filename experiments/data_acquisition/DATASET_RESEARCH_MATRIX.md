# Master Textile Dataset Research & Acquisition Matrix

This matrix synthesizes all investigated public, institutional, and in-repository textile datasets. Datasets are categorized according to their mathematical and physical utility for optical warp and weft thread density measurement.

---

## 1. Relevance Classification Taxonomy

* **Category A — Direct Physical Density Supervision:** Datasets providing ground-truth thread counts ($\text{ends/cm}, \text{picks/cm}$) and calibrated spatial dimensions.
* **Category B — Yarn-Level Annotations:** Datasets providing pixel-level or polygon annotations of individual warp/weft strands, centerlines, or float points.
* **Category C — Fabric Structure & Calibrated Scans:** Datasets with known spatial resolution ($\text{DPI}$) or structured weave architecture records.
* **Category D — Defect & Industrial Web Inspection:** Datasets capturing structural anomalies (missing threads, broken ends/picks) across industrial lines.
* **Category E — Optical Microscopy & Fiber Texture:** Datasets capturing fine microtextures under high optical magnification ($>50\times$).
* **Category F — Synthetic Generative Datasets:** Physics-simulated fabric models with mathematically exact pixel masks and centerlines.

---

## 2. Comprehensive Cross-Dataset Evaluation Matrix

| Dataset Identifier | Cat. | Acquisition Modality | Image Count | Resolution & FOV | Metric Calibration ($S$) | Ground Truth Annotations | License | Access Method | Scientific Priority |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **`fabricnet_microscopy`** | **A** | USB Digital Microscope | 130 RGB | $640\times 480\text{ px}$<br>($5\times 4\text{ mm}$ FOV) | $S_x=1280.0\text{ px/cm}$<br>$S_y=1200.0\text{ px/cm}$ | Warp ($20\text{--}62$), Weft ($15\text{--}93$), Mass, Weave pattern | CC BY 4.0 | Direct in repo / Hugging Face | **HIGHEST** |
| **`client_reference_specimen`** | **A** | Macro Smartphone Rig | 1 ($5$ regions) | $2448\times 3264\text{ px}$<br>($9.3\times 15.7\text{ cm}$) | $S_x=263.5\text{ px/cm}$<br>$S_y=208.4\text{ px/cm}$ | 5-region manual count: Warp $31$, Weft $27$ ($\pm 2$) | Proprietary | In repo (`data/samples/`) | **CRITICAL** |
| **`zenodo_cdatp_textiles`** | **C** | Vizoo xTex Scanning | 406 materials<br>($2,436$ PBR maps) | $3840\times 3840\text{ px}$<br>($16.1\times 16.1\text{ cm}$) | **$605\text{ DPI}$ fixed**<br>($S=238.19\text{ px/cm}$) | Known metric scale, PBR normal, displacement, roughness | CC BY-SA 4.0 | Zenodo REST API (`21872364`) | **VERY HIGH** |
| **`harvard_textile_microtexture`**| **E** | Raspberry Pi HQ + 100x Lens| 100+ images | Microtexture crops | High optical magnification | 40+ quantitative Haralick, LBP, and wavelet metrics | **CC0 (Public Domain)**| Direct HTTP (21.7 MB) | **HIGH** |
| **`roboflow_fabric_lby7e`** | **B** | Macro Camera + Ruler | 74 base / 308 aug. | $1792\times 1184\text{ px}$ | In-frame scale class (`measure`) | Polygon masks for warp/weft float points + ruler | CC BY 4.0 | Roboflow API / Export | **HIGH** |
| **`roboflow_warp_weft_new_prod`** | **B** | Digital Camera | 52 base / 274 aug. | $875\times 879\text{ px}$ | Unscaled ($640\times 640\text{ px}$) | Longitudinal bounding boxes for warp and weft strands | CC BY 4.0 | Roboflow API / Export | **MEDIUM** |
| **`mendeley_raw_fabrid`** | **D** | Basler Line-Scan Camera | 709 grayscale | $1792\times 1024\text{ px}$ | Industrial moving web | Pixel masks for defected and clean woven swatches | CC BY 4.0 | Mendeley REST API | **MEDIUM** |
| **`mendeley_fabrid`** | **D** | Real-world Cameras | 2,407 RGB | Variable | Uncalibrated optical capture | 5 classes: Missing Yarn, Needle Mark, Hole, Stain, Clean | CC BY 4.0 | Mendeley REST API | **MEDIUM** |
| **`ten_fabrics`** | **C** | Calibrated Flatbed Scan | 2,969 PNG | $256\times 256\text{ px}$ | **$300\text{ DPI}$ fixed**<br>($S=118.11\text{ px/cm}$) | 10 fabric types, 27 defect types, block grid binary labels | Academic Open | In repo (`data/ten_fabrics/`) | **HIGH** |
| **`aitex_database`** | **D** | Industrial Web Line-Scan | 354 PNG | $4096\times 256\text{ px}$ | Web width ($1.0\text{--}1.5\text{ m}$) | 12 industrial defect classes (broken end, broken pick) | Academic Open | In repo (`data/aitex_database/`) | **MEDIUM** |
| **`synthetic_yarn_lattices`** | **F** | Procedural Physics Generator| 1,000+ synthetic | $512\times 512\text{ px}$ | $S=512.0\text{ px/cm}$ | Exact pixel centerlines, binary masks, ground-truth pitch | MIT (Internal) | Local Python generator | **CRITICAL** |
| **`tsfabrics`** | **D** | Circular Knitting Monitor | 93,196 images | $800\times 640\text{ px}$ | Machine aperture | Circular knitting defects (courses and wales, loops) | CC BY 4.0 | Figshare (`29573381`) | **EXCLUDE** (Knitting) |

---

## 3. Methodological Usability Analysis

### 3.1. Direct Physical Density Supervision (Category A)
Only datasets in Category A provide explicit mathematical truth for evaluating factory acceptance ($\pm 2.0\text{ threads/cm}$).
* **FabricNET** allows testing spectral and spatial algorithms in high-magnification microscopy where individual yarn crowns are $15\text{--}30\text{ pixels}$ wide.
* **Client Specimen 2** is the singular physical ground truth for the actual client factory smartphone workflow. Because $N=1$, it is reserved strictly as a locked test benchmark.

### 3.2. Surface Geometry with Known Physical Scale (Category C & E)
* **Zenodo CDATP:** Provides $3840\times 3840$ textures with an exact, immutable physical scale of $605\text{ DPI}$ ($S = 238.19\text{ px/cm}$). This scale closely mirrors the client smartphone stand profile ($S_x=263.5, S_y=208.4\text{ px/cm}$). Selected downloads of CDATP woven swatches provide ideal zero-distortion testbeds for spatial frequency estimators.
* **Harvard Textile Microtexture Dataset:** Provides high-magnification ($100\times$) optical images under a CC0 license with quantitative texture vectors, ideal for evaluating feature extractors without license friction.

### 3.3. Structural Yarn Segmentation (Category B & F)
* Pure bounding box detection (YOLOv8) suffers from severe NMS suppression on adjacent yarns.
* Semantic and instance segmentation networks (U-Net, SegFormer, Mask2Former) trained on synthetic procedural yarn lattices (`Category F`) predict continuous yarn probability masks $\hat{M}(x,y)$, which can be skeletonized into discrete physical centerlines.
