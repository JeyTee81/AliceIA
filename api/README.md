# 🌐 API REST pour Unity

API REST locale pour connecter votre avatar Unity à l'IA personnelle.

## 🚀 Démarrage Rapide

### 1. Installer les dépendances

```bash
pip install flask flask-cors
```

### 2. Démarrer le serveur API

```bash
python api_server.py
# ou
python main.py --api
```

Le serveur démarre sur `http://localhost:5000`

### 3. Importer dans Unity

- **Version complète** : `api/unity_client.cs` (nécessite Newtonsoft.Json)
- **Version simple** : `api/unity_client_simple.cs` (utilise uniquement JsonUtility natif)

## 📡 Endpoints

- `GET /api/health` - Vérifie que le serveur est actif
- `POST /api/talk` - Envoie un message à l'IA
- `GET /api/emotion` - Récupère l'état émotionnel
- `GET /api/avatar/state` - Récupère l'état de l'avatar
- `GET /api/status` - Statut complet de l'IA
- `POST /api/teach` - Enseigne à l'IA
- `GET /api/memories` - Récupère les souvenirs

## 📖 Documentation Complète

Voir `UNITY_INTEGRATION.md` pour le guide complet d'intégration.
