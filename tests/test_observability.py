"""Test Observability Module."""

import time
from unittest.mock import MagicMock, patch

import pytest

from memory.memory_bank import MemoryBank
from utils.metrics import AgentMetrics, MetricsCollector


def test_metrics_collection():
    collector = MetricsCollector("test_debate_id")

    # Simulate action
    start_time = time.time()
    time.sleep(0.1)
    collector.track_action(
        agent_name="TestAgent",
        action_type="test_action",
        start_time=start_time,
        input_text="input",
        output_text="output",
    )

    metrics = collector.get_metrics_dict()
    assert metrics["debate_id"] == "test_debate_id"
    assert metrics["total_tokens"] > 0
    assert metrics["total_latency_ms"] > 0
    assert len(metrics["agent_actions"]) == 1

    action = metrics["agent_actions"][0]
    assert action["agent_name"] == "TestAgent"
    assert action["latency_ms"] >= 100  # At least 100ms


def test_error_capturing():
    collector = MetricsCollector("test_debate_id")

    try:
        raise ValueError("Test Error")
    except Exception as e:
        collector.track_action(
            agent_name="TestAgent", action_type="error_action", start_time=time.time(), error=e
        )

    metrics = collector.get_metrics_dict()
    assert len(metrics["errors"]) == 1
    assert "ValueError: Test Error" in metrics["errors"][0]


@patch("utils.metrics.logger")
def test_model_io_sampling(mock_logger):
    # Force sampling
    collector = MetricsCollector("test_debate_id")
    collector.sample_rate = 1.0

    collector.track_action(
        agent_name="TestAgent",
        action_type="generate_response",
        start_time=time.time(),
        input_text="input",
        output_text="output",
    )

    # The print statement is disabled, but logger.debug is called
    mock_logger.debug.assert_called_once()
    call_args = str(mock_logger.debug.call_args)
    assert "Model IO sample" in call_args or "TestAgent" in call_args


def test_metrics_persistence_in_memory_bank(tmp_path):
    # Setup MemoryBank with local storage
    bank = MemoryBank(storage_dir=tmp_path)

    # Create dummy metrics
    metrics = {"debate_id": bank.debate_id, "total_latency_ms": 500.0, "total_tokens": 100}

    # Save with metrics
    file_path = bank.save_debate(metrics=metrics)

    # Verify file content
    import json

    with open(file_path, "r") as f:
        data = json.load(f)

    assert "metrics" in data
    assert data["metrics"]["total_latency_ms"] == 500.0
