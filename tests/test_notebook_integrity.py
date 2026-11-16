import ast
import json
import os
import unittest


class TestFabricNetNotebookIntegrity(unittest.TestCase):
    def setUp(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "notebooks", "04_real_fabric_benchmark.ipynb"
        )
        with open(path, "r", encoding="utf-8") as handle:
            self.notebook = json.load(handle)

    def test_notebook_is_valid_json_with_expected_cells_and_no_stale_outputs(self):
        self.assertEqual(len(self.notebook["cells"]), 7)
        for cell in self.notebook["cells"]:
            if cell["cell_type"] == "code":
                self.assertIsNone(cell["execution_count"])
                self.assertEqual(cell["outputs"], [])

    def test_notebook_uses_canonical_runner_and_python_cells_parse(self):
        source = "\\n".join(
            "".join(cell["source"])
            for cell in self.notebook["cells"]
            if cell["cell_type"] == "code"
        )
        self.assertIn("scripts/run_fabricnet_benchmark.py", source)
        self.assertIn('benchmark.get("total_samples") != 130', source)
        self.assertNotIn("import torch", source)
        self.assertNotIn("import cv2", source)
        for cell in self.notebook["cells"]:
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]))

        runner_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "run_fabricnet_benchmark.py"
        )
        with open(runner_path, "r", encoding="utf-8") as handle:
            runner_source = handle.read()
        self.assertIn("allow_nan=False", runner_source)
        self.assertIn("bootstrap_samples=1000", runner_source)



if __name__ == "__main__":
    unittest.main()
