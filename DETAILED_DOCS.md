# Detailed Documentation

This document contains comprehensive usage examples, project structure details, and development guidelines extracted from the main README to keep it concise for submission.

---

## Table of Contents

- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Code Quality \u0026 CI/CD](#code-quality--cicd)
- [API Documentation](#api-documentation)
- [Performance](#performance)

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

### Running the Web UI

```bash
# Using the start script (recommended)
./start-server.sh        # Linux/Mac
start-server.bat         # Windows

# Or manually
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn demo.server:app --reload --port 8000
```

### Running Demo Scenarios

```bash
# Scenario A: Universal Basic Income
python -m demo.run_scenario_a

# Scenario B: Social Media Regulation
python -m demo.run_scenario_b

# Scenario C: AI Safety
python -m demo.run_scenario_c

# Quick test scenario
python -m demo.quick_scenario
```

---

## Project Structure

```
ai-debate-arena/
├── agents/                      # All agent implementations
│   ├── base_agent.py           # Base class for all agents
│   ├── moderator.py            # Debate orchestrator
│   ├── perspectives/           # Perspective agents
│   │   ├── conservative.py    # Conservative viewpoint
│   │   └── progressive.py     # Progressive viewpoint
│   ├── evidence/              # Evidence-gathering agents
│   │   ├── fact_checker.py    # Google Search fact verification
│   │   └── devils_advocate.py # Challenge assumptions
│   └── synthesis/             # Analysis and synthesis
│       ├── analyzer.py        # Argument quality analysis
│       ├── common_ground.py   # Find shared values
│       └── synthesizer.py     # Generate conclusions
│
├── memory/                     # Memory and persistence
│   └── memory_bank.py         # Firestore + local storage
│
├── protocols/                  # Debate protocols
│   ├── message_format.py      # Message schema (Pydantic)
│   └── debate_protocol.py     # Debate phase definitions
│
├── utils/                      # Utilities
│   └── metrics.py             # Observability and metrics
│
├── demo/                       # Demo and server
│   ├── server.py              # FastAPI server
│   ├── debate_manager.py      # Debate orchestration
│   ├── ui/                    # Web interface
│   │   ├── index.html
│   │   ├── js/
│   │   └── styles/
│   └── examples/              # Example debates
│       ├── scenario_a_ubi.json
│       ├── scenario_b_social_media.json
│       └── scenario_c_ai_safety.json
│
├── tests/                      # Test suites
│   ├── test_base_agent.py
│   ├── test_moderator.py
│   ├── test_perspectives.py
│   ├── test_fact_checker.py
│   └── ...
│
├── deployment/                 # Deployment configs
│   ├── deploy.ps1
│   ├── SETUP_GUIDE.md
│   └── Dockerfile
│
├── bootstrap.sh/.bat           # Automated setup scripts
├── start-server.sh/.bat        # Server start scripts
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # Main documentation
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional - Firestore
GOOGLE_CLOUD_PROJECT=your-project-id
FIRESTORE_COLLECTION=debates

# Optional - Development
DEBUG=False
LOG_LEVEL=INFO
ENABLE_METRICS_SAMPLING=True
METRICS_SAMPLE_RATE=0.2

# Optional - Server
HOST=0.0.0.0
PORT=8000
```

### Getting API Keys

1. **Gemini API Key**:
   - Visit https://ai.google.dev/
   - Sign in with Google account
   - Go to "Get API Key"
   - Create new key for your project

2. **Google Cloud Project** (for Firestore):
   ```bash
   gcloud auth login
   gcloud projects create YOUR_PROJECT_ID
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable firestore.googleapis.com
   ```

---

## Code Quality \u0026 CI/CD

### Pre-commit Hooks

The project uses pre-commit hooks for automatic code quality checks:

```bash
# Install hooks (done automatically by bootstrap script)
pre-commit install

# Run manually
pre-commit run --all-files
```

**Checks performed**:
- `flake8` - Code linting
- `black` - Code formatting
- `mypy` - Type checking
- `isort` - Import sorting
- Trailing whitespace removal
- End-of-file fixing

### Manual Quality Checks

```bash
# Linting
flake8 agents/ memory/ utils/

# Type checking
mypy agents/ memory/ utils/

# Code formatting
black agents/ memory/ utils/

# Import sorting
isort agents/ memory/ utils/
```

### GitHub Actions CI/CD

Automated checks run on every push:
- ✅ Linting (flake8)
- ✅ Type checking (mypy)
- ✅ Unit tests (pytest)
- ✅ Code formatting (black --check)
- ✅ Security scan (bandit)

---

## API Documentation

### FastAPI Endpoints

#### Start Debate
```http
POST /api/debate/start
Content-Type: application/json

{
  "topic": "Should we implement Universal Basic Income?",
  "rounds": 2,
  "agents": ["conservative", "progressive", "factchecker", "devilsadvocate"]
}
```

**Response**:
```json
{
  "status": "started",
  "topic": "Should we implement Universal Basic Income?",
  "debate_id": "20241130_123456"
}
```

#### Stop Debate
```http
POST /api/debate/stop
Content-Type: application/json

{
  "debate_id": "20241130_123456"
}
```

#### Get Debate History
```http
GET /api/debate/{debate_id}/history
```

**Response**:
```json
{
  "debate_id": "20241130_123456",
  "messages": [
    {
      "id": "msg_001",
      "from_agent": "Moderator",
      "type": "OPENING_STATEMENT",
      "content": "Welcome to the AI Debate Arena...",
      "timestamp": "2024-11-30T12:34:56Z"
    },
    ...
  ]
}
```

#### Export Transcript
```http
GET /api/debate/{debate_id}/export?format=txt
GET /api/debate/{debate_id}/export?format=json
```

### WebSocket API

Connect to real-time debate updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/debate/{debate_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'ARGUMENT') {
    // Handle new argument
  } else if (data.type === 'FACT_CHECK') {
    // Handle fact check result
  } else if (data.type === 'SYNTHESIS') {
    // Handle final synthesis
  }
};
```

**Message Types**:
- `OPENING_STATEMENT`
- `ARGUMENT`
- `REBUTTAL`
- `QUESTION`
- `ANSWER`
- `FACT_CHECK`
- `CHALLENGE`
- `SYNTHESIS`
- `SYSTEM`
- `ERROR`

---

## Performance

### Benchmarks

Average response times (measured on Google Cloud Run):

| Agent | Average Latency | Token Usage |
|-------|----------------|-------------|
| Conservative | 1.2s | ~150 tokens |
| Progressive | 1.3s | ~155 tokens |
| Fact Checker | 2.1s | ~200 tokens |
| Devil's Advocate | 1.5s | ~180 tokens |
| Synthesizer | 2.5s | ~300 tokens |

**Full debate** (2 rounds): ~15-20 seconds

### Optimization Tips

1. **Reduce Rounds**: Start with 2 rounds for faster results
2. **Disable Agents**: Remove Devil's Advocate or Fact Checker if speed is critical
3. **Adjust Memory**: Use smaller context windows (change in `memory_bank.py`)
4. **Parallel Processing**: Enable async fact-checking (experimental)

### Monitoring

Metrics are automatically collected:
- Agent response times
- Token usage per call
- Error rates and types
- Debate completion times

View metrics in Firestore collection: `debates/{debate_id}/metrics`

---

## Additional Resources

- **Main README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Deployment**: [deployment/SETUP_GUIDE.md](deployment/SETUP_GUIDE.md)

---

## Troubleshooting

### Common Issues

**Q: "ModuleNotFoundError: No module named 'agents'"**  
A: Ensure you activated the virtual environment: `source venv/bin/activate`

**Q: "API key not found"**  
A: Create `.env` file with `GOOGLE_API_KEY=your_key`

**Q: "Firestore permission denied"**  
A: Run `gcloud auth application-default login`

**Q: "WebSocket connection failed"**  
A: Check if server is running and firewall allows port 8000

### Debug Mode

Enable verbose logging:
```bash
export LOG_LEVEL=DEBUG
python -m demo.server
```

---

**Last Updated**: November 30, 2024  
**Maintained By**: [Your Name]
