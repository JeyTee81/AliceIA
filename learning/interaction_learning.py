"""
Système d'apprentissage par interaction humaine.
L'IA apprend à partir des échanges et corrections.
"""

from typing import Dict, Optional
from datetime import datetime
import sqlite3
from pathlib import Path

import config


class InteractionLearning:
    """
    Moteur d'apprentissage à partir des interactions humaines.
    L'IA apprend parce que l'utilisateur interagit avec elle.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialise les tables d'apprentissage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                ai_response TEXT,
                correction TEXT,
                validated INTEGER DEFAULT 0,
                importance REAL DEFAULT 0.5,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Ajouter la colonne importance si elle n'existe pas (migration)
        try:
            cursor.execute("ALTER TABLE learning_interactions ADD COLUMN importance REAL DEFAULT 0.5")
        except sqlite3.OperationalError:
            pass  # La colonne existe déjà
        
        conn.commit()
        conn.close()
    
    def record_interaction(
        self,
        user_input: str,
        ai_response: str = None,
        correction: str = None,
        importance: float = 0.5
    ) -> int:
        """
        Enregistre une interaction d'apprentissage.
        
        Args:
            user_input: L'entrée de l'utilisateur
            ai_response: La réponse de l'IA (si disponible)
            correction: Correction de l'utilisateur (si applicable)
            importance: Importance de cette interaction (0.0-1.0)
        
        Returns:
            L'ID de l'interaction enregistrée
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validated = 1 if correction else 0
        
        cursor.execute("""
            INSERT INTO learning_interactions
            (user_input, ai_response, correction, validated, importance, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_input,
            ai_response,
            correction,
            validated,
            importance,
            datetime.now().isoformat()
        ))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return interaction_id
    
    def validate_correction(self, interaction_id: int, validated: bool = True):
        """Marque une correction comme validée."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE learning_interactions
            SET validated = ?
            WHERE id = ?
        """, (1 if validated else 0, interaction_id))
        
        conn.commit()
        conn.close()
    
    def get_learning_history(self, limit: int = 50) -> list[Dict]:
        """Récupère l'historique d'apprentissage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_input, ai_response, correction, validated, importance, timestamp
            FROM learning_interactions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        interactions = []
        for row in rows:
            interactions.append({
                "id": row[0],
                "user_input": row[1],
                "ai_response": row[2],
                "correction": row[3],
                "validated": bool(row[4]),
                "importance": row[5],
                "timestamp": row[6]
            })
        
        return interactions
    
    def get_validated_corrections(self) -> list[Dict]:
        """Récupère toutes les corrections validées."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_input, correction, importance
            FROM learning_interactions
            WHERE validated = 1 AND correction IS NOT NULL
            ORDER BY importance DESC, timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        corrections = []
        for row in rows:
            corrections.append({
                "user_input": row[0],
                "correction": row[1],
                "importance": row[2]
            })
        
        return corrections
