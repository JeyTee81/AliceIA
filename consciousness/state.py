"""
État global de la conscience de l'IA.
Gère l'état interne de l'entité cognitive.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class ConversationContext:
    """Contexte de la conversation actuelle."""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    topic: str = ""
    emotional_context: Dict[str, float] = field(default_factory=dict)


@dataclass
class ConsciousnessState:
    """
    État global de la conscience de l'IA.
    Contient toutes les informations sur l'état actuel de l'entité.
    """
    # Identité
    name: str = "IA Personnelle"
    session_id: str = ""
    
    # Contexte conversationnel
    current_conversation: ConversationContext = field(default_factory=ConversationContext)
    
    # État émotionnel actuel
    current_emotion: Dict[str, float] = field(default_factory=dict)
    
    # État de la personnalité
    personality: Dict[str, float] = field(default_factory=dict)
    
    # Statistiques
    total_interactions: int = 0
    total_memories: int = 0
    session_start: datetime = field(default_factory=datetime.now)
    
    # État système
    is_learning: bool = False
    is_thinking: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'état en dictionnaire pour sérialisation."""
        return {
            "name": self.name,
            "session_id": self.session_id,
            "total_interactions": self.total_interactions,
            "total_memories": self.total_memories,
            "current_emotion": self.current_emotion,
            "personality": self.personality,
            "is_learning": self.is_learning,
            "session_start": self.session_start.isoformat()
        }
