@echo off
setlocal
cd /d "%~dp0\..\..\.."
python -m jupyter lab "papers\cheng-2024-mouse-embryo-3d\notebooks\01_data_inventory.ipynb"
if errorlevel 1 (
  echo.
  echo Jupyter Lab 启动失败。请先运行：
  echo python -m pip install -r papers\cheng-2024-mouse-embryo-3d\notebooks\requirements.txt
  pause
)
