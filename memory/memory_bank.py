"""Memory system for AI Debate Arena."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from protocols.message_format import DebateMessage

logger = logging.getLogger(__name__)

try:
    from google.auth.exceptions import DefaultCredentialsError
    from google.cloud import firestore

    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    logger.warning("google-cloud-firestore not installed. Using local storage only.")


class MemoryBank:
    """
    Manages debate history and context persistence.

    Stores messages, allows retrieval by criteria, and handles saving/loading debates.
    Supports both local JSON storage and Google Cloud Firestore.
    """

    def __init__(self, storage_dir: str = "data/debates"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.messages: List[DebateMessage] = []
        self.debate_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize Firestore
        self.firestore_client = None
        if FIRESTORE_AVAILABLE:
            try:
                # Only init if GOOGLE_APPLICATION_CREDENTIALS is set or in Cloud Run
                if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("K_SERVICE"):
                    self.firestore_client = firestore.Client()
                    logger.info("🔥 Firestore initialized successfully")
                else:
                    logger.info("⚠️ No Google Cloud credentials found. Using local storage only.")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Firestore: {e}")
        else:
            logger.info("⚠️ Firestore library not available. Using local storage only.")

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

    def save_debate(self, filename: Optional[str] = None, metrics: Optional[Dict[str, Any]] = None):
        """
        Save current debate history to JSON and Firestore.

        Args:
            filename: Optional filename for local storage.
            metrics: Optional metrics dictionary to save.

        Returns:
            Path to local file.
        """
        if not filename:
            filename = f"debate_{self.debate_id}.json"

        file_path = self.storage_dir / filename

        data = {
            "debate_id": self.debate_id,
            "timestamp": datetime.now().isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "metrics": metrics if metrics else {},
        }

        # 1. Save to Local JSON
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"💾 Debate saved locally to {file_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save local file: {e}")

        # 2. Save to Firestore (if enabled)
        if self.firestore_client:
            try:
                doc_ref = self.firestore_client.collection("debates").document(self.debate_id)
                doc_ref.set(data)
                logger.info(f"🔥 Debate saved to Firestore: debates/{self.debate_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save to Firestore: {e}")

        return str(file_path)

    def load_debate(self, filename: str):
        """Load debate history from JSON."""
        file_path = self.storage_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Debate file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.debate_id = data.get("debate_id", self.debate_id)
        self.messages = [DebateMessage(**msg) for msg in data.get("messages", [])]

        logger.info(f"📂 Loaded {len(self.messages)} messages from {filename}")
