#!/bin/bash
# third_party/vendor.sh

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Change to the project root (Buck2 sets this variable)
cd "${BUILD_WORKING_DIRECTORY:-.}" || exit 1

WHEEL_DIR="third_party/python/wheels"

echo "📦 1. Compiling requirements (using uv)..."
# Create a virtual environment
uv venv .venv --python 3.11.13 --seed --clear
source .venv/bin/activate

# CRITICAL: uv venvs are empty. We must install pip to use 'pip download'
uv pip install pip

echo "🐍 Verifying environment..."

# 1. Get the path of the current python3 binary
PYTHON_BIN=$(which python3)

# 2. Get the expected venv path (Assuming we are in the root and venv is .venv)
# We use $(pwd) to ensure absolute path comparison
VENV_PATH="$(pwd)/.venv"

# 3. Check if python is running from inside the .venv directory
if [[ "$PYTHON_BIN" != *"$VENV_PATH"* ]]; then
    echo "❌ MISMATCH DETECTED!"
    echo "   Current Python: $PYTHON_BIN"
    echo "   Expected Venv:  $VENV_PATH/..."
    echo "   Please run: source .venv/bin/activate"
    exit 1
fi

# 4. Verify pip is actually installed in this specific python
if ! python3 -m pip --version > /dev/null 2>&1; then
    echo "❌ Error: 'pip' module not found in $(python3 --version)."
    echo "   Running 'uv pip install pip' to fix..."
    uv pip install pip
fi

echo "✅ Environment is healthy: using .venv python."

# Compile the lockfile
# Note: Added specific index URLs to ensure we find the right packages
uv pip compile third_party/python/requirements.in \
  -o third_party/python/requirements.txt \
  --python-platform linux \
  --python-version 3.11.13 \
  --generate-hashes \
  --emit-index-url \
  --no-strip-extras \
  --index-strategy unsafe-best-match \
  --index-url=https://pypi.tuna.tsinghua.edu.cn/simple \
  --extra-index-url=https://pypi.org/simple  \
  --extra-index-url=https://download.pytorch.org/whl/cu130

# echo "🧹 2. Cleaning old wheels..."
# rm -rf "$WHEEL_DIR"
# mkdir -p "$WHEEL_DIR"

echo "⬇️  3. Downloading wheels..."
# We use standard pip here because 'uv' doesn't support 'download' yet.
# Since we are using a strict requirements.txt with hashes, we use standard
# pip download -r instead of xargs to ensure hashes are verified correctly.

uv run python third_party/python/mp_download.py --target-dir "$WHEEL_DIR"

echo "⚙️  4. Generating BUCK file..."
# FIX: Passed the WHEEL_DIR variable correctly
uv run python third_party/python/generate.py --target-dir "$WHEEL_DIR"

echo "✅ Done! Wheels are ready in $WHEEL_DIR."