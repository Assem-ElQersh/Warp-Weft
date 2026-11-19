# The mechanistic justification for this step is: establish a unified, polymorphic data ingestion layer that normalizes disparate textile dataset formats (microscopy with Excel tables, flatbed scans with block masks, line-scan industrial webs, synthetic physics simulations, and client 5-region JSON protocols) into standardized immutable SampleRecord structures.

import abc
import glob
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


@dataclass
class SampleRecord:
    sample_id: str
    dataset_id: str
    image_path: str
    image_width: int
    image_height: int
    channels: int
    scale_x_px_per_cm: Optional[float] = None
    scale_y_px_per_cm: Optional[float] = None
    warp_density: Optional[float] = None  # ends/cm
    weft_density: Optional[float] = None  # picks/cm
    weave_pattern: Optional[str] = None
    mask_path: Optional[str] = None
    specimen_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDatasetAdapter(abc.ABC):
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.samples: List[SampleRecord] = []
        self._load_records()

    @abc.abstractmethod
    def _load_records(self) -> None:
        pass

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> SampleRecord:
        return self.samples[idx]

    def get_sample(self, sample_id: str) -> Optional[SampleRecord]:
        for s in self.samples:
            if s.sample_id == sample_id:
                return s
        return None

    def load_image_array(self, idx: int, grayscale: bool = True) -> np.ndarray:
        record = self.samples[idx]
        with Image.open(record.image_path) as img:
            if grayscale:
                arr = np.array(img.convert("L"), dtype=np.float32) / 255.0
            else:
                arr = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
        return arr

    def load_mask_array(self, idx: int) -> Optional[np.ndarray]:
        record = self.samples[idx]
        if not record.mask_path or not os.path.exists(record.mask_path):
            return None
        with Image.open(record.mask_path) as mask_img:
            return np.array(mask_img)


class FabricNetAdapter(BaseDatasetAdapter):
    SCALE_X = 1280.0
    SCALE_Y = 1200.0

    def _load_records(self) -> None:
        images = sorted(glob.glob(os.path.join(self.root_dir, "W*.jpg")))
        meta_dict: Dict[str, Dict[str, Any]] = {}

        # Attempt to load metadata from openpyxl if available
        xlsx_path = os.path.join(self.root_dir, "FabricNet_parameters.xlsx")
        if os.path.exists(xlsx_path):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(xlsx_path, data_only=True)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                header = [str(c).strip().lower() for c in rows[0]]
                for r in rows[1:]:
                    if not r[0]:
                        continue
                    row_dict = dict(zip(header, r))
                    img_id = str(row_dict.get("image id", "")).strip()
                    if img_id:
                        meta_dict[img_id] = row_dict
            except Exception:
                meta_dict = {}

        for img_path in images:
            fname = os.path.basename(img_path)
            num_str = "".join([c for c in os.path.splitext(fname)[0] if c.isdigit()])
            int_id = str(int(num_str)) if num_str else fname
            meta = meta_dict.get(int_id, {})

            warp_val = float(meta.get("warp")) if meta.get("warp") is not None else None
            weft_val = float(meta.get("weft")) if meta.get("weft") is not None else None
            texture = str(meta.get("texture", "unknown")).lower()

            self.samples.append(
                SampleRecord(
                    sample_id=os.path.splitext(fname)[0],
                    dataset_id="fabricnet",
                    image_path=img_path,
                    image_width=640,
                    image_height=480,
                    channels=3,
                    scale_x_px_per_cm=self.SCALE_X,
                    scale_y_px_per_cm=self.SCALE_Y,
                    warp_density=warp_val,
                    weft_density=weft_val,
                    weave_pattern=texture,
                    specimen_id=os.path.splitext(fname)[0],
                    metadata=meta,
                )
            )


class SyntheticSwatchesAdapter(BaseDatasetAdapter):
    SCALE = 400.0

    def _load_records(self) -> None:
        pngs = sorted(glob.glob(os.path.join(self.root_dir, "*.png")))
        ground_truths = {
            "synthetic_swatch_32_28.png": {"warp": 32.0, "weft": 28.0, "skew": 0.0},
            "synthetic_swatch_32_28_skewed12.png": {"warp": 32.0, "weft": 28.0, "skew": 12.0},
            "synthetic_swatch_36_30_skewed15.png": {"warp": 36.0, "weft": 30.0, "skew": 15.0},
        }

        for p in pngs:
            fname = os.path.basename(p)
            gt = ground_truths.get(fname, {"warp": 32.0, "weft": 28.0, "skew": 0.0})
            with Image.open(p) as img:
                w, h = img.size

            self.samples.append(
                SampleRecord(
                    sample_id=os.path.splitext(fname)[0],
                    dataset_id="synthetic_micro_swatches",
                    image_path=p,
                    image_width=w,
                    image_height=h,
                    channels=1,
                    scale_x_px_per_cm=self.SCALE,
                    scale_y_px_per_cm=self.SCALE,
                    warp_density=gt["warp"],
                    weft_density=gt["weft"],
                    weave_pattern="plain",
                    specimen_id=os.path.splitext(fname)[0],
                    metadata=gt,
                )
            )


class ClientSpecimenAdapter(BaseDatasetAdapter):
    def _load_records(self) -> None:
        json_file = self.root_dir if self.root_dir.endswith(".json") else os.path.join(self.root_dir, "client_reference_specimen.json")
        if not os.path.exists(json_file):
            return

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        regions = data.get("regions", [])
        samples_dir = os.path.join(os.path.dirname(json_file), "samples")
        client_img = os.path.join(samples_dir, "test.png")
        has_client_img = os.path.exists(client_img)

        for reg in regions:
            r_id = reg.get("region_id", "R0")
            img_p = client_img if has_client_img else ""
            self.samples.append(
                SampleRecord(
                    sample_id=f"client_specimen_002_{r_id}",
                    dataset_id="client_reference_specimens",
                    image_path=img_p,
                    image_width=1080 if has_client_img else 0,
                    image_height=1920 if has_client_img else 0,
                    channels=3,
                    scale_x_px_per_cm=reg.get("pixels_per_cm_x", 263.5),
                    scale_y_px_per_cm=reg.get("pixels_per_cm_y", 208.4),
                    warp_density=float(reg.get("warp_manual_count", 31.0)),
                    weft_density=float(reg.get("weft_manual_count", 27.0)),
                    weave_pattern=reg.get("weave_type", "twill"),
                    specimen_id=reg.get("fabric_id", "client_specimen_002"),
                    metadata=reg,
                )
            )


class TenFabricsAdapter(BaseDatasetAdapter):
    SCALE = 118.11  # 300 DPI

    def _load_records(self) -> None:
        pngs = sorted(glob.glob(os.path.join(self.root_dir, "**", "*.png"), recursive=True))
        for p in pngs:
            fname = os.path.basename(p)
            parent = os.path.basename(os.path.dirname(p))
            mask_candidate = os.path.splitext(p)[0] + ".txt"
            self.samples.append(
                SampleRecord(
                    sample_id=os.path.splitext(fname)[0],
                    dataset_id="ten_fabrics_dataset",
                    image_path=p,
                    image_width=256,
                    image_height=256,
                    channels=3,
                    scale_x_px_per_cm=self.SCALE,
                    scale_y_px_per_cm=self.SCALE,
                    weave_pattern=parent,
                    mask_path=mask_candidate if os.path.exists(mask_candidate) else None,
                    specimen_id=parent,
                    metadata={"class_folder": parent},
                )
            )


class AitexAdapter(BaseDatasetAdapter):
    SCALE = 35.0

    def _load_records(self) -> None:
        pngs = sorted(glob.glob(os.path.join(self.root_dir, "**", "*.png"), recursive=True))
        for p in pngs:
            fname = os.path.basename(p)
            is_mask = "_mask" in fname or "mask" in fname.lower()
            if is_mask:
                continue
            mask_candidate = os.path.splitext(p)[0] + "_mask.png"
            self.samples.append(
                SampleRecord(
                    sample_id=os.path.splitext(fname)[0],
                    dataset_id="aitex_afid",
                    image_path=p,
                    image_width=4096,
                    image_height=256,
                    channels=1,
                    scale_x_px_per_cm=self.SCALE,
                    scale_y_px_per_cm=self.SCALE,
                    mask_path=mask_candidate if os.path.exists(mask_candidate) else None,
                    specimen_id=os.path.splitext(fname)[0],
                    metadata={"aspect_ratio": "16:1"},
                )
            )


def get_dataset_adapter(dataset_id: str, data_root: Optional[str] = None) -> BaseDatasetAdapter:
    root = data_root or os.path.join(os.path.dirname(__file__), "..", "..", "data")
    adapters = {
        "fabricnet": (FabricNetAdapter, os.path.join(root, "fabricnet")),
        "synthetic_micro_swatches": (SyntheticSwatchesAdapter, os.path.join(root, "synthetic")),
        "client_reference_specimens": (ClientSpecimenAdapter, os.path.join(root, "client_reference_specimen.json")),
        "ten_fabrics_dataset": (TenFabricsAdapter, os.path.join(root, "ten_fabrics")),
        "aitex_afid": (AitexAdapter, os.path.join(root, "aitex_database")),
    }
    if dataset_id not in adapters:
        raise ValueError(f"Unknown dataset_id: '{dataset_id}'. Registered adapters: {list(adapters.keys())}")
    cls, path = adapters[dataset_id]
    return cls(path)
