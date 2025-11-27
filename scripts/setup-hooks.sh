#!/bin/bash
# Setup script for AI Debate Arena Git hooks
# This script configures git to use hooks from the .githooks directory

set -e

echo "Setting up Git hooks for AI Debate Arena..."

# Get the repository root directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# Configure git to use .githooks directory
git config core.hooksPath .githooks

echo "✓ Git hooks configured successfully!"
echo ""
echo "Git is now configured to use hooks from: ${REPO_ROOT}/.githooks"
echo ""
echo "Available hooks:"
echo "  - pre-commit: Auto-formats code with Black, sorts imports with isort, and checks with flake8"
echo ""
echo "To install development dependencies, run:"
echo "  pip install -r requirements-dev.txt"
