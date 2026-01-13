"""
Mémoire à long terme émotionnelle.
Coordonne FAISS (rappel) et SQLite (traçabilité).
"""

import sqlite3
from typing import List, Dict
from datetime import datetime
from pathlib import Path

from memory.vector_store import VectorStore
import config


class LongTermMemory:
    """
    Mémoire autobiographique.
    """

    def __init__(self):
        self.db_path = Path(config.DB_PATH)
        self.vector_store = VectorStore()
        self._initialize_database()

    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                importance REAL,
                emotion TEXT,
                intensity REAL,
                timestamp TEXT,
                vector_id INTEGER
            )
        """)

        conn.commit()
        conn.close()

    # --------------------------------------------------
    # STORE
    # --------------------------------------------------

    def store_memory(
        self,
        text: str,
        emotion: Dict,
        importance: float = None,
    ) -> int:

        importance = importance if importance is not None else emotion.get("intensity", 0.5)

        if importance < config.MIN_MEMORY_IMPORTANCE:
            return -1

        vector_metadata = {
            "emotion": emotion,
            "intensity": emotion.get("intensity", 0.5),
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
        }

        vector_id = self.vector_store.add_memory(text, vector_metadata)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO memories
            (text, importance, emotion, intensity, timestamp, vector_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            text,
            importance,
            str(emotion),
            emotion.get("intensity", 0.5),
            datetime.now().isoformat(),
            vector_id,
        ))

        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return memory_id

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------

    def retrieve_memories(
        self,
        user_message: str,
        current_emotion: Dict,
        k: int = None,
    ) -> List[Dict]:

        results = self.vector_store.search(
            query=user_message,
            current_emotion=current_emotion,
            k=k or config.MEMORY_RETRIEVAL_K,
        )

        memories = []
        for meta, score in results:
            memories.append({
                "text": meta.get("text"),
                "emotion": meta.get("emotion"),
                "importance": meta.get("importance"),
                "intensity": meta.get("intensity"),
                "timestamp": meta.get("timestamp"),
                "score": score,
            })

        return memories

    # --------------------------------------------------
    # UTILITIES
    # --------------------------------------------------

    def get_memory_count(self) -> int:
        return self.vector_store.get_memory_count()
