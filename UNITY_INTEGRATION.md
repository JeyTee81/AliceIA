# 🎮 Intégration Unity - Guide Complet

Ce guide explique comment connecter votre avatar Unity à l'IA personnelle.

## 🏗️ Architecture

```
Unity Avatar ←→ API REST (Flask) ←→ IA Personnelle
```

L'IA expose une API REST locale sur `http://localhost:5000` que Unity peut interroger.

---

## 🚀 Démarrage Rapide

### 1. Démarrer le serveur API

```bash
python api_server.py
```

Le serveur démarre sur `http://localhost:5000`

### 2. Importer le script Unity

1. Copiez `api/unity_client.cs` dans votre projet Unity
2. Créez un GameObject vide dans votre scène
3. Ajoutez le composant `IAPersonalClient`
4. Configurez l'URL (par défaut: `http://localhost:5000`)

### 3. Utiliser dans Unity

```csharp
// Dans votre script Unity
IAPersonalClient iaClient;

void Start()
{
    iaClient = FindObjectOfType<IAPersonalClient>();
    
    // Envoyer un message
    iaClient.SendMessage("Bonjour", (response) => {
        Debug.Log($"IA répond: {response}");
    });
    
    // Écouter les changements d'émotion
    iaClient.OnEmotionChanged.AddListener((emotion) => {
        UpdateAvatarExpression(emotion);
    });
}
```

---

## 📡 Endpoints API

### `POST /api/talk`

Envoie un message à l'IA et récupère la réponse.

**Request:**
```json
{
  "message": "Bonjour, comment vas-tu ?"
}
```

**Response:**
```json
{
  "response": "Bonjour ! Je vais bien, merci.",
  "emotion": {
    "valence": 0.65,
    "arousal": 0.5,
    "dominance": 0.5,
    "confidence": 0.55,
    "curiosity": 0.6,
    "attachment": 0.35,
    "intensity": 0.55,
    "label": "content"
  },
  "success": true
}
```

### `GET /api/emotion`

Récupère l'état émotionnel actuel.

**Response:**
```json
{
  "emotion": {
    "valence": 0.65,
    "arousal": 0.5,
    "dominance": 0.5,
    "confidence": 0.55,
    "curiosity": 0.6,
    "attachment": 0.35,
    "intensity": 0.55,
    "label": "content"
  },
  "success": true
}
```

### `GET /api/avatar/state`

Récupère l'état complet de l'avatar pour les animations Unity.

**Response:**
```json
{
  "avatar": {
    "expression": "content",
    "animation": "idle",
    "intensity": 0.55,
    "eye_brightness": 0.9,
    "mouth_shape": "neutral",
    "head_tilt": 0.0
  },
  "emotion": { ... },
  "success": true
}
```

### `POST /api/teach`

Enseigne quelque chose à l'IA.

**Request:**
```json
{
  "content": "Python est un langage de programmation",
  "importance": 0.8
}
```

### `GET /api/status`

Récupère le statut complet de l'IA.

### `GET /api/memories?limit=10`

Récupère les souvenirs récents.

---

## 🎭 Mapping Émotions → Animations Unity

### Expressions disponibles

- `neutre` → Animation neutre/idle
- `enthousiaste` → Animation joyeuse, sourire
- `serein` → Animation calme, détendue
- `content` → Animation positive, légèrement souriante
- `curieux` → Animation interrogative, tête penchée
- `attentif` → Animation concentrée, yeux ouverts
- `inquiet` → Animation préoccupée, sourcils froncés
- `mélancolique` → Animation triste, regard baissé
- `confiant` → Animation assurée, posture droite

### Paramètres d'animation

```csharp
public class AvatarController : MonoBehaviour
{
    IAPersonalClient iaClient;
    Animator animator;
    
    void Start()
    {
        iaClient = FindObjectOfType<IAPersonalClient>();
        animator = GetComponent<Animator>();
        
        // Écouter les changements d'état
        iaClient.OnAvatarStateChanged.AddListener(UpdateAvatar);
    }
    
    void UpdateAvatar(AvatarState state)
    {
        // Expression faciale
        animator.SetTrigger(state.expression);
        
        // Intensité (pour blend trees)
        animator.SetFloat("Intensity", state.intensity);
        
        // Head tilt
        animator.SetFloat("HeadTilt", state.head_tilt);
        
        // Eye brightness (pour shaders)
        // SetMaterialProperty("_EyeBrightness", state.eye_brightness);
        
        // Mouth shape (pour blend shapes)
        // SetBlendShape("Mouth", GetMouthBlendValue(state.mouth_shape));
    }
    
    float GetMouthBlendValue(string shape)
    {
        return shape switch
        {
            "smile" => 1.0f,
            "neutral" => 0.5f,
            "frown" => 0.0f,
            _ => 0.5f
        };
    }
}
```

---

## 🔄 Mise à jour en Temps Réel

Le script `IAPersonalClient` met automatiquement à jour l'état de l'avatar toutes les 0.5 secondes (configurable).

Vous pouvez aussi mettre à jour manuellement :

```csharp
// Mise à jour manuelle
iaClient.GetEmotion((emotion) => {
    // Traiter l'émotion
});
```

---

## 🎨 Exemple Complet Unity

```csharp
using UnityEngine;
using UnityEngine.UI;

public class AvatarManager : MonoBehaviour
{
    [Header("Références")]
    public IAPersonalClient iaClient;
    public Animator avatarAnimator;
    public Text dialogueText;
    public InputField inputField;
    
    [Header("Paramètres")]
    public float emotionUpdateRate = 0.5f;
    
    private EmotionState currentEmotion;
    
    void Start()
    {
        // Trouver le client IA
        if (iaClient == null)
            iaClient = FindObjectOfType<IAPersonalClient>();
        
        // Écouter les événements
        iaClient.OnEmotionChanged.AddListener(OnEmotionChanged);
        iaClient.OnResponseReceived.AddListener(OnResponseReceived);
        iaClient.OnAvatarStateChanged.AddListener(OnAvatarStateChanged);
    }
    
    void OnEmotionChanged(EmotionState emotion)
    {
        currentEmotion = emotion;
        
        // Mettre à jour l'animation basée sur l'émotion
        UpdateAnimation(emotion);
    }
    
    void OnResponseReceived(string response)
    {
        // Afficher la réponse
        dialogueText.text = response;
        
        // Déclencher animation de parole
        avatarAnimator.SetTrigger("Speaking");
    }
    
    void OnAvatarStateChanged(AvatarState state)
    {
        // Mettre à jour les paramètres d'animation
        avatarAnimator.SetFloat("Intensity", state.intensity);
        avatarAnimator.SetFloat("HeadTilt", state.head_tilt);
        
        // Changer l'expression
        avatarAnimator.SetTrigger(state.expression);
    }
    
    void UpdateAnimation(EmotionState emotion)
    {
        // Mapping émotion → paramètres d'animation
        avatarAnimator.SetFloat("Valence", emotion.valence);
        avatarAnimator.SetFloat("Arousal", emotion.arousal);
        avatarAnimator.SetFloat("Intensity", emotion.intensity);
    }
    
    // Appelé depuis un bouton UI
    public void SendMessage()
    {
        string message = inputField.text;
        if (!string.IsNullOrEmpty(message))
        {
            iaClient.SendMessage(message);
            inputField.text = "";
        }
    }
}
```

---

## 🔧 Configuration

### Modifier le port de l'API

Dans `config.py` :
```python
API_PORT = 5000  # Changez le port si nécessaire
```

### Modifier l'URL dans Unity

Dans l'inspecteur Unity, modifiez le champ `Api Url` du composant `IAPersonalClient`.

---

## 📦 Dépendances Unity

Pour utiliser le script Unity, vous devez installer :

1. **Newtonsoft.Json** (pour la désérialisation JSON)
   - Via Package Manager : `com.unity.nuget.newtonsoft-json`

Ou utilisez `JsonUtility` (natif Unity) en modifiant légèrement le script.

---

## 🎯 Workflow Recommandé

1. **Démarrer l'IA** : `python api_server.py`
2. **Démarrer Unity** : Ouvrir votre projet
3. **Tester la connexion** : Le script vérifie automatiquement au démarrage
4. **Intégrer les animations** : Connecter les événements aux animations
5. **Personnaliser** : Adapter les mappings émotion → animation selon votre avatar

---

## 🐛 Dépannage

### Unity ne se connecte pas

- Vérifiez que le serveur API est démarré
- Vérifiez l'URL dans Unity (doit être `http://localhost:5000`)
- Vérifiez les logs Unity pour les erreurs

### Erreurs CORS

Le serveur utilise `flask-cors` pour autoriser les requêtes depuis Unity. Si vous avez des problèmes, vérifiez que `flask-cors` est installé.

### L'IA ne répond pas

- Vérifiez qu'Ollama est démarré : `ollama serve`
- Vérifiez les logs du serveur API
- Testez l'API avec curl ou Postman

---

## 🚀 Exemple avec Curl

Testez l'API depuis la ligne de commande :

```bash
# Vérifier la santé
curl http://localhost:5000/api/health

# Envoyer un message
curl -X POST http://localhost:5000/api/talk \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour"}'

# Récupérer l'émotion
curl http://localhost:5000/api/emotion

# Récupérer l'état de l'avatar
curl http://localhost:5000/api/avatar/state
```

---

## 📝 Notes

- L'API est **100% locale** - aucune donnée ne quitte votre machine
- Le serveur doit être démarré avant Unity
- Les émotions sont mises à jour en temps réel
- Vous pouvez personnaliser les mappings émotion → animation selon vos besoins

---

**🎮 Prêt à créer votre avatar intelligent !**
