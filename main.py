"""
Point d'entrée principal de l'IA personnelle autonome.
Initialise le système et lance l'interface CLI.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from consciousness.core import CoreConsciousness
from interface.cli import CLI


def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(description="IA Personnelle Autonome & Locale")
    parser.add_argument(
        "--api",
        action="store_true",
        help="Démarrer le serveur API pour Unity au lieu de l'interface CLI"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port du serveur API (défaut: 5000)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Initialisation de l'IA personnelle...")
    
    try:
        # Initialiser la conscience centrale
        consciousness = CoreConsciousness()
        
        # Vérifier la disponibilité d'Ollama
        if not consciousness.llm.check_available():
            print("\n⚠️  ATTENTION: Ollama n'est pas disponible!")
            print("   Assurez-vous qu'Ollama est installé et démarré.")
            print("   Installation: https://ollama.ai")
            print("   Démarrer: ollama serve")
            print("\n   L'IA peut fonctionner en mode limité sans Ollama.")
            
            # En mode API, continuer automatiquement (pas d'input bloquant)
            if args.api:
                print("   Mode API: continuation automatique...")
            else:
                # Mode CLI uniquement : demander confirmation
                response = input("   Continuer quand même? (o/n): ")
                if response.lower() != 'o':
                    return
        
        # Mode API pour Unity
        if args.api:
            from api.server import APIServer
            server = APIServer(consciousness, port=args.port)
            print(f"\n🌐 Serveur API démarré sur http://localhost:{args.port}")
            print("📡 Unity peut maintenant se connecter à l'IA")
            print("\nAppuyez sur Ctrl+C pour arrêter.\n")
            server.start(blocking=True)
        else:
            # Mode CLI
            cli = CLI(consciousness)
            cli.run()
    
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt demandé par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
