"""
Quick test - just test the core components without server.
Run this FIRST to identify issues before testing with server.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    print("="*60)
    print("QUICK TEST - Core Components")
    print("="*60)

    # Test 1: Import check
    print("\n1. Testing imports...")
    try:
        from demo.debate_manager import DebateManager
        from agents.moderator import ModeratorAgent
        from memory.memory_bank import MemoryBank
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return

    # Test 2: API key check
    print("\n2. Testing API key...")
    try:
        from config import settings
        if settings.google_api_key and len(settings.google_api_key) > 10:
            print(f"   ✅ API key configured ({len(settings.google_api_key)} chars)")
        else:
            print("   ❌ API key not configured or too short")
            return
    except Exception as e:
        print(f"   ❌ Settings error: {e}")
        return

    # Test 3: Single agent response
    print("\n3. Testing single agent response...")
    try:
        moderator = ModeratorAgent()
        print(f"   - Agent created: {moderator.name}")

        print("   - Sending prompt to Gemini API...")
        response = await moderator.generate_response(
            context="",
            prompt="Reply with exactly: 'Hello, I am the moderator.'"
        )

        print(f"   - Response ({len(response)} chars): {response[:100]}...")

        if len(response) > 5:
            print("   ✅ Agent responding successfully")
        else:
            print("   ❌ Response too short")
            return
    except Exception as e:
        print(f"   ❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 4: DebateManager initialization
    print("\n4. Testing DebateManager...")
    try:
        messages = []

        async def capture_broadcast(msg):
            messages.append(msg)
            print(f"   📨 {msg.get('type', '?')}: {msg.get('from_agent', '?')}")

        manager = DebateManager(broadcast_func=capture_broadcast)
        await manager.initialize_agents()

        print(f"   - Moderator: {manager.moderator is not None}")
        print(f"   - Conservative: {manager.conservative is not None}")
        print(f"   - Progressive: {manager.progressive is not None}")

        if manager.moderator and manager.conservative and manager.progressive:
            print("   ✅ DebateManager initialized successfully")
        else:
            print("   ❌ Some agents not initialized")
            return
    except Exception as e:
        print(f"   ❌ DebateManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 5: Start debate and get one message
    print("\n5. Testing debate start (waiting 10 seconds)...")
    try:
        # Start debate in background
        debate_task = asyncio.create_task(
            manager.start_debate("Test Topic", rounds=1)
        )

        # Wait for first message
        for i in range(10):
            await asyncio.sleep(1)
            print(f"   - Waiting... ({i+1}/10s) - Messages: {len(messages)}")
            if len(messages) > 0:
                break

        # Stop debate
        await manager.stop_debate()
        debate_task.cancel()

        try:
            await debate_task
        except asyncio.CancelledError:
            pass

        print(f"\n   Total messages received: {len(messages)}")

        if len(messages) > 0:
            print("   ✅ Debate is working! Messages received:")
            for i, msg in enumerate(messages[:3]):
                print(f"      {i+1}. {msg.get('type', '?')} from {msg.get('from_agent', '?')}")
        else:
            print("   ❌ No messages received from debate")
            print("   This means agents are not generating responses.")
            print("   Check:")
            print("      - Google API key is valid")
            print("      - No quota limits exceeded")
            print("      - Internet connection working")
            return

    except Exception as e:
        print(f"   ❌ Debate test failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*60)
    print("✅ ALL QUICK TESTS PASSED!")
    print("="*60)
    print("\nNext step: Start server and test UI")
    print("  1. Run: python -m demo.server")
    print("  2. Open: http://localhost:8000")
    print("  3. Click 'Start Debate'")

if __name__ == "__main__":
    asyncio.run(main())
