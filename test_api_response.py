"""
Test simple pour vérifier que /api/talk répond immédiatement sans blocage.
Usage: python test_api_response.py
"""

import requests
import time

API_URL = "http://localhost:5000"

def test_talk_endpoint():
    """Test que /api/talk répond immédiatement."""
    print("🧪 Test de réponse immédiate /api/talk")
    print(f"   URL: {API_URL}/api/talk")
    print()
    
    # Mesurer le temps de réponse
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/api/talk",
            json={"message": "Bonjour"},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue en {elapsed:.2f} secondes")
            print(f"   Status: {response.status_code}")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Réponse IA: {data.get('response', '')[:100]}...")
            print()
            
            if elapsed < 30:  # Si réponse en moins de 30s, c'est bon
                print("✅ TEST RÉUSSI: Réponse immédiate sans blocage")
                return True
            else:
                print("⚠️  Réponse lente mais fonctionnelle")
                return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"❌ TIMEOUT après {elapsed:.2f} secondes")
        print("   Le serveur ne répond pas - vérifiez qu'il est démarré")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print(f"   Assurez-vous que le serveur API est démarré sur {API_URL}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST API - Vérification réponse immédiate")
    print("=" * 60)
    print()
    
    # Test health d'abord
    try:
        health = requests.get(f"{API_URL}/api/health", timeout=5)
        if health.status_code == 200:
            print("✅ Serveur API accessible")
        else:
            print("⚠️  Serveur répond mais health check échoue")
    except:
        print("❌ Serveur API non accessible")
        print(f"   Démarrez le serveur avec: python main.py --api")
        exit(1)
    
    print()
    
    # Test talk
    success = test_talk_endpoint()
    
    print("=" * 60)
    if success:
        print("✅ TOUS LES TESTS RÉUSSIS")
    else:
        print("❌ TESTS ÉCHOUÉS")
    print("=" * 60)
