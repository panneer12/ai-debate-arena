# AI Debate Arena - Quick Start Guide

**Get up and running in 5 minutes!**

This guide will help you quickly set up and run the AI Debate Arena. For detailed information about the project architecture, features, and development, see [README.md](README.md).

---

## What is AI Debate Arena?

A multi-agent AI system where specialized agents (Conservative, Progressive, Fact Checker, Devil's Advocate, etc.) engage in formal debates to surface multiple perspectives and find common ground on controversial topics.

---

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** ([Download here](https://www.python.org/downloads/))
- **Google AI API Key** ([Get one free here](https://ai.google.dev/))
- **Git** (for cloning the repository)

Check your Python version:
```bash
python --version  # Should be 3.10 or higher
```

---

## Quick Setup (Recommended)

We provide automated scripts that handle everything for you.

### Linux / Mac / WSL

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-debate-arena.git
cd ai-debate-arena

# 2. Run bootstrap script (one-time setup)
chmod +x bootstrap.sh
./bootstrap.sh

# 3. Configure your API key
nano .env  # or use your preferred editor (vim, code, etc.)
# Replace 'your_google_api_key_here' with your actual API key

# 4. Start the application
./start-server.sh
```

### Windows

```cmd
REM 1. Clone the repository
git clone https://github.com/yourusername/ai-debate-arena.git
cd ai-debate-arena

REM 2. Run bootstrap script (one-time setup)
bootstrap.bat

REM 3. Configure your API key
notepad .env
REM Replace 'your_google_api_key_here' with your actual API key

REM 4. Start the application
start-server.bat
```

**That's it!** The scripts handle:
- ✅ Python version check
- ✅ Installing `uv` (ultra-fast package manager)
- ✅ Creating virtual environment
- ✅ Installing all dependencies
- ✅ Setting up configuration
- ✅ Configuring git hooks
- ✅ Validating your setup before starting

---

## Manual Setup (Alternative)

If you prefer to set up manually without using the automated scripts:

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-debate-arena.git
cd ai-debate-arena

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate.bat         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env              # Linux/Mac
copy .env.example .env            # Windows

# Edit .env and add your GOOGLE_API_KEY
nano .env  # or notepad .env on Windows

# Run the application
python main.py
```

---

## Running the Application

### Using the Start Script (Recommended)

The `start-server.sh` (or `start-server.bat` on Windows) script validates your setup before starting:

**Linux/Mac/WSL:**
```bash
./start-server.sh          # Normal mode
./start-server.sh --debug  # Debug mode (verbose logging)
./start-server.sh --demo   # Demo mode (runs demo scenario)
```

**Windows:**
```cmd
start-server.bat           # Normal mode
start-server.bat debug     # Debug mode
start-server.bat demo      # Demo mode
```

The script performs 6 pre-flight checks:
1. ✓ Virtual environment exists
2. ✓ Required packages installed
3. ✓ .env file exists
4. ✓ GOOGLE_API_KEY configured
5. ✓ Python version compatible
6. ✓ Application files present

### Manual Start

```bash
# Activate virtual environment
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat     # Windows

# Run the application
python main.py
```

---

## What the Scripts Do

### Bootstrap Script (`bootstrap.sh` / `bootstrap.bat`)

**What is `uv`?**
[uv](https://github.com/astral-sh/uv) is a blazingly fast Python package installer (10-100x faster than pip) written in Rust. It's fully compatible with pip and PyPI.

**The bootstrap script:**
1. Checks Python 3.10+ is installed
2. Installs `uv` package manager (if not already installed)
3. Creates a virtual environment using `uv`
4. Installs all dependencies from requirements.txt
5. Creates .env file from .env.example
6. Sets up git hooks for code quality
7. Installs development tools (black, isort, flake8, mypy)

**When to run:** Once during initial setup, or when dependencies change.

### Start Server Script (`start-server.sh` / `start-server.bat`)

**The start script:**
- Validates your entire setup with 6 pre-flight checks
- Ensures GOOGLE_API_KEY is configured (not the default value)
- Activates the virtual environment
- Starts the application in the mode you specify

**When to run:** Every time you want to start the application.

---

## Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat     # Windows

# Run all tests
pytest

# Run only fast unit tests (no API calls)
pytest -m unit

# Run integration tests (requires GOOGLE_API_KEY)
pytest -m integration

# Run with coverage report
pytest --cov=agents --cov=protocols --cov=tools
```

For detailed testing information, see [README.md](README.md#testing).

---

## Common Issues & Solutions

### ❌ "GOOGLE_API_KEY not set"

**Solution:** Edit `.env` and add your Google AI API key:
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```
Get a free API key at: https://ai.google.dev/

### ❌ "Python 3.10+ required"

**Solution:** Install Python 3.10 or higher from https://www.python.org/downloads/

Check your version: `python --version`

### ❌ "Virtual environment not found"

**Solution:** Run the bootstrap script:
```bash
./bootstrap.sh    # Linux/Mac
bootstrap.bat     # Windows
```

### ❌ "Permission denied" (Linux/Mac)

**Solution:** Make scripts executable:
```bash
chmod +x bootstrap.sh start-server.sh
```

### ❌ "Module not found" errors

**Solution:** Ensure virtual environment is activated and reinstall:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
uv pip install -r requirements.txt
# Or use pip: pip install -r requirements.txt
```

### ❌ Scripts not working on Windows

**Solution:** Use the `.bat` versions:
```cmd
bootstrap.bat
start-server.bat
```

---

## What to Configure

The main configuration is in the `.env` file:

**Required:**
- `GOOGLE_API_KEY` - Your Google AI API key (get it at https://ai.google.dev/)

**Optional (common settings):**
- `LLM_MODEL` - Gemini model to use (default: `gemini-2.5-flash-lite`)
- `LLM_TEMPERATURE` - Temperature 0.0-1.0 (default: `0.7`)
- `MAX_DEBATE_ROUNDS` - Max rounds (default: `5`)
- `LOG_LEVEL` - Logging level (default: `INFO`, use `DEBUG` for verbose)

For all available configuration options, see `.env.example` or [README.md](README.md#environment-variables).

---

## Next Steps

### 🎯 For Users

1. ✅ You're all set up! Run `./start-server.sh` to start
2. 📖 Read [README.md](README.md) for architecture, features, and detailed usage
3. 🧪 Explore the `demo/` directory for example scenarios
4. 🚀 See [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md) for production deployment

### 💻 For Contributors

1. ✅ You're all set up! The bootstrap script installed dev tools
2. 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. 🧪 Run the test suite: `pytest`
4. 🔍 Check code quality: `black . && isort . && flake8 .`
5. 💡 Pick an issue or feature to work on

---

## Getting Help

- 📖 Check [README.md](README.md) for detailed documentation
- 🐛 [Report issues on GitHub](https://github.com/yourusername/ai-debate-arena/issues)
- 💬 [Ask questions in Discussions](https://github.com/yourusername/ai-debate-arena/discussions)

---

## Quick Reference

```bash
# Setup (one-time)
./bootstrap.sh              # Linux/Mac
bootstrap.bat               # Windows

# Edit configuration
nano .env                   # Add your GOOGLE_API_KEY

# Start application
./start-server.sh           # Linux/Mac
start-server.bat            # Windows

# Run tests
pytest                      # All tests
pytest -m unit             # Fast unit tests only

# Code quality
black .                     # Format code
isort .                     # Sort imports
flake8 .                    # Check PEP 8
```

---

**Happy Debating! 🎯**

*"The best way to find truth isn't to ask one AI for the answer - it's to watch multiple AIs fight for it."*
