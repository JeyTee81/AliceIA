"""
Point d'entrée pour démarrer le serveur API.
Permet à Unity de communiquer avec l'IA.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from consciousness.core import CoreConsciousness
from api.server import APIServer
import config


def main():
    """Démarre le serveur API pour Unity."""
    print("🚀 Initialisation de l'IA personnelle...")
    
    # Initialiser la conscience
    consciousness = CoreConsciousness()
    
    # Vérifier Ollama
    if not consciousness.llm.check_available():
        print("\n⚠️  ATTENTION: Ollama n'est pas disponible!")
        print("   L'API fonctionnera mais les réponses seront limitées.")
        print("   Mode API: continuation automatique...")
        # Pas d'input() en mode API - continuer automatiquement
    
    # Créer et démarrer le serveur API
    server = APIServer(
        consciousness,
        host=config.API_HOST if hasattr(config, 'API_HOST') else "localhost",
        port=config.API_PORT if hasattr(config, 'API_PORT') else 5000
    )
    
    print(f"\n🌐 Serveur API démarré sur http://{server.host}:{server.port}")
    print("📡 Unity peut maintenant se connecter à l'IA")
    print("\nEndpoints disponibles:")
    print("  POST /api/talk          - Envoyer un message")
    print("  GET  /api/emotion       - État émotionnel")
    print("  GET  /api/avatar/state  - État de l'avatar")
    print("  GET  /api/status        - Statut complet")
    print("  POST /api/teach         - Enseigner à l'IA")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur.\n")
    
    try:
        server.start(blocking=True)
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur API...")
        consciousness.save_state()
        server.stop()


if __name__ == "__main__":
    main()
