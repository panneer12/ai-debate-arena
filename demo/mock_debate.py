"""Mock debate runner for testing flow without API key."""
import asyncio
import logging
import sys
from unittest.mock import AsyncMock

from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class MockConservative(ConservativeAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "I believe in free markets and tradition. [Mocked Argument]"

class MockProgressive(ProgressiveAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "I believe in social justice and equity. [Mocked Argument]"

async def main():
    print("\n🚀 Initializing MOCK Debate (No API Key needed)\n")

    # Initialize agents
    moderator = ModeratorAgent()
    conservative = MockConservative()
    progressive = MockProgressive()
    
    # Mock moderator broadcast to avoid trying to use LLM for synthesis if it was hooked up
    # But currently moderator doesn't use LLM for its own speech in the MVP, it uses hardcoded strings + broadcast
    # However, if we add synthesis later, we'd need to mock that too.
    
    print("👥 Agents Ready:")
    print(f"  - {moderator.name}")
    print(f"  - {conservative.name}")
    print(f"  - {progressive.name}")
    print("\n" + "="*50 + "\n")

    try:
        # Start debate
        result = await moderator.start_debate(
            topic="Should we have universal healthcare?",
            debaters=[conservative, progressive]
        )
        
        print("\n" + "="*50)
        print("✅ Mock Debate Complete!")
        print(f"Total Messages: {len(result['history'])}")
        
    except Exception as e:
        print(f"\n❌ Error during debate: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
