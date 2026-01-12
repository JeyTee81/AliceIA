# 🤖 IA Personnelle Autonome & Locale

Système cognitif autonome, local et incarné, capable d'interagir avec un humain, d'apprendre à partir de ses échanges, de développer une mémoire émotionnelle, et d'évoluer dans le temps comme une entité persistante.

## 🎯 Caractéristiques

- ✅ **100% Local** - Aucun cloud, aucune API externe
- 🧠 **Mémoire Multi-couches** - Court terme, long terme, vectorielle (FAISS)
- 🧡 **Mémoire Émotionnelle** - États émotionnels pour prioriser et interagir
- 📚 **Apprentissage** - Apprend de chaque interaction et correction
- 🎭 **Personnalité Évolutive** - Se développe à partir des expériences
- 🤖 **Incarnée** - Interface extensible vers avatar 3D (Unity)

## 🏗️ Architecture

```
ai_entity/
├── consciousness/     # Conscience centrale (orchestrateur)
├── emotion/           # Système émotionnel
├── memory/            # Mémoire (court/long terme, FAISS)
├── learning/          # Moteur d'apprentissage
├── reasoning/         # Raisonnement et personnalité
├── llm/              # Interface Ollama (LLM local)
├── embodiment/        # Incarnation (avatar)
└── interface/         # Interface CLI
```

## 📋 Prérequis

1. **Python 3.11+**
2. **Ollama** installé et démarré
   - Installation: https://ollama.ai
   - Démarrer: `ollama serve`
   - Télécharger un modèle: `ollama pull llama3`

## 🚀 Installation

1. Cloner ou télécharger ce projet

2. Installer les dépendances:
```bash
# Sur Windows:
python -m pip install -r requirements.txt
# ou
py -m pip install -r requirements.txt

# Sur Linux/Mac:
pip install -r requirements.txt
```

3. Vérifier qu'Ollama est démarré:
```bash
ollama serve
```

4. Télécharger un modèle (optionnel, mais recommandé):
```bash
ollama pull llama3
# ou
ollama pull mistral
# ou
ollama pull qwen
```

## 💻 Utilisation

### Mode CLI (Interface en ligne de commande)

Lancer l'IA:
```bash
python main.py
```

### Mode API (Pour Unity)

Démarrer le serveur API pour Unity:
```bash
python main.py --api
# ou
python api_server.py
```

Le serveur démarre sur `http://localhost:5000`

📖 **Voir `UNITY_INTEGRATION.md` pour l'intégration complète avec Unity**

### Commandes disponibles

- `talk <message>` - Parler avec l'IA
- `teach <contenu>` - Enseigner quelque chose à l'IA
- `correct <input> | <correction>` - Corriger une réponse
- `remember` - Voir les souvenirs récents
- `forget <id>` - Oublier un souvenir
- `emotion` - Voir l'état émotionnel actuel
- `status` - Voir le statut complet de l'IA
- `avatar` - Afficher l'état de l'avatar
- `ingest <fichier>` - Ingérer un document dans la mémoire
- `batch-ingest <dir>` - Ingérer tous les fichiers d'un répertoire
- `help` - Afficher l'aide
- `quit` / `exit` - Quitter

### Exemples

```bash
# Parler avec l'IA
talk Bonjour, comment vas-tu ?

# Enseigner quelque chose
teach Python est un langage de programmation interprété

# Corriger une réponse
correct Python | Python est un langage interprété et orienté objet

# Voir l'état émotionnel
emotion

# Voir le statut
status

# Ingérer un document
ingest mon_document.txt

# Ingérer tous les fichiers d'un répertoire
batch-ingest data/documents
```

## 🧠 Fonctionnement

### Cycle Cognitif

1. **Perception** - Réception du message utilisateur
2. **Émotion** - Analyse et génération d'état émotionnel
3. **Mémoire** - Récupération de souvenirs pertinents
4. **Raisonnement** - Construction du prompt avec contexte
5. **Réponse** - Génération via LLM local
6. **Apprentissage** - Stockage et mise à jour

### Mémoire Émotionnelle

L'IA modélise des états émotionnels (pas une simulation humaine) pour:
- Prioriser les souvenirs
- Influencer le ton de réponse
- Développer la personnalité
- Mieux interagir

Dimensions émotionnelles:
- **Valence**: Positif / Négatif
- **Arousal**: Calme / Intense
- **Dominance**: Passif / Actif
- **Confiance**: Confiance envers l'utilisateur
- **Curiosité**: Niveau de curiosité
- **Attachement**: Attachement contextuel

### Apprentissage

L'IA apprend de:
- Chaque interaction conversationnelle
- Enseignements explicites (`teach`)
- Corrections (`correct`)
- Documents ingérés (`ingest` ou `batch-ingest`)

📚 **Pour le fine-tuning et l'intégration de données en masse**, consultez `FINE_TUNING_GUIDE.md`

## 📂 Structure des Données

Les données sont stockées dans `data/`:
- `memory.db` - Base SQLite (métadonnées)
- `vectors.faiss` - Index FAISS (recherche sémantique)
- `memories/` - Fichiers de souvenirs
- `emotions/` - Historique émotionnel

## ⚙️ Configuration

Modifier `config.py` pour ajuster:
- Modèle LLM (llama3, mistral, qwen)
- Paramètres de mémoire
- Seuils émotionnels
- Personnalité par défaut

## 🔒 Sécurité & Confidentialité

- **100% Local** - Aucune donnée ne quitte votre machine
- **Aucune API externe** - Fonctionne hors ligne
- **Données privées** - Tous les souvenirs restent locaux

## 🎯 Vision Future

Cette IA peut devenir:
- Un compagnon numérique personnel
- Une entité incarnée dans Unity
- Un cerveau IA persistant cross-projets
- Une IA relationnelle éducable

## 📝 Notes

- L'IA ne "ressent" rien - elle modélise des états émotionnels pour mieux fonctionner
- Chaque fichier fait ≤ 200 lignes pour maintenir la lisibilité
- Architecture modulaire pour faciliter l'extension
- Code commenté et documenté

## 🐛 Dépannage

**Ollama non disponible:**
- Vérifier que `ollama serve` est démarré
- Vérifier que le modèle est téléchargé: `ollama list`

**Erreurs de mémoire:**
- Vérifier les permissions d'écriture dans `data/`
- Vérifier l'espace disque disponible

**Erreurs d'import:**
- Vérifier que toutes les dépendances sont installées: `pip install -r requirements.txt`

## 📄 Licence

Ce projet est fourni tel quel, pour usage personnel et éducatif.

---

**Développé avec ❤️ pour créer une IA vraiment personnelle et locale.**
