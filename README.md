# AI Debate Arena

**Multi-agent debate system for finding truth through structured conflict**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini-4285F4)](https://ai.google.dev/)

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

### Prerequisites

- Python 3.11+
- Google AI API key ([get one here](https://ai.google.dev/))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-debate-arena.git
cd ai-debate-arena

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### For Developers

If you're contributing to the project, install development dependencies and set up Git hooks:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up Git hooks for automatic code quality checks
./scripts/setup-hooks.sh

# (Optional) Install pre-commit framework
pre-commit install
```

The pre-commit hook will automatically:
- Format code with **Black** (line length: 100)
- Sort imports with **isort**
- Check code quality with **flake8** (PEP 8 compliance)
- Prevent commits with violations

### Run a Debate

```bash
python main.py
```

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

1. **Moderator** - Manages debate flow, enforces protocol
2. **Conservative Agent** - Traditional values, free market perspective
3. **Progressive Agent** - Social justice, collective action perspective  
4. **Fact Checker** - Real-time claim verification via Google Search
5. **Devil's Advocate** - Challenges all positions, prevents groupthink
6. **Synthesizer** - Generates nuanced conclusions, finds common ground

---

## Usage Example

```python
from agents.moderator import ModeratorAgent
from agents.perspectives import ConservativeAgent, ProgressiveAgent

# Initialize agents
moderator = ModeratorAgent()
conservative = ConservativeAgent()
progressive = ProgressiveAgent()

# Start debate
result = moderator.start_debate(
    topic="Should we have universal healthcare?",
    agents=[conservative, progressive]
)

# View results
print(result.synthesis.consensus_points)
print(result.synthesis.common_ground)
```

---

## Features

✨ **Multi-Agent Debate System**
- Parallel agent execution
- Sequential debate phases
- Formal argumentation protocols

🔍 **Real-Time Fact Checking**
- Google Search integration
- Source credibility scoring
- Confidence-weighted verification

🤝 **Common Ground Discovery**
- Shared value identification
- Compromise solution generation
- Nuanced, multi-perspective conclusions

📊 **Quality Metrics**
- Logical validity checking
- Fallacy detection
- Argument strength scoring

---

## Technology Stack

- **LLM:** Google Gemini 2.0 Flash
- **Framework:** Google ADK (Agent Development Kit)
- **Backend:** FastAPI + WebSockets
- **Deployment:** Docker + Google Cloud Run
- **Testing:** pytest

---

## Project Structure

```
ai-debate-arena/
├── agents/              # Agent implementations
│   ├── perspectives/    # Viewpoint agents
│   ├── evidence/        # Fact checker, devil's advocate
│   └── synthesis/       # Analyzer, synthesizer
├── protocols/           # Message format, debate rules
├── memory/              # Memory bank, caching
├── tools/               # Google Search integration
├── tests/               # Test suites
├── demo/                # Demo UI and examples
└── deployment/          # Docker, Cloud Run config
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov-report=html

# Run specific tests
pytest tests/test_perspectives.py -v
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

### Local Development Tools

#### Pre-commit Hooks

The project includes Git hooks that run automatically before each commit:

```bash
# Set up hooks (one-time setup)
./scripts/setup-hooks.sh
```

This configures Git to:
1. Auto-format code with **Black**
2. Auto-sort imports with **isort**
3. Check for PEP 8 violations with **flake8**
4. Prevent commits with code quality issues

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
docker build -t ai-debate-arena .
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key ai-debate-arena
```

### Google Cloud Run

```bash
gcloud run deploy ai-debate-arena \
  --source . \
  --set-env-vars GOOGLE_API_KEY=your_key
```

---

## Contributing

Contributions welcome! Areas for improvement:
- Additional perspective agents (Libertarian, International, etc.)
- Enhanced fact-checking sources
- UI improvements
- Performance optimizations
- Multi-language support

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

Built with [Google Agent Development Kit](https://ai.google.dev/) and [Gemini](https://ai.google.dev/gemini-api).

---

*"The best way to find truth isn't to ask one AI for the answer - it's to watch multiple AIs fight for it."*
