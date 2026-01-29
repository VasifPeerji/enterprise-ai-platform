@echo off
SETLOCAL EnableDelayedExpansion

echo 🚀 Starting Enterprise AI Platform API...

:: 1. Check if in conda environment
if "%CONDA_DEFAULT_ENV%"=="" (
    echo ⚠️  Conda environment not activated!
    echo Please run: conda activate enterprise-ai-platform
    exit /b 1
)

:: 2. Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating from .env.example...
    copy .env.example .env >nul
    echo ✅ .env created. Please edit it with your API keys.
    echo.
)

:: 3. Inform user of URLs
echo Starting server on http://localhost:8000
echo.
echo 📚 API Documentation: http://localhost:8000/docs
echo 📘 ReDoc: http://localhost:8000/redoc
echo ❤️  Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop
echo.

:: 4. Start the API server
poetry run uvicorn src.interfaces.http.main:app --reload --host 0.0.0.0 --port 8000

pause