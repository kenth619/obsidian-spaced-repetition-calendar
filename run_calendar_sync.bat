@echo off
REM === Change to the repo folder ===
cd /d "C:\Users\Kenth\obsidian-spaced-repetition-calendar"

REM === Ensure Python uses the correct environment variable ===
setlocal
if "%GITHUB_PAT%"=="" (
    echo ❌ ERROR: GITHUB_PAT environment variable is not set.
    echo Please run: setx GITHUB_PAT "your_token_here"
    pause
    exit /b 1
)

REM === Run the Python script ===
python auto_sync_obsidian_calendar.py

REM === Pause so you can see the output ===
echo.
echo ✅ Calendar sync completed. Press any key to close.
pause
