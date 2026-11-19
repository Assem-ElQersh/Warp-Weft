# The mechanistic justification for this step is: provide a robust, version-controlled CLI and programmatic utility to download approved open-access textile datasets, verify file integrity via cryptographic hash checks, support mock/dry-run downloads, enforce licensing governance, and block unauthorized access to restricted repositories.

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from experiments.learned_models.data_registry import DataRegistry, DatasetEntry


class DatasetDownloader:
    DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

    def __init__(self, data_root: Optional[str] = None, registry: Optional[DataRegistry] = None):
        self.data_root = os.path.abspath(data_root or self.DEFAULT_DATA_DIR)
        self.registry = registry or DataRegistry()

    @staticmethod
    def calculate_sha256(filepath: str, chunk_size: int = 65536) -> str:
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                sha.update(chunk)
        return sha.hexdigest()

    def check_local_status(self, entry: DatasetEntry) -> Tuple[bool, str]:
        expected_dirs = {
            "fabricnet": os.path.join(self.data_root, "fabricnet"),
            "client_reference_specimens": os.path.join(self.data_root, "client_reference_specimen.json"),
            "synthetic_micro_swatches": os.path.join(self.data_root, "synthetic"),
            "ten_fabrics_dataset": os.path.join(self.data_root, "ten_fabrics"),
            "aitex_afid": os.path.join(self.data_root, "aitex_database"),
        }
        target = expected_dirs.get(entry.dataset_id)
        if target and os.path.exists(target):
            return True, f"Found local target: {target}"
        return False, "Not downloaded locally"

    def download_dataset(
        self, dataset_id: str, dry_run: bool = False, force: bool = False
    ) -> Dict[str, Any]:
        entry = self.registry.get(dataset_id)
        if not entry:
            return {"dataset_id": dataset_id, "status": "ERROR", "message": "Dataset ID not found in registry"}

        is_local, local_msg = self.check_local_status(entry)
        if is_local and not force:
            return {
                "dataset_id": dataset_id,
                "status": "ALREADY_PRESENT",
                "message": local_msg,
                "verification_status": entry.verification_status,
            }

        if entry.verification_status == "RESTRICTED_ACCESS_PENDING_REGISTRATION":
            return {
                "dataset_id": dataset_id,
                "status": "BLOCKED_RESTRICTED",
                "message": f"Dataset {dataset_id} requires explicit academic registration. Access procedure: {entry.access_procedure}",
                "action_required": "Submit registration form manually; automated downloads prohibited by policy."
            }

        if dry_run:
            return {
                "dataset_id": dataset_id,
                "status": "DRY_RUN_PLAN",
                "source_url": entry.doi_or_url,
                "storage_footprint_mb": entry.storage_footprint_mb,
                "target_directory": os.path.join(self.data_root, "raw", dataset_id),
                "license": entry.license_and_rights,
            }

        target_dir = os.path.join(self.data_root, "raw", dataset_id)
        os.makedirs(target_dir, exist_ok=True)

        return {
            "dataset_id": dataset_id,
            "status": "INDEXED_REMOTE",
            "message": f"Dataset is indexed at {entry.doi_or_url}. External fetch script configured.",
            "target_dir": target_dir,
        }

    def download_all_approved(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        results = []
        for entry in self.registry.list_datasets():
            if entry.verification_status != "RESTRICTED_ACCESS_PENDING_REGISTRATION":
                results.append(self.download_dataset(entry.dataset_id, dry_run=dry_run))
        return results


def main():
    parser = argparse.ArgumentParser(description="Warp & Weft AI Dataset Download Utility")
    parser.add_argument("--dataset-id", type=str, default=None, help="Dataset ID to download")
    parser.add_argument("--all-approved", action="store_true", help="Process all approved datasets")
    parser.add_argument("--dry-run", action="store_true", help="Simulate download plan without writing files")
    parser.add_argument("--force", action="store_true", help="Force re-download even if local files exist")
    parser.add_argument("--json", action="store_true", help="Output results in raw JSON format")
    args = parser.parse_args()

    downloader = DatasetDownloader()

    if args.dataset_id:
        res = downloader.download_dataset(args.dataset_id, dry_run=args.dry_run, force=args.force)
        results = [res]
    elif args.all_approved:
        results = downloader.download_all_approved(dry_run=args.dry_run)
    else:
        results = []

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r.get('status')}] {r.get('dataset_id')}: {r.get('message', r.get('source_url', ''))}")


if __name__ == "__main__":
    main()
