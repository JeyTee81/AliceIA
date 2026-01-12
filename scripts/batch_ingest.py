"""
Script pour ingérer en masse des fichiers dans la mémoire de l'IA.
Utilisez ce script pour intégrer rapidement de grandes quantités de données.
"""

from pathlib import Path
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning.document_ingest import DocumentIngest
from memory.long_term import LongTermMemory
import config


def batch_ingest(directory: Path, importance: float = 0.6, recursive: bool = True):
    """
    Ingère tous les fichiers d'un répertoire dans la mémoire.
    
    Args:
        directory: Répertoire contenant les fichiers à ingérer
        importance: Importance des documents (0.0-1.0)
        recursive: Si True, parcourt les sous-répertoires
    
    Returns:
        Nombre total de souvenirs créés
    """
    if not directory.exists():
        print(f"❌ Répertoire non trouvé: {directory}")
        return 0
    
    memory = LongTermMemory()
    ingest = DocumentIngest(memory)
    
    total = 0
    files_processed = 0
    files_failed = 0
    
    # Extensions supportées
    supported_extensions = {'.txt', '.md', '.json', '.csv'}
    
    # Parcourir les fichiers
    pattern = "**/*" if recursive else "*"
    for file_path in directory.glob(pattern):
        if not file_path.is_file():
            continue
        
        # Vérifier l'extension
        if file_path.suffix.lower() not in supported_extensions:
            continue
        
        try:
            if file_path.suffix.lower() == '.json':
                count = ingest.ingest_json(file_path, importance)
            elif file_path.suffix.lower() == '.csv':
                # CSV nécessite un traitement spécial
                count = ingest_csv_file(file_path, memory, importance)
            else:
                count = ingest.ingest_text_file(file_path, importance)
            
            total += count
            files_processed += 1
            print(f"✅ {file_path.name}: {count} souvenirs créés")
        
        except Exception as e:
            files_failed += 1
            print(f"❌ {file_path.name}: {e}")
    
    print(f"\n📊 Résumé:")
    print(f"   Fichiers traités: {files_processed}")
    print(f"   Fichiers échoués: {files_failed}")
    print(f"   Total souvenirs: {total}")
    
    return total


def ingest_csv_file(file_path: Path, memory: LongTermMemory, importance: float = 0.6):
    """Ingère un fichier CSV."""
    import csv
    
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Essayer de trouver les colonnes pertinentes
            text = ""
            row_importance = importance
            
            # Chercher des colonnes communes
            if 'text' in row:
                text = row['text']
            elif 'content' in row:
                text = row['content']
            elif 'question' in row and 'answer' in row:
                text = f"Q: {row['question']}\nA: {row['answer']}"
            elif 'user' in row and 'assistant' in row:
                text = f"User: {row['user']}\nAssistant: {row['assistant']}"
            else:
                # Utiliser toutes les valeurs string
                text = " | ".join(str(v) for v in row.values() if v)
            
            if 'importance' in row:
                try:
                    row_importance = float(row['importance'])
                except:
                    pass
            
            if len(text.strip()) > 20:
                memory.store_memory(
                    text=text,
                    importance=row_importance,
                    metadata={"source": str(file_path), "type": "csv"}
                )
                count += 1
    
    return count


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingère en masse des fichiers dans la mémoire de l'IA"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Répertoire contenant les fichiers à ingérer"
    )
    parser.add_argument(
        "--importance",
        type=float,
        default=0.6,
        help="Importance des documents (0.0-1.0, défaut: 0.6)"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Ne pas parcourir les sous-répertoires"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Ingestion en masse depuis: {args.directory}")
    print(f"   Importance: {args.importance}")
    print(f"   Récursif: {not args.no_recursive}\n")
    
    total = batch_ingest(
        args.directory,
        importance=args.importance,
        recursive=not args.no_recursive
    )
    
    if total > 0:
        print(f"\n✅ Ingestion terminée: {total} souvenirs créés")
    else:
        print("\n⚠️  Aucun souvenir créé. Vérifiez le répertoire et les fichiers.")


if __name__ == "__main__":
    main()
