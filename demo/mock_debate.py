"""Mock debate runner for testing flow without API key."""

import asyncio
import logging
import sys
from unittest.mock import AsyncMock

from agents.evidence import DevilsAdvocateAgent, FactCheckerAgent
from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent
from agents.synthesis import ArgumentAnalyzerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class MockConservative(ConservativeAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "I believe in free markets and tradition. [Mocked Argument]"


class MockProgressive(ProgressiveAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "I believe in social justice and equity. [Mocked Argument]"


class MockFactChecker(FactCheckerAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "VERDICT: PARTIALLY_TRUE\nCONFIDENCE: 0.7\nEVIDENCE: Mixed evidence found. [Mocked]"


class MockDevilsAdvocate(DevilsAdvocateAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "CHALLENGE TYPE: assumption\nQUESTION: What evidence supports this claim?\nREASONING: This assumes facts not in evidence. [Mocked]"


class MockAnalyzer(ArgumentAnalyzerAgent):
    async def generate_response(self, context: str, prompt: str) -> str:
        return "LOGICAL_VALIDITY: 0.8\nEVIDENCE_QUALITY: 0.7\nFALLACIES: none\nSTRENGTHS: Clear logic\nWEAKNESSES: Could use more data"


async def main():
    print("\n🚀 Initializing MOCK Debate (No API Key needed)\n")

    # Initialize mocked agents
    moderator = ModeratorAgent()
    conservative = MockConservative()
    progressive = MockProgressive()
    fact_checker = MockFactChecker()
    devils_advocate = MockDevilsAdvocate()
    analyzer = MockAnalyzer()

    print("👥 Agents Ready:")
    print(f"  - {moderator.name}")
    print(f"  - {conservative.name}")
    print(f"  - {progressive.name}")
    print(f"  - {fact_checker.name}")
    print(f"  - {devils_advocate.name}")
    print(f"  - {analyzer.name}")
    print("\n" + "=" * 50 + "\n")

    try:
        # Start debate with all intelligence agents
        result = await moderator.start_debate(
            topic="Should we have universal healthcare?",
            debaters=[conservative, progressive],
            fact_checker=fact_checker,
            devils_advocate=devils_advocate,
        )

        print("\n" + "=" * 50)
        print("✅ Mock Debate Complete!")
        print(f"Total Messages: {len(result['history'])}")

    except Exception as e:
        print(f"\n❌ Error during debate: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
