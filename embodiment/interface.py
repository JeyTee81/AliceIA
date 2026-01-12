"""
Interface d'incarnation pour l'avatar.
Prévu pour intégration future avec Unity ou autres systèmes 3D.
"""

from typing import Optional
from emotion.emotional_state import EmotionalState
from embodiment.avatar_state import AvatarState


class EmbodimentInterface:
    """
    Interface pour l'incarnation de l'IA.
    Actuellement en mode texte, mais extensible vers Unity/3D.
    """
    
    def __init__(self):
        self.avatar_state = AvatarState()
        self.enabled = False  # Désactivé par défaut (mode CLI)
    
    def update(self, emotion: EmotionalState, is_thinking: bool = False):
        """
        Met à jour l'état de l'avatar basé sur l'émotion et l'état cognitif.
        
        Args:
            emotion: État émotionnel actuel
            is_thinking: Si l'IA est en train de réfléchir
        """
        if not self.enabled:
            return
        
        self.avatar_state.update_from_emotion(emotion)
        
        if is_thinking:
            self.avatar_state.set_animation("thinking")
        else:
            self.avatar_state.set_animation("idle")
    
    def get_avatar_state(self) -> AvatarState:
        """Retourne l'état actuel de l'avatar."""
        return self.avatar_state
    
    def enable(self):
        """Active l'interface d'incarnation."""
        self.enabled = True
    
    def disable(self):
        """Désactive l'interface d'incarnation."""
        self.enabled = False
    
    def render_text_avatar(self, emotion: EmotionalState) -> str:
        """
        Rend une représentation texte de l'avatar.
        Utile pour le mode CLI avec feedback visuel.
        
        Args:
            emotion: État émotionnel
        
        Returns:
            Représentation texte de l'avatar
        """
        label = emotion.get_emotional_label()
        intensity = emotion.intensity
        
        # Emojis basés sur l'émotion
        emoji_map = {
            "neutre": "😐",
            "enthousiaste": "😊",
            "serein": "😌",
            "content": "🙂",
            "curieux": "🤔",
            "attentif": "👂",
            "inquiet": "😟",
            "mélancolique": "😔",
            "confiant": "😎"
        }
        
        emoji = emoji_map.get(label, "🤖")
        
        # Barre d'intensité
        intensity_bar = "█" * int(intensity * 10) + "░" * (10 - int(intensity * 10))
        
        return f"""
╔═══════════════════════════════╗
║  Avatar IA: {emoji} {label:12s}  ║
║  Intensité: [{intensity_bar}]  ║
║  Confiance: {emotion.confidence:.2f}  ║
║  Curiosité: {emotion.curiosity:.2f}  ║
╚═══════════════════════════════╝
"""
