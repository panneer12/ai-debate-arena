"""Memory system for AI Debate Arena."""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from protocols.message_format import DebateMessage

logger = logging.getLogger(__name__)

class MemoryBank:
    """
    Manages debate history and context persistence.
    
    Stores messages, allows retrieval by criteria, and handles saving/loading debates.
    """
    
    def __init__(self, storage_dir: str = "data/debates"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.messages: List[DebateMessage] = []
        self.debate_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"🧠 Memory Bank initialized for debate {self.debate_id}")

    def add_message(self, message: DebateMessage):
        """Add a message to memory."""
        self.messages.append(message)
        
    def get_full_history(self) -> List[DebateMessage]:
        """Get entire debate history."""
        return self.messages.copy()
    
    def get_messages_by_agent(self, agent_name: str) -> List[DebateMessage]:
        """Get all messages from a specific agent."""
        return [msg for msg in self.messages if msg.from_agent == agent_name]
    
    def get_messages_by_role(self, role: str) -> List[DebateMessage]:
        """Get all messages from a specific role."""
        return [msg for msg in self.messages if msg.role == role]
        
    def save_debate(self, filename: Optional[str] = None):
        """Save current debate history to JSON."""
        if not filename:
            filename = f"debate_{self.debate_id}.json"
            
        file_path = self.storage_dir / filename
        
        data = {
            "debate_id": self.debate_id,
            "timestamp": datetime.now().isoformat(),
            "messages": [msg.to_dict() for msg in self.messages]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            
        logger.info(f"💾 Debate saved to {file_path}")
        return str(file_path)
    
    def load_debate(self, filename: str):
        """Load debate history from JSON."""
        file_path = self.storage_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Debate file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.debate_id = data.get("debate_id", self.debate_id)
        self.messages = [DebateMessage(**msg) for msg in data.get("messages", [])]
        
        logger.info(f"📂 Loaded {len(self.messages)} messages from {filename}")
