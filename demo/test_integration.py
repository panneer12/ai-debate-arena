"""
Integration test for AI Debate Arena.
Tests the full flow: API -> DebateManager -> WebSocket
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_debate_manager():
    """Test DebateManager directly without server."""
    print("\n" + "="*60)
    print("TEST 1: DebateManager Direct Test")
    print("="*60)

    try:
        from demo.debate_manager import DebateManager

        # Create a simple broadcast function to capture messages
        messages_received = []

        async def mock_broadcast(message):
            messages_received.append(message)
            print(f"📨 Broadcast: {message.get('type', 'UNKNOWN')} from {message.get('from_agent', 'UNKNOWN')}")

        # Initialize debate manager
        print("\n1. Initializing DebateManager...")
        manager = DebateManager(broadcast_func=mock_broadcast)

        print("2. Initializing agents...")
        await manager.initialize_agents()
        print(f"✅ Agents initialized: {manager.moderator is not None}")

        # Start a short debate
        print("\n3. Starting debate...")
        topic = "Testing Topic"
        rounds = 1

        # Start debate (non-blocking)
        debate_task = asyncio.create_task(
            manager.start_debate(topic, rounds, active_agents=None)
        )

        # Wait a bit and check messages
        print("4. Waiting for messages...")
        await asyncio.sleep(15)  # Wait 15 seconds for some messages

        print(f"\n✅ Received {len(messages_received)} messages")

        # Print first few messages
        for i, msg in enumerate(messages_received[:5]):
            msg_type = msg.get('type', 'UNKNOWN')
            from_agent = msg.get('from_agent', 'UNKNOWN')
            content_preview = str(msg.get('content', ''))[:50]
            print(f"  {i+1}. [{msg_type}] {from_agent}: {content_preview}...")

        # Stop debate
        print("\n5. Stopping debate...")
        await manager.stop_debate()

        # Cancel the task
        debate_task.cancel()
        try:
            await debate_task
        except asyncio.CancelledError:
            pass

        print("\n✅ TEST 1 PASSED" if len(messages_received) > 0 else "\n❌ TEST 1 FAILED: No messages received")
        return len(messages_received) > 0

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoint():
    """Test the API endpoint using httpx."""
    print("\n" + "="*60)
    print("TEST 2: API Endpoint Test")
    print("="*60)

    try:
        import httpx

        base_url = "http://localhost:8000"

        print(f"\n1. Testing health endpoint: {base_url}/health")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")

            if response.status_code != 200:
                print("❌ Health check failed")
                return False

            print("\n2. Testing debate start endpoint...")
            start_payload = {
                "topic": "Test Topic",
                "rounds": 1,
                "agents": ["moderator", "conservative", "progressive"]
            }

            response = await client.post(
                f"{base_url}/api/debate/start",
                json=start_payload
            )

            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {result}")

            if "debate_id" not in result:
                print("❌ No debate_id in response!")
                return False

            debate_id = result["debate_id"]
            print(f"   ✅ Got debate_id: {debate_id}")

            # Wait a bit for debate to start
            print("\n3. Waiting 10 seconds for debate to progress...")
            await asyncio.sleep(10)

            # Check status
            print("\n4. Checking debate status...")
            response = await client.get(f"{base_url}/api/debate/{debate_id}/status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")

            # Stop debate
            print("\n5. Stopping debate...")
            response = await client.post(
                f"{base_url}/api/debate/stop",
                json={"debate_id": debate_id}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")

            print("\n✅ TEST 2 PASSED")
            return True

    except ImportError:
        print("\n⚠️  httpx not installed. Run: pip install httpx")
        print("   Skipping API endpoint test")
        return None
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_connection():
    """Test WebSocket connection."""
    print("\n" + "="*60)
    print("TEST 3: WebSocket Connection Test")
    print("="*60)

    try:
        import websockets

        ws_url = "ws://localhost:8000/ws/debate/test123"

        print(f"\n1. Connecting to WebSocket: {ws_url}")

        async with websockets.connect(ws_url) as websocket:
            print("   ✅ Connected!")

            print("\n2. Waiting for messages (5 seconds)...")
            try:
                # Wait for a message with timeout
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"   ✅ Received message: {message[:100]}...")
            except asyncio.TimeoutError:
                print("   ⚠️  No messages received (this is expected if no debate is running)")

            print("\n✅ TEST 3 PASSED (connection successful)")
            return True

    except ImportError:
        print("\n⚠️  websockets not installed. Run: pip install websockets")
        print("   Skipping WebSocket test")
        return None
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_agent():
    """Test a single agent response."""
    print("\n" + "="*60)
    print("TEST 4: Single Agent Test")
    print("="*60)

    try:
        from agents.moderator import ModeratorAgent

        print("\n1. Initializing ModeratorAgent...")
        moderator = ModeratorAgent()
        print(f"   ✅ Agent created: {moderator.name}")

        print("\n2. Generating response...")
        prompt = "Say hello and introduce yourself in one sentence."

        response = await moderator.generate_response("", prompt)

        print(f"   ✅ Response received ({len(response)} chars)")
        print(f"   Response: {response[:200]}...")

        if len(response) > 10:
            print("\n✅ TEST 4 PASSED")
            return True
        else:
            print("\n❌ TEST 4 FAILED: Response too short")
            return False

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("AI DEBATE ARENA - INTEGRATION TESTS")
    print("="*60)
    print(f"Time: {datetime.now()}")

    results = {}

    # Test 4: Single agent (fastest, tests API key)
    print("\n\n🧪 Running Test 4: Single Agent...")
    results["single_agent"] = await test_single_agent()

    # Test 1: DebateManager (core functionality)
    print("\n\n🧪 Running Test 1: DebateManager...")
    results["debate_manager"] = await test_debate_manager()

    # Test 2: API endpoint (requires server running)
    print("\n\n🧪 Running Test 2: API Endpoint...")
    print("⚠️  Make sure server is running: python -m demo.server")
    input("Press Enter when server is ready...")
    results["api_endpoint"] = await test_api_endpoint()

    # Test 3: WebSocket (requires server running)
    print("\n\n🧪 Running Test 3: WebSocket...")
    results["websocket"] = await test_websocket_connection()

    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{test_name:20s}: {status}")

    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
