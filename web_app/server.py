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

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from web_app.engine import run_complete_fabric_analysis, pil_to_base64_data_url
from web_app.modes import get_analysis_modes

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

        # 3. Health Endpoint
        if url_path == "/api/health":
            self.send_json_response({
                "status": "healthy",
                "service": "Warp-Weft Thread Density Analyzer",
                "framework": "Pure NumPy / Pillow Mathematical Engine",
                "gpu_available": False,
                "offline": True
            })
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
                raw_scale = payload.get("pixels_per_cm", 400.0)
                pixels_per_cm_x = float(payload.get("pixels_per_cm_x", raw_scale))
                pixels_per_cm_y = float(payload.get("pixels_per_cm_y", pixels_per_cm_x))
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
                    custom_roi=custom_roi
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

    print(f"Warp-Weft Analysis Web Server running at http://{host}:{actual_port}/")
    return httpd, actual_port


if __name__ == "__main__":
    httpd, port = start_server(port=8080)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()
