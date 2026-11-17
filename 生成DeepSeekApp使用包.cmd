@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scripts\export_deepseek_app.py "..\DeepSeekApp使用包" --zip
if errorlevel 1 (
  echo Export failed. Read the error above. Existing files will not be overwritten.
) else (
  echo Open the exported folder and upload the TXT file in the DeepSeek App.
  start "" "..\DeepSeekApp使用包"
)
pause
