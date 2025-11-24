"""AI Debate Arena - Main entry point."""
import asyncio
import logging
from typing import List

from config import settings
from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent
from agents.evidence.fact_checker import FactCheckerAgent
from agents.evidence.devils_advocate import DevilsAdvocateAgent
from agents.synthesis.synthesizer import SynthesizerAgent


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_debate(topic: str) -> dict:
    """
    Run a complete debate on the given topic.
    
    Args:
        topic: The debate topic/question
        
    Returns:
        Complete debate results with synthesis
    """
    logger.info(f"Starting debate on topic: {topic}")
    
    # Initialize agents
    moderator = ModeratorAgent()
    conservative = ConservativeAgent()
    progressive = ProgressiveAgent()
    fact_checker = FactCheckerAgent()
    devils_advocate = DevilsAdvocateAgent()
    synthesizer = SynthesizerAgent()
    
    # Start debate
    result = await moderator.start_debate(
        topic=topic,
        debaters=[conservative, progressive],
        fact_checker=fact_checker,
        devils_advocate=devils_advocate,
        synthesizer=synthesizer
    )
    
    logger.info("Debate completed successfully")
    return result


async def main():
    """Main application entry point."""
    logger.info("AI Debate Arena starting...")
    
    # Example debate
    topic = "Should we have universal healthcare?"
    
    result = await run_debate(topic)
    
    # Print results
    print("\n" + "="*80)
    print(f"DEBATE: {topic}")
    print("="*80)
    print("\nCONSENSUS POINTS:")
    for point in result["synthesis"]["consensus_points"]:
        print(f"  ✓ {point}")
    
    print("\nSTRONGEST ARGUMENTS:")
    for agent, arg in result["synthesis"]["strongest_arguments"].items():
        print(f"  • {agent}: {arg}")
    
    print("\nCOMMON GROUND:")
    print(f"  {result['synthesis']['common_ground']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
