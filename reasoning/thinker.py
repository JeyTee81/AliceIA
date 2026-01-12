"""
Moteur de raisonnement et personnalité.
Gère la logique de décision et l'évolution de la personnalité.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

import config


class Thinker:
    """
    Moteur de raisonnement qui combine:
    - Mémoire factuelle
    - Mémoire émotionnelle
    - Personnalité
    - Logique de décision
    """
    
    def __init__(self):
        self.personality = dict(config.DEFAULT_PERSONALITY)
        self.personality_file = Path(config.DATA_DIR) / "personality.json"
        self._load_personality()
    
    def _load_personality(self):
        """Charge la personnalité depuis le disque."""
        if self.personality_file.exists():
            try:
                with open(self.personality_file, 'r', encoding='utf-8') as f:
                    self.personality = json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement de la personnalité: {e}")
                self.personality = dict(config.DEFAULT_PERSONALITY)
    
    def _save_personality(self):
        """Sauvegarde la personnalité sur le disque."""
        try:
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la personnalité: {e}")
    
    def get_personality(self) -> Dict[str, float]:
        """Retourne la personnalité actuelle."""
        return self.personality.copy()
    
    def update_personality_from_emotion(self, emotion: Dict[str, float], weight: float = 0.01):
        """
        Met à jour la personnalité basée sur les émotions cumulées.
        
        Args:
            emotion: État émotionnel
            weight: Poids de l'influence (faible pour évolution lente)
        """
        # L'émotion influence la personnalité progressivement
        valence = emotion.get("valence", 0.5)
        arousal = emotion.get("arousal", 0.5)
        confidence = emotion.get("confidence", 0.5)
        
        # Valence influence agreeableness et neuroticism
        if valence > 0.6:
            self.personality["agreeableness"] = min(1.0, 
                self.personality["agreeableness"] + weight)
            self.personality["neuroticism"] = max(0.0,
                self.personality["neuroticism"] - weight * 0.5)
        
        # Arousal influence extraversion
        if arousal > 0.6:
            self.personality["extraversion"] = min(1.0,
                self.personality["extraversion"] + weight)
        
        # Confidence influence openness
        if confidence > 0.6:
            self.personality["openness"] = min(1.0,
                self.personality["openness"] + weight)
        
        self._save_personality()
    
    def calculate_response_style(self, emotion: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule le style de réponse basé sur personnalité et émotion.
        
        Returns:
            Paramètres de style (température, longueur, ton)
        """
        # Température basée sur extraversion et arousal
        extraversion = self.personality.get("extraversion", 0.5)
        arousal = emotion.get("arousal", 0.5)
        temperature = 0.5 + (extraversion * 0.2) + ((arousal - 0.5) * 0.1)
        temperature = max(0.3, min(1.0, temperature))
        
        # Longueur basée sur openness et curiosity
        openness = self.personality.get("openness", 0.5)
        curiosity = emotion.get("curiosity", 0.5)
        max_tokens = int(500 + (openness + curiosity) * 1000)  # 500-2000 tokens
        max_tokens = min(max_tokens, 2048)  # Limite raisonnable mais généreuse
        
        return {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "verbosity": openness + curiosity
        }
    
    def decide_memory_importance(
        self,
        text: str,
        emotion: Dict[str, float],
        interaction_type: str = "normal"
    ) -> float:
        """
        Détermine l'importance d'un souvenir pour le stockage.
        
        Args:
            text: Le contenu du souvenir
            emotion: État émotionnel associé
            interaction_type: Type d'interaction (normal, teaching, correction)
        
        Returns:
            Score d'importance (0.0-1.0)
        """
        importance = 0.5  # Base
        
        # Importance basée sur l'émotion
        emotion_intensity = emotion.get("intensity", 0.5)
        importance += emotion_intensity * 0.2
        
        # Importance basée sur le type d'interaction
        if interaction_type == "teaching":
            importance += 0.3
        elif interaction_type == "correction":
            importance += 0.25
        elif interaction_type == "important":
            importance += 0.2
        
        # Importance basée sur la longueur (messages longs = plus importants)
        if len(text) > 100:
            importance += 0.1
        elif len(text) < 20:
            importance -= 0.1
        
        # Importance basée sur la confiance
        confidence = emotion.get("confidence", 0.5)
        if confidence > 0.7:
            importance += 0.1
        
        return max(0.0, min(1.0, importance))
    
    def should_store_memory(
        self,
        text: str,
        emotion: Dict[str, float],
        interaction_type: str = "normal"
    ) -> bool:
        """Détermine si un souvenir doit être stocké."""
        importance = self.decide_memory_importance(text, emotion, interaction_type)
        return importance >= config.MIN_MEMORY_IMPORTANCE
    
    def analyze_topic(self, messages: List[str]) -> Optional[str]:
        """
        Analyse les messages pour identifier le sujet de conversation.
        Simple extraction de mots-clés fréquents.
        """
        if not messages:
            return None
        
        # Concaténer les messages
        text = " ".join(messages).lower()
        
        # Mots à ignorer
        stop_words = {"le", "la", "les", "un", "une", "des", "de", "du", "et", "ou",
                     "est", "sont", "a", "as", "ont", "je", "tu", "il", "nous", "vous"}
        
        # Extraire les mots significatifs
        words = [w for w in text.split() if len(w) > 3 and w not in stop_words]
        
        if not words:
            return None
        
        # Compter les fréquences
        from collections import Counter
        word_freq = Counter(words)
        
        # Retourner les 2-3 mots les plus fréquents
        top_words = [word for word, _ in word_freq.most_common(3)]
        return " ".join(top_words)
