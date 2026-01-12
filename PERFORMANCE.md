# ⚡ Optimisation des Performances

Guide pour améliorer la vitesse de réponse de l'IA tout en préservant l'apprentissage continu.

## 🎯 Optimisations Appliquées (Sans Limiter l'Apprentissage)

### 1. Feedback Visuel Amélioré

- Indicateur de progression animé pendant la génération
- Gestion propre des interruptions (Ctrl+C)
- Meilleure expérience utilisateur

### 2. Configuration Optimisée

- **Tokens par défaut** : 1024 (équilibré entre vitesse et qualité)
- **Max tokens dynamique** : 500-2048 selon personnalité et curiosité
- **Timeout** : 120 secondes pour éviter les blocages

### 3. Mémoire et Contexte Préservés

- **Contexte complet** : Tous les messages de la session sont conservés
- **Souvenirs** : 2-4 souvenirs récupérés selon l'état émotionnel
- **Apprentissage continu** : Aucune limitation artificielle de la compréhension

## ⚙️ Configuration

L'IA est configurée pour **apprendre en continu sans limite** :

```python
# Configuration actuelle (optimisée pour apprentissage)
DEFAULT_MAX_TOKENS = 1024  # Réponses complètes
MAX_SHORT_TERM_MEMORY = 20  # Contexte complet préservé
MEMORY_RETRIEVAL_K = 5  # Souvenirs pertinents récupérés
```

**Note** : Si vous voulez sacrifier l'apprentissage pour la vitesse, vous pouvez réduire ces valeurs, mais cela limitera la capacité de l'IA à apprendre et à se souvenir.

## 🚀 Conseils pour de Meilleures Performances (Sans Limiter l'Apprentissage)

### 1. Utiliser un Modèle Plus Léger

```bash
# Modèles plus rapides (mais moins performants)
ollama pull llama3:8b      # Version 8B au lieu de 70B
ollama pull mistral:7b
ollama pull qwen:7b
```

Puis dans `config.py` :
```python
DEFAULT_MODEL = "llama3:8b"
```

### 2. Optimiser le Matériel

- Utiliser un GPU si disponible (Ollama le détecte automatiquement)
- Augmenter la RAM disponible pour Ollama
- Fermer les autres applications gourmandes

### 3. Ajuster la Température (Optionnel)

Température plus basse = réponses plus déterministes = légèrement plus rapides

```python
DEFAULT_TEMPERATURE = 0.6  # Au lieu de 0.7 (légère réduction)
```

**⚠️ Important** : Ne réduisez pas la mémoire ou le contexte si vous voulez que l'IA apprenne en continu !

## 📊 Temps de Réponse Typiques

Avec contexte complet et mémoire préservée :

- **Modèle 7B-8B** : 3-8 secondes
- **Modèle 13B** : 8-15 secondes
- **Modèle 70B** : 15-45 secondes

**Note** : Ces temps peuvent varier selon la longueur du contexte et le nombre de souvenirs récupérés. C'est normal et nécessaire pour un apprentissage continu.

## 🔧 Dépannage

### L'IA est toujours lente

1. Vérifiez le modèle utilisé : `ollama list`
2. Utilisez une version plus petite (8B au lieu de 70B)
3. Vérifiez que votre GPU est utilisé si disponible
4. Augmentez la RAM disponible

### Timeout fréquent

Augmentez dans `config.py` :
```python
OLLAMA_TIMEOUT = 180  # 3 minutes pour les modèles plus lourds
```

### Réponses trop courtes

Augmentez dans `config.py` :
```python
DEFAULT_MAX_TOKENS = 1536  # Réponses plus longues
```

### ⚠️ Ne Sacrifiez Pas l'Apprentissage

Si vous réduisez la mémoire ou le contexte pour la vitesse, l'IA perdra sa capacité à :
- Apprendre en continu
- Se souvenir des interactions précédentes
- Développer une compréhension cumulative

**Recommandation** : Utilisez un modèle plus léger plutôt que de limiter la mémoire.

---

**💡 Philosophie** : L'objectif est un apprentissage continu sans limite, pas la vitesse maximale. La patience permet une IA plus intelligente et plus mémorielle.
