import os
import unittest


class TestWebUIContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(root, "web_app", "index.html"), "r", encoding="utf-8") as handle:
            cls.html = handle.read()

    def test_existing_workflow_controls_and_diagnostic_panels_are_preserved(self):
        required_ids = [
            "upload-dropzone", "file-input", "preset-grid",
            "preset-scale-select", "input-pixels-cm", "select-weave-hint",
            "input-prominence", "chk-auto-skew", "img-roi-preview",
            "img-rectified-crop", "img-radon-sweep", "img-warp-profile",
            "img-weft-profile", "img-fft-spectrum", "tab-audit",
            "btn-dl-en", "btn-dl-ar",
        ]
        for element_id in required_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

    def test_three_modes_model_registry_and_comparison_controls_exist(self):
        for element_id in (
            "select-analysis-mode", "select-learned-model",
            "model-config-status", "chk-compare-methods",
            "comparison-panel", "comparison-rows", "comparison-unavailable",
        ):
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)
        for mode in ('value="classical"', 'value="learned"', 'value="hybrid"'):
            self.assertIn(mode, self.html)

    def test_bilingual_mode_and_comparison_labels_exist(self):
        for phrase in (
            "Compare all available methods on the same image",
            "مقارنة جميع الطرق المتاحة على نفس الصورة",
            "Registered model",
            "النموذج المسجل",
        ):
            self.assertIn(phrase, self.html)


if __name__ == "__main__":
    unittest.main()
