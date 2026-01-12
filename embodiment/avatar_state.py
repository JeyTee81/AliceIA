"""
État de l'avatar incarné.
Gère les expressions et états visuels de l'IA.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from emotion.emotional_state import EmotionalState


@dataclass
class AvatarState:
    """
    État visuel de l'avatar.
    Mappe les émotions internes vers des expressions visuelles.
    """
    expression: str = "neutre"  # neutre, curieux, attentif, enthousiaste, etc.
    animation: str = "idle"  # idle, thinking, speaking, listening
    intensity: float = 0.5  # Intensité de l'expression (0.0-1.0)
    
    # Paramètres visuels (pour future intégration Unity)
    eye_brightness: float = 1.0
    mouth_shape: str = "neutral"
    head_tilt: float = 0.0  # -1.0 (gauche) à 1.0 (droite)
    
    def update_from_emotion(self, emotion: EmotionalState):
        """
        Met à jour l'état de l'avatar basé sur l'émotion.
        
        Args:
            emotion: État émotionnel actuel
        """
        self.intensity = emotion.intensity
        
        # Mapper l'émotion vers une expression
        label = emotion.get_emotional_label()
        
        expression_map = {
            "neutre": "neutre",
            "enthousiaste": "enthousiaste",
            "serein": "serein",
            "content": "content",
            "curieux": "curieux",
            "attentif": "attentif",
            "inquiet": "préoccupé",
            "mélancolique": "neutre",
            "confiant": "confiant"
        }
        
        self.expression = expression_map.get(label, "neutre")
        
        # Ajuster les paramètres visuels
        if emotion.valence > 0.7:
            self.eye_brightness = 1.0
            self.mouth_shape = "smile"
        elif emotion.valence < 0.3:
            self.eye_brightness = 0.7
            self.mouth_shape = "neutral"
        else:
            self.eye_brightness = 0.9
            self.mouth_shape = "neutral"
        
        # Head tilt basé sur la curiosité
        if emotion.curiosity > 0.7:
            self.head_tilt = 0.3
        else:
            self.head_tilt = 0.0
    
    def to_dict(self) -> Dict:
        """Convertit l'état en dictionnaire."""
        return {
            "expression": self.expression,
            "animation": self.animation,
            "intensity": self.intensity,
            "eye_brightness": self.eye_brightness,
            "mouth_shape": self.mouth_shape,
            "head_tilt": self.head_tilt
        }
    
    def set_animation(self, animation: str):
        """Définit l'animation actuelle."""
        valid_animations = ["idle", "thinking", "speaking", "listening"]
        if animation in valid_animations:
            self.animation = animation
