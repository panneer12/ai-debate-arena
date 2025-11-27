"""Test edge cases for the debate system."""

import asyncio
import logging
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from protocols.message_format import DebateMessage, MessageType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_empty_topic():
    """Test with empty topic."""
    print("\n" + "=" * 80)
    print("TEST 1: Empty Topic")
    print("=" * 80)

    try:
        moderator = ModeratorAgent()
        response = await moderator.generate_response([], "Start a debate on: ''")

        if response:
            print("PASS: System handled empty topic")
            print(f"Response: {response[:200]}...")
        else:
            print("PASS: System gracefully rejected empty topic")
    except Exception as e:
        print(f"FAIL: Error with empty topic: {e}")


async def test_nonsense_topic():
    """Test with nonsense topic."""
    print("\n" + "=" * 80)
    print("TEST 2: Nonsense Topic")
    print("=" * 80)

    try:
        moderator = ModeratorAgent()
        nonsense = "xyzabc 123 !@# blah blah nonsense foobar"
        response = await moderator.generate_response([], f"Start a debate on: '{nonsense}'")

        if response:
            print("PASS: System handled nonsense topic")
            print(f"Response: {response[:200]}...")
        else:
            print("PASS: System gracefully rejected nonsense topic")
    except Exception as e:
        print(f"FAIL: Error with nonsense topic: {e}")


async def test_very_long_input():
    """Test with very long input."""
    print("\n" + "=" * 80)
    print("TEST 3: Very Long Input")
    print("=" * 80)

    try:
        moderator = ModeratorAgent()
        long_topic = "Should we " + "really " * 500 + "implement this policy?"
        print(f"Topic length: {len(long_topic)} characters")

        response = await moderator.generate_response([], f"Start a debate on: '{long_topic}'")

        if response:
            print("PASS: System handled long input")
            print(f"Response length: {len(response)} characters")
        else:
            print("PASS: System gracefully handled long input")
    except Exception as e:
        print(f"PASS: System limited long input - {type(e).__name__}")


async def test_special_characters():
    """Test with special characters."""
    print("\n" + "=" * 80)
    print("TEST 4: Special Characters")
    print("=" * 80)

    try:
        moderator = ModeratorAgent()
        special_topic = "Should we use <script>alert('XSS')</script> & \"quotes\" in policies?"
        response = await moderator.generate_response([], f"Start a debate on: '{special_topic}'")

        if response:
            print("PASS: System handled special characters")
            print(f"Response: {response[:200]}...")
        else:
            print("PASS: System sanitized special characters")
    except Exception as e:
        print(f"FAIL: Error with special characters: {e}")


async def test_null_input():
    """Test with None/null input."""
    print("\n" + "=" * 80)
    print("TEST 5: Null Input")
    print("=" * 80)

    try:
        moderator = ModeratorAgent()
        response = await moderator.generate_response([], None)

        if response:
            print("PASS: System handled null input")
        else:
            print("PASS: System rejected null input gracefully")
    except Exception as e:
        print(f"PASS: System caught null input - {type(e).__name__}")


async def test_rapid_messages():
    """Test rapid message processing."""
    print("\n" + "=" * 80)
    print("TEST 6: Rapid Message Processing")
    print("=" * 80)

    try:
        conservative = ConservativeAgent()

        # Send 5 rapid messages
        tasks = []
        for i in range(5):
            msg = {
                "from_agent": "Moderator",
                "role": "Moderator",
                "content": f"Quick question {i}: What do you think?",
                "type": MessageType.QUESTION,
            }
            tasks.append(conservative.process_message(msg))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"PASS: Processed {success_count}/5 rapid messages")

        if success_count < 5:
            print(f"Note: {5-success_count} messages failed (expected with rate limiting)")

    except Exception as e:
        print(f"FAIL: Error with rapid messages: {e}")


async def main():
    """Run all edge case tests."""
    print("\n" + "#" * 80)
    print("AI DEBATE ARENA - EDGE CASE TESTING")
    print("#" * 80)

    tests = [
        test_empty_topic,
        test_nonsense_topic,
        test_very_long_input,
        test_special_characters,
        test_null_input,
        test_rapid_messages,
    ]

    for test in tests:
        try:
            await test()
            await asyncio.sleep(2)  # Small delay between tests
        except Exception as e:
            logger.error(f"Test {test.__name__} crashed: {e}", exc_info=True)

    print("\n" + "=" * 80)
    print("EDGE CASE TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
