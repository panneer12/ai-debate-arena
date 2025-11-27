"""
Quick test script to verify server can start and agents are initialized.
Run this before starting the full server.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from demo.debate_manager import DebateManager

        print("✅ DebateManager imported successfully")

        from agents.moderator import ModeratorAgent

        print("✅ ModeratorAgent imported successfully")

        from memory.memory_bank import MemoryBank

        print("✅ MemoryBank imported successfully")

        from utils.metrics import MetricsCollector

        print("✅ MetricsCollector imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_api_key():
    """Test that Google API key is configured."""
    print("\nTesting API key...")
    try:
        from config import settings

        if settings.google_api_key:
            print(f"✅ Google API key configured (length: {len(settings.google_api_key)})")
            return True
        else:
            print("❌ Google API key not configured")
            print("   Set GOOGLE_API_KEY environment variable or add to .env file")
            return False
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False


def test_static_files():
    """Test that UI files exist."""
    print("\nTesting UI files...")
    ui_path = os.path.join(os.path.dirname(__file__), "ui")

    required_files = [
        "index.html",
        "js/app.js",
        "js/websocket.js",
        "js/debate.js",
        "js/voice.js",
        "js/utils.js",
    ]

    all_exist = True
    for file in required_files:
        path = os.path.join(ui_path, file)
        if os.path.exists(path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            all_exist = False

    return all_exist


def main():
    print("=" * 60)
    print("AI Debate Arena - Server Pre-flight Check")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("API Key", test_api_key()))
    results.append(("UI Files", test_static_files()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(result[1] for result in results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")

    print()
    if all_passed:
        print("🎉 All checks passed! Ready to start server.")
        print("\nRun: python -m demo.server")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
