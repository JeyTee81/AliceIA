"""
Stockage vectoriel FAISS avec pondération émotionnelle.
Mémoire sémantique + affective.
"""

import faiss
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from sentence_transformers import SentenceTransformer
import pickle
import math

import config


class VectorStore:
    """
    Mémoire vectorielle émotionnelle.
    Les souvenirs sont rappelés selon :
    - similarité sémantique
    - proximité émotionnelle
    - intensité vécue
    """

    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.dimension = config.EMBEDDING_DIM
        self.index = None
        self.metadata: List[Dict] = []
        self.vectors_path = Path(config.VECTORS_PATH)
        self._initialize_index()

    # --------------------------------------------------
    # INITIALISATION
    # --------------------------------------------------

    def _initialize_index(self):
        if self.vectors_path.exists():
            self._load_index()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def _load_index(self):
        try:
            self.index = faiss.read_index(str(self.vectors_path))
            meta_path = self.vectors_path.with_suffix(".pkl")
            if meta_path.exists():
                with open(meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
        except Exception as e:
            print(f"Erreur chargement mémoire vectorielle: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def _save_index(self):
        faiss.write_index(self.index, str(self.vectors_path))
        with open(self.vectors_path.with_suffix(".pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    # --------------------------------------------------
    # AJOUT MÉMOIRE
    # --------------------------------------------------

    def add_memory(self, text: str, metadata: Dict) -> int:
        embedding = self.embedding_model.encode([text])[0].astype("float32")

        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)

        self.index.add(np.array([embedding]))

        metadata["text"] = text
        metadata["vector_id"] = len(self.metadata)

        # Sécurité émotionnelle
        metadata.setdefault("emotion", {})
        metadata.setdefault("intensity", 0.5)
        metadata.setdefault("importance", 0.5)

        self.metadata.append(metadata)
        self._save_index()

        return metadata["vector_id"]

    # --------------------------------------------------
    # RECHERCHE ÉMOTIONNELLE
    # --------------------------------------------------

    def search(
        self,
        query: str,
        current_emotion: Dict,
        k: int = None,
    ) -> List[Tuple[Dict, float]]:

        if self.index is None or self.index.ntotal == 0:
            return []

        k = k or config.MEMORY_RETRIEVAL_K

        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = query_embedding.astype("float32").reshape(1, -1)

        distances, indices = self.index.search(
            query_embedding,
            min(k * 3, self.index.ntotal),  # Sur-échantillonnage
        )

        scored_memories = []

        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            semantic_score = 1.0 / (1.0 + dist)

            emotional_score = self._emotional_alignment(
                current_emotion,
                meta.get("emotion", {}),
            )

            intensity = meta.get("intensity", 0.5)
            importance = meta.get("importance", 0.5)

            # Score cognitif final
            final_score = (
                semantic_score * 0.5
                + emotional_score * 0.3
                + importance * 0.1
                + intensity * 0.1
            )

            scored_memories.append((meta, final_score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return scored_memories[:k]

    # --------------------------------------------------
    # ALIGNEMENT ÉMOTIONNEL
    # --------------------------------------------------

    def _emotional_alignment(self, current: Dict, past: Dict) -> float:
        """
        Compare deux états émotionnels.
        Retourne un score 0–1.
        """

        if not current or not past:
            return 0.5

        score = 0.0
        dimensions = 0

        for key in ["valence", "arousal", "dominance"]:
            if key in current and key in past:
                diff = abs(current[key] - past[key])
                score += 1.0 - diff
                dimensions += 1

        if dimensions == 0:
            return 0.5

        return max(0.0, min(1.0, score / dimensions))

    # --------------------------------------------------
    # UTILITAIRES
    # --------------------------------------------------

    def get_memory_count(self) -> int:
        return self.index.ntotal if self.index else 0

    def get_all_memories(self) -> List[Dict]:
        return self.metadata.copy()
