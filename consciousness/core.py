"""
Core Consciousness
Orchestrateur central de l'IA.
Gère le cycle perception → émotion → mémoire → raisonnement → réponse.
"""

from typing import Dict
import uuid

from consciousness.state import ConsciousnessState
from emotion.emotion_engine import EmotionEngine
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from learning.interaction_learning import InteractionLearning
from reasoning.thinker import Thinker
from reasoning.prompt_builder import PromptBuilder
from llm.local_llm import LocalLLM

import config


class CoreConsciousness:
    """
    Cerveau central.
    Toute décision cognitive transite par cette classe.
    """

    def __init__(self):
        # --- State ---
        self.state = ConsciousnessState()
        self.state.session_id = str(uuid.uuid4())
        self.state.personality = config.DEFAULT_PERSONALITY.copy()

        # --- Engines ---
        self.emotion_engine = EmotionEngine()
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.learning_engine = InteractionLearning(config.DB_PATH)
        self.thinker = Thinker()
        self.prompt_builder = PromptBuilder()
        self.llm = LocalLLM()

        # Charger l'état émotionnel précédent si disponible
        self.emotion_engine.load(self.state.session_id)

        # Ne pas bloquer avec print en mode API - juste un warning silencieux
        # Le check_available() est déjà fait dans main.py/api_server.py
        if not self.llm.check_available():
            pass  # Warning déjà géré au niveau supérieur

    # ============================================================
    # MAIN INTERACTION
    # ============================================================

    def process_interaction(self, user_message: str) -> str:
        self.state.is_thinking = True

        # 1️⃣ ÉMOTION (TOUJOURS EN PREMIER)
        current_emotion = self.emotion_engine.process_interaction(user_message)
        self.state.current_emotion = current_emotion

        # 2️⃣ RÉCUPÉRATION MÉMOIRE ÉMOTIONNELLE
        relevant_memories = self.long_term_memory.retrieve_memories(
            query=user_message,
            k=config.MEMORY_RETRIEVAL_K
        )

        # 3️⃣ CONTEXTE COURT TERME (format messages pour LLM)
        # Contexte complet pour apprentissage continu
        context_messages = self.short_term_memory.get_conversation_messages()

        # 4️⃣ PROMPTS
        personality = self.thinker.get_personality()

        system_prompt = self.prompt_builder.build_system_prompt(
            emotion=current_emotion,
            personality=personality,
            stats={
                "interactions": self.state.total_interactions,
                "memories": self.state.total_memories,
            },
        )

        user_prompt = self.prompt_builder.build_user_prompt(
            user_message=user_message,
            memories=relevant_memories,
            emotion=current_emotion,
        )

        # 5️⃣ STYLE DE RÉPONSE (OPTIONNEL MAIS UTILE)
        response_style = self.thinker.calculate_response_style(current_emotion)

        # 6️⃣ GÉNÉRATION LLM
        try:
            ai_response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                context=context_messages,
                temperature=response_style.get("temperature", 0.7),
                max_tokens=response_style.get("max_tokens", 512),
            )
        except Exception as e:
            ai_response = f"Erreur lors de la génération: {e}"

        # 7️⃣ MÉMOIRE COURT TERME
        self.short_term_memory.add_interaction(
            user_message=user_message,
            ai_response=ai_response,
            emotion=current_emotion,
        )

        # 8️⃣ MÉMOIRE LONG TERME (ÉMOTIONNELLE)
        if self.thinker.should_store_memory(
            text=f"{user_message} | {ai_response}",
            emotion=current_emotion,
            interaction_type="normal",
        ):
            self.long_term_memory.store_memory(
                text=f"User: {user_message}\nAI: {ai_response}",
                emotion=current_emotion,
            )
            self.state.total_memories += 1

        # 9️⃣ APPRENTISSAGE
        self.learning_engine.record_interaction(
            user_message,
            ai_response,
            importance=current_emotion["intensity"],
        )

        # 🔟 PERSONNALITÉ
        self.thinker.update_personality_from_emotion(current_emotion)

        # 🔟+1️⃣ STATS
        self.state.total_interactions += 1
        self.state.is_thinking = False

        return ai_response

    # ============================================================
    # TEACH MODE
    # ============================================================

    def teach(self, content: str, importance: float = 0.7) -> str:
        self.state.is_learning = True

        current_emotion = self.emotion_engine.process_interaction(content)

        teaching_prompt = self.prompt_builder.build_teaching_prompt(content)

        system_prompt = self.prompt_builder.build_system_prompt(
            emotion=current_emotion,
            personality=self.thinker.get_personality(),
            stats={
                "interactions": self.state.total_interactions,
                "memories": self.state.total_memories,
            },
        )

        try:
            response = self.llm.generate(
                prompt=teaching_prompt,
                system_prompt=system_prompt,
                temperature=0.6,
            )
        except Exception as e:
            response = f"Information enregistrée (erreur LLM: {e})"

        self.long_term_memory.store_memory(
            text=content,
            emotion=current_emotion,
        )

        self.learning_engine.record_interaction(
            f"Teaching: {content}",
            response,
            importance=importance,
        )

        self.state.total_memories += 1
        self.state.total_interactions += 1
        self.state.is_learning = False

        return response

    # ============================================================
    # CORRECTION MODE
    # ============================================================

    def correct(self, user_input: str, correction: str) -> str:
        current_emotion = self.emotion_engine.process_interaction(correction)

        learning_prompt = self.prompt_builder.build_learning_prompt(
            user_input,
            "",
            correction,
        )

        system_prompt = self.prompt_builder.build_system_prompt(
            emotion=current_emotion,
            personality=self.thinker.get_personality(),
            stats={
                "interactions": self.state.total_interactions,
                "memories": self.state.total_memories,
            },
        )

        try:
            response = self.llm.generate(
                prompt=learning_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
            )
        except Exception as e:
            response = f"Correction enregistrée (erreur LLM: {e})"

        self.long_term_memory.store_memory(
            text=f"Correction: {correction} (pour: {user_input})",
            emotion=current_emotion,
        )

        self.learning_engine.record_interaction(
            user_input,
            correction,
            importance=0.8,
        )

        self.state.total_memories += 1
        self.state.total_interactions += 1

        return response

    # ============================================================
    # STATUS & SAVE
    # ============================================================

    def get_status(self) -> Dict:
        return {
            "state": self.state.to_dict(),
            "emotion": self.emotion_engine.get_state(),
            "personality": self.thinker.get_personality(),
            "memory": {
                "short_term": len(self.short_term_memory.get_recent_context()),
                "long_term": self.long_term_memory.get_memory_count(),
            },
            "llm_available": self.llm.check_available(),
        }

    def save_state(self):
        self.emotion_engine.save(self.state.session_id)
