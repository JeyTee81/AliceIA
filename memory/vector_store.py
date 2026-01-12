"""
Stockage vectoriel FAISS pour la mémoire sémantique.
Gère les embeddings et la recherche de similarité.
"""

import faiss
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from sentence_transformers import SentenceTransformer
import pickle

import config


class VectorStore:
    """
    Stockage vectoriel pour la mémoire sémantique.
    Utilise FAISS pour la recherche rapide de similarité.
    """
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.dimension = config.EMBEDDING_DIM
        self.index = None
        self.metadata: List[Dict] = []  # Métadonnées associées aux vecteurs
        self.vectors_path = Path(config.VECTORS_PATH)
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialise ou charge l'index FAISS."""
        if self.vectors_path.exists():
            self._load_index()
        else:
            # Créer un nouvel index FAISS (L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def _load_index(self):
        """Charge l'index FAISS depuis le disque."""
        try:
            # Charger l'index
            self.index = faiss.read_index(str(self.vectors_path))
            
            # Charger les métadonnées
            metadata_path = self.vectors_path.with_suffix('.pkl')
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de l'index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    def _save_index(self):
        """Sauvegarde l'index FAISS sur le disque."""
        try:
            faiss.write_index(self.index, str(self.vectors_path))
            
            # Sauvegarder les métadonnées
            metadata_path = self.vectors_path.with_suffix('.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'index: {e}")
    
    def add_memory(self, text: str, metadata: Dict) -> int:
        """
        Ajoute un souvenir au stockage vectoriel.
        
        Args:
            text: Le texte du souvenir
            metadata: Métadonnées (timestamp, émotion, importance, etc.)
        
        Returns:
            L'index du vecteur ajouté
        """
        # Générer l'embedding
        embedding = self.embedding_model.encode([text])[0]
        embedding = embedding.astype('float32')
        
        # Ajouter à l'index FAISS
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(np.array([embedding]))
        
        # Ajouter les métadonnées
        metadata['text'] = text
        metadata['vector_id'] = len(self.metadata)
        self.metadata.append(metadata)
        
        # Sauvegarder
        self._save_index()
        
        return len(self.metadata) - 1
    
    def search(self, query: str, k: int = None) -> List[Tuple[Dict, float]]:
        """
        Recherche les souvenirs les plus similaires.
        
        Args:
            query: La requête de recherche
            k: Nombre de résultats à retourner
        
        Returns:
            Liste de tuples (métadonnées, score de similarité)
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        k = k or config.MEMORY_RETRIEVAL_K
        
        # Générer l'embedding de la requête
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Recherche dans FAISS
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Construire les résultats avec métadonnées
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                # Convertir la distance L2 en score de similarité (0-1)
                similarity = 1.0 / (1.0 + dist)
                results.append((self.metadata[idx], similarity))
        
        return results
    
    def get_all_memories(self) -> List[Dict]:
        """Retourne tous les souvenirs avec leurs métadonnées."""
        return self.metadata.copy()
    
    def get_memory_count(self) -> int:
        """Retourne le nombre total de souvenirs."""
        if self.index is None:
            return 0
        return self.index.ntotal
