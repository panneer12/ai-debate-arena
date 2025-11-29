@echo off
REM bootstrap.bat - Setup development environment for AI Debate Arena (Windows)
REM Usage: bootstrap.bat

setlocal enabledelayedexpansion

echo ============================================
echo AI Debate Arena - Bootstrap Script (Windows)
echo ============================================
echo.

REM Check Python version
echo [*] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected
echo.

REM Check if uv is installed
echo [*] Checking for uv package manager...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] uv not found. Installing uv...
    python -m pip install --user uv
    if errorlevel 1 (
        echo [ERROR] Failed to install uv
        echo Please install manually: pip install uv
        exit /b 1
    )
    echo [OK] uv installed successfully
) else (
    echo [OK] uv is already installed
)
echo.

REM Create virtual environment
echo [*] Setting up virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Skipping creation.
) else (
    echo Creating virtual environment with uv...
    uv venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo [*] Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [ERROR] Could not find activation script
    exit /b 1
)
echo.

REM Install dependencies
echo [*] Installing dependencies with uv...
if exist requirements.txt (
    echo Installing from requirements.txt...
    uv pip install -r requirements.txt
    echo [OK] Dependencies installed
) else (
    echo [ERROR] requirements.txt not found
    exit /b 1
)
echo.

REM Setup .env file
echo [*] Setting up environment configuration...
if not exist .env (
    if exist .env.example (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
        echo [WARNING] Please update .env with your actual API keys and configuration
        echo            Required: GOOGLE_API_KEY
    ) else (
        echo [WARNING] .env.example not found. Please create .env manually
    )
) else (
    echo [OK] .env file already exists
)
echo.

REM Setup git hooks
if exist scripts\setup-hooks.sh (
    echo [*] Setting up git hooks...
    bash scripts\setup-hooks.sh 2>nul
    if errorlevel 1 (
        echo [WARNING] Git hooks setup failed or bash not available
    ) else (
        echo [OK] Git hooks configured
    )
    echo.
)

REM Install development tools
echo [*] Installing development tools...
uv pip install black isort flake8 mypy pre-commit 2>nul
echo.

echo ============================================
echo [SUCCESS] Bootstrap completed successfully!
echo ============================================
echo.
echo Next steps:
echo   1. Edit .env and add your GOOGLE_API_KEY
echo   2. Run: venv\Scripts\activate.bat
echo   3. Run: start-server.bat
echo.
echo For testing:
echo   pytest                    # Run all tests
echo   pytest -m unit           # Run unit tests only
echo   pytest -m integration    # Run integration tests
echo.

endlocal
