import pytest

import os
import pytest

def _is_ci() -> bool:
    # Common CI env vars: GitHub Actions, Buildkite, GitLab CI, CircleCI, etc.
    return any(os.getenv(k) for k in ["CI", "GITHUB_ACTIONS", "BUILDKITE", "GITLAB_CI", "CIRCLECI"])

@pytest.mark.skipif(_is_ci(), reason="Skipped on CI (often no GPU/CUDA or torch wheel differs).")
def test_torch_import():
    torch = pytest.importorskip("torch")  # skips if torch isn't installed

    assert torch.__version__
    assert hasattr(torch, "randn")
    assert hasattr(torch, "matmul")

    # CPU sanity check (no CUDA usage)
    a = torch.randn(2, 3)
    b = torch.randn(3, 4)
    c = torch.matmul(a, b)
    assert c.shape == (2, 4)
    assert not getattr(a, "is_cuda", False)


def test_mujoco_import():
    """Test that mujoco can be imported successfully."""
    import mujoco
    assert mujoco.__version__ is not None
    assert hasattr(mujoco, 'MjModel')
    assert hasattr(mujoco, 'MjData')