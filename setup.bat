@echo off
REM Setup script for Enterprise AI Platform (Windows)
REM This script creates the conda environment and initializes Poetry

echo 🚀 Setting up Enterprise AI Platform...

REM Check if conda is installed
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Conda is not installed. Please install Miniconda or Anaconda first.
    exit /b 1
)

REM Create conda environment
echo 📦 Creating conda environment...
call conda env create -f environment.yml

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create conda environment
    exit /b 1
)

echo ✅ Conda environment created successfully!
echo.
echo Next steps:
echo   1. Activate the environment:
echo      conda activate enterprise-ai-platform
echo.
echo   2. Initialize Poetry dependencies:
echo      poetry install
echo.
echo   3. Start development!

pause
