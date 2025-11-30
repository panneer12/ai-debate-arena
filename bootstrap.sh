#!/bin/bash
# bootstrap.sh - Setup development environment for AI Debate Arena
# Usage: ./bootstrap.sh

set -e  # Exit on error

echo "============================================"
echo "AI Debate Arena - Bootstrap Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.10"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}❌ Python $PYTHON_VERSION is installed, but Python 3.10+ is required.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo ""

# Check if uv is installed, if not install it
echo "📦 Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠ uv not found. Installing uv...${NC}"

    # Install uv using pip
    if ! python3 -m pip install --user uv; then
        echo -e "${YELLOW}⚠ pip install failed, trying alternative method...${NC}"
        # Alternative: use curl (for Linux/Mac)
        if command -v curl &> /dev/null; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
        else
            echo -e "${RED}❌ Failed to install uv. Please install it manually:${NC}"
            echo "   pip install uv"
            echo "   OR visit: https://github.com/astral-sh/uv"
            exit 1
        fi
    fi

    # Add uv to PATH if needed
    export PATH="$HOME/.local/bin:$PATH"

    echo -e "${GREEN}✓ uv installed successfully${NC}"
else
    echo -e "${GREEN}✓ uv is already installed${NC}"
fi
echo ""

# Create virtual environment if it doesn't exist
echo "🔨 Setting up virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Skipping creation.${NC}"
else
    echo "Creating virtual environment with uv..."
    uv venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo -e "${RED}❌ Could not find activation script${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies using uv
echo "📥 Installing dependencies with uv..."
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    uv pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Setup .env file if it doesn't exist
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please update .env with your actual API keys and configuration${NC}"
        echo -e "${YELLOW}   Required: GOOGLE_API_KEY${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found. Please create .env manually${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Setup pre-commit hooks if available
if [ -f "scripts/setup-hooks.sh" ]; then
    echo "🔧 Setting up git hooks..."
    bash scripts/setup-hooks.sh
    echo -e "${GREEN}✓ Git hooks configured${NC}"
    echo ""
fi

# Install development tools
echo "🛠️  Installing development tools..."
uv pip install black isort flake8 mypy pre-commit 2>/dev/null || echo -e "${YELLOW}⚠ Some dev tools may already be installed${NC}"
echo ""

echo "============================================"
echo -e "${GREEN}✅ Bootstrap completed successfully!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your GOOGLE_API_KEY"
echo "  2. Run: source venv/bin/activate  (or venv\\Scripts\\activate on Windows)"
echo "  3. Run: ./start-server.sh"
echo ""
echo "For testing:"
echo "  pytest                    # Run all tests"
echo "  pytest -m unit           # Run unit tests only"
echo "  pytest -m integration    # Run integration tests"
echo ""
