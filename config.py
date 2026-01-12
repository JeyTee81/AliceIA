"""
Configuration globale de l'IA personnelle autonome.
Toutes les configurations sont locales et modifiables.
"""

import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MEMORIES_DIR = DATA_DIR / "memories"
EMOTIONS_DIR = DATA_DIR / "emotions"
DB_PATH = DATA_DIR / "memory.db"
VECTORS_PATH = DATA_DIR / "vectors.faiss"

# Création des dossiers si nécessaire
DATA_DIR.mkdir(exist_ok=True)
MEMORIES_DIR.mkdir(exist_ok=True)
EMOTIONS_DIR.mkdir(exist_ok=True)

# Configuration Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"  # Modèles supportés: llama3, mistral, qwen
OLLAMA_TIMEOUT = 120  # Timeout en secondes pour les requêtes Ollama

# Configuration LLM
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 1024  # Permet des réponses complètes tout en restant raisonnable

# Configuration embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modèle local sentence-transformers
EMBEDDING_DIM = 384

# Configuration mémoire
MAX_SHORT_TERM_MEMORY = 20  # Nombre de messages en mémoire court terme
MEMORY_RETRIEVAL_K = 5  # Nombre de souvenirs à récupérer
MIN_MEMORY_IMPORTANCE = 0.3  # Seuil d'importance minimale pour stockage

# Configuration émotionnelle
EMOTION_DECAY_RATE = 0.95  # Taux de décroissance émotionnelle par cycle
EMOTION_INTENSITY_THRESHOLD = 0.5  # Seuil d'intensité pour déclencher stockage

# Configuration personnalité
DEFAULT_PERSONALITY = {
    "openness": 0.7,
    "conscientiousness": 0.6,
    "extraversion": 0.5,
    "agreeableness": 0.8,
    "neuroticism": 0.3
}

# Configuration apprentissage
LEARNING_ENABLED = True
REQUIRE_HUMAN_VALIDATION = True  # Validation humaine pour apprentissage critique

# Configuration API (pour Unity)
API_HOST = "localhost"
API_PORT = 5000
