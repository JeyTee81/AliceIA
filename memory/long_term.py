"""
Mémoire à long terme.
Gère le stockage persistant dans SQLite et FAISS.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

from memory.vector_store import VectorStore
import config


class LongTermMemory:
    """
    Mémoire à long terme persistante.
    Combine SQLite (métadonnées) et FAISS (recherche sémantique).
    """
    
    def __init__(self):
        self.db_path = Path(config.DB_PATH)
        self.vector_store = VectorStore()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialise la base de données SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des souvenirs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                emotion_intensity REAL DEFAULT 0.5,
                emotion_type TEXT,
                timestamp TEXT NOT NULL,
                vector_id INTEGER,
                metadata TEXT
            )
        """)
        
        # Table des interactions d'apprentissage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                ai_response TEXT,
                correction TEXT,
                validated INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_memory(
        self,
        text: str,
        importance: float = 0.5,
        emotion: Dict[str, float] = None,
        metadata: Dict = None
    ) -> int:
        """
        Stocke un souvenir en mémoire long terme.
        
        Args:
            text: Le contenu du souvenir
            importance: Score d'importance (0.0-1.0)
            emotion: État émotionnel associé
            metadata: Métadonnées supplémentaires
        
        Returns:
            L'ID du souvenir stocké
        """
        if importance < config.MIN_MEMORY_IMPORTANCE:
            return -1  # Pas assez important pour stocker
        
        emotion_intensity = 0.5
        emotion_type = "neutre"
        if emotion:
            emotion_intensity = emotion.get("intensity", 0.5)
            emotion_type = emotion.get("label", "neutre")
        
        # Ajouter au stockage vectoriel
        vector_metadata = {
            "importance": importance,
            "emotion_intensity": emotion_intensity,
            "emotion_type": emotion_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        vector_id = self.vector_store.add_memory(text, vector_metadata)
        
        # Ajouter à SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = str(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO memories 
            (text, importance, emotion_intensity, emotion_type, timestamp, vector_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            text,
            importance,
            emotion_intensity,
            emotion_type,
            datetime.now().isoformat(),
            vector_id,
            metadata_json
        ))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    def retrieve_memories(
        self,
        query: str,
        k: int = None,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """
        Récupère des souvenirs pertinents via recherche sémantique.
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats
            min_importance: Importance minimale
        
        Returns:
            Liste de souvenirs avec métadonnées
        """
        # Recherche vectorielle
        vector_results = self.vector_store.search(query, k)
        
        # Filtrer par importance et formater
        memories = []
        for metadata, similarity in vector_results:
            if metadata.get("importance", 0.0) >= min_importance:
                memory = {
                    "text": metadata.get("text", ""),
                    "importance": metadata.get("importance", 0.5),
                    "emotion_intensity": metadata.get("emotion_intensity", 0.5),
                    "emotion_type": metadata.get("emotion_type", "neutre"),
                    "similarity": similarity,
                    "timestamp": metadata.get("timestamp"),
                    "metadata": metadata.get("metadata", {})
                }
                memories.append(memory)
        
        # Trier par importance * similarité
        memories.sort(key=lambda x: x["importance"] * x["similarity"], reverse=True)
        
        return memories[:k or config.MEMORY_RETRIEVAL_K]
    
    def get_all_memories(self, limit: int = 100) -> List[Dict]:
        """Récupère tous les souvenirs (limité)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, text, importance, emotion_intensity, emotion_type, timestamp
            FROM memories
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memories.append({
                "id": row[0],
                "text": row[1],
                "importance": row[2],
                "emotion_intensity": row[3],
                "emotion_type": row[4],
                "timestamp": row[5]
            })
        
        return memories
    
    def delete_memory(self, memory_id: int) -> bool:
        """Supprime un souvenir."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer le vector_id
        cursor.execute("SELECT vector_id FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        
        if row:
            # Supprimer de SQLite
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            # Note: La suppression de FAISS est plus complexe, on laisse pour l'instant
            conn.close()
            return True
        
        conn.close()
        return False
    
    def get_memory_count(self) -> int:
        """Retourne le nombre total de souvenirs."""
        return self.vector_store.get_memory_count()
