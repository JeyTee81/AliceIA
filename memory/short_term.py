"""
Mémoire à court terme.
Gère le contexte conversationnel récent.
"""

from typing import List, Dict, Any
from datetime import datetime
from collections import deque
import config


class ShortTermMemory:
    """
    Mémoire à court terme pour le contexte conversationnel.
    Stocke les interactions récentes et les états émotionnels.
    """
    
    def __init__(self):
        self.max_size = config.MAX_SHORT_TERM_MEMORY
        self.conversation_history: deque = deque(maxlen=self.max_size)
        self.recent_emotions: deque = deque(maxlen=10)
        self.current_topic: str = ""
    
    def add_interaction(
        self,
        user_message: str,
        ai_response: str,
        emotion: Dict[str, float] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Ajoute une interaction à la mémoire court terme.
        
        Args:
            user_message: Message de l'utilisateur
            ai_response: Réponse de l'IA
            emotion: État émotionnel associé
            metadata: Métadonnées supplémentaires
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "ai": ai_response,
            "emotion": emotion or {},
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(interaction)
        
        if emotion:
            self.recent_emotions.append({
                "timestamp": datetime.now().isoformat(),
                "emotion": emotion
            })
    
    def get_recent_context(self, n: int = None) -> List[Dict]:
        """
        Récupère les n dernières interactions.
        
        Args:
            n: Nombre d'interactions (par défaut: toutes)
        
        Returns:
            Liste des interactions récentes
        """
        if n is None:
            return list(self.conversation_history)
        return list(self.conversation_history)[-n:]
    
    def get_conversation_messages(self) -> List[Dict[str, str]]:
        """
        Retourne l'historique au format messages pour le LLM.
        Format: [{"role": "user", "content": "..."}, ...]
        """
        messages = []
        for interaction in self.conversation_history:
            messages.append({
                "role": "user",
                "content": interaction["user"]
            })
            messages.append({
                "role": "assistant",
                "content": interaction["ai"]
            })
        return messages
    
    def get_recent_emotions(self, n: int = 5) -> List[Dict]:
        """Récupère les n dernières émotions."""
        return list(self.recent_emotions)[-n:]
    
    def set_topic(self, topic: str):
        """Définit le sujet de conversation actuel."""
        self.current_topic = topic
    
    def get_topic(self) -> str:
        """Retourne le sujet de conversation actuel."""
        return self.current_topic
    
    def clear(self):
        """Efface la mémoire court terme."""
        self.conversation_history.clear()
        self.recent_emotions.clear()
        self.current_topic = ""
