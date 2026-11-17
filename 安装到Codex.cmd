@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scripts\install_local.py --client codex
if errorlevel 1 (
  echo Installation failed. Read the error above. Python 3.10+ is required.
) else (
  echo Installed. Use $mathmodel-skill on your next Codex turn.
)
pause
