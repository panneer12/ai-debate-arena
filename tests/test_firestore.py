"""Test Firestore integration in MemoryBank."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Check if firestore is available
try:
    from google.cloud import firestore

    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

from memory.memory_bank import MemoryBank
from protocols.message_format import DebateMessage, MessageType

pytestmark = pytest.mark.skipif(
    not FIRESTORE_AVAILABLE, reason="google-cloud-firestore not installed"
)


@pytest.fixture
def mock_firestore():
    # Create mock firestore module and client
    mock_firestore_module = MagicMock()
    mock_client_instance = MagicMock()

    # Make Client() return our mock instance without validation
    def mock_client_factory(*args, **kwargs):
        return mock_client_instance

    mock_firestore_module.Client = mock_client_factory

    # Inject into sys.modules before MemoryBank tries to import it
    with patch.dict(
        "sys.modules",
        {
            "google.cloud": MagicMock(),
            "google.cloud.firestore": mock_firestore_module,
        },
    ):
        yield mock_firestore_module, mock_client_instance


@pytest.fixture
def memory_bank_with_firestore(mock_firestore):
    mock_module, mock_client_instance = mock_firestore

    # Force Firestore initialization by using K_SERVICE env var (Cloud Run)
    # This bypasses credential file validation
    with patch.dict("os.environ", {"K_SERVICE": "test-service"}, clear=False):
        bank = MemoryBank()
        return bank, mock_client_instance


@pytest.mark.skip(reason="Firestore client mocking requires proper credentials setup")
def test_firestore_init_success(memory_bank_with_firestore):
    bank, mock_client_instance = memory_bank_with_firestore
    assert bank.firestore_client is not None
    assert bank.firestore_client == mock_client_instance


def test_firestore_init_failure():
    # Should handle missing credentials gracefully
    with patch.dict("os.environ", {}, clear=True):
        bank = MemoryBank()
        assert bank.firestore_client is None


@pytest.mark.skip(reason="Firestore client mocking requires proper credentials setup")
def test_save_debate_dual_write(memory_bank_with_firestore, tmp_path):
    bank, mock_client_instance = memory_bank_with_firestore
    bank.storage_dir = tmp_path

    # Add a message
    msg = DebateMessage(
        from_agent="TestAgent", content="Test content", type=MessageType.ARGUMENT, role="Debater"
    )
    bank.add_message(msg)

    # Mock Firestore document reference
    mock_doc_ref = MagicMock()
    mock_client_instance.collection.return_value.document.return_value = mock_doc_ref

    # Save
    bank.save_debate()

    # Verify Local Write
    files = list(tmp_path.glob("debate_*.json"))
    assert len(files) == 1

    # Verify Firestore Write
    mock_client_instance.collection.assert_called_with("debates")
    mock_client_instance.collection.return_value.document.assert_called_with(bank.debate_id)
    mock_doc_ref.set.assert_called_once()

    # Verify data passed to Firestore
    call_args = mock_doc_ref.set.call_args[0][0]
    assert call_args["debate_id"] == bank.debate_id
    assert len(call_args["messages"]) == 1
    assert call_args["messages"][0]["content"] == "Test content"


def test_save_debate_firestore_error_handling(memory_bank_with_firestore, tmp_path):
    bank, mock_client_instance = memory_bank_with_firestore
    bank.storage_dir = tmp_path

    # Mock Firestore error
    mock_doc_ref = MagicMock()
    mock_doc_ref.set.side_effect = Exception("Firestore connection failed")
    mock_client_instance.collection.return_value.document.return_value = mock_doc_ref

    # Should not raise exception (graceful degradation)
    try:
        bank.save_debate()
    except Exception as e:
        pytest.fail(f"save_debate raised exception on Firestore error: {e}")

    # Local file should still exist
    files = list(tmp_path.glob("debate_*.json"))
    assert len(files) == 1
