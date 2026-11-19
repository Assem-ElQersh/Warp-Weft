# EXECUTION BASELINE AUDIT — PHASE 0
**Repository:** Warp & Weft AI (`/home/assem-elqersh/Desktop/Warp Weft Project/`)  
**Canonical Branch:** `main` (Tracking `origin/main` @ commit `8f0e7ce`)  
**Audit Timestamp:** 2026-11-19T21:55:00+02:00  
**Authorship / Role:** Principal ML Engineer, Computer Vision Researcher, Textile Metrology Lead  

---

## 1. Verified Repository State & Working Tree Context

### 1.1. Git Topology
* **Active Branch:** `main` (sole canonical branch; obsolete local feature branches `feat/reconciled-research-validation` and `feat/comprehensive-textile-model-research` deleted).
* **Head Commit:** `8f0e7ce` (`feat(ui): add interactive info button and explanation to Pixels per Centimeter input`).
* **Remote Tracking:** Synced with `origin/main`.
* **Working Tree Protection:**
  - `data/samples/test.png` ($1200\times 1600$, $2.47\text{ MB}$, SHA-256 `fad7284aab78f25ddcd75cd39433b06a4301360132d6156db7b2d5d1c1da853b`) is strictly ignored by `.gitignore` lines 128–129 (`data/samples/*`, `!data/samples/.gitkeep`).
  - Large external weights and datasets are ignored by `.gitignore`:
    - `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth` ($84.20\text{ MB}$, matched by `*.pth`)
    - `experiments/models/checkpoints/segformer_b0/model.safetensors` ($14.34\text{ MB}$, matched by `*.safetensors`)
    - `experiments/data_acquisition/downloads/NithinAruswamy_TextileResearchDataset.zip` ($20.72\text{ MB}$, matched by `*.zip`)
    - `experiments/data_acquisition/downloads/harvard_microtexture/` ($42.5\text{ MB}$, matched by `downloads/`)
    - `docs/Papers/*.pdf` ($8.89\text{ MB}$, matched by `docs/Papers/*.pdf`)

---

## 2. Environment & Hardware Profile

```text
Host Architecture: Linux x86_64
Python Interpreter: /home/assem-elqersh/anaconda3/bin/python (v3.13.9 | Anaconda, Inc.)
PyTorch Framework: 2.13.0+cu130
Torchvision: 0.28.0+cu130
OpenCV: 5.0.0
SciPy: 1.16.3
NumPy: 2.3.5
scikit-learn: 1.7.2
XGBoost: 3.2.0
Transformers: 5.19.0
timm: 1.0.29
Pillow: 12.3.0
CUDA Capability: True
Device: NVIDIA GeForce RTX 3050 Ti Laptop GPU (1 device)
Total VRAM: 3.68 GB (Active allocated: 0.00 MB)
System RAM: Total 15.41 GB, Available 10.41 GB (32.5% utilized)
Storage Capacity: Total 467.35 GB, Free 23.16 GB
```

---

## 3. Automated Test Suite Verification

Execution command: `/home/assem-elqersh/anaconda3/bin/python -m pytest tests/`
* **Result:** **87 of 87 tests passed (100% success rate)** in $5.06\text{ seconds}$.
* **Test Suite Coverage:**
  - `test_benchmark_artifact_integrity.py`: 2 tests
  - `test_benchmark_integrity.py`: 4 tests
  - `test_calibration.py`: 6 tests
  - `test_calibration_uncertainty.py`: 3 tests
  - `test_client_image_failure_regression.py`: 2 tests
  - `test_data_engine.py`: 6 tests
  - `test_fusion.py`: 4 tests
  - `test_ground_truth_protocol.py`: 7 tests
  - `test_grouped_splits.py`: 3 tests
  - `test_metrology_metrics.py`: 4 tests
  - `test_model_registry.py`: 4 tests
  - `test_notebook_integrity.py`: 2 tests
  - `test_orientation.py`: 2 tests
  - `test_roi.py`: 3 tests
  - `test_smartphone_regression.py`: 1 test
  - `test_spatial.py`: 2 tests
  - `test_specimen_workflow.py`: 4 tests
  - `test_spectral.py`: 2 tests
  - `test_validation_metrics.py`: 7 tests
  - `test_web_modes.py`: 4 tests
  - `test_web_server_integration.py`: 10 tests
  - `test_web_ui_contract.py`: 5 tests
* **Static Syntax Checks:** `/home/assem-elqersh/anaconda3/bin/python scripts/check_inline_javascript.py` $\implies$ 1 inline script verified, 0 syntax errors.

---

## 4. Local Dataset Forensics & File Integrity

Audited using PIL byte-level verification across all local dataset directories:

| Dataset Identifier | Local Directory | File Pattern | Total Files | Valid Images | Corrupted Files | Native Image Resolution | Ground Truth Labels Provided |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`fabricnet`** | `data/fabricnet/` | `*.jpg` | 130 | 130 | 0 | $640\times 480$ (RGB) | Specimen-level warp/weft density (ends/picks per cm) in `FabricNet_parameters.xlsx` |
| **`synthetic_micro_swatches`** | `data/synthetic/` | `*.png` | 3 | 3 | 0 | $400\times 400$, $800\times 800$ (Grayscale) | Exact known pitch ($\Delta_x=12.5, \Delta_y=14.28\text{ px}$), warp 32, weft 28 |
| **`client_reference_specimens`** | `data/samples/` | `*.png` | 2 | 2 | 0 | $1200\times 1600$, $391\times 278$ | Specimen 2 manual counts: Warp 31 ends/cm, Weft 27 picks/cm |
| **`ten_fabrics_dataset`** | `data/ten_fabrics/` | `**/*.png` | 2,969 | 2,969 | 0 | $256\times 256$ (RGB) | 10 weave pattern classes (plain, twill, satin, etc.); defect masks |
| **`aitex_afid`** | `data/aitex_database/` | `**/*.png` | 354 | 354 | 0 | $4096\times 256$, $3796\times 256$ | Industrial line-scan loom captures; defect pixel masks |
| **`harvard_microtexture`** | `experiments/data_acquisition/downloads/harvard_microtexture/` | `**/*.jpg` | 190 | 190 | 0 | $512\times 512$, $640\times 480$ | 100x optical microscopy swatches + `features.csv` (40+ texture descriptors) |

---

## 5. Checkpoint Inventory & Model Architecture Status

| Checkpoint Name | Size (Bytes) | SHA-256 (16-char) | Framework | Architecture | Purpose & Empirical Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `unet_yarn_segmentation.pt` | 7,750,029 ($7.39\text{ MB}$) | `d68a7479c464f929` | PyTorch | `WarpWeftUNet` (1.93M params) | Trained on synthetic micro-swatches. Fails on real smartphone captures ($8.50/6.32\text{ threads/cm}$). Flagged `available: false`. |
| `net.h5` | 93,740,448 ($89.39\text{ MB}$) | `d2439b2fd7c94154` | Keras / TF | 14-layer Dual-Illumination FCN | Requires paired 6-channel front/back-lit inputs. Incompatible with standard single-exposure microscopy or smartphones. |
| `dinov2_vits14_pretrain.pth` | 88,289,404 ($84.20\text{ MB}$) | `f2f5d5df475ec750` | PyTorch | DINOv2 ViT-S/14 (22.06M params) | Pretrained self-supervised visual backbone. Excluded by `.gitignore`. Used for feature extraction / weave classification. |
| `model.safetensors` | 15,036,944 ($14.34\text{ MB}$) | `6ae39addd01de6b1` | HuggingFace | SegFormer-B0 (3.75M params) | Pretrained semantic segmentation backbone. Excluded by `.gitignore`. Primary candidate for lightweight yarn segmentation. |

---

## 6. Reproduced Baseline Benchmark Metrics (FabricNET $N=130$)

Reproduced directly from `experiments/learned_models/results/fabricnet_test_benchmark.json` and `results/fabricnet_benchmark.json`:

```text
=== RAW DETERMINISTIC CANDIDATE ESTIMATES (All 130 Specimens) ===
Warp MAE: 13.43 threads/cm
Warp RMSE: 18.67 threads/cm
Warp Mean Bias Error (MBE): -12.82 threads/cm
Warp Max Error: 45.90 threads/cm
Warp % Within +/- 1.0: 15.4%
Warp % Within +/- 2.0: 26.1%
Warp Bland-Altman Mean Diff: -12.82 threads/cm
Warp Bland-Altman 95% LoA: [-39.53, +13.89] threads/cm

Weft MAE: 11.26 threads/cm
Weft RMSE: 15.91 threads/cm
Weft Mean Bias Error (MBE): -10.32 threads/cm
Weft Max Error: 39.87 threads/cm
Weft % Within +/- 1.0: 16.9%
Weft % Within +/- 2.0: 27.7%
Weft Bland-Altman Mean Diff: -10.32 threads/cm
Weft Bland-Altman 95% LoA: [-34.16, +13.52] threads/cm

Composite Joint % (Both within +/- 2.0): 6.15%
Mean Latency: 219.43 ms/specimen

=== CONSENSUS-GATED ACCEPTED SUBSET ===
Warp Accepted Count: 25 / 130 (19.23% coverage, 80.77% rejected as NEEDS_REVIEW)
Warp Accepted MAE: 2.48 threads/cm (80.0% within +/- 2.0)
Weft Accepted Count: 32 / 130 (24.62% coverage, 75.38% rejected as NEEDS_REVIEW)
Weft Accepted MAE: 2.38 threads/cm (62.5% within +/- 2.0)
```

---

## 7. Known Scientific Limitations & Critical Boundaries

1. **Circular Calibration on Client Specimen:** The scales $S_x=263.5, S_y=208.4\text{ px/cm}$ were back-calculated from observed yarn period and manual counts. They demonstrate that spatial peak detection works when scale is correct, but do NOT prove independent calibration.
2. **Specimen-Only Physical Ground Truth:** Only one macroscopic photograph of Specimen 2 was supplied. The 5 regional ROIs are digital spatial crops, not independently photographed physical pick-glass placements.
3. **Lack of Real-Domain Yarn Segmentation Masks:** No public textile dataset provides pixel-level yarn centerline or float instance masks on real smartphone captures. All existing segmentation models were trained on synthetic swatches.
4. **Magnification Domain Gap:** Feature regressors (Random Forest, XGBoost) trained on USB microscopy ($1280\text{ px/cm}$) produce $+21.05$ warp and $+41.55$ weft errors on smartphone captures ($263.5\text{ px/cm}$) due to implicit pixel scale memorization.
5. **Discrete Integer Quantization Error:** Integer pixel peak finding on $8\text{ px}$ thread periods induces $\pm 1.8\text{ to }3.7\text{ threads/cm}$ quantization jumps. Parabolic sub-bin interpolation is mathematically mandatory.
