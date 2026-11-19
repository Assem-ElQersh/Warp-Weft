# The mechanistic justification for this step is: verify model registry loading, checkpoint cryptographic integrity, and PyTorch model instantiation across deterministic and deep learning architectures.

import os
import unittest
import torch
import numpy as np

from experiments.learned_models.model_registry import ModelRegistry


class TestModelRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = ModelRegistry()

    def test_registry_contains_required_models(self):
        models = self.registry.list_models()
        self.assertGreaterEqual(len(models), 10)
        m_ids = [m.model_id for m in models]
        self.assertIn("deterministic_dual_engine", m_ids)
        self.assertIn("warp_weft_unet_v1", m_ids)
        self.assertIn("segformer_b0", m_ids)
        self.assertIn("sam_2_1_tiny", m_ids)
        self.assertIn("dinov2_vits14", m_ids)
        self.assertIn("hybrid_unet_skeleton_pitch", m_ids)

    def test_checkpoint_verification(self):
        ok_det, msg_det = self.registry.verify_checkpoint("deterministic_dual_engine")
        self.assertTrue(ok_det)

        ok_unet, msg_unet = self.registry.verify_checkpoint("warp_weft_unet_v1")
        self.assertTrue(ok_unet)
        self.assertIn("bytes", msg_unet)

    def test_instantiate_and_run_unet(self):
        model = self.registry.instantiate_model("warp_weft_unet_v1", device="cpu")
        self.assertIsInstance(model, torch.nn.Module)

        # Forward pass dummy tensor: [B, 1, 256, 256]
        dummy = torch.randn(1, 1, 256, 256, dtype=torch.float32)
        with torch.no_grad():
            out = model(dummy)
        self.assertEqual(out.shape, (1, 3, 256, 256))

    def test_instantiate_and_run_deterministic(self):
        det_runner = self.registry.instantiate_model("deterministic_dual_engine", device="cpu")
        # Test on dummy 200x200 plain weave image
        img = np.ones((200, 200), dtype=np.uint8) * 128
        res = det_runner(image=img, scale_x=250.0, scale_y=250.0, weave_type="plain")
        self.assertIn("warp_density", res)
        self.assertIn("weft_density", res)
        self.assertIn("decision_status", res)


if __name__ == "__main__":
    unittest.main()
