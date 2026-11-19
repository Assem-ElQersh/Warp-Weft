# The mechanistic justification for this step is: establish formal scientific documentation for the Master Textile Dataset Registry, codifying the metrology taxonomy (Categories A through G), physical calibration requirements (D = S / Delta), optical resolution limits (Nyquist criterion), and data governance protocols.

# Master Textile Dataset Registry & Metrology Audit

## 1. Executive Metrology Overview
Physical thread counting—quantifying warp ends/cm and weft picks/cm—is a **physical metrology problem**, distinct from classification or standard object detection. The fundamental physical equation relating image pixels to physical thread density is:

$$D = \frac{S}{\Delta}$$

where:
- $D$ is the physical thread density in **threads/cm** (ends/cm or picks/cm).
- $S$ is the spatial calibration scale in **pixels/cm** ($S_x$ horizontally, $S_y$ vertically).
- $\Delta$ is the spatial period (inter-yarn pitch or spacing) in **pixels/thread**.

Without calibrated physical scale $S$, an algorithm operating purely in pixel space cannot distinguish between a coarse canvas photographed up close (e.g. 15 threads/cm at 60 px/thread) and a fine silk photographed from a distance (e.g. 60 threads/cm at 60 px/thread).

---

## 2. Dataset Metrology Taxonomy (Categories A through G)

Every candidate dataset in this repository is strictly assigned to one of seven functional categories:

| Taxonomy Category | Category Definition | Core Attributes | Direct Usability for Physical Thread Density | Example Datasets |
| :--- | :--- | :--- | :--- | :--- |
| **Category A** | **Physical Density Labels** | Paired optical images and certified ground-truth ends/cm and picks/cm | **Gold Standard Ground Truth** for end-to-end metrology validation | `fabricnet`, `client_reference_specimens` |
| **Category B** | **Yarn-Level Segmentation / Detection** | Pixel-level masks, continuous centerlines, or bounding boxes on individual yarns | **High Relevance**: Enables spatial pitch ($\Delta$) measurement when paired with metric scale $S$ | `fiberdefect_ct`, `cheomseongdae/fabric-lby7e`, `ayushiit/warp-weft-new-prod` |
| **Category C** | **Textile Appearance / Surface Physics** | High-resolution multi-view, SVBRDF normal maps, or calibrated flatbed scans | **High Structural Relevance**: Isolates 3D yarn crown geometry without surface dye bias | `cdatp`, `ten_fabrics_dataset` |
| **Category D** | **Defect / Missing-Yarn Disruption** | Industrial web scans and factory frames labeled with yarn disruptions (broken ends, mispicks) | **Validation of Discontinuity Only**: **DO NOT CONFLATE WITH THREAD COUNT**. Lacks periodic thread ground truth. | `raw_fabrid`, `aitex_afid`, `fabrid`, `tsfabrics`, `dme_fabric_defects`, `fdd-dsbrx` |
| **Category E** | **Texture / Statistical Microtexture** | Multi-illumination, multi-angle photometric reflectometry with statistical texture descriptors | **Filter Benchmark**: Validates illumination-invariant Gabor, GLCM, and Radon angle estimation | `harvard_microtexture`, `tilda_textile` |
| **Category F** | **Synthetic Simulation** | Analytically generated yarn waveforms with zero-uncertainty mathematical ground truth | **Unit Testbed**: Establishes exact baseline precision without physical measurement error | `synthetic_micro_swatches` |
| **Category G** | **Auxiliary Tabular** | Industrial loom and knitting machine manufacturing parameters (EPI, PPI, yarn counts) | **Statistical Prior Only**: Defines physical industrial distributions of commercial fabrics | `textile_weaving_tabular`, `textile_knitting_tabular` |

---

## 3. Master Dataset Inventory Matrix

| Dataset ID | Modality & Optical Setup | Native Resolution | Physical FOV / Scale ($S$) | Sample Count & Storage | Taxonomy | Usability / Relevance | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`fabricnet`** | USB Optical Microscope + Ring LED | $640 \times 480\text{ px}$ | $5.0 \times 4.0\text{ mm}$<br>$S_x=1280, S_y=1200\text{ px/cm}$ | 130 samples<br>$13.36\text{ MB}$ | **A** | Gold-standard microscope density benchmark | `VERIFIED_LOCAL` |
| **`client_reference_specimens`** | Handheld Smartphone Camera | $1080 \times 1920\text{ px}$ | $41.0 \times 92.1\text{ mm}$<br>$S_x=263.5, S_y=208.4\text{ px/cm}$ | 6 captures<br>$10.02\text{ MB}$ | **A** | Certified ASTM D3775 factory acceptance | `VERIFIED_LOCAL` |
| **`synthetic_micro_swatches`** | Physics-Simulated Waveforms | $256 \times 256\text{ px}$ | $10.0 \times 10.0\text{ mm}$<br>$S=400.0\text{ px/cm}$ | 120 swatches<br>$0.67\text{ MB}$ | **F** | Zero-uncertainty unit testbed | `VERIFIED_LOCAL` |
| **`fiberdefect_ct`** | Synchrotron 3D Micro-CT | $512 \times 512 \times 1000\text{ vx}$ | $0.77 \times 0.77 \times 1.5\text{ mm}$<br>$S=6666.7\text{ vx/cm}$ | 12 volumes<br>$397\text{ MB}$ | **B** | True 3D yarn morphology and centerlines | `INDEXED_REMOTE` |
| **`cheomseongdae/fabric-lby7e`** | Grayscale Macro Camera + In-Frame Ruler | $1792 \times 1184\text{ px}$ | Approx. $20 \times 15\text{ mm}$<br>Dynamic ruler scale | 308 images<br>$100\text{ MB}$ | **B** | Surface float polygons + `measure` scale class | `AUDITED_REMOTE` |
| **`ayushiit/warp-weft-new-prod`** | Macro Camera Photography | $875 \times 879\text{ px}$ | Uncalibrated pixel window | 274 images<br>$56\text{ MB}$ | **B** | Yarn bounding boxes (NMS suppression alert) | `AUDITED_REMOTE` |
| **`ayushiit/warp-weft-detection-june-2024`**| Macro Camera Photography | $640 \times 640\text{ px}$ | Uncalibrated pixel window | 297 images<br>$60\text{ MB}$ | **B** | Yarn bounding boxes | `AUDITED_REMOTE` |
| **`cdatp`** | Photometric Stereo Dome (16 LEDs) | $3840 \times 3840\text{ px}$ | $100 \times 100\text{ mm}$<br>$S=384.0\text{ px/cm}$ | 406 fabrics<br>$72.9\text{ GB}$ | **C** | Surface normal maps isolating yarn crowns | `INDEXED_REMOTE` |
| **`ten_fabrics_dataset`** | Calibrated 300 DPI Flatbed Scanner | $256 \times 256\text{ px}$ | $21.7 \times 21.7\text{ mm}$<br>$S=118.11\text{ px/cm}$ | 2,969 crops<br>$423.22\text{ MB}$ | **C** | Calibrated scanner baseline | `VERIFIED_LOCAL` |
| **`harvard_microtexture`** | Photometric Reflectometer (16 Angles) | $1280 \times 1024\text{ px}$ | $25.6 \times 20.5\text{ mm}$<br>$S=500.0\text{ px/cm}$ | 112 images<br>$120\text{ MB}$ | **E** | Microtexture statistical descriptors | `INDEXED_REMOTE` |
| **`tilda_textile`** | Controlled Lab Camera (3 Lights, 4 Angles)| $768 \times 512\text{ px}$ | Fixed stand distance<br>Uncalibrated | 3,200 images<br>$1.2\text{ GB}$ | **E** | Multi-illumination invariance benchmark | `RESTRICTED_ACCESS_PENDING_REGISTRATION` |
| **`raw_fabrid`** | Industrial Web Scan & Raw Frames | $2048 \times 2048\text{ px}$ | Uncalibrated macro web | 709 images<br>$1.5\text{ GB}$ | **D** | Broken end/pick defect localization | `INDEXED_REMOTE` |
| **`aitex_afid`** | Industrial Web Line-Scan Cameras | $4096 \times 256\text{ px}$ | $1.0\text{--}1.5\text{ m}$ web width<br>$S<35\text{ px/cm}$ | 354 images<br>$168.05\text{ MB}$ | **D** | Macro web inspection (sub-Nyquist) | `VERIFIED_LOCAL` |
| **`fabrid`** | Industrial Surface Inspection | $1024 \times 1024\text{ px}$ | Uncalibrated | 2,407 images<br>$2.5\text{ GB}$ | **D** | Industrial defect benchmark | `INDEXED_REMOTE` |
| **`tsfabrics`** | High-Speed Loom Inspection Video | $1920 \times 1080\text{ px}$ | Line speed synchronized | 93,000 frames<br>$100.0\text{ GB}$ | **D** | Video motion blur and loom vibration | `INDEXED_REMOTE` |
| **`dme_fabric_defects`** | Laboratory Test Bench Camera | $768 \times 576\text{ px}$ | Uncalibrated | 520 images<br>$150\text{ MB}$ | **D** | Structural defect classification | `INDEXED_REMOTE` |
| **`roboflow_fdd_defect`** | Macro Defect Photography | $1280 \times 1280\text{ px}$ | Uncalibrated | 731 images<br>$150\text{ MB}$ | **D** | Yarn flaw instance segmentation | `AUDITED_REMOTE` |

---

## 4. Optical Resolution & Nyquist-Shannon Boundaries

To reliably detect individual yarn crowns and inter-yarn boundaries:
1. **Sampling Threshold**: A minimum of **$8\text{ to }12\text{ pixels per yarn period}$** ($\Delta \ge 8\text{ px}$) is required to resolve yarn edges without phase aliasing.
2. **Physical Criterion**:
   $$\Delta x_{\text{max}} = \frac{10,000\,\mu\text{m}}{D_{\text{max}} \times 10\text{ pixels}}$$
   - For $D = 50\text{ ends/cm}$, pixel pitch must be $\Delta x \le 20.0\,\mu\text{m/px}$ ($S \ge 500\text{ px/cm}$).
   - In `fabricnet`, $\Delta x = 7.81\,\mu\text{m/px}$ ($S_x = 1280\text{ px/cm}$), yielding $\Delta = 25.6\text{ px}$ at $50\text{ ends/cm}$, comfortably exceeding Nyquist.
   - In `aitex_afid`, line-scan resolution ($S \approx 35\text{ px/cm}$) yields $\Delta \approx 0.7\text{ px}$, causing total spatial aliasing. AITEX is strictly unsuitable for direct thread counting.

---

## 5. Data Access, Download, and Storage Governance

1. **Local and Free Public Data**:
   - `data/fabricnet/`: Verified local ($13.36\text{ MB}$).
   - `data/ten_fabrics/`: Verified local ($423.22\text{ MB}$).
   - `data/aitex_database/`: Verified local ($168.05\text{ MB}$).
   - `data/synthetic/`: Verified local ($0.67\text{ MB}$).
   - Total current local footprint: **$5.07\text{ GB}$** (including tabular data).
2. **Large Public Remote Data**:
   - `CDATP` ($72.9\text{ GB}$): Do NOT download full archive to local disk. Retrieve sample 5-fabric sub-pack ($1.2\text{ GB}$) when normal map validation is executed.
   - `FiberDefect-CT` ($397\text{ MB}$): Can be retrieved directly via Zenodo DOI `10.5281/zenodo.5574312`.
3. **Restricted Access Data**:
   - `TILDA Textile Database`: Requires formal registration with Albert-Ludwigs-Universität Freiburg (Computer Vision Group).
   - **Protocol**: The access procedure is fully documented; registration requests must be submitted directly by the user/organization. No automated bypassing of auth barriers.

---

## 6. Zero-Leakage Specimen Partitioning Invariant
Random patch cropping across a single fabric swatch introduces extreme **data leakage** because adjacent crops share identical yarn weave tension, dye batch, and optical lighting. All dataset splits must strictly adhere to **Specimen-Level Grouped Splitting**:
- Training, Validation, and Test sets must never contain patches or augmented variants of the same fabric specimen or capture session.
- Grouping identifier: `specimen_id` or `fabric_id`.
