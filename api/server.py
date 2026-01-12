"""
Serveur API REST pour Unity avec IA émotionnelle.
Thread-safe, stable, flush correct pour éviter blocage Unity.
"""

from flask import Flask, request, jsonify
from pathlib import Path
import threading
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from consciousness.core import CoreConsciousness

# CORS
try:
    from flask_cors import CORS
    cors_available = True
except ImportError:
    cors_available = False
    print("⚠️ flask-cors non installé (pip install flask-cors)")

class APIServer:
    def __init__(self, consciousness: CoreConsciousness,
                 host: str = "localhost",
                 port: int = 5000):
        self.consciousness = consciousness
        self.host = host
        self.port = port
        self.app = Flask(__name__)

        # 🔒 Verrou global pour l'IA
        self.ia_lock = threading.Lock()

        # CORS
        if cors_available:
            CORS(self.app)
        else:
            @self.app.after_request
            def cors_headers(response):
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                return response

        self._setup_routes()

    # ---------------------------
    # ROUTES
    # ---------------------------
    def _setup_routes(self):
        @self.app.route("/api/health", methods=["GET"])
        def health():
            return jsonify({
                "status": "ok",
                "llm_available": self.consciousness.llm.check_available()
            })

        @self.app.route("/api/talk", methods=["POST"])
        def talk():
            data = request.json
            if not data or "message" not in data:
                return jsonify({"error": "Message requis", "success": False}), 400

            try:
                with self.ia_lock:
                    response_text = self.consciousness.process_interaction(data["message"])
                    emotion = self.consciousness.emotion_engine.get_state()

                # Retour immédiat à Unity
                return jsonify({
                    "response": response_text,
                    "emotion": emotion,
                    "success": True
                })

            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route("/api/teach", methods=["POST"])
        def teach():
            data = request.json
            if not data or "content" not in data:
                return jsonify({"error": "Contenu requis", "success": False}), 400

            try:
                with self.ia_lock:
                    response_text = self.consciousness.teach(
                        data["content"],
                        data.get("importance", 0.7)
                    )

                return jsonify({"response": response_text, "success": True})

            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route("/api/emotion", methods=["GET"])
        def emotion():
            try:
                with self.ia_lock:
                    emo = self.consciousness.emotion_engine.get_state()
                return jsonify({"emotion": emo, "success": True})
            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route("/api/status", methods=["GET"])
        def status():
            try:
                with self.ia_lock:
                    stat = self.consciousness.get_status()
                return jsonify({"status": stat, "success": True})
            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route("/api/memories", methods=["GET"])
        def memories():
            try:
                limit = request.args.get("limit", 10, type=int)
                with self.ia_lock:
                    mems = self.consciousness.long_term_memory.get_all_memories(limit=limit)
                return jsonify({"memories": mems, "success": True})
            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route("/api/avatar/state", methods=["GET"])
        def avatar_state():
            try:
                from emotion.emotional_state import EmotionalState
                from embodiment.avatar_state import AvatarState

                with self.ia_lock:
                    emotion = self.consciousness.emotion_engine.get_state()

                emo = EmotionalState(
                    valence=emotion.get("valence", 0.5),
                    arousal=emotion.get("arousal", 0.5),
                    dominance=emotion.get("dominance", 0.5),
                    confidence=emotion.get("confidence", 0.5),
                    curiosity=emotion.get("curiosity", 0.5),
                    attachment=emotion.get("attachment", 0.3)
                )
                emo.intensity = emotion.get("intensity", 0.5)

                avatar = AvatarState()
                avatar.update_from_emotion(emo)

                return jsonify({
                    "avatar": avatar.to_dict(),
                    "emotion": emotion,
                    "success": True
                })
            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

    # ---------------------------
    # START / STOP
    # ---------------------------
    def start(self, blocking: bool = True):
        print(f"🌐 Serveur API démarré sur http://{self.host}:{self.port}")
        sys.stdout.flush()
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False,
            threaded=True,      # 🔹 essentiel pour requêtes concurrentes
            use_reloader=False  # 🔹 évite double processus
        )

    def stop(self):
        """Arrête le serveur (Ctrl+C ou SIGTERM)."""
        pass
