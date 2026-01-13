"""
Thinker
Moteur de raisonnement, personnalité et instinct mémoriel.
"""

from typing import Dict, List, Optional
import json
from pathlib import Path
import math

import config


class Thinker:
    """
    Cortex décisionnel.
    """

    def __init__(self):
        self.personality = dict(config.DEFAULT_PERSONALITY)
        self.personality_file = Path(config.DATA_DIR) / "personality.json"
        self._load_personality()

    # --------------------------------------------------
    # PERSONALITY
    # --------------------------------------------------

    def _load_personality(self):
        if self.personality_file.exists():
            try:
                with open(self.personality_file, "r", encoding="utf-8") as f:
                    self.personality = json.load(f)
            except Exception:
                self.personality = dict(config.DEFAULT_PERSONALITY)

    def _save_personality(self):
        with open(self.personality_file, "w", encoding="utf-8") as f:
            json.dump(self.personality, f, indent=2)

    def get_personality(self) -> Dict[str, float]:
        return self.personality.copy()

    def update_personality_from_emotion(self, emotion: Dict, weight: float = 0.005):
        """
        Évolution lente et irréversible de la personnalité.
        """
        valence = emotion.get("valence", 0.5)
        arousal = emotion.get("arousal", 0.5)
        dominance = emotion.get("dominance", 0.5)

        # Valence → agreeableness / neuroticism
        self.personality["agreeableness"] += (valence - 0.5) * weight
        self.personality["neuroticism"] -= (valence - 0.5) * weight

        # Arousal → extraversion
        self.personality["extraversion"] += (arousal - 0.5) * weight

        # Dominance → openness / confidence cognitive
        self.personality["openness"] += (dominance - 0.5) * weight

        # Clamp
        for k in self.personality:
            self.personality[k] = max(0.0, min(1.0, self.personality[k]))

        self._save_personality()

    # --------------------------------------------------
    # RESPONSE STYLE
    # --------------------------------------------------

    def calculate_response_style(self, emotion: Dict) -> Dict[str, float]:
        extraversion = self.personality.get("extraversion", 0.5)
        openness = self.personality.get("openness", 0.5)

        arousal = emotion.get("arousal", 0.5)
        intensity = emotion.get("intensity", 0.5)

        temperature = 0.4 + extraversion * 0.3 + arousal * 0.2
        temperature = max(0.3, min(1.0, temperature))

        max_tokens = int(400 + (openness + intensity) * 900)
        max_tokens = min(max_tokens, 2048)

        return {
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    # --------------------------------------------------
    # MEMORY INSTINCT
    # --------------------------------------------------

    def should_store_memory(self, emotion: Dict) -> bool:
        """
        Décision instinctive.
        """
        intensity = emotion.get("intensity", 0.5)
        dominance = emotion.get("dominance", 0.5)

        threshold = config.MIN_MEMORY_IMPORTANCE

        # Plus l'émotion est forte, plus le souvenir est gravé
        instinct_score = (intensity * 0.7) + (dominance * 0.3)

        return instinct_score >= threshold

    def decide_memory_importance(self, emotion: Dict) -> float:
        """
        Importance ressentie, pas raisonnée.
        """
        intensity = emotion.get("intensity", 0.5)
        dominance = emotion.get("dominance", 0.5)

        importance = (intensity * 0.6) + (dominance * 0.4)
        return max(0.0, min(1.0, importance))

    # --------------------------------------------------
    # TOPIC ANALYSIS
    # --------------------------------------------------

    def analyze_topic(self, messages: List[str]) -> Optional[str]:
        if not messages:
            return None

        text = " ".join(messages).lower()
        words = [w for w in text.split() if len(w) > 3]

        if not words:
            return None

        from collections import Counter
        common = Counter(words).most_common(3)
        return " ".join([w for w, _ in common])
