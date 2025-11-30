#!/bin/bash
# start-server.sh - Start AI Debate Arena server with validation
# Usage: ./start-server.sh [--debug] [--demo]

set -e  # Exit on error

echo "============================================"
echo "AI Debate Arena - Server Startup"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DEBUG_MODE=false
DEMO_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --demo)
            DEMO_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./start-server.sh [--debug] [--demo]"
            exit 1
            ;;
    esac
done

# Validation checks
VALIDATION_FAILED=false

# Detect the correct Python executable in venv
if [ -f "venv/bin/python" ]; then
    VENV_PYTHON="venv/bin/python"
elif [ -f "venv/Scripts/python.exe" ]; then
    VENV_PYTHON="venv/Scripts/python.exe"
else
    VENV_PYTHON="python"
fi

echo "🔍 Running pre-flight checks..."
echo ""

# 1. Check if virtual environment exists
echo "1️⃣  Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo -e "${YELLOW}   Run: ./bootstrap.sh${NC}"
    VALIDATION_FAILED=true
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# 2. Check if venv has required packages
echo "2️⃣  Checking installed packages..."
if [ -f "$VENV_PYTHON" ]; then
    # Check for key packages using venv Python
    MISSING_PACKAGES=()

    if ! $VENV_PYTHON -c "import google.genai" 2>/dev/null; then
        MISSING_PACKAGES+=("google-genai")
    fi

    if ! $VENV_PYTHON -c "import fastapi" 2>/dev/null; then
        MISSING_PACKAGES+=("fastapi")
    fi

    if ! $VENV_PYTHON -c "import pydantic" 2>/dev/null; then
        MISSING_PACKAGES+=("pydantic")
    fi

    if ! $VENV_PYTHON -c "import dotenv" 2>/dev/null; then
        MISSING_PACKAGES+=("python-dotenv")
    fi

    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing packages: ${MISSING_PACKAGES[*]}${NC}"
        echo -e "${YELLOW}   Run: ./bootstrap.sh${NC}"
        VALIDATION_FAILED=true
    else
        echo -e "${GREEN}✓ Required packages installed${NC}"
    fi
fi

# 3. Check if .env file exists
echo "3️⃣  Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}   Run: cp .env.example .env${NC}"
    echo -e "${YELLOW}   Then edit .env with your API keys${NC}"
    VALIDATION_FAILED=true
else
    echo -e "${GREEN}✓ .env file exists${NC}"

    # 4. Validate required environment variables
    echo "4️⃣  Validating environment variables..."

    # Load .env file
    export $(grep -v '^#' .env | xargs)

    MISSING_VARS=()

    # Check GOOGLE_API_KEY
    if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
        MISSING_VARS+=("GOOGLE_API_KEY")
    fi

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing or invalid environment variables: ${MISSING_VARS[*]}${NC}"
        echo -e "${YELLOW}   Edit .env and set: ${MISSING_VARS[*]}${NC}"
        VALIDATION_FAILED=true
    else
        echo -e "${GREEN}✓ Required environment variables configured${NC}"
    fi
fi

# 5. Check Python version
echo "5️⃣  Checking Python version..."
if [ -f "$VENV_PYTHON" ]; then
    if ! $VENV_PYTHON -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
        echo -e "${RED}❌ Python 3.10+ required${NC}"
        VALIDATION_FAILED=true
    else
        PYTHON_VERSION=$($VENV_PYTHON --version | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
    fi
else
    echo -e "${RED}❌ Virtual environment Python not found${NC}"
    VALIDATION_FAILED=true
fi

# 6. Check if main.py exists
echo "6️⃣  Checking application files..."
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py not found${NC}"
    VALIDATION_FAILED=true
else
    echo -e "${GREEN}✓ Application files present${NC}"
fi

echo ""

# If validation failed, exit
if [ "$VALIDATION_FAILED" = true ]; then
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}❌ Pre-flight checks failed${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    echo "Please fix the errors above and try again."
    echo ""
    exit 1
fi

# All checks passed
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ All pre-flight checks passed${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Start the server
if [ "$DEMO_MODE" = true ]; then
    echo -e "${BLUE}🚀 Starting in DEMO mode...${NC}"
    echo ""

    if [ -f "demo/run_scenario_a.py" ]; then
        $VENV_PYTHON -m demo.run_scenario_a
    else
        echo -e "${YELLOW}⚠ Demo script not found, running main.py instead${NC}"
        $VENV_PYTHON main.py
    fi

elif [ "$DEBUG_MODE" = true ]; then
    echo -e "${BLUE}🐛 Starting in DEBUG mode...${NC}"
    echo ""
    export LOG_LEVEL=DEBUG
    $VENV_PYTHON main.py

else
    echo -e "${BLUE}🚀 Starting AI Debate Arena Server...${NC}"
    echo ""

    # Check if we should run the FastAPI server or CLI
    if [ -f "demo/server.py" ]; then
        echo "Starting FastAPI server..."
        $VENV_PYTHON -m uvicorn demo.server:app --host ${HOST:-0.0.0.0} --port ${PORT:-8080} --reload
    elif [ -f "server.py" ]; then
        echo "Starting FastAPI server..."
        $VENV_PYTHON -m uvicorn server:app --host ${HOST:-0.0.0.0} --port ${PORT:-8080} --reload
    elif [ -f "api/main.py" ]; then
        echo "Starting FastAPI server..."
        $VENV_PYTHON -m uvicorn api.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8080} --reload
    else
        # No server file, run CLI
        echo -e "${YELLOW}⚠ No server.py found, running CLI mode${NC}"
        $VENV_PYTHON main.py
    fi
fi
