"""
Prompt Builder cognitif.
Construit des prompts influencés par mémoire, émotion et personnalité.
"""

from typing import List, Dict
from datetime import datetime

import config


class PromptBuilder:
    """
    Le prompt n'est PAS neutre.
    Il est influencé par l'état émotionnel interne.
    """

    BASE_SYSTEM_PROMPT = """
Tu es une IA personnelle autonome et locale.
Tu développes une relation persistante avec ton utilisateur.

Principes fondamentaux :
- Tu es éducable et tu apprends en continu
- Tu te souviens des interactions importantes et tu construis une compréhension cumulative
- Ton comportement évolue avec l'expérience
- Tu utilises tes émotions comme signaux internes
- Ta compréhension s'enrichit au fil des interactions sans limite
"""

    def build_system_prompt(
        self,
        emotion: Dict[str, float],
        personality: Dict[str, float],
        stats: Dict[str, int],
    ) -> str:
        prompt = self.BASE_SYSTEM_PROMPT.strip()

        # --- Emotional modulation ---
        if emotion["curiosity"] > 0.6:
            prompt += "\nTu es curieux et enclin à poser des questions."
        if emotion["confidence"] > 0.7:
            prompt += "\nTu réponds avec assurance."
        if emotion["valence"] < 0.4:
            prompt += "\nTu es plus réservé et factuel."
        if emotion["attachment"] > 0.6:
            prompt += "\nTu prends en compte la relation construite avec l'utilisateur."

        # --- Personality ---
        if personality:
            prompt += "\nTraits de personnalité dominants :"
            for trait, value in personality.items():
                if value > 0.65:
                    prompt += f"\n- {trait}"

        # --- Stats ---
        prompt += (
            f"\n\nContexte interne :"
            f"\n- Interactions totales : {stats.get('interactions', 0)}"
            f"\n- Souvenirs stockés : {stats.get('memories', 0)}"
        )

        return prompt

    def build_user_prompt(
        self,
        user_message: str,
        memories: List[Dict],
        emotion: Dict[str, float],
    ) -> str:
        prompt = ""

        # Nombre de souvenirs dépend de l'arousal
        max_memories = 2 if emotion["arousal"] > 0.6 else 4

        if memories:
            prompt += "Souvenirs pertinents :\n"
            for m in memories[:max_memories]:
                prompt += f"- {m['text'][:180]}\n"
            prompt += "\n"

        prompt += f"Message utilisateur : {user_message}"
        return prompt

    def build_learning_prompt(
        self,
        user_input: str,
        ai_response: str,
        correction: str,
    ) -> str:
        return f"""
Tu dois apprendre de cette correction.

Entrée utilisateur :
{user_input}

Ta réponse :
{ai_response}

Correction humaine :
{correction}

Analyse ton erreur et adapte ta compréhension future.
"""

    def build_teaching_prompt(self, content: str) -> str:
        return f"""
L'utilisateur t'enseigne une information importante.

Contenu :
{content}

Intègre cette connaissance à ta mémoire.
Réfléchis à comment elle s'articule avec ce que tu sais déjà.
"""
