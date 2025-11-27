"""Test the rate limiting and retry logic."""

import asyncio
import logging
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_rate_limiting():
    """Test that delays are working between agent calls."""
    print("\n" + "=" * 80)
    print("RATE LIMITING TEST")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Primary Model: {settings.llm_model}")
    print(f"  Fallback Model: {settings.llm_fallback_model}")
    print(f"  Agent Delay: {settings.agent_delay_seconds}s")
    print(f"  Retry Attempts: {settings.retry_attempts}")
    print(f"  Retry Delay: {settings.retry_delay_seconds}s")
    print()

    # Initialize agents
    conservative = ConservativeAgent()
    progressive = ProgressiveAgent()

    test_msg = {
        "from_agent": "Moderator",
        "role": "Moderator",
        "content": "What is your opinion on climate change policy?",
        "type": "QUESTION",
    }

    # Test 1: Single call
    print("Test 1: Single agent call...")
    import time

    start = time.time()
    response1 = await conservative.process_message(test_msg)
    elapsed1 = time.time() - start
    print(f"  Conservative responded in {elapsed1:.2f}s")
    print(f"  Response preview: {response1['content'][:100]}...")
    print()

    # Test 2: Two calls with delay
    print("Test 2: Two sequential calls with delay...")
    start = time.time()

    response2 = await progressive.process_message(test_msg)
    print(f"  Progressive call 1 completed")

    await asyncio.sleep(settings.agent_delay_seconds)
    print(f"  Waited {settings.agent_delay_seconds}s...")

    response3 = await conservative.process_message(test_msg)
    print(f"  Conservative call 2 completed")

    elapsed2 = time.time() - start
    print(f"  Total time: {elapsed2:.2f}s")
    print()

    # Test 3: Check for errors
    print("Test 3: Error handling check...")
    if "[" in response1["content"] and "]" in response1["content"]:
        print("  WARNING: Agent returned error message")
        print(f"  Error: {response1['content']}")
    else:
        print("  SUCCESS: No error messages detected")
    print()

    print("=" * 80)
    print("RATE LIMITING TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_rate_limiting())
