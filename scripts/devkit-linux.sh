#!/usr/bin/env bash
set -e

echo "LoadWhistler DevelopmentKit for Linux"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if ! command -v uv >/dev/null 2>&1; then
    echo "[INFO] Installing uv..."
    curl -Ls https://astral.sh/uv/install.sh | sh
    echo "Please re-open to Use PATH"
    exit 0
else
    echo "[INFO] uv is already installed."
fi

export PATH="$HOME/.cargo/bin:$PATH"

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating venv..."
    uv venv --python 3.12
else
    echo "[INFO] venv is ok"
fi

echo "[INFO] Get dependent packages..."
uv pip install --upgrade pip
uv pip install customtkinter pygame nuitka

echo
echo "[SUCCESS]"
echo
echo "Run   LoadWhistler :"
echo "uv run python LoadWhistler.py"
echo
echo "Build LoadWhistler : (AppImage)"
echo "sudo apt/dnf/other install binutils patchelf gcc build-essential"
echo
echo "chmod +x ./scripts/build-linux-x64-appimage.sh"
echo "./scripts/build-linux-x64-appimage.sh"
echo

exec bash
