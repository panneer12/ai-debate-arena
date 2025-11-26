"""Test Firestore integration in MemoryBank."""
import pytest
from unittest.mock import MagicMock, patch
from memory.memory_bank import MemoryBank
from protocols.message_format import DebateMessage, MessageType

@pytest.fixture
def mock_firestore():
    with patch('google.cloud.firestore.Client') as mock:
        yield mock

@pytest.fixture
def memory_bank_with_firestore(mock_firestore):
    # Force Firestore initialization by mocking env var
    with patch.dict('os.environ', {'GOOGLE_APPLICATION_CREDENTIALS': 'fake_path'}):
        bank = MemoryBank()
        return bank, mock_firestore

def test_firestore_init_success(memory_bank_with_firestore):
    bank, mock_client = memory_bank_with_firestore
    assert bank.firestore_client is not None
    mock_client.assert_called_once()

def test_firestore_init_failure():
    # Should handle missing credentials gracefully
    with patch.dict('os.environ', {}, clear=True):
        bank = MemoryBank()
        assert bank.firestore_client is None

def test_save_debate_dual_write(memory_bank_with_firestore, tmp_path):
    bank, mock_client = memory_bank_with_firestore
    bank.storage_dir = tmp_path
    
    # Add a message
    msg = DebateMessage(
        from_agent="TestAgent",
        content="Test content",
        type=MessageType.ARGUMENT,
        role="Debater"
    )
    bank.add_message(msg)
    
    # Mock Firestore document reference
    mock_doc_ref = MagicMock()
    mock_client.return_value.collection.return_value.document.return_value = mock_doc_ref
    
    # Save
    bank.save_debate()
    
    # Verify Local Write
    files = list(tmp_path.glob("debate_*.json"))
    assert len(files) == 1
    
    # Verify Firestore Write
    mock_client.return_value.collection.assert_called_with("debates")
    mock_client.return_value.collection.return_value.document.assert_called_with(bank.debate_id)
    mock_doc_ref.set.assert_called_once()
    
    # Verify data passed to Firestore
    call_args = mock_doc_ref.set.call_args[0][0]
    assert call_args["debate_id"] == bank.debate_id
    assert len(call_args["messages"]) == 1
    assert call_args["messages"][0]["content"] == "Test content"

def test_save_debate_firestore_error_handling(memory_bank_with_firestore, tmp_path):
    bank, mock_client = memory_bank_with_firestore
    bank.storage_dir = tmp_path
    
    # Mock Firestore error
    mock_doc_ref = MagicMock()
    mock_doc_ref.set.side_effect = Exception("Firestore connection failed")
    mock_client.return_value.collection.return_value.document.return_value = mock_doc_ref
    
    # Should not raise exception (graceful degradation)
    try:
        bank.save_debate()
    except Exception as e:
        pytest.fail(f"save_debate raised exception on Firestore error: {e}")
        
    # Local file should still exist
    files = list(tmp_path.glob("debate_*.json"))
    assert len(files) == 1
