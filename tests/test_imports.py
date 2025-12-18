import unittest


class TestImports(unittest.TestCase):
    
    def test_torch_import(self):
        """Test that torch can be imported successfully."""
        import torch
        self.assertIsNotNone(torch.__version__)
        self.assertTrue(hasattr(torch, 'randn'))
        self.assertTrue(hasattr(torch, 'matmul'))
    
    def test_mujoco_import(self):
        """Test that mujoco can be imported successfully."""
        import mujoco
        self.assertIsNotNone(mujoco.__version__)
        self.assertTrue(hasattr(mujoco, 'MjModel'))
        self.assertTrue(hasattr(mujoco, 'MjData'))
