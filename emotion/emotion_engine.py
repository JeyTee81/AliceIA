"""
Moteur émotionnel cognitif.
Génère, fait évoluer et exploite un état émotionnel interne.
Les émotions influencent la mémoire, le raisonnement et l'interaction.
"""

from dataclasses import dataclass
from typing import Dict
from datetime import datetime
import json
from pathlib import Path

import config


@dataclass
class EmotionalSnapshot:
    timestamp: str
    valence: float
    arousal: float
    dominance: float
    confidence: float
    curiosity: float
    attachment: float
    intensity: float
    trigger: str


class EmotionEngine:
    """
    Moteur émotionnel opérant.
    Les émotions sont :
    - persistantes
    - cumulatives
    - décroissantes
    - exploitables par la mémoire
    """

    def __init__(self):
        self.state = {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.5,
            "confidence": 0.5,
            "curiosity": 0.4,
            "attachment": 0.2,
        }
        self.history: list[EmotionalSnapshot] = []

        self.emotions_dir = Path(config.EMOTIONS_DIR)
        self.emotions_dir.mkdir(exist_ok=True)

    # ----------------------------
    # Core
    # ----------------------------

    def process_interaction(self, user_message: str) -> Dict[str, float]:
        """
        Analyse une interaction utilisateur et met à jour l'état émotionnel.
        """
        msg = user_message.lower()

        # Décroissance naturelle
        self._apply_decay()

        # Signaux simples mais cumulables
        self._update_valence(msg)
        self._update_arousal(msg)
        self._update_dominance(msg)
        self._update_curiosity(msg)

        # Attachement progresse lentement avec l'interaction
        self.state["attachment"] = min(1.0, self.state["attachment"] + 0.03)

        intensity = self._calculate_intensity()

        snapshot = EmotionalSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            trigger=user_message[:120],
            intensity=intensity,
            **self.state,
        )

        self.history.append(snapshot)
        self.history = self.history[-200:]

        return self.get_state()

    # ----------------------------
    # Emotion updates
    # ----------------------------

    def _update_valence(self, msg: str):
        positive = ["merci", "bien", "super", "parfait", "excellent", "bravo"]
        negative = ["faux", "erreur", "non", "stop", "nul", "mauvais"]

        pos = sum(w in msg for w in positive)
        neg = sum(w in msg for w in negative)

        self.state["valence"] = self._clamp(
            self.state["valence"] + 0.15 * pos - 0.2 * neg
        )

        self.state["confidence"] = self._clamp(
            self.state["confidence"] + 0.1 * pos - 0.15 * neg
        )

    def _update_arousal(self, msg: str):
        if "?" in msg or any(w in msg for w in ["pourquoi", "comment"]):
            self.state["arousal"] = self._clamp(self.state["arousal"] + 0.15)

        if "!" in msg:
            self.state["arousal"] = self._clamp(self.state["arousal"] + 0.2)

    def _update_dominance(self, msg: str):
        directives = ["fais", "explique", "montre", "apprends", "crée"]
        if any(w in msg for w in directives):
            self.state["dominance"] = self._clamp(self.state["dominance"] + 0.1)

    def _update_curiosity(self, msg: str):
        if len(msg.split()) > 12:
            self.state["curiosity"] = self._clamp(self.state["curiosity"] + 0.1)

    # ----------------------------
    # Utils
    # ----------------------------

    def _apply_decay(self):
        self.state["arousal"] *= 0.85
        self.state["confidence"] *= 0.95
        self.state["curiosity"] *= 0.9
        self.state["valence"] = 0.5 + (self.state["valence"] - 0.5) * 0.9
        self.state["dominance"] *= 0.97
        # attachement décroit très lentement
        self.state["attachment"] *= 0.995

    def _calculate_intensity(self) -> float:
        return round(
            (
                abs(self.state["valence"] - 0.5)
                + self.state["arousal"]
                + self.state["curiosity"]
            )
            / 3,
            3,
        )

    def get_state(self) -> Dict[str, float]:
        """Retourne l'état émotionnel avec l'intensité calculée."""
        state = {k: round(v, 3) for k, v in self.state.items()}
        state["intensity"] = self._calculate_intensity()
        # Déterminer le label émotionnel
        if state["intensity"] < 0.3:
            state["label"] = "neutre"
        elif state["valence"] > 0.7:
            if state["arousal"] > 0.7:
                state["label"] = "enthousiaste"
            elif state["arousal"] < 0.3:
                state["label"] = "serein"
            else:
                state["label"] = "content"
        elif state["valence"] < 0.3:
            if state["arousal"] > 0.7:
                state["label"] = "inquiet"
            elif state["arousal"] < 0.3:
                state["label"] = "mélancolique"
            else:
                state["label"] = "préoccupé"
        else:
            if state["curiosity"] > 0.7:
                state["label"] = "curieux"
            elif state["confidence"] > 0.7:
                state["label"] = "confiant"
            else:
                state["label"] = "attentif"
        return state

    def _clamp(self, v: float) -> float:
        return max(0.0, min(1.0, v))

    # ----------------------------
    # Persistence
    # ----------------------------

    def save(self, session_id: str):
        path = self.emotions_dir / f"emotion_{session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "state": self.state,
                    "history": [s.__dict__ for s in self.history],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
    
    def load(self, session_id: str) -> bool:
        """
        Charge l'état émotionnel sauvegardé.
        
        Args:
            session_id: ID de la session
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        path = self.emotions_dir / f"emotion_{session_id}.json"
        if not path.exists():
            return False
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "state" in data:
                self.state.update(data["state"])
            
            if "history" in data:
                self.history = [
                    EmotionalSnapshot(**snapshot) for snapshot in data["history"]
                ]
            
            return True
        except Exception as e:
            print(f"Erreur lors du chargement des émotions: {e}")
            return False