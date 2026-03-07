@echo off
setlocal

cd /d %~dp0\..

echo [INFO] Cleanup...
del /f config.ini
rmdir /S /Q .venv
rmdir /S /Q "LoadWhistler.dist"
rmdir /S /Q "__pycache__"

endlocal
exit /b