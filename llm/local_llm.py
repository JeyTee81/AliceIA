"""
Interface avec Ollama pour les LLM locaux.
Gère la communication avec le serveur Ollama local.
"""

import ollama
from typing import List, Dict, Optional
import signal
import sys
import config


class LocalLLM:
    """
    Interface pour communiquer avec Ollama (LLM local).
    Aucun appel réseau externe, uniquement localhost.
    """
    
    def __init__(self, model: str = None):
        self.model = model or config.DEFAULT_MODEL
        self.base_url = config.OLLAMA_BASE_URL
    
    def generate(
        self,
        prompt: str,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        system_prompt: str = "",
        context: List[Dict] = None
    ) -> str:
        """
        Génère une réponse à partir d'un prompt.
        
        Args:
            prompt: Le prompt utilisateur
            temperature: Contrôle la créativité (0.0-1.0)
            top_p: Contrôle la diversité (0.0-1.0)
            max_tokens: Nombre maximum de tokens
            system_prompt: Prompt système pour définir le comportement
            context: Historique de conversation (format messages)
        
        Returns:
            La réponse générée
        """
        temperature = temperature or config.DEFAULT_TEMPERATURE
        top_p = top_p or config.DEFAULT_TOP_P
        max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
        
        # Construire les messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Ajouter le contexte conversationnel
        # Le contexte doit être au format [{"role": "user", "content": "..."}, ...]
        if context:
            # Filtrer et valider le format des messages
            for msg in context:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({
                        "role": msg["role"],
                        "content": str(msg["content"])
                    })
        
        # Ajouter le prompt actuel
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Pas de limitation du contexte - l'IA doit pouvoir apprendre en continu
            # Le contexte complet est préservé pour une compréhension sans limite
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens
                }
            )
            
            content = response.get('message', {}).get('content', '')
            if not content:
                return "Désolé, je n'ai pas pu générer de réponse."
            
            return content
        
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return "Désolé, la génération a pris trop de temps. Essayez avec un message plus court."
            raise Exception(f"Erreur lors de la génération LLM: {e}")
    
    def list_models(self) -> List[str]:
        """Liste les modèles disponibles localement."""
        try:
            models = ollama.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            # Ne pas utiliser print() qui peut bloquer - utiliser logging si nécessaire
            # print(f"Erreur lors de la liste des modèles: {e}")
            return []
    
    def check_available(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            ollama.list()
            return True
        except:
            return False
    
    def set_model(self, model: str):
        """Change le modèle utilisé."""
        self.model = model
