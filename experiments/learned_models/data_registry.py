# The mechanistic justification for this step is: provide an authoritative, programmatic API and CLI for loading, querying, validating, and filtering candidate textile datasets from the Master Textile Dataset Registry (experiments/datasets/registry.json).

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CalibrationDetails:
    scale_x_px_per_cm: Optional[float] = None
    scale_y_px_per_cm: Optional[float] = None
    pixel_pitch_x_um: Optional[float] = None
    pixel_pitch_y_um: Optional[float] = None
    scale_px_per_cm: Optional[float] = None
    pixel_pitch_um: Optional[float] = None
    dpi: Optional[float] = None
    verified_with_stage_micrometer: bool = False
    calibration_uncertainty_pct: float = 0.0
    method: str = "nominal"
    note: str = ""


@dataclass
class DatasetEntry:
    dataset_id: str
    official_name: str
    doi_or_url: str
    source_repository: str
    authors_or_organization: str
    version_or_release_date: str
    license_and_rights: str
    required_attribution: str
    size_bytes: int
    storage_footprint_mb: float
    file_format: str
    number_of_samples: int
    native_resolution: str
    optical_modality: str
    labels_provided: Dict[str, Any]
    physical_calibration_available: bool
    calibration_details: Dict[str, Any]
    taxonomy_category: str
    relevance_rating: str
    access_procedure: str
    verification_status: str
    field_of_view_mm: Optional[str] = None


class DataRegistry:
    DEFAULT_PATH = os.path.join(
        os.path.dirname(__file__), "..", "datasets", "registry.json"
    )

    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path or os.path.abspath(self.DEFAULT_PATH)
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Dataset registry not found at: {self.registry_path}")
        with open(self.registry_path, "r", encoding="utf-8") as handle:
            self.raw_data = json.load(handle)

        self.schema_version = self.raw_data.get("schema_version", "1.0.0")
        self.taxonomy_categories = self.raw_data.get("taxonomy_categories", {})
        self.entries: List[DatasetEntry] = [
            DatasetEntry(**d) for d in self.raw_data.get("datasets", [])
        ]
        self._by_id: Dict[str, DatasetEntry] = {e.dataset_id: e for e in self.entries}

    def list_datasets(self) -> List[DatasetEntry]:
        return list(self.entries)

    def get(self, dataset_id: str) -> Optional[DatasetEntry]:
        return self._by_id.get(dataset_id)

    def filter_by_category(self, category: str) -> List[DatasetEntry]:
        category_clean = category.strip().upper()
        return [e for e in self.entries if e.taxonomy_category.upper() == category_clean]

    def filter_by_verification_status(self, status: str) -> List[DatasetEntry]:
        status_clean = status.strip().upper()
        return [e for e in self.entries if e.verification_status.upper() == status_clean]

    def filter_by_calibration(self, has_calibration: bool = True) -> List[DatasetEntry]:
        return [e for e in self.entries if e.physical_calibration_available == has_calibration]

    def summary_table(self) -> List[Dict[str, Any]]:
        rows = []
        for e in self.entries:
            rows.append({
                "dataset_id": e.dataset_id,
                "name": e.official_name[:35],
                "category": e.taxonomy_category,
                "samples": e.number_of_samples,
                "resolution": e.native_resolution,
                "calibration": e.physical_calibration_available,
                "status": e.verification_status,
                "storage_mb": e.storage_footprint_mb,
            })
        return rows


def main():
    parser = argparse.ArgumentParser(description="Warp & Weft AI Master Dataset Registry CLI")
    parser.add_argument("--registry-path", type=str, default=None, help="Path to registry.json")
    parser.add_argument("--list", action="store_true", help="List all datasets in registry")
    parser.add_argument("--category", type=str, default=None, help="Filter by taxonomy category (A-G)")
    parser.add_argument("--id", type=str, default=None, help="Show full details for specific dataset ID")
    parser.add_argument("--status", type=str, default=None, help="Filter by verification status")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    registry = DataRegistry(args.registry_path)

    if args.id:
        entry = registry.get(args.id)
        if not entry:
            sys.exit(1)
        if args.json:
            print(json.dumps(entry.__dict__, indent=2))
        else:
            for k, v in entry.__dict__.items():
                print(f"{k}: {v}")
        return

    datasets = registry.list_datasets()
    if args.category:
        datasets = [d for d in datasets if d.taxonomy_category.upper() == args.category.upper()]
    if args.status:
        datasets = [d for d in datasets if d.verification_status.upper() == args.status.upper()]

    if args.json:
        print(json.dumps([d.__dict__ for d in datasets], indent=2))
    else:
        print(f"Total Datasets: {len(datasets)}")
        for d in datasets:
            calib = "YES" if d.physical_calibration_available else "NO"
            print(f"[{d.taxonomy_category}] {d.dataset_id:<30} | {d.number_of_samples:>5} samples | Calibrated: {calib:<3} | {d.verification_status:<25} | {d.storage_footprint_mb:>8.2f} MB")


if __name__ == "__main__":
    main()
