@echo off
chcp 65001 > nul
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
python -u run_pipeline.py
pause
