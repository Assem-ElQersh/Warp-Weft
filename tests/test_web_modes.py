import json
import os
import tempfile
import unittest

from web_app.modes import get_analysis_modes


class TestWebModeAvailability(unittest.TestCase):
    def test_classical_is_available_but_learned_modes_are_not_fabricated(self):
        with tempfile.TemporaryDirectory() as root:
            result = get_analysis_modes(root)
        modes = {item["id"]: item for item in result["modes"]}
        self.assertTrue(modes["classical"]["available"])
        self.assertFalse(modes["learned"]["available"])
        self.assertFalse(modes["hybrid"]["available"])
        self.assertIn("no validated learned inference dispatcher", modes["learned"]["reason"])


    def test_malformed_registry_is_reported_as_unavailable_without_server_error(self):
        with tempfile.TemporaryDirectory() as root:
            learned_dir = os.path.join(root, "experiments", "learned_models")
            os.makedirs(learned_dir)
            with open(os.path.join(learned_dir, "model_registry.json"), "w", encoding="utf-8") as handle:
                json.dump(["not", "an", "object"], handle)
            result = get_analysis_modes(root)
        modes = {item["id"]: item for item in result["modes"]}
        self.assertFalse(modes["learned"]["available"])
        self.assertEqual(result["registered_models"], [])

    def test_checkpoint_path_cannot_escape_learned_model_directory(self):
        with tempfile.TemporaryDirectory() as root:
            learned_dir = os.path.join(root, "experiments", "learned_models")
            os.makedirs(learned_dir)
            with open(os.path.join(root, "outside.bin"), "wb") as handle:
                handle.write(b"not a model")
            with open(os.path.join(learned_dir, "model_registry.json"), "w", encoding="utf-8") as handle:
                json.dump({"checkpoint_path":"../../outside.bin"}, handle)
            web_dir = os.path.join(root, "web_app")
            os.makedirs(web_dir)
            with open(os.path.join(web_dir, "learned_inference.py"), "w", encoding="utf-8") as handle:
                handle.write("# adapter placeholder")
            result = get_analysis_modes(root)
        modes = {item["id"]: item for item in result["modes"]}
        self.assertFalse(modes["learned"]["available"])
        self.assertFalse(modes["learned"]["artifacts_present"])

    def test_learned_modes_require_registry_checkpoint_and_adapter(self):
        with tempfile.TemporaryDirectory() as root:
            learned_dir = os.path.join(root, "experiments", "learned_models")
            os.makedirs(learned_dir)
            with open(os.path.join(learned_dir, "model_registry.json"), "w", encoding="utf-8") as handle:
                json.dump({"checkpoint_path":"model.bin"}, handle)
            with open(os.path.join(learned_dir, "model.bin"), "wb") as handle:
                handle.write(b"weights")
            web_dir = os.path.join(root, "web_app")
            os.makedirs(web_dir)
            with open(os.path.join(web_dir, "learned_inference.py"), "w", encoding="utf-8") as handle:
                handle.write("# adapter placeholder")
            result = get_analysis_modes(root)
        modes = {item["id"]: item for item in result["modes"]}
        self.assertFalse(modes["learned"]["available"])
        self.assertFalse(modes["hybrid"]["available"])
        self.assertTrue(modes["learned"]["artifacts_present"])


if __name__ == "__main__":
    unittest.main()
