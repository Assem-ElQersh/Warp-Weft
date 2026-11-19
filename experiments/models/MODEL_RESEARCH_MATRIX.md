# Master Model Architecture & Deep Learning Research Matrix

This matrix evaluates candidate neural network architectures, foundation models, and feature regression frameworks for automated textile thread density measurement.

---

## 1. Architectural Suitability Evaluation

A high benchmark score on standard object detection (COCO mAP) or semantic segmentation (ADE20K mIoU) does **not** translate to accurate physical yarn metrology. Each architecture is evaluated against 5 physical metrology invariants:
1. **Parallel Boundary Separation:** Ability to distinguish touching, parallel yarn filaments without merging them into bundles.
2. **NMS Robustness:** Immunity to Non-Maximum Suppression suppression on dense overlapping bounding boxes.
3. **Hardware Feasibility:** Executable inference and training on the workstation's NVIDIA RTX 3050 Ti ($3.68\text{ GB}$ VRAM).
4. **Physical Scale Coupling:** Capacity to accept external optical calibration ($S_x, S_y\text{ px/cm}$) rather than guessing dimensionless integer pixel counts.
5. **Licensing Permissibility:** Compatibility with commercial or industrial deployment.

---

## 2. Comparative Model Architecture Matrix

| Model Identifier | Architecture Family | Checkpoint Size | Parameter Count | VRAM Usage (Inference / Train) | API Availability | Offline Checkpoint | License | Physical Metrology Suitability |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **`warpweft_unet_synthetic`** | 4-Stage U-Net (PyTorch) | **$7.39\text{ MB}$** | $1.94\text{ M}$ | **$450\text{ MB}$ / $1.2\text{ GB}$** | Local only | In Repo (`.pt`) | MIT | **HIGH:** Lightweight, dual-channel masks, subpixel centerlines; requires native resolution tiling to avoid fuzz merging. |
| **`segformer_b0`** | Transformer Seg (MiT-B0) | **$14.9\text{ MB}$** | $3.72\text{ M}$ | **$650\text{ MB}$ / $1.8\text{ GB}$** | HF Inference API | HF Hub (`.safetensors`)| Apache-2.0 | **VERY HIGH:** Multi-head self-attention models long-range periodic yarn grids efficiently within 4 GB VRAM. |
| **`dinov2_vits14`** | Vision Transformer (Small) | **$88.2\text{ MB}$** | $22.05\text{ M}$ | **$1.2\text{ GB}$ / $2.8\text{ GB}$** | Local only | PyTorch Hub (`.pth`) | Apache-2.0 | **HIGH:** Dense patch feature vectors ($384\text{-d}$) capture periodic weave harmonics without manual feature engineering. |
| **`deeplabv3_mobilenet_v3`** | Dilated CNN (ASPP) | **$42.8\text{ MB}$** | $11.02\text{ M}$ | **$850\text{ MB}$ / $2.1\text{ GB}$** | Local only | Torchvision | BSD-3-Clause | **HIGH:** Atrous multiscale dilation filters capture periodic yarn intervals at varying frequencies. |
| **`mobile_sam`** | Distilled TinyViT + Decoder | **$39.0\text{ MB}$** | $9.60\text{ M}$ | **$1.4\text{ GB}$ / $3.2\text{ GB}$** | Local only | GitHub (`.pt`) | Apache-2.0 | **MEDIUM:** Promptable mask generator for rapid assisted point-annotation of yarn crowns. |
| **`sam2.1_hiera_tiny`** | Hierarchical ViT (Hiera) | **$156.4\text{ MB}$** | $38.90\text{ M}$ | **$2.2\text{ GB}$ / $>4.0\text{ GB}$** | Local only | GitHub (`.pt`) | Apache-2.0 | **MEDIUM:** Excellent visual masks but heavy memory footprint; cannot be fine-tuned on 4 GB GPU without offloading. |
| **`csrnet_density`** | Dilated CNN Density Reg. | **$66.2\text{ MB}$** | $16.26\text{ M}$ | **$1.1\text{ GB}$ / $2.5\text{ GB}$** | Local only | GitHub (`.pth`) | MIT | **MEDIUM:** Density map regression avoids boundary segmentation; requires point-supervised yarn crown annotations. |
| **`textile_fcn_rwth`** | Modified U-Net (`net.h5`) | **$93.74\text{ MB}$** | $7.80\text{ M}$ | **$800\text{ MB}$ / N/A** | Local only | In Repo (`net.h5`) | GPL-3.0 | **LOW (REJECTED):** Requires legacy TensorFlow 1.11 and 6-channel paired front/backlighting; non-transferable to phones. |
| **`fabricnet_global_262d_rf`** | Random Forest Regressor | **$1.48\text{ MB}$** | $100\text{ trees}$ | **CPU ($<50\text{ MB}$ RAM)** | Local only | In Repo (`.json`) | MIT | **HIGH for Microscopy, FAILS on Smartphone:** $\text{MAE} = 4.88$ on microscope, error $>41\text{ ends/cm}$ on smartphone. |
| **`fabricnet_ifv_xgboost`** | Sliding-Window XGBoost | **$0.82\text{ MB}$** | $100\text{ trees}$ | **CPU ($<40\text{ MB}$ RAM)** | Local only | In Repo (`.json`) | MIT | **HIGH for Microscopy:** $\text{MAE} = 6.67$ on microscope; sliding-window outlier pooling rejects local illumination artifacts. |
| **`roboflow_yolov8_warp_weft`**| YOLOv8n Object Detection | **$6.20\text{ MB}$** | $3.20\text{ M}$ | **$600\text{ MB}$ / $1.6\text{ GB}$** | Roboflow API | Roboflow Export | CC BY 4.0 | **UNSUITABLE:** Standard NMS suppresses $30\text{--}50\%$ of parallel yarns; bounding boxes have no physical scale. |

---

## 3. Engineering Recommendations by Subsystem

1. **Production Primary Measurement:** Retain the classical deterministic dual-engine (Radon skew rectification + 2D FFT with parabolic refinement + 1D spatial projection + multi-hypothesis evidence arbiter). It is computationally instant ($45\text{ ms}$), requires zero training data, and is physically grounded by camera calibration ($S_x, S_y$).
2. **Next-Generation Learned Segmentation Engine:** Build around **SegFormer-B0** ($14.9\text{ MB}$) and **`WarpWeftUNet`** ($7.39\text{ MB}$). Both fit comfortably within the $3.68\text{ GB}$ VRAM ceiling, execute inference in $<20\text{ ms}$, and output dense probability maps that can be topologically thinned into exact physical yarn centerlines.
3. **Representation & Harmonic Feature Extraction:** Deploy **DINOv2 ViT-S/14** ($88.2\text{ MB}$) as a frozen self-supervised backbone to extract dense spatial feature fields for validating weave periodicity in challenging patterned fabrics.
