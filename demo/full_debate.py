"""
Full system debate demo integrating all agents and memory.

This script demonstrates the complete AI Debate Arena flow:
1. Moderator starts debate
2. Debaters (Conservative/Progressive) argue
3. Fact Checker verifies claims
4. Devil's Advocate challenges assumptions
5. Argument Analyzer evaluates logic
6. Memory Bank stores history
7. Synthesizer & Common Ground Finder conclude
"""
import asyncio
import logging
from typing import List

from agents.moderator import ModeratorAgent
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent
from agents.evidence.fact_checker import FactCheckerAgent
from agents.evidence.devils_advocate import DevilsAdvocateAgent
from agents.synthesis.analyzer import ArgumentAnalyzerAgent
from agents.synthesis.synthesizer import SynthesizerAgent
from agents.synthesis.common_ground import CommonGroundFinder
from memory.memory_bank import MemoryBank
from protocols.message_format import DebateMessage, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/full_debate.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_full_debate():
    """Run a complete end-to-end debate."""
    print("\n🚀 Starting Full AI Debate System...\n")
    
    # 1. Initialize all agents
    print("Init Moderator...")
    moderator = ModeratorAgent()
    print("Init Moderator Done.")
    
    print("Init Conservative...")
    conservative = ConservativeAgent()
    print("Init Progressive...")
    progressive = ProgressiveAgent()
    
    print("Init FactChecker...")
    fact_checker = FactCheckerAgent()
    print("Init DevilsAdvocate...")
    devils_advocate = DevilsAdvocateAgent()
    print("Init Analyzer...")
    analyzer = ArgumentAnalyzerAgent()
    
    print("Init Synthesizer...")
    synthesizer = SynthesizerAgent()
    print("Init CommonGround...")
    common_ground = CommonGroundFinder()
    
    # 2. Initialize Memory
    print("Init Memory...")
    memory = MemoryBank()
    
    # 3. Setup Debate
    topic = "Universal Basic Income (UBI)"
    rounds = 2
    
    print(f"Topic: {topic}")
    print(f"Rounds: {rounds}")
    print("-" * 50)
    
    # -- Opening --
    print("\n📢 Moderator Opening...")
    opening_prompt = f"Welcome everyone. Please provide an opening statement for the debate on '{topic}'. Introduce the topic and the participants: Conservative and Progressive."
    opening_text = await moderator.generate_response([], opening_prompt)
    
    opening_msg = {
        "from_agent": moderator.name,
        "role": moderator.role,
        "content": opening_text,
        "type": MessageType.OPENING_STATEMENT
    }
    memory.add_message(DebateMessage(**opening_msg))
        
    print(f"Moderator: {opening_text}")
    
    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num} ---")
        
        # -- Conservative Turn --
        print("\n🐘 Conservative Speaking...")
        history = memory.get_full_history()
        con_response = await conservative.process_message(history[-1].to_dict())
        con_msg = DebateMessage(**con_response)
        con_msg.round_number = round_num
        memory.add_message(con_msg)
        print(f"Conservative: {con_msg.content[:100]}...")
        
        # Analysis & Checks (Parallel)
        print("   🔍 Analyzing...")
        checks = await asyncio.gather(
            fact_checker.check_claim(con_msg.content),
            devils_advocate.challenge_argument(con_msg.content, "Conservative"),
            analyzer.analyze_argument(con_msg.content, "Conservative")
        )
        
        # Log checks (simplified output)
        fc_res, da_res, aa_res = checks
        if fc_res['verdict'] != 'TRUE':
            print(f"   ⚠️ Fact Check: {fc_res['verdict']}")
        if da_res:
            print(f"   😈 Devil's Advocate: Challenging {da_res['challenge_type']}")
        
        # -- Progressive Turn --
        print("\n🐘 Progressive Speaking...")
        history = memory.get_full_history()
        prog_response = await progressive.process_message(history[-1].to_dict())
        prog_msg = DebateMessage(**prog_response)
        prog_msg.round_number = round_num
        memory.add_message(prog_msg)
        print(f"Progressive: {prog_msg.content[:100]}...")
        
        # Analysis & Checks (Parallel)
        print("   🔍 Analyzing...")
        checks = await asyncio.gather(
            fact_checker.check_claim(prog_msg.content),
            devils_advocate.challenge_argument(prog_msg.content, "Progressive"),
            analyzer.analyze_argument(prog_msg.content, "Progressive")
        )
    
    # 5. Synthesis Phase
    print("\n--- Synthesis Phase ---")
    
    # Get full debate history from memory
    history = memory.get_full_history()
    
    print("\n🤝 Finding Common Ground...")
    cg_result = await common_ground.find_common_ground(history, topic)
    print(f"Shared Values: {', '.join(cg_result['shared_values'])}")
    print(f"Agreement Score: {cg_result['agreement_score']}%")
    
    print("\n🧠 Generating Conclusion...")
    synth_result = await synthesizer.synthesize_debate(history, topic)
    print(f"Winner: {synth_result['winner']}")
    print(f"Summary: {synth_result['summary']}")
    
    # 6. Save Debate
    saved_path = memory.save_debate()
    print(f"\n💾 Debate saved to: {saved_path}")
    print("\n✅ Full System Test Complete!")

if __name__ == "__main__":
    asyncio.run(run_full_debate())
