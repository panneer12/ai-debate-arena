# Test Strategy Summary

## Overview

This project uses a **two-tier testing strategy** to balance speed, cost, and confidence:

1. **Unit Tests** (70 tests) - Fast, free, run on every commit
2. **Integration Tests** (21 tests) - Slow, costs money, run on main branch only

## Test Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Feature Branch / PR                              │
│                                                                     │
│  Developer commits → GitHub PR opened                               │
│                                                                     │
│  CI/CD Runs:                                                        │
│  ✅ Code quality (black, isort, flake8)                            │
│  ✅ Unit tests (70 tests, ~1 min, FREE)                           │
│  ✅ Coverage check (80% threshold)                                 │
│  ❌ Integration tests SKIPPED                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ PR Merged
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Main Branch                                 │
│                                                                     │
│  Code merged to main → Triggers integration tests                   │
│                                                                     │
│  CI/CD Runs:                                                        │
│  ✅ Integration tests (21 tests, ~2 min, COSTS MONEY)             │
│  ✅ Full end-to-end validation with real API                       │
│                                                                     │
│  Result: Production-ready code verified                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Required Secrets

To run integration tests on GitHub Actions, configure this secret:

**GitHub Settings → Secrets and variables → Actions → New repository secret:**

- **Name:** `GOOGLE_API_KEY`
- **Value:** Your Google AI API key (e.g., `AIzaSy...`)

## Test Breakdown

### Unit Tests (70 tests)
**Files:**
- `test_analyzer.py` (5 tests)
- `test_base_architecture.py` (4 tests)
- `test_common_ground.py` (3 tests)
- `test_devils_advocate.py` (4 tests)
- `test_error_handling.py` (7 tests)
- `test_fact_checker.py` (4 tests)
- `test_firestore.py` (2 tests, 2 skipped)
- `test_memory.py` (3 tests)
- `test_moderator.py` (3 tests)
- `test_observability.py` (4 tests)
- `test_perspectives.py` (5 tests)
- `test_server.py` (23 tests) ⭐ **FastAPI endpoints**
- `test_synthesizer.py` (3 tests)

**Characteristics:**
- ⏱️ Runtime: ~1 minute
- 💰 Cost: Free (no API calls)
- 🎯 Coverage: All components with mocked dependencies
- 🚀 Run: On every commit/PR

### Integration Tests (21 tests)
**Files:**
- `test_debate_manager.py` (18 tests) - Full debate flow
- `test_moderator_validation.py` (3 tests) - Topic validation

**Characteristics:**
- ⏱️ Runtime: ~2-3 minutes
- 💰 Cost: $0.01-$0.10 per run (API usage)
- 🎯 Coverage: End-to-end flows with real LLM
- 🚀 Run: On main branch push only

## Cost Analysis

### Development Phase (Feature Branches)
- ✅ Unit tests run on every commit
- ❌ Integration tests do NOT run
- **Cost per commit:** $0 (free)
- **Time per commit:** ~1 minute

### Main Branch (After Merge)
- ✅ Unit tests run
- ✅ Integration tests run
- **Cost per merge:** ~$0.05
- **Time per merge:** ~3 minutes

### Estimated Monthly Cost
Assuming:
- 20 working days/month
- 5 commits/day to feature branches = 100 commits
- 2 merges/day to main = 40 merges

**Monthly Cost:**
- Feature branch commits: 100 × $0 = **$0**
- Main branch merges: 40 × $0.05 = **$2.00**
- **Total: ~$2/month**

Compare to running integration on every commit:
- All commits: 140 × $0.05 = **$7/month**
- **Savings: $5/month (71% reduction)**

## Commands

### For Developers
```bash
# Quick check before commit (recommended)
pytest -m "not integration"

# With coverage
pytest -m "not integration" --cov

# Run integration tests locally (before major changes)
pytest -m integration -v

# Run everything
pytest
```

### For CI/CD
```bash
# PR/Commit pipeline (fast, free)
pytest -m "not integration" --cov

# Main branch pipeline (slow, costs money)
pytest -m integration -v
```

## When to Run Which Tests

### Always Run (Automated):
- ✅ Unit tests on feature branches
- ✅ Unit tests on main branch
- ✅ Integration tests on main branch (after merge)

### Run Manually (Optional):
- 🔧 Integration tests locally before major refactors
- 🔧 Integration tests via GitHub Actions UI when needed
- 🔧 Full test suite before releases

### Never Run:
- ❌ Integration tests on every feature branch commit (too slow, too expensive)

## Benefits of This Strategy

1. **Fast Feedback Loop**
   - Developers get results in ~1 minute, not 3 minutes
   - Can iterate quickly on feature branches

2. **Cost Effective**
   - Save ~70% on API costs
   - Only pay for final validation on main branch

3. **High Confidence**
   - Unit tests catch 90% of bugs (fast, free)
   - Integration tests validate production readiness (slow, costs money)
   - Main branch always has verified code

4. **No Rate Limits**
   - Feature branch commits don't hit API
   - Integration tests only on main = fewer API calls

5. **Clear Separation**
   - Developers: Run unit tests
   - Main branch: Run everything
   - Simple to understand and maintain

## Troubleshooting

### "Integration tests not running on main branch"
**Check:**
1. Is `GOOGLE_API_KEY` secret configured in GitHub?
2. Did you push to `main` branch (not a feature branch)?
3. Did you only change `.md` files? (These are ignored)

### "Integration tests failing on main branch"
**This is GOOD!** It means:
- Unit tests passed (fast feedback)
- But something broke with real API integration
- Fix the issue before deploying to production

### "I want to skip integration tests on a main branch commit"
Add `[skip ci]` to your commit message:
```bash
git commit -m "docs: Update README [skip ci]"
```

Or only commit documentation files (automatically ignored).
