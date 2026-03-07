@echo off
setlocal enabledelayedexpansion
echo LoadWhistler DevelopmentKit for Windows
echo.

cd /d %~dp0\..

where uv >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing uv...
    powershell -ExecutionPolicy Bypass -Command ^
        "iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex"
    if errorlevel 1 (
        echo [CRITICAL] Failed to install uv
        exit /b 1
    )
) else (
    echo [INFO] uv is already installed.
)

if not exist .venv (
    echo [INFO] Creating venv...
    uv venv --python 3.12
    if errorlevel 1 (
        echo [CRITICAL] Failed to Create venv
        exit /b 1
    )
) else (
    echo [INFO] venv is ok
)

echo [INFO] Get dependent packages...
uv pip install --upgrade pip
uv pip install customtkinter pygame nuitka
if errorlevel 1 (
    echo [ERROR] Failed to install packages
    exit /b 1
)

echo.
echo [SUCCESS] 
echo.
echo Run LoadWhistler  :
echo uv run python LoadWhistler.py
echo.
echo Build LoadWhistler:
echo call scripts/build.bat
echo.
cmd /k