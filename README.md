# AI Debate Arena

**Multi-agent debate system for finding truth through structured conflict**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini-4285F4)](https://ai.google.dev/)

> 📖 **New here?** Check out [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide with automated scripts!

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Code Quality & CI/CD](#code-quality--cicd)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **AI Debate Arena** is a multi-agent AI system where specialized agents engage in formal debates on controversial topics. Through adversarial discourse, real-time fact-checking, and synthesis, the system surfaces multiple perspectives and finds common ground.

### The Problem

- 68% of Americans trapped in information echo chambers
- Misinformation spreads 6x faster than truth
- Political polarization at record highs
- Single-perspective AI reinforces existing biases

### The Solution

Multiple specialized AI agents debate complex topics:
- **Perspective Agents** argue different viewpoints (Conservative, Progressive, etc.)
- **Fact Checker** verifies claims in real-time using Google Search
- **Devil's Advocate** challenges all positions to prevent groupthink
- **Moderator** orchestrates formal debate structure
- **Synthesizer** generates nuanced conclusions with common ground

---

## Quick Start

**Get started in 3 simple steps:**

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/ai-debate-arena.git
cd ai-debate-arena

# 2. Run bootstrap (one-time setup)
./bootstrap.sh           # Linux/Mac/WSL
bootstrap.bat            # Windows

# 3. Configure and start
# Edit .env with your GOOGLE_API_KEY, then:
./start-server.sh        # Linux/Mac/WSL
start-server.bat         # Windows
```

**📖 For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)**

### What the Bootstrap Script Does

Our automated setup script handles everything:
- ✅ Checks Python 3.10+ installation
- ✅ Installs `uv` (ultra-fast package manager)
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up environment configuration
- ✅ Configures git hooks for code quality
- ✅ Installs development tools

---

## Architecture

```
┌─────────────────────────────────┐
│     MODERATOR AGENT             │
│   (Debate Orchestration)        │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼─────┐
│CONSERV-│      │PROGRESS- │
│ATIVE   │◄────►│IVE       │
└───┬────┘      └────┬─────┘
    │                │
    └────────┬───────┘
             │
    ┌────────▼────────┐
    │  FACT CHECKER   │
    │  (Google Search)│
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ DEVIL'S ADVOCATE│
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  SYNTHESIZER    │
    └─────────────────┘
```

### Core Agents

1. **Moderator Agent** (`agents/moderator.py`)
   - Manages debate flow and enforces protocol
   - Orchestrates sequential debate phases
   - Coordinates timing and turn-taking

2. **Conservative Agent** (`agents/perspectives/conservative.py`)
   - Traditional values perspective
   - Free market economic approach
   - Individual responsibility focus

3. **Progressive Agent** (`agents/perspectives/progressive.py`)
   - Social justice perspective
   - Collective action approach
   - Systemic change focus

4. **Fact Checker Agent** (`agents/evidence/fact_checker.py`)
   - Real-time claim verification via Google Search
   - Source credibility scoring
   - Confidence-weighted verification

5. **Devil's Advocate Agent** (`agents/evidence/devils_advocate.py`)
   - Challenges all positions to prevent groupthink
   - Identifies logical fallacies
   - Questions assumptions

6. **Synthesizer Agent** (`agents/synthesis/synthesizer.py`)
   - Generates nuanced conclusions
   - Finds common ground between perspectives
   - Identifies consensus points

---

## Features

### ✨ Multi-Agent Debate System
- **Parallel agent execution** - Agents process information simultaneously
- **Sequential debate phases** - Opening statements, rebuttals, cross-examination, closing
- **Formal argumentation protocols** - Structured debate rules and timing

### 🔍 Real-Time Fact Checking
- **Google Search integration** - Automated web search for claim verification
- **Source credibility scoring** - Evaluates reliability of sources
- **Confidence-weighted verification** - Assigns confidence levels to fact-checks

### 🤝 Common Ground Discovery
- **Shared value identification** - Finds areas of agreement
- **Compromise solution generation** - Synthesizes middle-ground positions
- **Nuanced conclusions** - Avoids binary thinking

### 📊 Quality Metrics
- **Logical validity checking** - Identifies sound arguments
- **Fallacy detection** - Catches common logical errors
- **Argument strength scoring** - Rates persuasiveness

### 🔧 Developer Experience
- **Automated setup** - Bootstrap script handles everything
- **Pre-commit hooks** - Automatic code formatting and linting
- **Comprehensive tests** - Unit and integration test suites
- **Type safety** - MyPy type checking
- **CI/CD pipeline** - Automated quality checks

---

## Usage Examples

### Basic Usage (CLI)

```python
import asyncio
from agents.moderator import ModeratorAgent
from agents.perspectives import ConservativeAgent, ProgressiveAgent
from agents.evidence import FactCheckerAgent, DevilsAdvocateAgent
from agents.synthesis import SynthesizerAgent

async def main():
    # Initialize agents
    moderator = ModeratorAgent()
    conservative = ConservativeAgent()
    progressive = ProgressiveAgent()
    fact_checker = FactCheckerAgent()
    devils_advocate = DevilsAdvocateAgent()
    synthesizer = SynthesizerAgent()

    # Start debate
    result = await moderator.start_debate(
        topic="Should we have universal healthcare?",
        debaters=[conservative, progressive],
        fact_checker=fact_checker,
        devils_advocate=devils_advocate,
        synthesizer=synthesizer
    )

    # View results
    print("\nCONSENSUS POINTS:")
    for point in result["synthesis"]["consensus_points"]:
        print(f"  ✓ {point}")

    print("\nSTRONGEST ARGUMENTS:")
    for agent, arg in result["synthesis"]["strongest_arguments"].items():
        print(f"  • {agent}: {arg}")

    print("\nCOMMON GROUND:")
    print(f"  {result['synthesis']['common_ground']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Application

```bash
# Using the start script (recommended)
./start-server.sh        # Linux/Mac
start-server.bat         # Windows

# Or manually
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

### Running Demos

```bash
# Run demo scenario
./start-server.sh --demo  # Linux/Mac
start-server.bat demo     # Windows

# Or directly
python -m demo.run_scenario_a
python -m demo.quick_scenario
```

---

## Project Structure

```
ai-debate-arena/
├── agents/                      # Agent implementations
│   ├── perspectives/            # Viewpoint agents
│   │   ├── conservative.py      # Conservative perspective
│   │   ├── progressive.py       # Progressive perspective
│   │   └── __init__.py
│   ├── evidence/                # Evidence verification
│   │   ├── fact_checker.py      # Fact checking agent
│   │   ├── devils_advocate.py   # Devil's advocate agent
│   │   └── __init__.py
│   ├── synthesis/               # Analysis and synthesis
│   │   ├── analyzer.py          # Argument analyzer
│   │   ├── synthesizer.py       # Synthesis agent
│   │   ├── common_ground.py     # Common ground finder
│   │   └── __init__.py
│   └── moderator.py             # Debate orchestration
│
├── protocols/                   # Message formats and protocols
│   ├── debate_protocol.py       # Debate rules and structure
│   ├── message_types.py         # Message type definitions
│   └── __init__.py
│
├── memory/                      # Memory and caching
│   ├── memory_bank.py           # Conversation memory
│   ├── fact_cache.py            # Fact-check cache
│   └── __init__.py
│
├── tools/                       # External integrations
│   ├── google_search.py         # Google Search integration
│   └── __init__.py
│
├── tests/                       # Test suites
│   ├── unit/                    # Unit tests (with mocks)
│   ├── integration/             # Integration tests (real API)
│   ├── test_perspectives.py
│   ├── test_fact_checker.py
│   └── conftest.py
│
├── demo/                        # Demo scenarios
│   ├── run_scenario_a.py        # Full debate scenario
│   ├── quick_scenario.py        # Quick demo
│   └── __init__.py
│
├── deployment/                  # Deployment configuration
│   ├── Dockerfile               # Docker image
│   ├── deploy.sh                # Deployment script
│   ├── setup-secrets.sh         # Secrets setup
│   └── DEPLOYMENT_GUIDE.md      # Deployment guide
│
├── scripts/                     # Utility scripts
│   └── setup-hooks.sh           # Git hooks setup
│
├── main.py                      # Main entry point
├── config.py                    # Configuration settings
├── bootstrap.sh                 # Setup script (Linux/Mac)
├── bootstrap.bat                # Setup script (Windows)
├── start-server.sh              # Start script (Linux/Mac)
├── start-server.bat             # Start script (Windows)
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── pyproject.toml               # Project configuration
├── .env.example                 # Environment template
├── .flake8                      # Flake8 configuration
├── README.md                    # This file
├── QUICKSTART.md                # Quick setup guide
└── CONTRIBUTING.md              # Contribution guidelines
```

---

## Technology Stack

- **LLM:** Google Gemini (2.5 Flash / 1.5 Flash)
- **Framework:** Google ADK (Agent Development Kit)
- **Backend:** FastAPI + WebSockets
- **Data Validation:** Pydantic + Pydantic Settings
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Code Quality:** Black, isort, flake8, mypy
- **Package Management:** uv (ultra-fast Rust-based installer)
- **Deployment:** Docker + Google Cloud Run
- **CI/CD:** GitHub Actions

---

## Environment Variables

Configuration is managed through the `.env` file. Copy `.env.example` to `.env` and configure:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key ([Get here](https://ai.google.dev/)) | `AIza...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| **LLM Configuration** | | |
| `LLM_MODEL` | Primary Gemini model | `gemini-2.5-flash-lite` |
| `LLM_FALLBACK_MODEL` | Fallback model if primary fails | `gemini-2.5-flash` |
| `LLM_TEMPERATURE` | Model temperature (0.0-1.0) | `0.7` |
| `LLM_MAX_TOKENS` | Max tokens per response | `1024` |
| **Debate Configuration** | | |
| `MAX_DEBATE_ROUNDS` | Maximum debate rounds | `5` |
| `OPENING_STATEMENT_SECONDS` | Time for opening statements | `120` |
| `REBUTTAL_SECONDS` | Time for rebuttals | `60` |
| `CLOSING_SECONDS` | Time for closing statements | `90` |
| **Performance** | | |
| `AGENT_TIMEOUT_SECONDS` | Agent response timeout | `30` |
| `FACT_CHECK_TIMEOUT_SECONDS` | Fact check timeout | `10` |
| `AGENT_DELAY_SECONDS` | Delay between agent calls | `1.0` |
| `RETRY_ATTEMPTS` | Number of retry attempts | `3` |
| `RETRY_DELAY_SECONDS` | Delay between retries | `2.0` |
| **Logging** | | |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `LOG_FORMAT` | Log format style | `detailed` |
| **Server** | | |
| `PORT` | Server port (auto-set by Cloud Run) | `8080` |
| `HOST` | Server host | `0.0.0.0` |
| **Caching** | | |
| `ENABLE_FACT_CACHE` | Enable fact-check caching | `True` |
| `FACT_CACHE_TTL_DAYS` | Fact cache time-to-live | `7` |
| **Google Search (Optional)** | | |
| `GOOGLE_SEARCH_API_KEY` | Google Custom Search API key | - |
| `GOOGLE_SEARCH_ENGINE_ID` | Google Custom Search Engine ID | - |

See `.env.example` for the complete list with descriptions.

---

## Testing

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat     # Windows

# Run all tests
pytest

# Run only unit tests (fast, no API calls)
pytest -m unit

# Run only integration tests (requires GOOGLE_API_KEY)
pytest -m integration

# Run with coverage report
pytest --cov=agents --cov=protocols --cov=tools --cov=utils --cov=memory

# Generate HTML coverage report
pytest --cov-report=html
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/test_perspectives.py -v

# Run with verbose output
pytest -vv
```

### Test Categories

- **Unit tests** (`-m unit`): Fast tests with mocks, no external API calls
- **Integration tests** (`-m integration`): Real API calls, requires `GOOGLE_API_KEY`
- **Coverage threshold**: 80% minimum (enforced by CI/CD)

### Test Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "unit: Fast unit tests with mocks",
    "integration: Integration tests with real API calls",
]
```

---

## Code Quality & CI/CD

### Automated Code Quality Checks

The project uses GitHub Actions to automatically check code quality on every push and pull request to the `main` branch.

**CI/CD Pipeline includes:**
- ✅ **PEP 8 Compliance**: Checks with `flake8`
- ✅ **Code Formatting**: Validates with `black`
- ✅ **Import Sorting**: Verifies with `isort`
- ✅ **Test Coverage**: Runs `pytest` with coverage reports
- ✅ **Coverage Threshold**: Fails if coverage drops below 80%

**⚠️ Important**: The CI/CD pipeline checks **all files** in the repository, not just modified files. This ensures consistent code quality across the entire codebase.

### Local Development Tools

#### Pre-commit Hooks

The project includes Git hooks that run automatically before each commit:

```bash
# Set up hooks (one-time setup, done by bootstrap script)
./scripts/setup-hooks.sh
```

This configures Git to:
1. Auto-format code with **Black** (line length: 100)
2. Auto-sort imports with **isort**
3. Check for PEP 8 violations with **flake8**
4. Prevent commits with code quality issues

**⚠️ Important**: Pre-commit hooks only check **modified/staged files** to keep commits fast. The CI/CD pipeline will check all files to ensure repository-wide quality.

#### Manual Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Check PEP 8 compliance
flake8 .

# Run type checking
mypy .

# Run all pre-commit checks manually
pre-commit run --all-files
```

### Configuration

All tools are configured in `pyproject.toml` and `.flake8`:
- **Line length**: 100 characters
- **Python target**: 3.10+
- **Import style**: Black-compatible
- **Coverage threshold**: 80%

---

## Deployment

### Docker

```bash
# Build image
docker build -t ai-debate-arena .

# Run container
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key ai-debate-arena
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy ai-debate-arena \
  --source . \
  --set-env-vars GOOGLE_API_KEY=your_key

# Or use secrets (recommended for production)
gcloud run deploy ai-debate-arena \
  --source . \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest
```

**📖 For detailed deployment instructions, see [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)**

---

## Contributing

Contributions are welcome! We'd love your help improving the AI Debate Arena.

### Areas for Contribution

- 🤖 **Additional perspective agents** (Libertarian, International, Economist, etc.)
- 🔍 **Enhanced fact-checking sources** (multiple search engines, academic databases)
- 🎨 **UI improvements** (web interface, visualization)
- ⚡ **Performance optimizations** (caching, parallel processing)
- 🌍 **Multi-language support** (debate in different languages)
- 📊 **Analytics and metrics** (debate quality scoring)
- 🧪 **Testing** (more test coverage, edge cases)

### Development Workflow

1. **Fork the repository** and clone your fork
2. **Run the bootstrap script** to set up your environment
3. **Create a branch** for your feature: `git checkout -b feature/my-feature`
4. **Make your changes** and write tests
5. **Run tests**: `pytest`
6. **Check code quality**: `black . && isort . && flake8 .`
7. **Commit your changes**: `git commit -m "Add my feature"`
8. **Push to your fork**: `git push origin feature/my-feature`
9. **Create a Pull Request** from your fork to the main repository

**📖 For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)**

### Code Standards

- Follow PEP 8 style guide (enforced by flake8)
- Use Black for code formatting (line length: 100)
- Write docstrings for all public functions/classes
- Add type hints where appropriate
- Write tests for new features
- Maintain 80%+ test coverage

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

Built with:
- [Google Agent Development Kit (ADK)](https://ai.google.dev/)
- [Gemini API](https://ai.google.dev/gemini-api)
- [uv - Ultra-fast Python package installer](https://github.com/astral-sh/uv)

Special thanks to the open-source community for the amazing tools and libraries that make this project possible.

---

## Contact & Support

- 📖 **Documentation**: [QUICKSTART.md](QUICKSTART.md) | [CONTRIBUTING.md](CONTRIBUTING.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/ai-debate-arena/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-debate-arena/discussions)
- 🚀 **Deployment Help**: [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)

---

*"The best way to find truth isn't to ask one AI for the answer - it's to watch multiple AIs fight for it."*
