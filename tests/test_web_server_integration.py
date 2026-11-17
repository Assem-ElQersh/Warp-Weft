import http.client
import json
import threading
import unittest

from web_app.server import FabricAnalysisHandler, ThreadedHTTPServer


class TestWebServerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadedHTTPServer(("127.0.0.1", 0), FabricAnalysisHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        body = None if payload is None else json.dumps(payload)
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read()
        status = response.status
        content_type = response.getheader("Content-Type")
        connection.close()
        parsed = json.loads(content.decode("utf-8")) if content_type and "application/json" in content_type else content
        return status, parsed, content_type

    def test_health_and_presets_routes_remain_available(self):
        status, health, content_type = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["status"], "healthy")
        self.assertIn("application/json", content_type)

        status, presets, _ = self.request("GET", "/api/presets")
        self.assertEqual(status, 200)
        self.assertEqual(len(presets["presets"]), 4)
        self.assertTrue(all("thumbnail_b64" in preset for preset in presets["presets"]))

    def test_models_endpoint_describes_all_three_modes_and_registry(self):
        status, catalog, _ = self.request("GET", "/api/models")
        self.assertEqual(status, 200)
        self.assertEqual(catalog["default_mode"], "classical")
        self.assertTrue(catalog["comparison_supported"])
        modes = {item["id"]: item for item in catalog["modes"]}
        self.assertTrue(modes["classical"]["available"])
        self.assertFalse(modes["learned"]["available"])
        self.assertFalse(modes["hybrid"]["available"])
        self.assertEqual(catalog["registered_models"], [])

    def test_unavailable_learned_mode_is_rejected_before_image_decode(self):
        status, result, _ = self.request("POST", "/api/analyze", {
            "analysis_mode": "learned",
            "image": "not-valid-base64",
        })
        self.assertEqual(status, 409)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["code"], "analysis_mode_unavailable")

    def test_unavailable_hybrid_mode_is_rejected_before_image_decode(self):
        status, result, _ = self.request("POST", "/api/analyze", {
            "analysis_mode": "hybrid",
            "image": "not-valid-base64",
        })
        self.assertEqual(status, 409)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["analysis_mode"], "hybrid")
        self.assertEqual(result["code"], "analysis_mode_unavailable")

    def test_unknown_analysis_mode_is_rejected(self):
        status, result, _ = self.request("POST", "/api/analyze", {
            "analysis_mode": "neural-magically",
            "image": "not-valid-base64",
        })
        self.assertEqual(status, 400)
        self.assertEqual(result["code"], "unknown_analysis_mode")


    def test_compare_methods_requires_a_boolean(self):
        status, result, _ = self.request("POST", "/api/analyze", {
            "compare_methods": "false",
            "image": "not-valid-base64",
        })
        self.assertEqual(status, 400)
        self.assertEqual(result["code"], "invalid_compare_methods")

    def test_classical_mode_still_runs_through_http_api(self):
        status, result, _ = self.request("POST", "/api/analyze", {
            "analysis_mode": "classical",
            "preset_id": "synthetic_skewed_12",
            "pixels_per_cm": 400.0,
            "pixels_per_cm_x": 400.0,
            "pixels_per_cm_y": 400.0,
            "auto_skew": False,
            "prominence": 0.012,
            "weave_hint": "plain",
        })
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["analysis_mode"], "classical")
        self.assertIn("results", result)
        self.assertIn("audit", result)
        self.assertIn("visuals", result)
        uncertainty = result["results"]["calibration_uncertainty"]
        self.assertEqual(uncertainty["relative_uncertainty_pct"], 5.0)
        self.assertFalse(uncertainty["is_verified"])
        self.assertIn("not a statistical confidence interval", uncertainty["interpretation"])

    def test_comparison_executes_every_currently_available_method(self):
        status, result, _ = self.request("POST", "/api/analyze", {
            "analysis_mode": "learned",
            "compare_methods": True,
            "preset_id": "synthetic_skewed_12",
            "pixels_per_cm": 400.0,
            "pixels_per_cm_x": 400.0,
            "pixels_per_cm_y": 400.0,
            "auto_skew": False,
            "prominence": 0.012,
            "weave_hint": "plain",
        })
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["analysis_mode"], "comparison")
        comparison = result["comparison"]
        self.assertTrue(comparison["requested"])
        self.assertEqual([item["id"] for item in comparison["methods"]], ["classical"])
        self.assertEqual(
            {item["id"] for item in comparison["unavailable_methods"]},
            {"learned", "hybrid"},
        )
        self.assertIn("candidate_measurements", comparison["methods"][0])

    def test_calibration_profiles_endpoint(self):
        status, result, content_type = self.request("GET", "/api/calibration/profiles")
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "success")
        self.assertIn("profiles", result)
        profile_ids = [p["profile_id"] for p in result["profiles"]]
        self.assertIn("smartphone_macro_stand_v1", profile_ids)
        self.assertIn("smartphone_pick_glass_v1", profile_ids)
        self.assertIn("microscope_fabricnet_nominal", profile_ids)

    def test_specimen_analysis_endpoint(self):
        status, result, _ = self.request("POST", "/api/analyze/specimen", {
            "fabric_id": "test_specimen_1",
            "preset_id": "synthetic_skewed_12",
            "scale_x": 400.0,
            "scale_y": 400.0,
            "target_warp": 36.0,
            "target_weft": 30.0,
            "tolerance": 4.0,
        })
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "success")
        self.assertIn("specimen", result)
        spec = result["specimen"]
        self.assertEqual(spec["expected_regions"], 5)
        self.assertEqual(len(spec["regions"]), 5)
        self.assertIn("decision_status", spec)
        self.assertIn("warp_mean_ends_per_cm", spec)
        self.assertIn("weft_mean_picks_per_cm", spec)


if __name__ == "__main__":
    unittest.main()
