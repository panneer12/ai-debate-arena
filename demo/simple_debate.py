"""Simple CLI debate runner."""
import asyncio
import logging
import argparse
import sys
from dotenv import load_dotenv

# Load env before imports that might use settings
load_dotenv()

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

async def main():
    parser = argparse.ArgumentParser(description="Run a simple AI debate.")
    parser.add_argument("--topic", type=str, default="Should we have universal healthcare?", help="Debate topic")
    args = parser.parse_args()

    print(f"\n🚀 Initializing Debate: {args.topic}\n")

    # Initialize agents
    moderator = ModeratorAgent()
    conservative = ConservativeAgent()
    progressive = ProgressiveAgent()

    print("👥 Agents Ready:")
    print(f"  - {moderator.name} ({moderator.role})")
    print(f"  - {conservative.name} ({conservative.role})")
    print(f"  - {progressive.name} ({progressive.role})")
    print("\n" + "="*50 + "\n")

    try:
        # Start debate
        result = await moderator.start_debate(
            topic=args.topic,
            debaters=[conservative, progressive]
        )
        
        print("\n" + "="*50)
        print("✅ Debate Complete!")
        print(f"Total Messages: {len(result['history'])}")
        
    except Exception as e:
        print(f"\n❌ Error during debate: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
