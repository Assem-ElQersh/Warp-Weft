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

    def test_notebook_uses_current_numpy_pipeline_and_rejects_partial_datasets(self):
        source = "\n".join(
            "".join(cell["source"])
            for cell in self.notebook["cells"]
            if cell["cell_type"] == "code"
        )
        self.assertIn("NumPy FFT and Pillow", source)
        self.assertNotIn("import torch", source)
        self.assertNotIn("import cv2", source)
        self.assertIn("len(df_res) != 130", source)
        self.assertIn("allow_nan=False", source)
        self.assertIn("rejection_rate_pct", source)


if __name__ == "__main__":
    unittest.main()
