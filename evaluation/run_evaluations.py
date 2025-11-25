"""
Evaluation runner for AI Debate Arena agents.

This script evaluates agent quality using Google ADK's evaluation framework.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

from agents.evidence.fact_checker import FactCheckerAgent
from agents.evidence.devils_advocate import DevilsAdvocateAgent
from agents.synthesis.analyzer import ArgumentAnalyzerAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentEvaluator:
    """Evaluator for debate agents using evalsets."""
    
    def __init__(self):
        self.evalsets_dir = Path("evaluation/evalsets")
        self.criteria_dir = Path("evaluation/criteria")
        self.results = {}
    
    async def load_evalset(self, evalset_path: Path) -> Dict[str, Any]:
        """Load an evalset JSON file."""
        with open(evalset_path, 'r') as f:
            return json.load(f)
    
    async def evaluate_fact_checker(self) -> Dict[str, Any]:
        """Evaluate Fact Checker Agent."""
        logger.info("🔍 Evaluating Fact Checker Agent...")
        
        agent = FactCheckerAgent()
        evalset = await self.load_evalset(self.evalsets_dir / "fact_checker_evalset.json")
        
        results = {
            "agent": "FactCheckerAgent",
            "total_cases": len(evalset["eval_cases"]),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for case in evalset["eval_cases"]:
            eval_id = case["eval_id"]
            conversation = case["conversation"][0]
            
            # Get user input
            user_text = conversation["user_content"]["parts"][0]["text"]
            expected_response = conversation["final_response"]["parts"][0]["text"]
            
            #  Run agent
            try:
                result = await agent.check_claim(user_text)
                actual_response = f"VERDICT: {result['verdict']}\nCONFIDENCE: {result['confidence']}\nEVIDENCE: {result['explanation']}"
                
                # Simple evaluation: check if verdict matches
                expected_verdict = expected_response.split("VERDICT:")[1].split("\n")[0].strip()
                actual_verdict = result['verdict']
                
                passed = expected_verdict == actual_verdict
                
                if passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                results["details"].append({
                    "eval_id": eval_id,
                    "status": "PASS" if passed else "FAIL",
                    "expected": expected_verdict,
                    "actual": actual_verdict
                })
                
            except Exception as e:
                logger.error(f"Error evaluating {eval_id}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "eval_id": eval_id,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return results
    
    async def evaluate_devils_advocate(self) -> Dict[str, Any]:
        """Evaluate Devil's Advocate Agent."""
        logger.info("🎭 Evaluating Devil's Advocate Agent...")
        
        agent = DevilsAdvocateAgent()
        evalset = await self.load_evalset(self.evalsets_dir / "devils_advocate_evalset.json")
        
        results = {
            "agent": "DevilsAdvocateAgent",
            "total_cases": len(evalset["eval_cases"]),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for case in evalset["eval_cases"]:
            eval_id = case["eval_id"]
            conversation = case["conversation"][0]
            
            user_text = conversation["user_content"]["parts"][0]["text"]
            expected_response = conversation["final_response"]["parts"][0]["text"]
            
            try:
                result = await agent.challenge_argument(user_text, "TestUser")
                
                # Check if challenge type matches
                expected_type = expected_response.split("CHALLENGE TYPE:")[1].split("\n")[0].strip()
                actual_type = result['challenge_type']
                
                passed = expected_type == actual_type
                
                if passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                results["details"].append({
                    "eval_id": eval_id,
                    "status": "PASS" if passed else "FAIL",
                    "expected": expected_type,
                    "actual": actual_type
                })
                
            except Exception as e:
                logger.error(f"Error evaluating {eval_id}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "eval_id": eval_id,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return results
    
    async def run_all_evaluations(self) -> Dict[str, Any]:
        """Run all agent evaluations."""
        logger.info("\n🚀 Starting Agent Evaluations\n")
        
        all_results = {}
        
        # Evaluate each agent
        all_results["fact_checker"] = await self.evaluate_fact_checker()
        all_results["devils_advocate"] = await self.evaluate_devils_advocate()
        
        # Summary
        total_passed = sum(r["passed"] for r in all_results.values())
        total_failed = sum(r["failed"] for r in all_results.values())
        total_cases = sum(r["total_cases"] for r in all_results.values())
        
        all_results["summary"] = {
            "total_cases": total_cases,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": total_passed / total_cases if total_cases > 0 else 0
        }
        
        logger.info(f"\n📊 Evaluation Summary:")
        logger.info(f"Total Cases: {total_cases}")
        logger.info(f"Passed: {total_passed}")
        logger.info(f"Failed: {total_failed}")
        logger.info(f"Pass Rate: {all_results['summary']['pass_rate']:.1%}\n")
        
        return all_results

async def main():
    evaluator = AgentEvaluator()
    results = await evaluator.run_all_evaluations()
    
    # Save results
    output_file = Path("evaluation/results/evaluation_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
