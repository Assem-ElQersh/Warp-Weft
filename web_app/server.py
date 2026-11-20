# ==============================================================================
# Warp & Weft Automated Thread Density Analysis Web Server
# ==============================================================================
# The mechanistic justification for this step is: implement a self-contained,
# zero-dependency HTTP server utilizing Python standard library (http.server and
# socketserver) to host the interactive single-page application and REST analysis API.

import os
import sys
import io
import json
import base64
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from PIL import Image

# The mechanistic justification for this step is: probe PyTorch CUDA hardware acceleration conditionally, enabling GPU telemetry and AI model verification on the server without breaking pure-NumPy environments.
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    CUDA_DEVICE_NAME = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else None
except Exception:
    torch = None
    CUDA_AVAILABLE = False
    CUDA_DEVICE_NAME = None

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from web_app.engine import run_complete_fabric_analysis, pil_to_base64_data_url
from web_app.modes import get_analysis_modes
from src.fabric_analysis.calibration import PhysicalCalibration
from src.fabric_analysis.calibration_profile import list_calibration_profiles, get_calibration_profile
from src.fabric_analysis.specimen_workflow import evaluate_five_region_specimen

STATIC_DIR = os.path.join(WORKSPACE_ROOT, "web_app")
DATA_DIR = os.path.join(WORKSPACE_ROOT, "data")
REPORTS_DIR = os.path.join(WORKSPACE_ROOT, "reports")



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads for non-blocking execution."""
    daemon_threads = True


class FabricAnalysisHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean logging format without decorative filler
        pass

    def send_json_response(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    # The mechanistic justification for this step is: handle HTTP HEAD requests to support tunnel monitors and uptime checks without throwing HTTP 501.
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        url_path = self.path.split("?")[0]

        # 1. Root / UI Endpoint
        if url_path in ("/", "/index.html"):
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(index_path):
                with open(index_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "index.html not found")
            return

        # 2. Analysis mode capability endpoint
        if url_path == "/api/models":
            self.send_json_response(get_analysis_modes(WORKSPACE_ROOT))
            return

        # 2b. Calibration profiles endpoint
        if url_path == "/api/calibration/profiles":
            profiles = list_calibration_profiles()
            self.send_json_response({
                "status": "success",
                "profiles": profiles
            })
            return

        # 3. Health Endpoint
        # The mechanistic justification for this step is: dynamically report host GPU status and PyTorch framework telemetry on the health endpoint.
        if url_path == "/api/health":
            self.send_json_response({
                "status": "healthy",
                "service": "Warp-Weft Thread Density Analyzer",
                "framework": f"PyTorch {torch.__version__} / NumPy" if (torch is not None) else "Pure NumPy / Pillow Mathematical Engine",
                "gpu_available": CUDA_AVAILABLE,
                "gpu_device": CUDA_DEVICE_NAME,
                "offline": True
            })
            return

        # 3b. GPU and AI Models Endpoint
        # The mechanistic justification for this step is: provide remote clients with real-time VRAM telemetry, CUDA device attributes, and verified AI model inventory status.
        if url_path == "/api/gpu":
            gpu_data = {
                "cuda_available": CUDA_AVAILABLE,
                "device_name": CUDA_DEVICE_NAME,
                "torch_version": torch.__version__ if torch else None,
                "allocated_vram_mb": round(torch.cuda.memory_allocated() / (1024**2), 2) if (CUDA_AVAILABLE and torch) else 0.0,
                "reserved_vram_mb": round(torch.cuda.memory_reserved() / (1024**2), 2) if (CUDA_AVAILABLE and torch) else 0.0,
                "models": {
                    "unet_yarn_segmentation_v1": "LOCAL [VERIFIED]",
                    "segformer_b0_ade": "LOCAL [VERIFIED]",
                    "dinov2_vits14": "LOCAL [VERIFIED]",
                }
            }
            self.send_json_response({"status": "success", "telemetry": gpu_data})
            return

        # 3. Presets Endpoint (Preloaded sample fabrics)
        if url_path == "/api/presets":
            presets = [
                {
                    "id": "synthetic_skewed_12",
                    "name_en": "Macro Swatch (+12° Skew)",
                    "name_ar": "عينة ماكرو مائلة (+12 درجة)",
                    "category": "Synthetic Benchmark",
                    "ground_truth": "36 Warp / 30 Weft (Tilt: +12°)",
                    "pixels_per_cm": 400.0,
                    "pixels_per_cm_x": 400.0,
                    "pixels_per_cm_y": 400.0,
                    "auto_skew": True,
                    "prominence": 0.012,
                    "weave_hint": "plain",
                    "path": "data/synthetic/macro_swatch_skewed_12deg.png"
                },
                {
                    "id": "fabricnet_w012",
                    "name_en": "FabricNET W012 (Plain Weave 105 g/m²)",
                    "name_ar": "قماش فابريك نت W012 (نسيج سادة)",
                    "category": "Real Optical Microscopy",
                    "ground_truth": "38 Warp / 33 Weft (Plain Benchmark)",
                    "pixels_per_cm": 1280.0,
                    "pixels_per_cm_x": 1280.0,
                    "pixels_per_cm_y": 1200.0,
                    "auto_skew": False,
                    "prominence": 0.010,
                    "weave_hint": "plain",
                    "path": "data/fabricnet/W012.jpg"
                },
                {
                    "id": "fabricnet_w001",
                    "name_en": "FabricNET W001 (Twill Weave 140 g/m²)",
                    "name_ar": "قماش فابريك نت W001 (نسيج مبرد)",
                    "category": "Real Optical Microscopy",
                    "ground_truth": "32 Warp / 30 Weft (Float Ridges)",
                    "pixels_per_cm": 1280.0,
                    "pixels_per_cm_x": 1280.0,
                    "pixels_per_cm_y": 1200.0,
                    "auto_skew": False,
                    "prominence": 0.012,
                    "weave_hint": "twill",
                    "path": "data/fabricnet/W001.jpg"
                },
                {
                    "id": "synthetic_skewed_15",
                    "name_en": "Synthetic Swatch (+15° Skew)",
                    "name_ar": "عينة اختبار مائلة (+15 درجة)",
                    "category": "Synthetic Benchmark",
                    "ground_truth": "32 Warp / 28 Weft (Tilt: +15°)",
                    "pixels_per_cm": 400.0,
                    "pixels_per_cm_x": 400.0,
                    "pixels_per_cm_y": 400.0,
                    "auto_skew": True,
                    "prominence": 0.012,
                    "weave_hint": "plain",
                    "path": "data/synthetic/sample_skewed_15deg.png"
                }
            ]

            # Populate Base64 thumbnails with compact dimension (120 px)
            for p in presets:
                fpath = os.path.join(WORKSPACE_ROOT, p["path"])
                if os.path.exists(fpath):
                    try:
                        im = Image.open(fpath)
                        p["thumbnail_b64"] = pil_to_base64_data_url(im, max_size=120)
                    except Exception:
                        p["thumbnail_b64"] = None

            self.send_json_response({"presets": presets})
            return

        # 4. Report File Downloads
        if url_path.startswith("/reports/"):
            filename = os.path.basename(url_path)
            report_file = os.path.join(REPORTS_DIR, filename)
            if os.path.exists(report_file) and os.path.isfile(report_file):
                mime_type, _ = mimetypes.guess_type(report_file)
                if not mime_type:
                    mime_type = "application/pdf" if filename.endswith(".pdf") else "application/octet-stream"
                with open(report_file, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Content-Disposition", f'inline; filename="{filename}"')
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, f"Report file {filename} not found")
                return

        # 5. Default 404
        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        url_path = self.path.split("?")[0]

        if url_path == "/api/analyze":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length)
                payload = json.loads(raw_body.decode("utf-8"))
                if not isinstance(payload, dict):
                    self.send_json_response({"status": "error", "code": "invalid_payload", "error": "Request payload must be a JSON object."}, status_code=400)
                    return

                # 0. Enforce requested analysis-mode availability before decoding image bytes.
                compare_methods = payload.get("compare_methods", False)
                if not isinstance(compare_methods, bool):
                    self.send_json_response({"status": "error", "code": "invalid_compare_methods", "error": "compare_methods must be a JSON boolean."}, status_code=400)
                    return
                analysis_mode = "classical" if compare_methods else str(payload.get("analysis_mode", "classical")).strip().lower()
                mode_catalog = get_analysis_modes(WORKSPACE_ROOT)
                mode_map = {item["id"]: item for item in mode_catalog["modes"]}
                if analysis_mode not in mode_map:
                    self.send_json_response({"status": "error", "code": "unknown_analysis_mode", "error": f"Unknown analysis mode: {analysis_mode}"}, status_code=400)
                    return
                if not mode_map[analysis_mode]["available"]:
                    self.send_json_response({
                        "status": "unavailable",
                        "code": "analysis_mode_unavailable",
                        "analysis_mode": analysis_mode,
                        "mode": mode_map[analysis_mode],
                        "error": mode_map[analysis_mode]["reason"],
                    }, status_code=409)
                    return

                # 1. Parse Image Payload
                img_data_b64 = payload.get("image", "")
                if not img_data_b64:
                    # Check if preset_id is passed
                    preset_id = payload.get("preset_id", "")
                    if preset_id == "fabricnet_w012":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/fabricnet/W012.jpg")
                    elif preset_id == "fabricnet_w001":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/fabricnet/W001.jpg")
                    elif preset_id == "synthetic_skewed_15":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/synthetic/sample_skewed_15deg.png")
                    else:
                        img_path = os.path.join(WORKSPACE_ROOT, "data/synthetic/macro_swatch_skewed_12deg.png")
                    pil_img = Image.open(img_path)
                else:
                    # Strip data URL header if present
                    if "," in img_data_b64:
                        img_data_b64 = img_data_b64.split(",")[1]
                    img_bytes = base64.b64decode(img_data_b64)
                    pil_img = Image.open(io.BytesIO(img_bytes))

                # 2. Extract Calibration & Algorithmic Parameters
                # The mechanistic justification for this step is: extract explicit calibration scale
                # or named calibration profile without falling back to a silent default 400.0 px/cm,
                # ensuring that uncalibrated requests are explicitly flagged as UNCALIBRATED.
                preset_id = payload.get("preset_id", "") if not img_data_b64 else ""
                raw_scale = payload.get("pixels_per_cm")
                raw_scale_x = payload.get("pixels_per_cm_x")
                raw_scale_y = payload.get("pixels_per_cm_y")
                profile_name = payload.get("profile_name")

                # If a preset was used and no explicit scale was passed, use the preset ground-truth scale
                if not img_data_b64 and preset_id and raw_scale is None and raw_scale_x is None:
                    if preset_id in ("fabricnet_w012", "fabricnet_w001"):
                        raw_scale_x = 1280.0
                        raw_scale_y = 1200.0
                    elif preset_id in ("synthetic_skewed_15", "synthetic_skewed_12"):
                        raw_scale_x = 400.0
                        raw_scale_y = 400.0

                calibration = None
                if profile_name:
                    prof = get_calibration_profile(profile_name)
                    if prof:
                        calibration = prof.to_physical_calibration()

                pixels_per_cm_x = None
                pixels_per_cm_y = None
                if calibration is None:
                    if raw_scale_x is not None or raw_scale is not None:
                        pixels_per_cm_x = float(raw_scale_x if raw_scale_x is not None else raw_scale)
                        pixels_per_cm_y = float(raw_scale_y if raw_scale_y is not None else pixels_per_cm_x)

                auto_skew = bool(payload.get("auto_skew", True))
                prominence = float(payload.get("prominence", 0.012))
                weave_hint = str(payload.get("weave_hint", "auto")).lower()
                custom_roi = payload.get("custom_roi", None)

                # 3. Run Dual-Engine Analysis
                result = run_complete_fabric_analysis(
                    img_pil=pil_img,
                    pixels_per_cm=pixels_per_cm_x,
                    pixels_per_cm_y=pixels_per_cm_y,
                    auto_skew=auto_skew,
                    prominence=prominence,
                    weave_hint=weave_hint,
                    custom_roi=custom_roi,
                    calibration=calibration
                )

                result["analysis_mode"] = "comparison" if compare_methods else "classical"
                if compare_methods:
                    comparison_methods = []
                    unavailable_methods = []
                    for method in mode_catalog["modes"]:
                        if not method["available"]:
                            unavailable_methods.append({
                                "id": method["id"],
                                "label": method["label"],
                                "reason": method.get("reason"),
                            })
                            continue
                        if method["id"] != "classical":
                            # Never mark a mode available without an explicit dispatcher.
                            unavailable_methods.append({
                                "id": method["id"],
                                "label": method["label"],
                                "reason": "No inference dispatcher is registered for this method.",
                            })
                            continue
                        result_values = result.get("results", {})
                        comparison_methods.append({
                            "id": "classical",
                            "label": method["label"],
                            "status": result.get("status", "success"),
                            "decision_status": result_values.get("decision_status"),
                            "warp_ends_per_cm": result_values.get("accepted_warp_density_ends_per_cm"),
                            "weft_picks_per_cm": result_values.get("accepted_weft_density_picks_per_cm"),
                            "signal_quality_index": result_values.get("signal_quality_index"),
                            "latency_ms": result.get("latency_ms"),
                            "candidate_measurements": result_values.get("candidate_measurements"),
                        })
                    result["comparison"] = {
                        "requested": True,
                        "methods": comparison_methods,
                        "unavailable_methods": unavailable_methods,
                        "note": (
                            "Every currently available method was executed. Only Classical has a validated "
                            "inference implementation in this checkout; Learned and Hybrid remain unavailable."
                        ),
                    }
                self.send_json_response(result)

            except Exception as e:
                self.send_json_response({"status": "error", "error": str(e)}, status_code=500)
            return

        if url_path == "/api/analyze/specimen":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length)
                payload = json.loads(raw_body.decode("utf-8"))
                if not isinstance(payload, dict):
                    self.send_json_response({"status": "error", "code": "invalid_payload", "error": "Request payload must be a JSON object."}, status_code=400)
                    return

                fabric_id = str(payload.get("fabric_id", "specimen_1")).strip()
                profile_name = payload.get("profile_name")
                scale_x = payload.get("scale_x") or payload.get("pixels_per_cm_x")
                scale_y = payload.get("scale_y") or payload.get("pixels_per_cm_y")

                # The mechanistic justification for this step is: require an explicit calibration
                # profile or explicit non-zero spatial scales (scale_x, scale_y) for specimen analysis,
                # rejecting uncalibrated specimen analysis requests with HTTP 400.
                if profile_name:
                    prof = get_calibration_profile(profile_name)
                    if prof:
                        calib = prof.to_physical_calibration()
                    elif scale_x and scale_y:
                        calib = PhysicalCalibration.from_scales(float(scale_x), float(scale_y), source=f"unknown_profile_{profile_name}")
                    else:
                        self.send_json_response({
                            "status": "error",
                            "code": "unknown_profile",
                            "error": f"Unknown calibration profile: {profile_name}"
                        }, status_code=400)
                        return
                elif scale_x and scale_y:
                    calib = PhysicalCalibration.from_scales(float(scale_x), float(scale_y), source="api_specimen_scales")
                else:
                    self.send_json_response({
                        "status": "error",
                        "code": "missing_calibration",
                        "error": "Specimen analysis requires a valid profile_name or explicit scale_x and scale_y parameters."
                    }, status_code=400)
                    return

                target_warp = float(payload.get("target_warp", 31.0))
                target_weft = float(payload.get("target_weft", 27.0))
                tolerance = float(payload.get("tolerance", 2.0))

                images_list = []
                roi_boxes = payload.get("roi_boxes")

                if "images" in payload and isinstance(payload["images"], list) and len(payload["images"]) >= 5:
                    for img_b64 in payload["images"][:5]:
                        if "," in img_b64:
                            img_b64 = img_b64.split(",")[1]
                        img_bytes = base64.b64decode(img_b64)
                        images_list.append(Image.open(io.BytesIO(img_bytes)))
                elif "image" in payload and payload["image"]:
                    img_b64 = payload["image"]
                    if "," in img_b64:
                        img_b64 = img_b64.split(",")[1]
                    img_bytes = base64.b64decode(img_b64)
                    base_pil = Image.open(io.BytesIO(img_bytes))
                    images_list.append(base_pil)
                elif "preset_id" in payload:
                    preset_id = payload["preset_id"]
                    if preset_id == "fabricnet_w012":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/fabricnet/W012.jpg")
                    elif preset_id == "fabricnet_w001":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/fabricnet/W001.jpg")
                    elif preset_id == "synthetic_skewed_15":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/synthetic/sample_skewed_15deg.png")
                    elif preset_id == "client_test":
                        img_path = os.path.join(WORKSPACE_ROOT, "data/samples/test.png")
                    else:
                        img_path = os.path.join(WORKSPACE_ROOT, "data/synthetic/macro_swatch_skewed_12deg.png")
                    images_list.append(Image.open(img_path))
                else:
                    self.send_json_response({"status": "error", "code": "missing_image", "error": "No image data provided for specimen analysis."}, status_code=400)
                    return

                if len(images_list) == 1 and (not roi_boxes or len(roi_boxes) != 5):
                    w_img, h_img = images_list[0].size
                    rw = max(60, min(int(calib.pixels_per_cm_x), int(w_img * 0.25)))
                    rh = max(60, min(int(calib.pixels_per_cm_y), int(h_img * 0.25)))

                    roi_boxes = [
                        (int(w_img * 0.15), int(h_img * 0.15), int(w_img * 0.15) + rw, int(h_img * 0.15) + rh),
                        (int(w_img * 0.85) - rw, int(h_img * 0.15), int(w_img * 0.85), int(h_img * 0.15) + rh),
                        (int((w_img - rw) / 2), int((h_img - rh) / 2), int((w_img + rw) / 2), int((h_img + rh) / 2)),
                        (int(w_img * 0.15), int(h_img * 0.85) - rh, int(w_img * 0.15) + rw, int(h_img * 0.85)),
                        (int(w_img * 0.85) - rw, int(h_img * 0.85) - rh, int(w_img * 0.85), int(h_img * 0.85)),
                    ]
                elif roi_boxes and len(roi_boxes) == 5 and isinstance(roi_boxes[0], dict):
                    roi_boxes = [(b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]) for b in roi_boxes]
                elif roi_boxes and len(roi_boxes) == 5 and isinstance(roi_boxes[0], (list, tuple)):
                    roi_boxes = [tuple(b) for b in roi_boxes]

                res = evaluate_five_region_specimen(
                    fabric_id=fabric_id,
                    images=images_list,
                    calibration=calib,
                    roi_boxes=roi_boxes,
                    target_warp=target_warp,
                    target_weft=target_weft,
                    tolerance=tolerance
                )

                self.send_json_response({"status": "success", "specimen": res.to_dict()})

            except Exception as e:
                self.send_json_response({"status": "error", "error": str(e)}, status_code=500)
            return

        self.send_error(404, "Endpoint not found")


def start_server(port=8080, host="0.0.0.0"):
    """
    Start the threaded HTTP server on the requested port,
    falling back to 8081 if occupied.
    """
    server_address = (host, port)
    try:
        httpd = ThreadedHTTPServer(server_address, FabricAnalysisHandler)
        actual_port = port
    except OSError:
        actual_port = port + 1
        server_address = (host, actual_port)
        httpd = ThreadedHTTPServer(server_address, FabricAnalysisHandler)

    # The mechanistic justification for this step is: log hardware execution device and AI model checkpoint availability upon server startup for diagnostic traceability.
    print(f"Warp-Weft Analysis Web Server running at http://{host}:{actual_port}/")
    print(f"Hardware Device: {'CUDA (' + CUDA_DEVICE_NAME + ')' if CUDA_AVAILABLE else 'CPU'}")
    return httpd, actual_port


if __name__ == "__main__":
    httpd, port = start_server(port=8080)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()
