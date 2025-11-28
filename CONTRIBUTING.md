# Contributing to AI Debate Arena

Thank you for contributing to AI Debate Arena! This guide will help you maintain code quality and consistency.

## Development Workflow Checklist

Before submitting any code changes, ensure you complete the following checklist:

### ✅ Pre-Commit Checklist

1. **Code Formatting**
   ```bash
   # Check formatting
   venv/Scripts/black.exe --check --diff .

   # Auto-format code
   venv/Scripts/black.exe .
   ```

2. **Linting**
   ```bash
   # Run flake8
   venv/Scripts/flake8.exe .
   ```

3. **Type Checking** (Optional but recommended)
   ```bash
   # Run mypy
   venv/Scripts/mypy.exe .
   ```

4. **Import Sorting**
   ```bash
   # Check import order
   venv/Scripts/isort.exe --check-only --diff .

   # Fix import order
   venv/Scripts/isort.exe .
   ```

5. **Run Tests**
   ```bash
   # Run all unit tests
   pytest -m unit -v

   # Run specific test file
   pytest tests/test_your_file.py -v

   # Check coverage
   pytest --cov=agents --cov=protocols --cov=tools --cov=utils --cov=memory
   ```

6. **Verify Coverage Requirements**
   - Ensure overall coverage is ≥80%
   - New code should have 100% test coverage when possible
   - Check the coverage report: `htmlcov/index.html`

### 📝 Writing Tests

When adding new features or fixing bugs:

1. **Write tests first** (TDD approach recommended)
2. **Cover edge cases:**
   - Invalid inputs
   - Empty/null values
   - Out-of-range values
   - Error conditions
   - Different data formats
3. **Use descriptive test names:**
   ```python
   async def test_synthesis_parsing_invalid_confidence():
       """Test parsing synthesis with invalid confidence score."""
   ```

4. **Mock external dependencies:**
   ```python
   @pytest.fixture
   def mock_genai_client():
       with patch("google.genai.Client") as mock:
           yield mock
   ```

### 🔍 Code Quality Standards

1. **Line Length:** Max 100 characters (configured in `pyproject.toml`)
2. **Docstrings:** Use Google-style docstrings for all public functions/classes
3. **Type Hints:** Add type hints where beneficial for clarity
4. **Error Handling:** Include appropriate try-except blocks with specific exceptions
5. **Logging:** Use the `logging` module, not `print()` statements

### 🚀 Git Commit Guidelines

1. **Commit Message Format:**
   ```
   Brief summary (50 chars or less)

   More detailed explanation if needed. Wrap at 72 characters.

   - Bullet points for key changes
   - Keep it concise and clear

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

2. **Branch Naming:**
   - Feature: `feature/description`
   - Bug fix: `fix/description`
   - Tests: `test/description`
   - Documentation: `docs/description`

3. **Before Pushing:**
   ```bash
   # Ensure all tests pass
   pytest -v

   # Ensure formatting is correct
   venv/Scripts/black.exe --check .

   # Ensure linting passes
   venv/Scripts/flake8.exe .
   ```

### 🔄 Pull Request Process

1. **Create a new branch** from `main`
2. **Make your changes** following the checklist above
3. **Update documentation** if needed
4. **Add tests** for new functionality
5. **Ensure CI passes** (all checks green)
6. **Request review** from maintainers

### 🧪 Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Fast unit tests with mocks (run on every commit)
- `@pytest.mark.integration` - Slow integration tests with real API calls (run on schedule/manually)
- `@pytest.mark.slow` - Tests that take a long time to run

### 📊 Coverage Requirements

| Module | Minimum Coverage |
|--------|-----------------|
| Overall | 80% |
| New Code | 90%+ |
| Critical Agents | 100% |

### 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/panneer12/ai-debate-arena.git
   cd ai-debate-arena
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run pre-commit checks:**
   ```bash
   # Install pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

### 📚 Additional Resources

- [Testing Guide](TESTING.md)
- [Test Strategy](TEST_STRATEGY.md)
- [Integration Tests](.github/INTEGRATION_TESTS.md)
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)

### 💡 Tips

- Use `pytest -v -s` to see print statements during test runs
- Use `pytest -k "test_name"` to run specific tests by name pattern
- Use `pytest --lf` to re-run only failed tests
- Use `pytest --cov-report=html` to generate HTML coverage report

### ❓ Questions?

If you have questions or need help, please:
1. Check existing documentation
2. Search closed issues
3. Open a new issue with the `question` label

Happy coding! 🎉
