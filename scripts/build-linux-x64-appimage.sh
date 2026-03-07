#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
APPDIR="$ROOT_DIR/LoadWhistler.AppDir"
BIN_DEST="$APPDIR/usr/bin/LoadWhistler"
APPIMAGETOOL="$SCRIPT_DIR/appimagetool-x86_64.AppImage"
APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
OUTPUT="$ROOT_DIR/LoadWhistler-x64.AppImage"

if [ ! -f "$APPIMAGETOOL" ]; then
    echo "[INFO] fetching AppImageTool"
    curl -fsSL "$APPIMAGETOOL_URL" -o "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
    echo "[INFO] fetched AppImageTool: $APPIMAGETOOL"
else
    echo "[INFO] AppImageTool is OK: $APPIMAGETOOL"
fi

echo "[INFO] Building binary with nuitka..."
cd "$ROOT_DIR"

uv run nuitka \
    --standalone --onefile\
    --enable-plugin=tk-inter \
    --include-data-files=font/noto.ttf=font/noto.ttf \
    --company-name=ABATBeliever \
    --product-name="LoadWhistler" \
    --file-description="Simple local music player" \
    LoadWhistler.py

echo "[INFO] Building binary OK"

NUITKA_OUTPUT="$ROOT_DIR/LoadWhistler.bin"
if [ ! -f "$NUITKA_OUTPUT" ]; then
    echo "[ERROR] Failed to find LoadWhistler.bin: $NUITKA_OUTPUT"
    exit 1
fi

mkdir -p "$APPDIR/usr/bin"
cp "$NUITKA_OUTPUT" "$BIN_DEST"

echo "[INFO] chmod..."
chmod +x "$APPDIR/AppRun"
chmod +x "$BIN_DEST"
chmod +x "$APPDIR/icon.png"

echo "[INFO] Building .AppImage with AppImageTool..."
cd "$ROOT_DIR"

ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "$OUTPUT"

chmod +x "$OUTPUT"

echo ""
echo "[INFO] Build Sucsess! [x64]"
