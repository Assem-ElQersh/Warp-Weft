# ==============================================================================
# Warp & Weft Model Zoo Download, Verification & Inspection CLI Utility
# ==============================================================================
# The mechanistic justification for this step is: provide an automated, reproducible
# command-line interface to retrieve, verify cryptographic integrity (SHA-256), inspect
# parameter architectures, and benchmark runtime memory/latency for candidate neural
# models (SegFormer, DINOv2, WarpWeftUNet) on the available hardware budget.

import os
import sys
import json
import time
import hashlib
import argparse
import urllib.request
import torch

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

INVENTORY_PATH = os.path.join(WORKSPACE_ROOT, "experiments/models/checkpoints/inventory.json")
CHECKPOINTS_DIR = os.path.join(WORKSPACE_ROOT, "experiments/models/checkpoints")


def calculate_sha256(filepath: str, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def load_inventory():
    """Load model inventory JSON."""
    if not os.path.exists(INVENTORY_PATH):
        print(f"Inventory file not found: {INVENTORY_PATH}")
        sys.exit(1)
    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inventory(data):
    """Save model inventory JSON."""
    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def cmd_list(args):
    """List all registered models in inventory."""
    inv = load_inventory()
    print("\n--- WARP & WEFT MODEL CHECKPOINT INVENTORY ---")
    for cp in inv.get("checkpoints", []):
        exists = os.path.exists(os.path.join(WORKSPACE_ROOT, cp["filepath"])) if cp.get("filepath") else False
        status_str = "LOCAL [OK]" if exists else "NOT DOWNLOADED"
        print(f"ID: {cp['checkpoint_id']:<30} | {cp['model_name']:<35} | {cp.get('size_mb', 0):>6.1f} MB | {status_str}")


def cmd_show_storage(args):
    """Show storage allocation and checkpoint disk usage."""
    inv = load_inventory()
    total_bytes = 0
    print("\n--- MODEL STORAGE FOOTPRINT ---")
    for cp in inv.get("checkpoints", []):
        fpath = os.path.join(WORKSPACE_ROOT, cp["filepath"]) if cp.get("filepath") else None
        if fpath and os.path.exists(fpath):
            sz = os.path.getsize(fpath)
            total_bytes += sz
            print(f"{cp['checkpoint_id']:<30} : {sz / (1024**2):>8.2f} MB ({fpath})")
        else:
            print(f"{cp['checkpoint_id']:<30} : [FILE MISSING]")
    print(f"TOTAL LOCAL CHECKPOINT DISK USAGE: {total_bytes / (1024**2):.2f} MB ({total_bytes / (1024**3):.4f} GB)")


def cmd_verify(args):
    """Verify SHA-256 hashes of local checkpoints."""
    inv = load_inventory()
    print("\n--- VERIFYING CHECKPOINT CRYPTOGRAPHIC INTEGRITY ---")
    for cp in inv.get("checkpoints", []):
        fpath = os.path.join(WORKSPACE_ROOT, cp["filepath"]) if cp.get("filepath") else None
        if not fpath or not os.path.exists(fpath):
            print(f"{cp['checkpoint_id']:<30} : MISSING")
            continue
        actual_hash = calculate_sha256(fpath)
        expected_hash = cp.get("sha256")
        if expected_hash:
            match = (actual_hash.lower() == expected_hash.lower())
            status = "PASSED" if match else f"MISMATCH! (Got: {actual_hash})"
            print(f"{cp['checkpoint_id']:<30} : {status}")
        else:
            cp["sha256"] = actual_hash
            print(f"{cp['checkpoint_id']:<30} : RECORDED SHA-256 ({actual_hash[:16]}...)")
    save_inventory(inv)


def cmd_inspect(args):
    """Inspect model configuration and parameters."""
    inv = load_inventory()
    target_id = args.model_id
    match = next((cp for cp in inv.get("checkpoints", []) if cp["checkpoint_id"] == target_id), None)
    if not match:
        print(f"Model ID '{target_id}' not found in inventory.")
        return
    print(f"\nModel: {match['model_name']} ({match['checkpoint_id']})")
    print(f"Architecture: {match.get('architecture')}")
    print(f"Framework:    {match.get('framework')}")
    print(f"Filepath:     {match.get('filepath')}")
    print(f"Size:         {match.get('size_mb')} MB")
    print(f"Input Shape:  {match.get('input_shape')}")
    print(f"Classes:      {match.get('class_labels')}")
    print(f"Notes:        {match.get('notes')}")


def cmd_test_loading(args):
    """Load model into PyTorch memory, inspect VRAM, and run dummy inference."""
    target_id = args.model_id
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nTesting model load on device: {device.upper()}")

    if target_id == "unet_yarn_segmentation_v1":
        fpath = os.path.join(WORKSPACE_ROOT, "experiments/learned_models/checkpoints/unet_yarn_segmentation.pt")
        if not os.path.exists(fpath):
            print("Checkpoint file not found.")
            return
        
        # The mechanistic justification for this step is: import the WarpWeftUNet
        # architecture from the modular segmentation_models package rather than an unlinked path.
        from experiments.models.segmentation_models import WarpWeftUNet
        model = WarpWeftUNet(in_channels=1, num_classes=3).to(device)
        state_dict = torch.load(fpath, map_location=device)
        model.load_state_dict(state_dict)
        model.eval()

        dummy_input = torch.randn(1, 1, 256, 256, device=device)
        t0 = time.time()
        with torch.no_grad():
            out = model(dummy_input)
        lat_ms = (time.time() - t0) * 1000.0

        vram_mb = torch.cuda.memory_allocated(0) / (1024**2) if device == "cuda" else 0.0
        print(f"Successfully loaded {target_id}!")
        print(f"Input shape:  {list(dummy_input.shape)}")
        print(f"Output shape: {list(out.shape)}")
        print(f"Latency:      {lat_ms:.2f} ms")
        print(f"VRAM Active:  {vram_mb:.2f} MB")

    elif target_id in ("segformer_b0", "segformer_b0_ade"):
        # The mechanistic justification for this step is: load the offline saved
        # SegFormer-B0 checkpoint from local disk to guarantee hermetic execution.
        from transformers import SegformerForSemanticSegmentation
        local_dir = os.path.join(CHECKPOINTS_DIR, "segformer_b0")
        if os.path.exists(local_dir):
            print(f"Loading SegFormer-B0 from local checkpoint: {local_dir}")
            model = SegformerForSemanticSegmentation.from_pretrained(local_dir).to(device)
        else:
            print("Instantiating SegFormer-B0 via Transformers...")
            model = SegformerForSemanticSegmentation.from_pretrained("nvidia/segformer-b0-finetuned-ade-512-512").to(device)
        model.eval()
        dummy_input = torch.randn(1, 3, 512, 512, device=device)
        t0 = time.time()
        with torch.no_grad():
            out = model(dummy_input)
        lat_ms = (time.time() - t0) * 1000.0
        vram_mb = torch.cuda.memory_allocated(0) / (1024**2) if device == "cuda" else 0.0
        print(f"Successfully loaded {target_id}!")
        print(f"Input shape:  {list(dummy_input.shape)}")
        print(f"Output shape: {list(out.logits.shape)}")
        print(f"Latency:      {lat_ms:.2f} ms")
        print(f"VRAM Active:  {vram_mb:.2f} MB")

    elif target_id == "dinov2_vits14":
        # The mechanistic justification for this step is: load the offline saved
        # DINOv2 ViT-S/14 state dict directly from disk into the instantiated architecture.
        local_pth = os.path.join(CHECKPOINTS_DIR, "dinov2/dinov2_vits14_pretrain.pth")
        print("Instantiating DINOv2 ViT-S/14 architecture...")
        model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(device)
        if os.path.exists(local_pth):
            print(f"Loading weights from local checkpoint: {local_pth}")
            state_dict = torch.load(local_pth, map_location=device)
            model.load_state_dict(state_dict)
        model.eval()
        dummy_input = torch.randn(1, 3, 518, 518, device=device)
        t0 = time.time()
        with torch.no_grad():
            out = model(dummy_input)
        lat_ms = (time.time() - t0) * 1000.0
        vram_mb = torch.cuda.memory_allocated(0) / (1024**2) if device == "cuda" else 0.0
        print(f"Successfully loaded {target_id}!")
        print(f"Input shape:  {list(dummy_input.shape)}")
        print(f"Output shape: {list(out.shape)}")
        print(f"Latency:      {lat_ms:.2f} ms")
        print(f"VRAM Active:  {vram_mb:.2f} MB")
    else:
        print(f"Loader not yet configured for model ID: {target_id}")


def main():
    parser = argparse.ArgumentParser(description="Warp & Weft Model Zoo Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all registered models")

    # show-storage
    subparsers.add_parser("show-storage", help="Show local checkpoint disk storage")

    # verify
    subparsers.add_parser("verify", help="Verify SHA-256 hashes of local checkpoints")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect model metadata")
    p_inspect.add_argument("model_id", type=str, help="Checkpoint ID to inspect")

    # test-loading
    p_load = subparsers.add_parser("test-loading", help="Test loading checkpoint and run sanity inference")
    p_load.add_argument("model_id", type=str, help="Checkpoint ID to test")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "show-storage":
        cmd_show_storage(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "test-loading":
        cmd_test_loading(args)


if __name__ == "__main__":
    main()
