@echo off
REM start-server.bat - Start AI Debate Arena server with validation (Windows)
REM Usage: start-server.bat [debug|demo]

setlocal enabledelayedexpansion

echo ============================================
echo AI Debate Arena - Server Startup (Windows)
echo ============================================
echo.

REM Parse arguments
set DEBUG_MODE=false
set DEMO_MODE=false

if "%1"=="--debug" set DEBUG_MODE=true
if "%1"=="debug" set DEBUG_MODE=true
if "%1"=="--demo" set DEMO_MODE=true
if "%1"=="demo" set DEMO_MODE=true

REM Validation checks
set VALIDATION_FAILED=false

echo [*] Running pre-flight checks...
echo.

REM 1. Check virtual environment
echo [1/6] Checking virtual environment...
if not exist venv (
    echo [ERROR] Virtual environment not found
    echo         Run: bootstrap.bat
    set VALIDATION_FAILED=true
) else (
    echo [OK] Virtual environment exists
)

REM 2. Activate venv and check packages
echo [2/6] Checking installed packages...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat

    REM Check for key packages
    python -c "import google.genai" 2>nul
    if errorlevel 1 (
        echo [ERROR] Missing package: google-genai
        set VALIDATION_FAILED=true
    )

    python -c "import fastapi" 2>nul
    if errorlevel 1 (
        echo [ERROR] Missing package: fastapi
        set VALIDATION_FAILED=true
    )

    python -c "import pydantic" 2>nul
    if errorlevel 1 (
        echo [ERROR] Missing package: pydantic
        set VALIDATION_FAILED=true
    )

    python -c "import dotenv" 2>nul
    if errorlevel 1 (
        echo [ERROR] Missing package: python-dotenv
        set VALIDATION_FAILED=true
    )

    if "!VALIDATION_FAILED!"=="false" (
        echo [OK] Required packages installed
    ) else (
        echo [ERROR] Some packages are missing. Run: bootstrap.bat
    )
)

REM 3. Check .env file
echo [3/6] Checking environment configuration...
if not exist .env (
    echo [ERROR] .env file not found
    echo         Run: copy .env.example .env
    echo         Then edit .env with your API keys
    set VALIDATION_FAILED=true
) else (
    echo [OK] .env file exists
)

REM 4. Validate environment variables
echo [4/6] Validating environment variables...
if exist .env (
    REM Load .env file
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )

    if "!GOOGLE_API_KEY!"=="" (
        echo [ERROR] GOOGLE_API_KEY not set in .env
        set VALIDATION_FAILED=true
    ) else if "!GOOGLE_API_KEY!"=="your_google_api_key_here" (
        echo [ERROR] GOOGLE_API_KEY has default value. Please update .env
        set VALIDATION_FAILED=true
    ) else (
        echo [OK] Required environment variables configured
    )
)

REM 5. Check Python version
echo [5/6] Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.10+ required
    set VALIDATION_FAILED=true
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python !PYTHON_VERSION!
)

REM 6. Check application files
echo [6/6] Checking application files...
if not exist main.py (
    echo [ERROR] main.py not found
    set VALIDATION_FAILED=true
) else (
    echo [OK] Application files present
)

echo.

REM Exit if validation failed
if "%VALIDATION_FAILED%"=="true" (
    echo ============================================
    echo [ERROR] Pre-flight checks failed
    echo ============================================
    echo.
    echo Please fix the errors above and try again.
    echo.
    exit /b 1
)

REM All checks passed
echo ============================================
echo [SUCCESS] All pre-flight checks passed
echo ============================================
echo.

REM Start the server
if "%DEMO_MODE%"=="true" (
    echo [*] Starting in DEMO mode...
    echo.
    if exist demo\run_scenario_a.py (
        python -m demo.run_scenario_a
    ) else (
        echo [WARNING] Demo script not found, running main.py instead
        python main.py
    )
) else if "%DEBUG_MODE%"=="true" (
    echo [*] Starting in DEBUG mode...
    echo.
    set LOG_LEVEL=DEBUG
    python main.py
) else (
    echo [*] Starting AI Debate Arena...
    echo.

    REM Check for FastAPI server
    if exist server.py (
        echo Starting FastAPI server...
        if "%PORT%"=="" set PORT=8080
        python -m uvicorn server:app --host 0.0.0.0 --port %PORT% --reload
    ) else if exist api\main.py (
        echo Starting FastAPI server...
        if "%PORT%"=="" set PORT=8080
        python -m uvicorn api.main:app --host 0.0.0.0 --port %PORT% --reload
    ) else (
        REM Run CLI application
        python main.py
    )
)

endlocal
