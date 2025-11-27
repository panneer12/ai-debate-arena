"""Simple CLI debate runner."""

import argparse
import asyncio
import logging
import sys

from dotenv import load_dotenv

# Load env before imports that might use settings
load_dotenv()

# Configure logging
import os
from datetime import datetime

from agents.evidence import DevilsAdvocateAgent, FactCheckerAgent
from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent

# Create logs directory
os.makedirs("logs", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/debate_{timestamp}.log"

# Configure root logger to write to file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8")],
)

# Configure console output (cleaner)
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")  # Just the message for console
console.setFormatter(formatter)


# Filter out noisy libraries from console
class NoisyFilter(logging.Filter):
    def filter(self, record):
        # Filter out http requests and internal library logs from console
        return not (
            record.name.startswith("httpx")
            or record.name.startswith("google_genai")
            or record.name.startswith("httpcore")
            or record.name.startswith("google.genai")
        )


console.addFilter(NoisyFilter())
logging.getLogger("").addHandler(console)

# Explicitly silence library loggers to be safe
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("google.genai").setLevel(logging.WARNING)


async def main():
    parser = argparse.ArgumentParser(description="Run a simple AI debate.")
    parser.add_argument(
        "--topic", type=str, default="Should we have universal healthcare?", help="Debate topic"
    )
    args = parser.parse_args()

    print(f"\n🚀 Initializing Debate: {args.topic}\n")

    # Initialize agents
    moderator = ModeratorAgent()
    conservative = ConservativeAgent()
    progressive = ProgressiveAgent()
    fact_checker = FactCheckerAgent()
    devils_advocate = DevilsAdvocateAgent()

    print("👥 Agents Ready:")
    print(f"  - {moderator.name} ({moderator.role})")
    print(f"  - {conservative.name} ({conservative.role})")
    print(f"  - {progressive.name} ({progressive.role})")
    print(f"  - {fact_checker.name} ({fact_checker.role})")
    print(f"  - {devils_advocate.name} ({devils_advocate.role})")
    print("\n" + "=" * 50 + "\n")

    try:
        # Start debate with intelligence agents
        result = await moderator.start_debate(
            topic=args.topic,
            debaters=[conservative, progressive],
            fact_checker=fact_checker,
            devils_advocate=devils_advocate,
        )

        print("\n" + "=" * 50)
        print("✅ Debate Complete!")
        print(f"Total Messages: {len(result['history'])}")
        print(f"\n📝 Full log saved to: {log_file}")

    except Exception as e:
        print(f"\n❌ Error during debate: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
