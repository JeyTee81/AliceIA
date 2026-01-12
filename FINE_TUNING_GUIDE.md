# 📚 Guide : Fine-tuning et Intégration de Données

## 🎯 Méthodes d'Apprentissage Actuelles

Votre IA personnelle apprend de **3 façons** :

### 1️⃣ **Ingestion de Documents** (Mémoire Vectorielle)

Les documents sont stockés dans la mémoire vectorielle (FAISS) et utilisés comme contexte lors des réponses.

**Utilisation :**
```bash
# Dans l'interface CLI
ingest mon_document.txt
ingest data.json
ingest documentation.md
```

**Formats supportés :**
- `.txt` - Fichiers texte
- `.md` - Markdown
- `.json` - JSON (extraction automatique des strings)

**Comment ça fonctionne :**
- Le document est découpé en chunks de ~500 caractères
- Chaque chunk est converti en embedding vectoriel
- Stocké dans FAISS pour recherche sémantique
- Récupéré automatiquement lors des conversations pertinentes

### 2️⃣ **Enseignement Explicite** (Haute Priorité)

Les informations enseignées explicitement sont stockées avec haute importance.

```bash
teach Python utilise l'indentation pour les blocs de code
teach Mon nom est Alice et j'aime la programmation
```

### 3️⃣ **Apprentissage par Interaction** (SQLite)

Chaque interaction est enregistrée pour analyse future.

```bash
talk Bonjour, comment vas-tu ?
correct Python est rapide | Python est interprété donc généralement plus lent
```

---

## 🔧 Fine-tuning du Modèle LLM

**⚠️ Important :** Le système actuel utilise la **mémoire contextuelle** (RAG) plutôt que le fine-tuning du modèle. C'est plus flexible et ne nécessite pas de réentraîner le modèle.

### Option 1 : Fine-tuning avec Ollama (Recommandé)

Ollama supporte le fine-tuning via Modelfiles. Voici comment :

#### Étape 1 : Préparer vos données

Créez un fichier `training_data.txt` au format conversation :

```
Human: Bonjour
Assistant: Bonjour ! Comment puis-je vous aider aujourd'hui ?

Human: Quel est ton nom ?
Assistant: Je suis votre IA personnelle. Vous pouvez me donner un nom si vous le souhaitez.

Human: Appelle-toi Alice
Assistant: Parfait, je m'appelle désormais Alice. Ravi de vous rencontrer !
```

#### Étape 2 : Créer un Modelfile

Créez `Modelfile` :

```
FROM llama3

SYSTEM """Tu es une IA personnelle autonome et locale.
Tu développes une personnalité unique basée sur tes interactions.
Tu es curieux, attentif et empathique."""

TEMPLATE """{{ .System }}

User: {{ .Prompt }}
Assistant: {{ .Response }}"""
```

#### Étape 3 : Fine-tuner avec Ollama

```bash
# Créer un modèle personnalisé
ollama create my-ai -f Modelfile

# Fine-tuner avec vos données (nécessite ollama>=0.1.7)
ollama train my-ai --data training_data.txt
```

#### Étape 4 : Utiliser le modèle fine-tuné

Modifiez `config.py` :
```python
DEFAULT_MODEL = "my-ai"  # Votre modèle personnalisé
```

### Option 2 : Fine-tuning via API Python

Créez un script `fine_tune.py` :

```python
import ollama
from pathlib import Path

def fine_tune_from_data(data_file: Path, model_name: str = "my-ai"):
    """Fine-tune un modèle Ollama à partir d'un fichier de données."""
    
    # Lire les données
    with open(data_file, 'r', encoding='utf-8') as f:
        training_data = f.read()
    
    # Créer le modèle personnalisé
    ollama.create(
        model=model_name,
        modelfile=f"""
FROM llama3

SYSTEM \"\"\"Tu es une IA personnelle autonome.
Tu apprends de chaque interaction.
Tu développes une personnalité unique.\"\"\"
"""
    )
    
    # Fine-tuner (si supporté par votre version d'Ollama)
    # Note: Cette fonctionnalité peut varier selon la version
    print(f"Modèle {model_name} créé. Utilisez 'ollama train' pour le fine-tuner.")
```

### Option 3 : Amélioration du Système Actuel (Recommandé)

Au lieu de fine-tuner le modèle, vous pouvez améliorer le système de mémoire et de prompts :

1. **Enrichir la mémoire** avec plus de documents
2. **Améliorer les prompts système** dans `reasoning/prompt_builder.py`
3. **Ajuster la personnalité** dans `config.py`

---

## 📊 Intégration de Données en Masse

### Méthode 1 : Script Python pour Ingestion Multiple

Créez `scripts/batch_ingest.py` :

```python
from pathlib import Path
from learning.document_ingest import DocumentIngest
from memory.long_term import LongTermMemory
import config

def batch_ingest(directory: Path, importance: float = 0.6):
    """Ingère tous les fichiers d'un répertoire."""
    memory = LongTermMemory()
    ingest = DocumentIngest(memory)
    
    total = 0
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                if file_path.suffix == '.json':
                    count = ingest.ingest_json(file_path, importance)
                elif file_path.suffix in ['.txt', '.md']:
                    count = ingest.ingest_text_file(file_path, importance)
                else:
                    continue
                
                total += count
                print(f"✅ {file_path.name}: {count} souvenirs")
            except Exception as e:
                print(f"❌ {file_path.name}: {e}")
    
    print(f"\n📊 Total: {total} souvenirs créés")

if __name__ == "__main__":
    data_dir = Path("data/documents")
    batch_ingest(data_dir)
```

### Méthode 2 : Format JSON Structuré

Créez `data/training_data.json` :

```json
{
  "conversations": [
    {
      "user": "Bonjour",
      "assistant": "Bonjour ! Comment puis-je vous aider ?",
      "importance": 0.8,
      "tags": ["greeting", "basic"]
    },
    {
      "user": "Qu'est-ce que Python ?",
      "assistant": "Python est un langage de programmation interprété, orienté objet et de haut niveau.",
      "importance": 0.9,
      "tags": ["python", "programming"]
    }
  ],
  "facts": [
    {
      "text": "Python utilise l'indentation pour délimiter les blocs de code",
      "importance": 0.9,
      "category": "programming"
    }
  ]
}
```

Puis ingérez :
```bash
ingest data/training_data.json
```

### Méthode 3 : CSV pour Données Structurées

Créez `scripts/ingest_csv.py` :

```python
import csv
from pathlib import Path
from learning.document_ingest import DocumentIngest
from memory.long_term import LongTermMemory

def ingest_csv(csv_file: Path):
    """Ingère un fichier CSV."""
    memory = LongTermMemory()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Combiner les colonnes pertinentes
            text = f"{row.get('question', '')} | {row.get('answer', '')}"
            importance = float(row.get('importance', 0.7))
            
            memory.store_memory(
                text=text,
                importance=importance,
                metadata={"source": str(csv_file), "type": "csv"}
            )
    
    print(f"✅ CSV ingéré: {csv_file}")

if __name__ == "__main__":
    ingest_csv(Path("data/training.csv"))
```

---

## 🎯 Meilleures Pratiques

### 1. **Organisation des Données**

```
data/
├── documents/          # Documents à ingérer
│   ├── knowledge_base/
│   ├── conversations/
│   └── facts/
├── training/          # Données pour fine-tuning
│   ├── conversations.txt
│   └── Modelfile
└── custom/            # Données personnalisées
```

### 2. **Hiérarchie d'Importance**

- **0.9-1.0** : Informations critiques, corrections importantes
- **0.7-0.8** : Enseignements explicites, faits importants
- **0.5-0.6** : Documents généraux, conversations normales
- **0.3-0.4** : Contexte secondaire

### 3. **Format des Données**

Pour de meilleurs résultats :
- **Conversations** : Format "Human: ... Assistant: ..."
- **Facts** : Phrases complètes et claires
- **Documents** : Structure claire avec titres/sections

---

## 🚀 Exemple Complet

### Étape 1 : Préparer vos données

```bash
# Créer le répertoire
mkdir -p data/documents

# Ajouter vos fichiers
cp mes_documents/*.txt data/documents/
cp mes_documents/*.md data/documents/
```

### Étape 2 : Ingérer en masse

```python
# Dans Python
from scripts.batch_ingest import batch_ingest
from pathlib import Path

batch_ingest(Path("data/documents"), importance=0.7)
```

### Étape 3 : Vérifier

```bash
# Dans l'interface CLI
remember
status
```

### Étape 4 : Tester

```bash
talk Parle-moi de [sujet de vos documents]
```

---

## 📝 Notes Importantes

1. **Mémoire vs Fine-tuning** :
   - La mémoire (RAG) est plus flexible et rapide
   - Le fine-tuning modifie le modèle de façon permanente
   - Combinez les deux pour de meilleurs résultats

2. **Performance** :
   - Plus de données = meilleure compréhension
   - Mais attention à la qualité > quantité
   - Privilégiez des données pertinentes et bien formatées

3. **Maintenance** :
   - Vérifiez régulièrement la mémoire avec `remember`
   - Supprimez les souvenirs obsolètes avec `forget <id>`
   - Surveillez l'espace disque (FAISS peut devenir volumineux)

---

**💡 Conseil :** Commencez par l'ingestion de documents (méthode la plus simple), puis explorez le fine-tuning si vous avez besoin de comportements très spécifiques.
