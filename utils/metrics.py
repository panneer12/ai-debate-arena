"""
Observability and Metrics module for AI Debate Arena.

Handles structured logging, metrics collection (latency, tokens),
and model output sampling.
"""

import json
import logging
import random
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for a single agent's action."""

    agent_name: str
    action_type: str  # e.g., "generate_response", "process_message"
    latency_ms: float
    token_count_input: int = 0
    token_count_output: int = 0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DebateMetrics:
    """Aggregated metrics for a full debate."""

    debate_id: str
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    agent_actions: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    quality_scores: List[Dict[str, Any]] = field(default_factory=list)


class MetricsCollector:
    """
    Central collector for debate metrics.
    Singleton-like usage per debate recommended.
    """

    def __init__(self, debate_id: str):
        self.metrics = DebateMetrics(debate_id=debate_id)
        self.sample_rate = 0.2  # Log 20% of raw model IO

    def track_action(
        self,
        agent_name: str,
        action_type: str,
        start_time: float,
        input_text: str = "",
        output_text: str = "",
        error: Optional[Exception] = None,
    ):
        """
        Track an agent action including latency and tokens.
        """
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Simple token estimation (4 chars ~= 1 token)
        input_tokens = len(input_text) // 4
        output_tokens = len(output_text) // 4

        action_metric = AgentMetrics(
            agent_name=agent_name,
            action_type=action_type,
            latency_ms=latency_ms,
            token_count_input=input_tokens,
            token_count_output=output_tokens,
            error=str(error) if error else None,
        )

        # Update aggregated metrics
        self.metrics.total_latency_ms += latency_ms
        self.metrics.total_tokens += input_tokens + output_tokens
        self.metrics.agent_actions.append(asdict(action_metric))

        if error:
            error_details = (
                f"{agent_name} error in {action_type}: {str(error)}\n{traceback.format_exc()}"
            )
            self.metrics.errors.append(error_details)
            logger.error(f"❌ Captured Error: {error_details}")

        # Sampling for Model IO logging (Cloud Logging)
        if random.random() < self.sample_rate:
            self._log_model_io(agent_name, action_type, input_text, output_text)

    def log_quality_score(self, agent_name: str, score_type: str, value: float):
        """Log a quality metric (e.g., logical validity)."""
        self.metrics.quality_scores.append(
            {
                "agent": agent_name,
                "metric": score_type,
                "value": value,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def _log_model_io(self, agent: str, action: str, input_text: str, output_text: str):
        """Log raw model inputs/outputs to Cloud Logging (structured)."""
        log_payload = {
            "event": "model_io_sample",
            "agent": agent,
            "action": action,
            "input_snippet": input_text[:500] + "..." if len(input_text) > 500 else input_text,
            "output_snippet": output_text[:500] + "..." if len(output_text) > 500 else output_text,
        }
        # In Cloud Run, printing JSON to stdout is captured as structured logs
        # print(json.dumps(log_payload))  # Disabled for cleaner console output
        logger.debug(f"Model IO sample: {agent} {action}")

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Return full metrics as dictionary."""
        return asdict(self.metrics)
