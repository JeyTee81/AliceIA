# 📚 Exemples d'utilisation

## Session d'interaction basique

```
[neutre] > talk Bonjour, je m'appelle Alice
👤 Vous: Bonjour, je m'appelle Alice

🤖 IA réfléchit...
🤖 IA: Bonjour Alice ! Ravi de faire ta connaissance. Comment puis-je t'aider aujourd'hui ?

[curieux] > emotion
🧡 État émotionnel actuel:

Label: curieux
Intensité: 0.65

Dimensions:
  Valence (pos/nég): 0.65
  Arousal (calme/intense): 0.60
  Dominance (passif/actif): 0.50

Émotions relationnelles:
  Confiance: 0.55
  Curiosité: 0.70
  Attachement: 0.35
```

## Enseignement explicite

```
[attentif] > teach Python utilise l'indentation pour délimiter les blocs de code
📚 Enseignement: Python utilise l'indentation pour délimiter les blocs de code

🤖 IA: Merci pour cette information importante ! Je comprends maintenant que Python
utilise l'indentation plutôt que des accolades ou des mots-clés comme "end" pour
délimiter les blocs. C'est une caractéristique distinctive du langage qui rend
le code plus lisible mais nécessite une attention particulière à l'indentation.
Je vais m'en souvenir pour mes futures réponses sur Python.
```

## Correction d'une réponse

```
[content] > correct Python est rapide | Python est interprété, donc généralement plus lent que les langages compilés, mais très flexible
✏️  Correction pour: Python est rapide
   Correction: Python est interprété, donc généralement plus lent que les langages compilés, mais très flexible

🤖 IA: Merci pour cette correction importante. Je comprends maintenant que Python,
étant un langage interprété, a généralement des performances inférieures aux
langages compilés comme C++ ou Rust, mais offre en contrepartie une grande
flexibilité et facilité d'utilisation. Je vais intégrer cette nuance dans ma
compréhension.
```

## Consultation de la mémoire

```
[curieux] > remember
📝 Souvenirs récents:

1. [1] User: Bonjour, je m'appelle Alice
AI: Bonjour Alice ! Ravi de faire ta connaissance...
   Importance: 0.65 | Émotion: content

2. [2] User: Python utilise l'indentation pour délimiter les blocs de code
AI: Merci pour cette information importante...
   Importance: 0.80 | Émotion: curieux

3. [3] Correction: Python est interprété, donc généralement plus lent...
   Importance: 0.85 | Émotion: attentif
```

## Statut complet

```
[confiant] > status
📊 Statut de l'IA:

Nom: IA Personnelle
Session: a3f5b2c1...
Interactions totales: 15
Souvenirs en mémoire: 8

Mémoire:
  Court terme: 10 messages
  Long terme: 8 souvenirs
  Sujet actuel: python programmation code

Personnalité:
  openness            : [████████████████████] 0.72
  conscientiousness   : [████████████████] 0.60
  extraversion        : [██████████████] 0.55
  agreeableness       : [████████████████████] 0.82
  neuroticism         : [██████] 0.28

Ollama disponible: ✅
```

## Ingestion de document

```
[attentif] > ingest mon_article.txt
✅ 12 souvenirs créés à partir de mon_article.txt
```

## Avatar

```
[enthousiaste] > avatar

╔═══════════════════════════════╗
║  Avatar IA: 😊 enthousiaste   ║
║  Intensité: [████████░░] 0.80  ║
║  Confiance: 0.75              ║
║  Curiosité: 0.85              ║
╚═══════════════════════════════╝
```

## Évolution de la personnalité

Au fil des interactions, la personnalité de l'IA évolue :

- **Interactions positives** → Augmente `agreeableness` et `openness`
- **Questions fréquentes** → Augmente `curiosity` et `openness`
- **Corrections** → Ajuste la `confidence` et augmente l'attention
- **Enseignements** → Augmente `conscientiousness`

## Cycle d'apprentissage

1. **Interaction** → L'IA génère une réponse
2. **Émotion** → Analyse l'état émotionnel
3. **Mémoire** → Récupère les souvenirs pertinents
4. **Stockage** → Décide si stocker (basé sur importance)
5. **Apprentissage** → Enregistre l'interaction
6. **Évolution** → Met à jour la personnalité

## Conseils d'utilisation

- **Parlez naturellement** : L'IA comprend le contexte
- **Enseignez explicitement** : Utilisez `teach` pour les informations importantes
- **Corrigez les erreurs** : Utilisez `correct` pour améliorer les réponses
- **Consultez la mémoire** : Utilisez `remember` pour voir ce que l'IA a retenu
- **Surveillez les émotions** : Utilisez `emotion` pour comprendre l'état interne
- **Ingérez des documents** : Utilisez `ingest` pour enrichir la mémoire

---

**L'IA apprend et évolue à chaque interaction !** 🚀
