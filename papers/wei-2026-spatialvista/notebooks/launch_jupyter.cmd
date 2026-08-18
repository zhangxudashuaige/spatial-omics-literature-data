@echo off
cd /d "%~dp0"
set "JUPYTER_RUNTIME_DIR=C:\Users\l\Documents\Codex\jupyter-runtime"
if not exist "%JUPYTER_RUNTIME_DIR%" mkdir "%JUPYTER_RUNTIME_DIR%"
"D:\anaconda\envs\spatialvista\Scripts\jupyter-lab.exe" "%~dp0spatialvista_mouse_brain.ipynb" --notebook-dir "%~dp0"
