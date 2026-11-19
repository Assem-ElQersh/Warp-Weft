# Verified Master Model Checkpoint Inventory & Architecture Ledger

**The mechanistic justification for this step is: audit all candidate neural architectures and deterministic pipelines, verify cryptographic hashes and operational VRAM footprints on the local GPU, and explicitly distinguish generic pretrained backbones from fine-tuned textile models to prevent misleading claims.**

---

## 1. Model Classification Taxonomy

Every model in Warp & Weft AI is classified under one of five operational tiers:
1. **Generic Pretrained Backbone:** Foundation model trained on general computer vision datasets (ImageNet, ADE20K). Contains general visual priors but has **zero textile-specific knowledge**.
2. **Pretrained Task-Specific Model:** Model trained for a specific task (e.g., object detection, defect detection) on an external domain.
3. **Fine-Tuned Textile Model:** Neural model whose weights have been specialized on real fabric swatches with domain-specific labels.
4. **Model Trained from Scratch:** Architecture initialized with random weights and trained directly on synthetic or real textile imagery.
5. **Deterministic Signal Engine:** Non-parametric algorithmic pipeline based on optics, Fourier transforms, and geometry.

---

## 2. Checkpoint Verification Ledger

| Checkpoint Identifier | Model Name | Architecture Type | Exact File Path | SHA-256 Checksum | File Size | Parameters | VRAM (Active) | Latency (Inference) | Model Classification Tier | Metrology Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`classical_deterministic_core`** | Dual-Engine Metrology Core | 2D Parabolic FFT + 1D Integral Proj | `src/fabric_analysis/pipeline.py` | N/A (Algorithmic) | $0\text{ MB}$ | 0 | $0\text{ MB}$ (CPU) | 12.4 ms | **Deterministic Signal Engine** | **CERTIFIED PRODUCTION DEFAULT** |
| **`unet_yarn_segmentation_v1`** | WarpWeftUNet (In-Repo Checkpoint) | DoubleConv Encoder-Decoder (4-stage) | `experiments/learned_models/checkpoints/unet_yarn_segmentation.pt` | `5b3fb3da3980ee4d0056b35745c5edc5a7dbe2cc2cc2c9aed58a5eb2e2c7cb6e` | 7.39 MB | 1,940,675 | 15.76 MB | 18.2 ms | **Trained from Scratch (Synthetic Only)** | Research Only (Fails on real smartphone swatches) |
| **`textile_defect_fcn_v1`** | RWTH Aachen Defect FCN | 14-layer Conv2D U-Net (Keras 1.11) | `experiments/reference_repos/TextileDefectDetection/example/net.h5` | `d2439b2fd7c94154950ec2805b99ece91472150f53b7ad1760d7645b894944b7` | 89.40 MB | 1,123,491 | N/A (Legacy) | N/A | **External Fine-Tuned (Legacy Archive)** | **UNSUITABLE** (Requires 6-ch front/back lighting) |
| **`segformer_b0_ade`** | SegFormer-B0 (MiT-B0 Encoder) | Hierarchical Transformer + MLP Head | `experiments/models/checkpoints/segformer_b0/model.safetensors` | `6ae39addd01de6b1b8bde2cf677d43a5cd733424b8d186de3f95d1c51fee23f9` | 14.34 MB | 3,752,694 | 34.85 MB | 354.13 ms | **Generic Pretrained Backbone (ADE20K)** | Pretrained Backbone for Future Fine-Tuning |
| **`dinov2_vits14`** | DINOv2 ViT-S/14 Patch Embedder | Vision Transformer (Patch 14, Dim 384) | `experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth` | `f2f5d5df475ec7502b6340fff6af81fac29cc7f42cd5e3fb64e1fb2c26334e39` | 84.20 MB | 22,056,576 | 182.59 MB | 215.04 ms | **Generic Foundation Model (Self-Supervised)** | Candidate Feature Extractor for Weave Mode |
| **`custom_262d_rf_regressor`** | Random Forest Regressor | Ensemble of 150 Regression Trees | `experiments/learned_models/results/fabricnet_features.npz` | N/A (Recomputable) | ~2.5 MB | ~350K nodes | $<65\text{ MB}$ RAM | 85.0 ms | **Trained from Scratch (FabricNET 262-d)** | Research Only (Fixed $1280\text{ px/cm}$ FOV lock) |
| **`custom_262d_xgb_regressor`** | XGBoost Regressor | Gradient Boosted Decision Trees (100) | `experiments/learned_models/results/fabricnet_features.npz` | N/A (Recomputable) | ~1.2 MB | ~120K nodes | $<45\text{ MB}$ RAM | 75.0 ms | **Trained from Scratch (FabricNET 262-d)** | Research Only (Fixed $1280\text{ px/cm}$ FOV lock) |

---

## 3. Detailed Tensor Contract & Operational Validation

### 3.1. `unet_yarn_segmentation_v1`
* **Input Tensor:** Shape `[B, 1, H, W]`, dtype `torch.float32`. Grayscale normalized to $[-1.0, 1.0]$ via $I_{\text{norm}} = (I / 255.0 - 0.5) / 0.5$.
* **Output Tensor:** Shape `[B, 3, H, W]`, dtype `torch.float32`. Unnormalized class logits:
  * Channel 0: Background & Inter-yarn crevices.
  * Channel 1: Longitudinal Warp yarn bodies (vertical).
  * Channel 2: Transverse Weft yarn bodies (horizontal).
* **Operational Test Result:** Successfully instantiated on `cuda:0` (NVIDIA RTX 3050 Ti Laptop GPU). Forward pass with dummy tensor `[1, 1, 256, 256]` yielded logits `[1, 3, 256, 256]` in $18.2\text{ ms}$ with $15.76\text{ MB}$ active VRAM.
* **Domain Limit:** Trained strictly on procedural synthetic images. When applied to real smartphone images, fiber fuzz causes it to segment multi-yarn clusters ($\Delta \approx 31\text{ px}$ instead of single yarns $\Delta \approx 8.5\text{ px}$).

### 3.2. `segformer_b0_ade`
* **Input Tensor:** Shape `[B, 3, 512, 512]`, dtype `torch.float32`. ImageNet normalized RGB ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$).
* **Output Tensor:** Shape `[B, 150, 128, 128]`, dtype `torch.float32`. 150 ADE20K semantic segmentation classes.
* **Operational Test Result:** Loaded from offline safetensors checkpoint (`experiments/models/checkpoints/segformer_b0/model.safetensors`). Forward pass with tensor `[1, 3, 512, 512]` executed on `cuda:0` in $354.13\text{ ms}$ with $34.85\text{ MB}$ active VRAM.
* **Pretrained Status:** This checkpoint is **NOT a yarn segmentation model**. It is a generic scene segmentation backbone preserved locally as a fine-tuning substrate for the planned factory dataset.

### 3.3. `dinov2_vits14`
* **Input Tensor:** Shape `[B, 3, 518, 518]`, dtype `torch.float32` (dimensions must be integer multiples of patch size $14$).
* **Output Tensor:** Shape `[B, 384]`, dtype `torch.float32`. Dense self-supervised feature vector.
* **Operational Test Result:** Loaded from offline `.pth` checkpoint (`experiments/models/checkpoints/dinov2/dinov2_vits14_pretrain.pth`). Forward pass with tensor `[1, 3, 518, 518]` executed on `cuda:0` in $215.04\text{ ms}$ with $182.59\text{ MB}$ active VRAM.
* **Pretrained Status:** Self-supervised patch representation; candidate for clustering and classifying weave patterns (plain, twill, satin) without manual supervision.
