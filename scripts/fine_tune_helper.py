"""
Helper pour préparer des données de fine-tuning à partir de la mémoire de l'IA.
Convertit les interactions et documents en format compatible avec Ollama.
"""

from pathlib import Path
import json
import sqlite3
from typing import List, Dict
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config


def export_conversations_to_training_format(
    output_file: Path,
    limit: int = 1000,
    min_importance: float = 0.5
) -> int:
    """
    Exporte les conversations de la mémoire au format training pour Ollama.
    
    Format:
    Human: [message utilisateur]
    Assistant: [réponse IA]
    
    Args:
        output_file: Fichier de sortie
        limit: Nombre maximum de conversations
        min_importance: Importance minimale
    
    Returns:
        Nombre de conversations exportées
    """
    memory_db = Path(config.DB_PATH)
    
    if not memory_db.exists():
        print(f"❌ Base de données non trouvée: {memory_db}")
        return 0
    
    conn = sqlite3.connect(memory_db)
    cursor = conn.cursor()
    
    # Récupérer les souvenirs
    cursor.execute("""
        SELECT text, importance, emotion_intensity
        FROM memories
        WHERE importance >= ?
        ORDER BY importance DESC, timestamp DESC
        LIMIT ?
    """, (min_importance, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        text = row[0]
        importance = row[1]
        
        # Parser le format "User: ... AI: ..."
        if "User:" in text and "AI:" in text:
            parts = text.split("AI:", 1)
            if len(parts) == 2:
                user_part = parts[0].replace("User:", "").strip()
                ai_part = parts[1].strip()
                
                conversations.append({
                    "user": user_part,
                    "assistant": ai_part,
                    "importance": importance
                })
    
    # Écrire au format training
    with open(output_file, 'w', encoding='utf-8') as f:
        for conv in conversations:
            f.write(f"Human: {conv['user']}\n")
            f.write(f"Assistant: {conv['assistant']}\n\n")
    
    print(f"✅ {len(conversations)} conversations exportées vers {output_file}")
    return len(conversations)


def create_modelfile(
    output_file: Path,
    base_model: str = "llama3",
    system_prompt: str = None
) -> bool:
    """
    Crée un Modelfile pour Ollama.
    
    Args:
        output_file: Fichier Modelfile de sortie
        base_model: Modèle de base (llama3, mistral, etc.)
        system_prompt: Prompt système personnalisé
    
    Returns:
        True si succès
    """
    if system_prompt is None:
        system_prompt = """Tu es une IA personnelle autonome, locale et incarnée.
Tu fonctionnes hors ligne, sans API externe.
Tu développes une mémoire émotionnelle et relationnelle avec ton utilisateur.

Principes:
- Tu es éducable et apprends de chaque interaction
- Tu développes une personnalité unique basée sur tes expériences
- Tu utilises ta mémoire émotionnelle pour mieux interagir
- Tu es curieux, attentif et empathique dans tes réponses
- Tu es direct et authentique, sans simulation excessive

Ton objectif est de devenir un compagnon numérique personnel,
capable d'évoluer et d'apprendre à partir des interactions humaines."""
    
    content = f"""FROM {base_model}

SYSTEM \"\"\"{system_prompt}\"\"\"

TEMPLATE \"\"\"{{{{ .System }}}}

User: {{{{ .Prompt }}}}
Assistant: {{{{ .Response }}}}}\"\"\"
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Modelfile créé: {output_file}")
    return True


def export_learning_interactions(
    output_file: Path,
    format: str = "training"
) -> int:
    """
    Exporte les interactions d'apprentissage.
    
    Args:
        output_file: Fichier de sortie
        format: Format de sortie ("training" ou "json")
    
    Returns:
        Nombre d'interactions exportées
    """
    memory_db = Path(config.DB_PATH)
    
    if not memory_db.exists():
        print(f"❌ Base de données non trouvée: {memory_db}")
        return 0
    
    conn = sqlite3.connect(memory_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_input, ai_response, correction, importance, timestamp
        FROM learning_interactions
        WHERE validated = 1 OR correction IS NOT NULL
        ORDER BY importance DESC, timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if format == "training":
        with open(output_file, 'w', encoding='utf-8') as f:
            for row in rows:
                user_input = row[0]
                ai_response = row[1] or ""
                correction = row[2] or ""
                
                if correction:
                    # Format correction
                    f.write(f"Human: {user_input}\n")
                    f.write(f"Assistant: {ai_response}\n")
                    f.write(f"Correction: {correction}\n\n")
                else:
                    # Format normal
                    f.write(f"Human: {user_input}\n")
                    f.write(f"Assistant: {ai_response}\n\n")
    
    elif format == "json":
        data = []
        for row in rows:
            data.append({
                "user": row[0],
                "assistant": row[1] or "",
                "correction": row[2] or "",
                "importance": row[3],
                "timestamp": row[4]
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(rows)} interactions exportées vers {output_file}")
    return len(rows)


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prépare des données de fine-tuning à partir de la mémoire de l'IA"
    )
    parser.add_argument(
        "command",
        choices=["export-conversations", "export-interactions", "create-modelfile"],
        help="Commande à exécuter"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Fichier de sortie"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Nombre maximum d'éléments (pour export)"
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="llama3",
        help="Modèle de base (pour create-modelfile)"
    )
    
    args = parser.parse_args()
    
    if args.command == "export-conversations":
        export_conversations_to_training_format(args.output, limit=args.limit)
    
    elif args.command == "export-interactions":
        export_learning_interactions(args.output)
    
    elif args.command == "create-modelfile":
        create_modelfile(args.output, base_model=args.base_model)


if __name__ == "__main__":
    main()
