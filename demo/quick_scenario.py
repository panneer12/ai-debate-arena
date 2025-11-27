"""Quick scenario recording - Minimal version without emojis."""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agents.evidence.devils_advocate import DevilsAdvocateAgent
from agents.evidence.fact_checker import FactCheckerAgent
from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent
from agents.synthesis.common_ground import CommonGroundFinder
from agents.synthesis.synthesizer import SynthesizerAgent
from memory.memory_bank import MemoryBank
from protocols.message_format import DebateMessage, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("demo/examples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def run_scenario(topic: str, scenario_name: str, rounds: int = 2):
    """Run a single debate scenario."""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"Topic: {topic}")
    print(f"{'='*80}\n")

    # Initialize agents
    print("Initializing agents...")
    moderator = ModeratorAgent()
    conservative = ConservativeAgent()
    progressive = ProgressiveAgent()
    fact_checker = FactCheckerAgent()
    devils_advocate = DevilsAdvocateAgent()
    synthesizer = SynthesizerAgent()
    common_ground = CommonGroundFinder()
    memory = MemoryBank()

    # Opening
    print("\nModerator Opening...")
    opening_prompt = f"Welcome. Today's debate: '{topic}'. Introduce the participants and begin."
    opening_text = await moderator.generate_response([], opening_prompt)
    opening_msg = {
        "from_agent": moderator.name,
        "role": moderator.role,
        "content": opening_text,
        "type": MessageType.OPENING_STATEMENT,
    }
    memory.add_message(DebateMessage(**opening_msg))
    print(f"Moderator: {opening_text[:200]}...")

    # Rounds
    for round_num in range(1, rounds + 1):
        print(f"\n{'-'*80}")
        print(f"ROUND {round_num}/{rounds}")
        print(f"{'-'*80}\n")

        # Conservative
        print("Conservative Speaking...")
        history = memory.get_full_history()
        con_response = await conservative.process_message(history[-1].to_dict())
        con_msg = DebateMessage(**con_response)
        con_msg.round_number = round_num
        memory.add_message(con_msg)
        print(f"Conservative: {con_msg.content[:200]}...")

        # Progressive
        print("\nProgressive Speaking...")
        history = memory.get_full_history()
        prog_response = await progressive.process_message(history[-1].to_dict())
        prog_msg = DebateMessage(**prog_response)
        prog_msg.round_number = round_num
        memory.add_message(prog_msg)
        print(f"Progressive: {prog_msg.content[:200]}...")

    # Synthesis
    print(f"\n{'-'*80}")
    print("SYNTHESIS")
    print(f"{'-'*80}\n")

    history = memory.get_full_history()

    print("Finding Common Ground...")
    cg_result = await common_ground.find_common_ground(history, topic)
    print(f"  Shared Values: {', '.join(cg_result.get('shared_values', []))}")
    print(f"  Agreement Score: {cg_result.get('agreement_score', 0)}%")

    print("\nGenerating Synthesis...")
    synth_result = await synthesizer.synthesize_debate(history, topic)
    print(f"  Winner: {synth_result.get('winner', 'Tie')}")
    print(f"  Summary: {synth_result.get('summary', '')[:200]}...")

    # Save
    output_file = OUTPUT_DIR / f"{scenario_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "scenario": scenario_name,
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "messages": [msg.to_dict() for msg in history],
                "synthesis": synth_result,
                "common_ground": cg_result,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    # Save transcript
    transcript_file = OUTPUT_DIR / f"{scenario_name}_transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(f"AI DEBATE ARENA - {scenario_name.upper()}\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"{'='*80}\n\n")

        for msg in history:
            f.write(f"[{msg.from_agent}] ({msg.type})\n")
            f.write(f"{msg.content}\n")
            f.write(f"{'-'*80}\n\n")

        f.write(f"\n{'='*80}\n")
        f.write("SYNTHESIS\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Winner: {synth_result.get('winner', 'Tie')}\n\n")
        f.write(f"Summary:\n{synth_result.get('summary', '')}\n\n")
        f.write(f"Common Ground:\n")
        for value in cg_result.get("shared_values", []):
            f.write(f"  - {value}\n")
        f.write(f"\nAgreement Score: {cg_result.get('agreement_score', 0)}%\n")

    print(f"\nSaved to:")
    print(f"  JSON: {output_file}")
    print(f"  Transcript: {transcript_file}")
    print("\nDone!")


async def main():
    """Run all scenarios."""
    scenarios = [
        ("scenario_a_ubi", "Universal Basic Income"),
        ("scenario_b_social_media", "Should social media companies be liable for user content?"),
        ("scenario_c_ai_safety", "Should there be mandatory AI safety regulations?"),
    ]

    for scenario_name, topic in scenarios:
        try:
            await run_scenario(topic, scenario_name, rounds=2)
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error in {scenario_name}: {e}", exc_info=True)
            print(f"\nError in {scenario_name}: {e}")

    print(f"\n{'='*80}")
    print("ALL SCENARIOS COMPLETE")
    print(f"Output: {OUTPUT_DIR.absolute()}")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(main())
