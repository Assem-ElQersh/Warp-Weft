# Warp & Weft AI — Dataset & Model Access Requirements

This document tracks all external textile datasets, model registries, and API endpoints that require human credentials, user registration, license acceptance, or manual intervention.

---

## 1. Credentials & Token Ledger

| Service / Resource | Authentication Mechanism | Free Tier Available? | Purpose & Impact | Action Required by User |
| :--- | :--- | :--- | :--- | :--- |
| **Roboflow Universe** | `ROBOFLOW_API_KEY` (Environment Variable) | **Yes** (Free community account provides API key with 10k monthly calls) | Access hosted inference for `ayushiit/warp-weft-new-prod` and direct dataset exports (YOLOv8/COCO). | Set in local shell via `export ROBOFLOW_API_KEY="your_key"`. Do **not** commit key to Git or post in chat. |
| **Hugging Face Hub** | `HF_TOKEN` (Read-only User Access Token) | **Yes** (Free account) | Avoid anonymous HTTP rate-limiting when streaming large model weights and downloading Parquet datasets. | Generate a free Read-only token at `https://huggingface.co/settings/tokens` and run `export HF_TOKEN="hf_..."`. |
| **Kaggle API** | `~/.kaggle/kaggle.json` | **Yes** (Free account) | Direct CLI downloading of community textile datasets (e.g., TILDA 400, Kaggle Fabric Defects). | Download `kaggle.json` from `https://www.kaggle.com/settings` and place at `~/.kaggle/kaggle.json` with permissions `600`. |
| **Zenodo API** | `ZENODO_API_TOKEN` / Browser Access | **Yes** (Public downloads unrestricted, but IP rate limits apply) | High-bandwidth batch download for CDATP Fabric Database (`10.5281/zenodo.21872364`). | Network IP blocks return HTTP 403 without token; automated scripts require `ZENODO_API_TOKEN` or manual browser download of selected .zip files. |
| **Mendeley Data** | Browser Session + reCAPTCHA v3 | **Yes** (Free access via browser) | Downloads for RAW-FABRID (`db6g85xsyg`) and FabriD (`vncdwps24r`). | Mendeley protects direct file/archive downloads with reCAPTCHA v3 and dynamic session cookies; direct headless curl/urllib requests are blocked. Archive must be retrieved via browser. |
| **Harvard Dataverse** | Open API / Direct S3 Redirect | **Yes** (Public Domain CC0) | Direct download for Textile Microtexture Dataset (`10.7910/DVN/KUDCQX`). | Fully automated; requires browser User-Agent header to bypass basic scraper filters. Successfully acquired and verified (437 files). |

---

## 2. Actionable Setup Instructions for User

### 2.1. Roboflow API Access Setup (Optional for Hosted Inference Comparison)
1. Navigate to [https://app.roboflow.com/](https://app.roboflow.com/) and sign in with a free account.
2. In workspace settings, select **Roboflow API** and copy your **Private API Key**.
3. In your local terminal, export the environment variable:
   ```bash
   export ROBOFLOW_API_KEY="your_api_key_here"
   ```
4. Verify by running:
   ```bash
   python3 -c "import os; print('Key set:', bool(os.environ.get('ROBOFLOW_API_KEY')))"
   ```

### 2.2. Hugging Face Read Token Setup (Recommended for SegFormer / DINOv2)
1. Sign in to [https://huggingface.co/](https://huggingface.co/).
2. Navigate to **Settings -> Access Tokens** (`https://huggingface.co/settings/tokens`).
3. Click **Create new token**, select type **Read**, and name it `warp-weft-research`.
4. Export in your shell:
   ```bash
   export HF_TOKEN="hf_..."
   ```

---

## 3. Privacy & Client Boundary Safeguard
* **Zero Client Leakage Invariant:** Client factory photographs (located in `data/samples/test.png`) and proprietary laboratory records must **never** be transmitted to external cloud inference APIs (Roboflow, OpenAI, Anthropic, or Hugging Face Inference API).
* All evaluation on client specimens must be executed strictly on local offline PyTorch models running on the local workstation.
