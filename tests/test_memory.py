"""Test Memory Bank."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from memory.memory_bank import MemoryBank
from protocols.message_format import DebateMessage, MessageType


@pytest.fixture
def temp_memory_dir(tmp_path):
    return str(tmp_path / "debates")


def test_memory_initialization(temp_memory_dir):
    """Test memory bank initialization."""
    memory = MemoryBank(storage_dir=temp_memory_dir)
    assert Path(temp_memory_dir).exists()
    assert memory.messages == []
    assert memory.debate_id is not None


def test_add_and_retrieve_messages(temp_memory_dir):
    """Test adding and retrieving messages."""
    memory = MemoryBank(storage_dir=temp_memory_dir)

    msg1 = DebateMessage(
        from_agent="Agent A", role="Debater", content="Hello", type=MessageType.OPENING_STATEMENT
    )
    msg2 = DebateMessage(
        from_agent="Agent B", role="Debater", content="Hi", type=MessageType.OPENING_STATEMENT
    )

    memory.add_message(msg1)
    memory.add_message(msg2)

    assert len(memory.get_full_history()) == 2
    assert len(memory.get_messages_by_agent("Agent A")) == 1
    assert memory.get_messages_by_agent("Agent A")[0].content == "Hello"


def test_save_and_load_debate(temp_memory_dir):
    """Test saving and loading debate history."""
    memory = MemoryBank(storage_dir=temp_memory_dir)

    msg = DebateMessage(
        from_agent="Agent A", role="Debater", content="Test", type=MessageType.ARGUMENT
    )
    memory.add_message(msg)

    # Save
    file_path = memory.save_debate("test_debate.json")
    assert Path(file_path).exists()

    # Load into new memory bank
    new_memory = MemoryBank(storage_dir=temp_memory_dir)
    new_memory.load_debate("test_debate.json")

    assert len(new_memory.messages) == 1
    assert new_memory.messages[0].content == "Test"
    assert new_memory.messages[0].from_agent == "Agent A"
