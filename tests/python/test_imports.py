import pytest

def test_torch_import():
    """Test that torch can be imported successfully."""
    import torch
    assert torch.__version__ is not None
    assert hasattr(torch, 'randn')
    assert hasattr(torch, 'matmul')

def test_mujoco_import():
    """Test that mujoco can be imported successfully."""
    import mujoco
    assert mujoco.__version__ is not None
    assert hasattr(mujoco, 'MjModel')
    assert hasattr(mujoco, 'MjData')