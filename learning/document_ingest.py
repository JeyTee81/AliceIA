"""
Système d'ingestion de documents pour l'apprentissage.
Permet à l'IA d'apprendre à partir de fichiers texte.
"""

from typing import List, Dict
from pathlib import Path
import json

from memory.long_term import LongTermMemory


class DocumentIngest:
    """
    Ingestion de documents pour enrichir la mémoire.
    Supporte les formats texte, markdown, JSON.
    """
    
    def __init__(self, long_term_memory: LongTermMemory):
        self.memory = long_term_memory
    
    def ingest_text_file(self, file_path: Path, importance: float = 0.6) -> int:
        """
        Ingère un fichier texte dans la mémoire.
        
        Args:
            file_path: Chemin vers le fichier
            importance: Importance du document
        
        Returns:
            Nombre de souvenirs créés
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture: {e}")
        
        # Découper en chunks (paragraphes ou lignes)
        chunks = self._chunk_text(content)
        
        count = 0
        for chunk in chunks:
            if len(chunk.strip()) > 20:  # Ignorer les chunks trop courts
                self.memory.store_memory(
                    text=chunk,
                    importance=importance,
                    metadata={"source": str(file_path), "type": "document"}
                )
                count += 1
        
        return count
    
    def ingest_markdown(self, file_path: Path, importance: float = 0.6) -> int:
        """Ingère un fichier Markdown."""
        return self.ingest_text_file(file_path, importance)
    
    def ingest_json(self, file_path: Path, importance: float = 0.6) -> int:
        """
        Ingère un fichier JSON.
        Extrait le texte des valeurs string.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture JSON: {e}")
        
        # Extraire récursivement les strings
        texts = self._extract_strings(data)
        
        count = 0
        for text in texts:
            if len(text.strip()) > 20:
                self.memory.store_memory(
                    text=text,
                    importance=importance,
                    metadata={"source": str(file_path), "type": "json"}
                )
                count += 1
        
        return count
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Découpe le texte en chunks.
        Préfère les coupures aux paragraphes.
        """
        # D'abord par paragraphes
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Si les chunks sont trop grands, découper par phrases
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > chunk_size * 1.5:
                sentences = chunk.split('. ')
                temp_chunk = ""
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) < chunk_size:
                        temp_chunk += sentence + ". "
                    else:
                        if temp_chunk:
                            final_chunks.append(temp_chunk.strip())
                        temp_chunk = sentence + ". "
                if temp_chunk:
                    final_chunks.append(temp_chunk.strip())
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _extract_strings(self, obj, max_depth: int = 10) -> List[str]:
        """Extrait récursivement les strings d'un objet JSON."""
        if max_depth <= 0:
            return []
        
        texts = []
        
        if isinstance(obj, str):
            texts.append(obj)
        elif isinstance(obj, dict):
            for value in obj.values():
                texts.extend(self._extract_strings(value, max_depth - 1))
        elif isinstance(obj, list):
            for item in obj:
                texts.extend(self._extract_strings(item, max_depth - 1))
        
        return texts
