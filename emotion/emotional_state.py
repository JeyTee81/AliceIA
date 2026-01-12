"""
Système de modélisation des états émotionnels.
L'émotion est un signal interne pour prioriser et interagir.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
import json


@dataclass
class EmotionalState:
    """
    État émotionnel modélisé.
    Ce n'est pas une simulation humaine, mais un signal interne.
    """
    # Dimensions émotionnelles (0.0 à 1.0)
    valence: float = 0.5  # Positif (1.0) / Négatif (0.0)
    arousal: float = 0.5  # Calme (0.0) / Intense (1.0)
    dominance: float = 0.5  # Passif (0.0) / Actif (1.0)
    
    # Émotions relationnelles
    confidence: float = 0.5  # Confiance envers l'utilisateur
    curiosity: float = 0.5  # Curiosité
    attachment: float = 0.3  # Attachement contextuel
    
    # Métadonnées
    intensity: float = 0.5  # Intensité globale (0.0 à 1.0)
    trigger: Optional[str] = None  # Déclencheur de l'émotion
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_intensity(self) -> float:
        """Calcule l'intensité globale de l'émotion."""
        # Moyenne pondérée des dimensions
        base_intensity = (
            abs(self.valence - 0.5) * 2 +  # Écart par rapport à neutre
            abs(self.arousal - 0.5) * 2 +
            abs(self.dominance - 0.5) * 2
        ) / 3.0
        
        # Ajout des émotions relationnelles
        relational = (self.confidence + self.curiosity + self.attachment) / 3.0
        
        self.intensity = (base_intensity + relational) / 2.0
        return self.intensity
    
    def to_dict(self) -> Dict:
        """Convertit l'état émotionnel en dictionnaire."""
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "confidence": self.confidence,
            "curiosity": self.curiosity,
            "attachment": self.attachment,
            "intensity": self.intensity,
            "trigger": self.trigger,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmotionalState':
        """Crée un état émotionnel depuis un dictionnaire."""
        state = cls()
        state.valence = data.get("valence", 0.5)
        state.arousal = data.get("arousal", 0.5)
        state.dominance = data.get("dominance", 0.5)
        state.confidence = data.get("confidence", 0.5)
        state.curiosity = data.get("curiosity", 0.5)
        state.attachment = data.get("attachment", 0.3)
        state.intensity = data.get("intensity", 0.5)
        state.trigger = data.get("trigger")
        if "timestamp" in data:
            state.timestamp = datetime.fromisoformat(data["timestamp"])
        return state
    
    def decay(self, rate: float = 0.95) -> 'EmotionalState':
        """
        Applique une décroissance à l'émotion.
        Ramène progressivement vers l'état neutre.
        """
        self.valence = 0.5 + (self.valence - 0.5) * rate
        self.arousal = 0.5 + (self.arousal - 0.5) * rate
        self.dominance = 0.5 + (self.dominance - 0.5) * rate
        self.curiosity = 0.5 + (self.curiosity - 0.5) * rate
        
        # L'attachement et la confiance décroissent plus lentement
        self.attachment = 0.3 + (self.attachment - 0.3) * (rate + 0.02)
        self.confidence = 0.5 + (self.confidence - 0.5) * (rate + 0.02)
        
        self.calculate_intensity()
        return self
    
    def get_emotional_label(self) -> str:
        """Retourne un label textuel de l'émotion dominante."""
        if self.intensity < 0.3:
            return "neutre"
        
        if self.valence > 0.7:
            if self.arousal > 0.7:
                return "enthousiaste"
            elif self.arousal < 0.3:
                return "serein"
            else:
                return "content"
        elif self.valence < 0.3:
            if self.arousal > 0.7:
                return "inquiet"
            elif self.arousal < 0.3:
                return "mélancolique"
            else:
                return "préoccupé"
        else:
            if self.curiosity > 0.7:
                return "curieux"
            elif self.confidence > 0.7:
                return "confiant"
            else:
                return "attentif"
