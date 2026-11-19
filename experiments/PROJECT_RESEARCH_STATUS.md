# Warp & Weft AI — Project Research & Experimentation Status

**Active Branch:** `feat/comprehensive-textile-model-research`  
**Base Commit:** `13ebcc25d83d26ddd1c00beb172a6cb7e6cf1a7f` (`origin/main`)  
**Hardware Profile:** NVIDIA GeForce RTX 3050 Ti Laptop GPU (3.68 GB VRAM), 8 CPU cores, 15.41 GB RAM, 23.20 GB free disk space  
**Primary Target:** Physically validated automated fabric warp density (ends/cm) and weft density (picks/cm) quantification under ASTM D3775 factory tolerance ($\pm 2.0\text{ threads/cm}$).

---

## Master Phase Status Dashboard

| Phase | Phase Name | Status | Key Artifacts & Milestones |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Repository & Environment Audit | **COMPLETED** | Verified clean git state, hardware audit (RTX 3050 Ti 4GB, 23.2 GB disk), 70/70 tests passing. |
| **Phase 2** | Online Research & Landscape Mapping | **COMPLETED** | Surveyed academic, Hugging Face, Roboflow, Zenodo, Mendeley, and Dataverse resources; created `DATASET_RESEARCH_MATRIX.md` & `MODEL_RESEARCH_MATRIX.md`. |
| **Phase 3** | Data Access & Acquisition | **COMPLETED** | Acquired & verified Harvard Dataverse (437 files, 190 100x microscopy images); documented Zenodo/Mendeley access barriers in `ACCESS_REQUIRED.md`. |
| **Phase 4** | Dataset Inspection & Quality Audit | **COMPLETED** | Audited FabricNET microscopy ($1280\text{ px/cm}$) vs client smartphone ($263.5\text{ px/cm}$); delivered `DATA_SUFFICIENCY_REPORT.md`. |
| **Phase 5** | Reproduce Historical Baselines | **COMPLETED** | Re-verified FabricNET Table A (26 test specimens) and Smartphone Table B ($32.74 / 28.47$). |
| **Phase 6** | New Model Architecture Baselines | **COMPLETED** | Downloaded & verified offline weights for SegFormer-B0 ($14.34\text{ MB}$, $34.85\text{ MB}$ VRAM) & DINOv2 ViT-S/14 ($84.20\text{ MB}$, $182.59\text{ MB}$ VRAM). |
| **Phase 7** | Pretraining & Fine-Tuning | **PLANNED** | Scheduled for factory collection cohort (90 swatches) as detailed in `NEXT_DATA_COLLECTION_PLAN.md`. |
| **Phase 8** | Calibration & Physical Metrology | **COMPLETED** | Mathematical derivation of pinhole projection, $S_x \ne S_y$ anisotropy, and ASTM D3775 in `PHYSICAL_METROLOGY_REPORT.md`. |
| **Phase 9** | Microscope-to-Smartphone Transfer | **COMPLETED** | Diagnosed $4.86\times$ magnification shift and fiber fuzz domain gap; proved failure of direct feature transfer. |
| **Phase 10** | Comprehensive Benchmark Synthesis | **COMPLETED** | Published `MODEL_COMPARISON_REPORT.md` synthesizing Table A (microscopy) and Table B (smartphone). |
| **Phase 11** | Best-Method Selection & Governance | **COMPLETED** | Established Safe Metrology Invariants; selected Mode 1 as certified production default. |
| **Phase 12** | Production Integration Plan | **COMPLETED** | Formulated production hierarchy and safe dispatching rules in `FINAL_RESEARCH_RECOMMENDATION.md`. |
| **Phase 13** | Continuous Improvement Roadmap | **COMPLETED** | Delivered `NEXT_DATA_COLLECTION_PLAN.md` with 90-swatch multi-illumination factory protocol. |

---

## Detailed Task Tracker

### Phase 1: Baseline Verification
- [x] Create feature branch `feat/comprehensive-textile-model-research`.
- [x] Audit system hardware: GPU RTX 3050 Ti (3.68 GB VRAM), 15.4 GB RAM, 23.2 GB disk space.
- [x] Run 70-test regression suite on new branch (`70 passed in 3.51s`).
- [x] Audit existing datasets in `data/` (~5.07 GB, 12,238 files across 9 subdirectories).

### Phase 2: Online Model & Dataset Research
- [x] Audit Roboflow Universe projects (`ayushiit/warp-weft-new-prod`, `ayushiit/warp-weft-detection-june-2024`, `cheomseongdae/fabric-lby7e`).
- [x] Audit academic GitHub repositories (RWTH Aachen `TextileDefectDetection`, `TextileNet`, `TSFabric`).
- [x] Audit scientific repositories (Zenodo CDATP 605 DPI, Mendeley RAW-FABRID, Harvard Dataverse Textile Microtexture 100x).
- [x] Build `experiments/data_acquisition/DATASET_RESEARCH_MATRIX.md` and `dataset_registry.json`.
- [x] Build `experiments/models/MODEL_RESEARCH_MATRIX.md` and `model_registry.json`.

### Phase 3: Acquisition & Storage Budgeting
- [x] Define storage budget in `experiments/data_acquisition/storage_plan.json`.
- [x] Download Harvard Dataverse CC0 Textile Microtexture dataset (20.7 MB archive, 437 extracted files).
- [x] Document access barriers and API tokens in `experiments/data_acquisition/ACCESS_REQUIRED.md`.
- [x] Implement CLI tooling in `experiments/data_acquisition/download_datasets.py`.

### Phase 6: Model Checkpoints & Offline Zoo
- [x] Retrieve SegFormer-B0 offline checkpoint (`model.safetensors`, 14.34 MB, SHA-256 `6ae39add...`).
- [x] Retrieve DINOv2 ViT-S/14 offline checkpoint (`dinov2_vits14_pretrain.pth`, 84.20 MB, SHA-256 `f2f5d5df...`).
- [x] Verify offline checkpoint cryptographic integrity via `download_models.py verify`.
- [x] Benchmark VRAM and runtime inference latency on RTX 3050 Ti Laptop GPU.

### Phases 8–13: Reports & Governance Deliverables
- [x] `experiments/reports/DATA_SUFFICIENCY_REPORT.md` (Domain gap audit and $N=1$ proof).
- [x] `experiments/reports/PHYSICAL_METROLOGY_REPORT.md` (Optics, calibration, and ASTM D3775 mathematics).
- [x] `experiments/reports/MODEL_COMPARISON_REPORT.md` (Synthesis of Table A & Table B benchmarks).
- [x] `experiments/reports/NEXT_DATA_COLLECTION_PLAN.md` (90-swatch factory acquisition protocol).
- [x] `experiments/reports/FINAL_RESEARCH_RECOMMENDATION.md` (Production architecture and safety invariants).

---

## Blocking Issues & Dependencies
* **Local GPU VRAM Boundary:** 3.68 GB usable VRAM on RTX 3050 Ti requires batch size $\le 4$ for SegFormer-B0 / U-Net at $512\times 512$, and rules out local fine-tuning of multi-billion parameter foundation models (e.g. SAM 2.1 Large). Lightweight backbones (SegFormer-B0, MobileSAM, DINOv2-ViT-S) must be prioritized.
* **Disk Space Quota:** 23.2 GB free space available; total acquisition footprint must be strictly capped at $\le 10\text{ GB}$ to leave headroom for OS operations, pip caches, and training checkpoints.
