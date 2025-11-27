# Testing Guide

## Test Types

This project has two types of tests:

### 1. Unit Tests (Fast, Mocked)
- **Runtime**: ~30 seconds
- **Cost**: Free (no API calls)
- **When to run**: On every commit/PR
- **What they test**: Individual components with mocked dependencies

### 2. Integration Tests (Slow, Real API Calls)
- **Runtime**: 2-3 minutes
- **Cost**: Money (makes real LLM API calls)
- **When to run**:
  - Before releases
  - On a schedule (nightly)
  - Manually when needed
- **What they test**: End-to-end flows with real API interactions
- **Files**:
  - `tests/test_debate_manager.py` - Full debate flow
  - `tests/test_moderator_validation.py` - Topic validation

## Running Tests

### Run Unit Tests Only (Recommended for Development)
```bash
# Fast unit tests only - run on every change
pytest -m "not integration"

# With coverage
pytest -m "not integration" --cov

# Specific test file
pytest tests/test_server.py -v
```

### Run Integration Tests
```bash
# All integration tests (requires API key, costs money)
pytest -m integration

# Single integration test
pytest tests/test_debate_manager.py -v
```

### Run All Tests
```bash
# Run everything (slow, expensive)
pytest

# With coverage
pytest --cov
```

## CI/CD Pipeline

### On Every PR/Commit:
- ✅ Code quality checks (black, isort, flake8)
- ✅ **Unit tests only** (fast, no API calls)
- ✅ Coverage report (80% threshold)

### On Main Branch Push (After Merge):
- ✅ Integration tests (real API calls, ~2 min)
- ⚠️ Requires `GOOGLE_API_KEY` secret in GitHub Settings
- ⚠️ Costs money - validates production-ready code

### Manual Trigger (Optional):
- ✅ Integration tests (via GitHub Actions "Run workflow" button)

## Test Coverage Requirements

- **Minimum coverage**: 80%
- **Measured on**: Unit tests only
- **Excludes**:
  - `demo/` directory
  - Integration tests
  - Test files themselves

## Best Practices

1. **Write unit tests first** - They're fast and catch most bugs
2. **Mock external dependencies** - Use `unittest.mock` for API calls
3. **Integration tests for critical flows** - Only test happy paths end-to-end
4. **Don't over-test integrations** - They're expensive and slow
5. **Run unit tests before committing** - Catch issues early

## Example: Adding a New Feature

```bash
# 1. Write unit tests for new feature
pytest tests/test_my_feature.py -v

# 2. Run all unit tests to ensure nothing broke
pytest -m "not integration"

# 3. (Optional) Run integration tests locally if touching critical flows
pytest tests/test_debate_manager.py -v

# 4. Commit - CI will run unit tests automatically
git commit -m "Add new feature"
```

## Debugging Failed Tests

### Unit Test Failures
```bash
# Run with verbose output
pytest tests/test_file.py::test_name -vv

# Run with print statements visible
pytest tests/test_file.py::test_name -s

# Run with debugger
pytest tests/test_file.py::test_name --pdb
```

### Integration Test Failures
```bash
# Check API credentials
cat .env | grep GOOGLE_API_KEY

# Run single integration test
pytest tests/test_debate_manager.py::TestDebateManagerLifecycle::test_initialize_agents -v

# Check rate limits
# Integration tests make many API calls - wait a few minutes if hitting limits
```

## Test Markers

Markers are defined in `pyproject.toml`:

- `@pytest.mark.unit` - Fast unit test (not currently used, implied by default)
- `@pytest.mark.integration` - Slow integration test with real API calls
- `@pytest.mark.slow` - Any slow-running test

## Adding New Tests

### For Unit Tests:
1. Create test file: `tests/test_my_module.py`
2. Use mocks for external dependencies
3. Keep tests fast (<1s each)
4. No marker needed (unit tests are default)

### For Integration Tests:
1. Add to existing integration test file or create new one
2. Add `pytestmark = pytest.mark.integration` at top of file
3. Document why integration test is needed
4. Keep integration tests minimal (only critical paths)

Example:
```python
"""Integration test for critical authentication flow."""

import pytest

pytestmark = pytest.mark.integration  # Mark entire file

@pytest.mark.asyncio
async def test_auth_flow_end_to_end():
    # Real API calls here
    pass
```
