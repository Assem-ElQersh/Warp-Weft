# Automated Fabric Warp & Weft Thread Density Analysis (1 cm)

## 1. Project Overview & Operational Objective
The objective of this project is to develop an automated computer vision pipeline to quantify the physical thread density—specifically the number of warp threads (vertical) and weft threads (horizontal) per 1.0 centimeter ($10,000\,\mu\text{m}$)—from high-resolution macro photography of woven textile samples.

The system is architected to operate under resource constraints (standard laptop CPUs/GPUs, limited network bandwidth, memory footprint $< 500\text{ MB}$, model artifact size $< 50\text{ MB}$) with dual-mode execution support for local machines and Kaggle environments (`/kaggle/input/...` and `/kaggle/working/...` with local fallback logic).

---

## 2. The Provenance Ledger

| The Empirical Finding / Metric | Exact Script/Notebook Name | Analytical Deduction (What this rules out/forces next) |
| :--- | :--- | :--- |
| `ayushiit/warp-weft-new-prod` achieves 95.4% mAP@50 using longitudinal bounding boxes across 52 base macro images (875×879 px) | `https://universe.roboflow.com/ayushiit/warp-weft-new-prod` | Proves bounding box detectors can isolate individual yarn lines; rules out using this dataset alone for metric 1 cm density due to lack of embedded metric spatial calibration scale. |
| `cheomseongdae/fabric-lby7e` segments individual surface float polygons with 35.7% mIoU across 74 macro images (1792×1184 px) with dedicated `measure` class | `https://universe.roboflow.com/cheomseongdae/fabric-lby7e` | Low mIoU rules out raw semantic float segmentation for direct thread counting; confirms utility of `measure` class for automated in-frame pixel-to-millimeter calibration. |
| `fdd-dsbrx/fabric-defect-detections` isolates 8 defect categories with 65.5% mAP@50 across 305 images (1280×1280 px) | `https://universe.roboflow.com/fdd-dsbrx/fabric-defect-detections` | Confirms defect detectors isolate yarn disruptions (missing threads, floats, mispicks); rules out defect models as direct periodic yarn counters. |
| `nexuswho/fabric-defects-dataset` compiles 2,739 images including AITEX (4096×256 px) and Moratuwa datasets | `https://www.kaggle.com/datasets/nexuswho/fabric-defects-dataset` | Wide-web imaging (<1 px per thread) rules out non-macro defect datasets for thread counting; confirms AITEX defect-free subset as benchmark for macro texture analysis. |
| `nxb4shgs9h/1` provides 121,148 industrial production records across 18 columns including target EPI/PPI specs | `https://data.mendeley.com/datasets/nxb4shgs9h/1` | Rules out tabular data for direct visual thread counting; confirms industrial ground truth distribution for commercial fabric densities (EPI/PPI). |
| `mwasifanwar/neurofabric-ai` implements 2D FFT spectral peak extraction and GLCM texture features alongside PyTorch CNNs | `https://github.com/mwasifanwar/neurofabric-ai` | Validates frequency-domain spectral analysis as mathematically optimal for periodic yarn density extraction without requiring manual per-thread bounding box annotations. |
| `chaeyeon2367/dl-python-ImageDetection` implements 256×256 patch cropping with multi-scale Inception CNNs | `https://github.com/chaeyeon2367/dl-python-ImageDetection` | Validates sub-patch tiling pipeline for processing high-resolution fabric scans on edge GPUs. |
| Nyquist-Shannon sampling threshold requires $\ge 8\text{ to }12\text{ pixels per thread period}$ for optical edge localization | `notebooks/01_optical_and_spectral_sandbox.ipynb` | Establishes minimum spatial resolution bound ($\Delta x \le 20\,\mu\text{m/pixel}$) for fine weave fabrics up to 50 threads/cm. |
| PyTorch 2D FFT (`torch.fft.rfft2` / `fftshift`) calculates orthogonal spatial frequency harmonics $(u_0, v_0)$ in $< 3\text{ ms}$ on CPU with $< 15\text{ MB}$ RAM | `notebooks/01_optical_and_spectral_sandbox.ipynb` | Confirms 2D Fourier spectral analysis as zero-weight, ultra-lightweight, zero-download engine runnable on resource-constrained hardware. |
| Synthetic 400×400 px Plain Weave: True Warp=32, FFT Warp=32 ($\Delta=0$), Proj Warp=31 ($\Delta=1$); True Weft=28, FFT Weft=28 ($\Delta=0$), Proj Weft=27 ($\Delta=1$) | `notebooks/01_optical_and_spectral_sandbox.ipynb` | Confirms 2D FFT extracts exact fundamental spatial frequency with zero boundary truncation error; proves 1D projection requires boundary padding to capture edge yarn crowns; validates consensus engine between both techniques. |
| Roboflow MCP (`https://mcp.roboflow.com/mcp`) & 13 Computer Vision Skills integrated into `.agents/skills` and `.mcp.json` | `https://github.com/roboflow/computer-vision-skills` | Equips workspace with remote Roboflow model inference, dataset manipulation, and workflow capabilities without requiring local storage of heavy weights. |

---

## 3. Executive Cross-Comparative Audit of Literature & Benchmarks

| # | Source URL / Resource | Primary Task & Domain | Base & Augmented Dataset Volume | Native & Model Resolutions | Annotation Format | Model Architecture & Benchmarks |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | [**`ayushiit/warp-weft-new-prod`**](https://universe.roboflow.com/ayushiit/warp-weft-new-prod) | Yarn Detection & Density Counting | **52 base macro images**<br>v1: 274 images<br>v2: 200 images | Native: 875×879 px<br>Model input: 640×640 px | Longitudinal Bounding Boxes & 4-point Polygons covering continuous yarn lines | Roboflow 3.0 Fast (YOLOv8-based)<br>mAP@50: 95.4%<br>Precision: 85.1%<br>Recall: 91.2% |
| **2** | [**`cheomseongdae/fabric-lby7e`**](https://universe.roboflow.com/cheomseongdae/fabric-lby7e) | Surface Float & Metric Scale Segmentation | **74 base cross-weave images**<br>v1: 73, v2: 277, v3: 216, v4: 308, v5: 74, v6: 308 images | Native: 1792×1184 px<br>Model input: 1184×1184 px (grayscale) | Fine multi-point polygon masks for interlacing surface floats + bounding box for physical scale (`measure`) | Roboflow 2.0 Base Semantic Segmentation<br>mIoU: 35.7% |
| **3** | [**`fdd-dsbrx/fabric-defect-detections`**](https://universe.roboflow.com/fdd-dsbrx/fabric-defect-detections) | Textile Structural Defect Segmentation | **305 base images**<br>v1: 731 images<br>v2: 731 images | Native: 640–1280 px<br>Model input: 1280×1280 px (fit black edges) | Instance segmentation polygon masks covering localized defect boundaries | Roboflow 3.0 Nano Segmentation (`roboflow-3-n-seg`)<br>mAP@50: 65.5%<br>Precision: 65.8%<br>Recall: 65.0% |
| **4** | [**`nexuswho/fabric-defects-dataset`**](https://www.kaggle.com/datasets/nexuswho/fabric-defects-dataset) | Fabric Defect Benchmark Aggregation | **2,739 total images**<br>(1,666 defect-free, 1,073 defected) | Multi-resolution:<br>4096×256 px (AITEX)<br>1920×1080 px (Moratuwa Stain)<br>640×360 px (Moratuwa Defect) | Binary PNG masks + image-level classification categories | PyTorch ResNet18/ResNet50 classifiers (>95% accuracy), UNet defect segmentation |
| **5** | [**`zenodo.org/record/7498062`**](https://zenodo.org/record/7498062) (`weaving_dataset`) | Loom Weaving Production Data ETL | Software release (v1.0, 8.2 MB)<br>ETL notebooks & Excel data | Tabular industrial production metrics | Tabular parameters (machine RPM, stops, breaks, linear yarn count) | Python / Jupyter data preprocessing pipeline (`raw_data_all.xlsx`, data cleaning notebooks) |
| **6** | [**`data.mendeley.com/datasets/nxb4shgs9h/1`**](https://data.mendeley.com/datasets/nxb4shgs9h/1) (`full_weaving_dataset`) | Industrial Weaving Loom Production Records | **121,148 rows × 18 columns** (12.7 MB CSV) | 9 months of production time-series records | Industrial attributes: loom ID, warp stop, weft stop, loom RPM, efficiency, Ne count, fabric construction specs | Statistical manufacturing monitoring, correlation between operational parameters and yarn breakages |
| **7** | [**`mwasifanwar/neurofabric-ai`**](https://github.com/mwasifanwar/neurofabric-ai) | Smart Textiles Analysis Framework | Complete Python/FastAPI software suite | Dynamic macro & web input resolutions | Algorithmic feature maps & classification targets | Hybrid CV & Deep Learning: 2D FFT, GLCM, PyTorch ResNet50/EfficientNet (94.2% accuracy), Conditional GAN |
| **8** | [**`chaeyeon2367/dl-python-ImageDetection`**](https://github.com/chaeyeon2367/dl-python-ImageDetection) | Automated Defect Classification Pipeline | 245 base images (AITEX), sliced into 256×256 px patches | 4096×256 px sliced to 256×256 px crops | Patch-level classification labels & binary defect masks (`_mask.png`) | Multi-scale CNN with Inception blocks and residual skip connections; TFRecord serialization; automated Excel reporting |

---

## 4. Optical & Mathematical Resolution Invariants

### 4.1. Nyquist-Shannon Sampling Criteria
To measure thread density (Ends/cm and Picks/cm) in physical fabric samples:
* **Commercial Fabric Densities:**
  * Coarse / Canvas / Medical Gauze: 10–20 threads/cm (yarn period $T = 500\text{--}1000\,\mu\text{m}$).
  * Medium / Plain Shirting / Denim: 25–45 threads/cm (yarn period $T = 220\text{--}400\,\mu\text{m}$).
  * Fine / Poplin / Microfiber: 50–90+ threads/cm (yarn period $T = 110\text{--}200\,\mu\text{m}$).
* **Nyquist-Shannon Bound:** Resolving a periodic signal requires a sampling frequency $f_s > 2 f_{\max}$. In practice, yarn hairiness, shadow variation, and inter-thread gaps demand **$\ge 8\text{ to }12\text{ pixels per yarn width}$** for robust edge localization.
* **Spatial Resolution Formula:**
  $$\Delta x \le \frac{10,000\,\mu\text{m}}{N_{\text{threads/cm}} \times 10\text{ pixels}}$$
  For 50 threads/cm:
  $$\Delta x \le \frac{10,000}{500} = 20\,\mu\text{m/pixel}$$

### 4.2. Metric Calibration Paradigms
Three calibration methods establish the scale factor $S = \text{pixels/cm}$:
1. **Hardware Optical Lock:** USB digital microscope or fixed stand with known focal distance. A calibration graticule or ruler is imaged once:
   $$S = \frac{\Delta x_{\text{pixels}}}{1.0\text{ cm}}$$
2. **Scanner Standard Resolution:** Flatbed scanner imaging at fixed DPI:
   $$S = \frac{\text{DPI}}{2.54}$$
3. **In-Frame Metric Reference (ArUco / Calibration Scale):** Detection of an in-frame scale marker (analogous to the `measure` class in `fabric-lby7e`) yielding automated scale extraction per capture.

---

## 5. Algorithmic Architecture for Resource-Constrained Execution

To eliminate heavy model downloads (>6 GB) and prevent hardware bottlenecks on low-spec laptops, the pipeline employs a **hybrid analytical framework**:

```mermaid
flowchart TD
    A["Raw Fabric Sample Image"] --> B["Spatial Calibration Engine"]
    B --> C["1.0 cm x 1.0 cm ROI Cropper"]
    C --> D["Grayscale & CLAHE Enhancement"]
    D --> E["Radon / Hessian Skew Rectification Engine"]
    
    E --> F1["Engine 1: PyTorch 2D FFT Spectral Analysis"]
    E --> F2["Engine 2: 1D Spatial Projection Profile Engine"]
    
    F1 --> G1["Fundamental Harmonic Peaks (u0, v0)"]
    F2 --> G2["Prominence-Filtered Spatial Peak Counting"]
    
    G1 --> H["Cross-Verification & Consensus Engine"]
    G2 --> H
    H --> I["Outputs: Ends/cm (Warp), Picks/cm (Weft), Thread Spacing"]
```

### Algorithmic Advantages:
1. **Zero Model Download Overhead:** Employs mathematical signal processing and PyTorch tensor operations (`torch.fft`).
2. **Sub-Second Execution:** Processes a 1 cm² ROI in $< 10\text{ ms}$ on standard laptop CPUs.
3. **Memory Footprint:** Operates within $< 100\text{ MB}$ of system RAM.
4. **Environment Portability:** Fully functional offline with zero cloud API dependencies.

---

## 6. Implementation Notebook Directory Structure

All implementation code is strictly maintained as `.ipynb` files:

```
Warp Weft Project/
├── README.md                                    # Central Project Memory & Provenance Ledger
├── data/
│   ├── synthetic/                               # Synthetically generated micro-fabrics with known ground truth
│   └── samples/                                 # Real macro textile test captures
├── notebooks/
│   ├── 01_optical_and_spectral_sandbox.ipynb    # Mathematical validation of 2D FFT & 1D projection
│   ├── 02_skew_rectification_engine.ipynb       # Automatic thread rotation & alignment
│   ├── 03_end_to_end_thread_counter.ipynb       # Integrated production pipeline for 1 cm analysis
│   └── 04_lightweight_cnn_verifier.ipynb        # PyTorch lightweight verification (optional edge CNN)
└── results/
    ├── output.txt                               # Raw mathematical outputs from notebook runs
    └── output.json                              # Structured verification metrics
```
