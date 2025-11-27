# Integration Tests Setup

## Overview

Integration tests make **real API calls** to Google's Gemini LLM service. They:
- Take 2-3 minutes to run
- Cost money (API usage charges)
- Run automatically on **main branch pushes only** (after PR merges)
- Can also be triggered manually when needed

## How to Run Integration Tests

### Locally (Recommended for Development)

1. **Ensure you have a `.env` file with your API key:**
   ```bash
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

2. **Run integration tests:**
   ```bash
   pytest -m integration -v
   ```

3. **Cost**: You'll be charged for API usage during the test run

### On GitHub Actions (Automatic)

Integration tests run automatically when you:
- **Push/merge to the main branch**
- Changes to documentation-only files (`.md`, `docs/`) are ignored

**Requirements:**
- `GOOGLE_API_KEY` secret must be configured (see setup below)
- Only runs on main branch, not on feature branches or PRs

### On GitHub Actions (Manual Trigger)

1. **Configure GitHub Secret** (one-time setup):
   - Go to your GitHub repository
   - Navigate to: **Settings → Secrets and variables → Actions**
   - Click **"New repository secret"**
   - Add:
     - Name: `GOOGLE_API_KEY`
     - Value: Your Google AI API key (e.g., `AIzaSy...`)

2. **Trigger the workflow manually:**
   - Go to **Actions** tab in GitHub
   - Click **"Integration Tests"** workflow
   - Click **"Run workflow"** button
   - Select branch (usually `main`)
   - Click **"Run workflow"**

3. **Monitor the run:**
   - The workflow will check if API keys are configured
   - If missing, it will fail with instructions
   - If present, it will run all integration tests (~2-3 minutes)

## When to Run Integration Tests

✅ **DO run integration tests:**
- Before creating a release
- After major changes to debate logic or agent behavior
- When you need to verify end-to-end functionality
- After updating LLM prompts or parameters

❌ **DON'T run integration tests:**
- On every commit (too slow, too expensive)
- During active development (use unit tests instead)
- When testing small changes that don't affect LLM integration

## What Gets Tested

The integration test suite (`tests/test_debate_manager.py`) includes:
- Full debate lifecycle (initialization → debate → conclusion)
- Message broadcasting between agents
- Round progression and turn handling
- Analysis phase (fact checking, devil's advocate)
- Synthesis phase (finding common ground, generating conclusions)
- Memory integration (saving/loading debates)
- Error handling with real API failures

## Cost Estimation

Each integration test run makes approximately:
- **~50-100 LLM API calls** (varies by test configuration)
- **Cost**: $0.01 - $0.10 per run (depends on model and usage)
- **Frequency**: Only when manually triggered = minimal cost

## Troubleshooting

### "API keys not configured" error
```bash
❌ ERROR: GOOGLE_API_KEY secret not configured
```
**Solution**: Add the secret in GitHub Settings (see step 1 above)

### "Rate limit exceeded" error
```
429 RESOURCE_EXHAUSTED: Rate limit exceeded
```
**Solution**: Wait a few minutes and try again. Integration tests make many API calls in quick succession.

### Tests timeout
**Solution**: This is normal for integration tests. They can take 2-3 minutes. Check the workflow timeout setting if needed.

## Alternatives

If you don't want to use GitHub Actions for integration tests:

1. **Run locally before releases:**
   ```bash
   pytest -m integration
   ```

2. **Use a separate CI/CD service** (CircleCI, GitLab CI, etc.) with your API keys

3. **Skip integration tests entirely** and rely on unit tests + manual testing

The unit test suite (`pytest -m "not integration"`) provides 70+ tests that run in ~1 minute without API calls.
