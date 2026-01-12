"""
Interface CLI pour interagir avec l'IA personnelle.
Version non bloquante, compatible IA émotionnelle + API Unity.
"""

import threading
import queue
import time
from pathlib import Path

from consciousness.core import CoreConsciousness
from embodiment.interface import EmbodimentInterface


class CLI:
    """
    Interface en ligne de commande pour l'IA personnelle.
    """

    def __init__(self, consciousness: CoreConsciousness):
        self.consciousness = consciousness
        self.embodiment = EmbodimentInterface()
        self.running = True
        self.input_queue = queue.Queue()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def print_banner(self):
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🤖 IA PERSONNELLE AUTONOME & LOCALE 🤖              ║
║                                                              ║
║  Système cognitif incarné • Mémoire émotionnelle • Local    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        print("Tapez 'help' pour voir les commandes.")
        print("Tapez 'quit' ou 'exit' pour quitter.\n")

    def print_help(self):
        print("""
Commandes disponibles:

  talk <message>          - Parler avec l'IA
  teach <contenu>         - Enseigner quelque chose
  correct <a> | <b>       - Corriger une réponse
  remember                - Voir les souvenirs récents
  forget <id>             - Oublier un souvenir
  emotion                 - Voir l'état émotionnel
  status                  - Statut complet
  avatar                  - État avatar
  ingest <fichier>        - Ingérer un document
  batch-ingest <dir>      - Ingestion en masse
  help                    - Aide
  quit / exit             - Quitter
        """)

    # ------------------------------------------------------------------
    # INPUT THREAD
    # ------------------------------------------------------------------

    def _input_loop(self):
        while self.running:
            try:
                emotion = self.consciousness.emotion_engine.get_state()
                label = emotion.get("label", "neutre")
                prompt = f"[{label}] > "
                text = input(prompt)
                self.input_queue.put(text)
            except EOFError:
                self.running = False

    # ------------------------------------------------------------------
    # COMMANDES
    # ------------------------------------------------------------------

    def handle_talk(self, args):
        if not args:
            print("❌ Usage: talk <message>\n")
            return

        message = " ".join(args)
        print(f"\n👤 Vous: {message}\n")

        thinking = True

        def spinner():
            dots = 0
            while thinking:
                print(f"\r🤖 IA réfléchit{'.' * (dots % 4)}   ", end="", flush=True)
                dots += 1
                time.sleep(0.4)
            print("\r" + " " * 40 + "\r", end="", flush=True)

        t = threading.Thread(target=spinner, daemon=True)
        t.start()

        try:
            response = self.consciousness.process_interaction(message)
        finally:
            thinking = False
            time.sleep(0.1)

        print(f"🤖 IA: {response}\n", flush=True)

    def handle_teach(self, args):
        if not args:
            print("❌ Usage: teach <contenu>\n")
            return

        content = " ".join(args)
        file_path = Path(content)

        if file_path.exists():
            from learning.document_ingest import DocumentIngest
            ingest = DocumentIngest(self.consciousness.long_term_memory)
            count = ingest.ingest_text_file(file_path)
            print(f"✅ {count} souvenirs créés.\n")
        else:
            response = self.consciousness.teach(content)
            print(f"🤖 IA: {response}\n")

    def handle_correct(self, args):
        full = " ".join(args)
        if "|" not in full:
            print("❌ Usage: correct <input> | <correction>\n")
            return

        a, b = map(str.strip, full.split("|", 1))
        response = self.consciousness.correct(a, b)
        print(f"🤖 IA: {response}\n")

    def handle_remember(self):
        memories = self.consciousness.long_term_memory.get_all_memories(limit=10)
        if not memories:
            print("📝 Aucun souvenir.\n")
            return

        print("\n📝 Souvenirs récents:\n")
        for m in memories:
            print(f"[{m['id']}] {m['text'][:80]}...")

        print()

    def handle_emotion(self):
        e = self.consciousness.emotion_engine.get_state()
        print("\n🧠 État émotionnel:\n")
        for k, v in e.items():
            print(f"{k:15s}: {v}")
        print()

    def handle_status(self):
        status = self.consciousness.get_status()
        print("\n📊 Statut IA:\n")
        for k, v in status.items():
            print(f"{k}: {v}")
        print()

    def handle_avatar(self):
        from emotion.emotional_state import EmotionalState
        e = self.consciousness.emotion_engine.get_state()
        emo = EmotionalState(**{k: e.get(k, 0.5) for k in [
            "valence", "arousal", "dominance",
            "confidence", "curiosity", "attachment"
        ]})
        emo.intensity = e.get("intensity", 0.5)
        print(self.embodiment.render_text_avatar(emo))

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self):
        self.print_banner()

        threading.Thread(target=self._input_loop, daemon=True).start()

        while self.running:
            try:
                if not self.input_queue.empty():
                    user_input = self.input_queue.get().strip()
                    if not user_input:
                        continue

                    parts = user_input.split(maxsplit=1)
                    command = parts[0].lower()
                    args = parts[1].split() if len(parts) > 1 else []

                    if command in ("quit", "exit"):
                        print("\n👋 Sauvegarde et arrêt...")
                        self.consciousness.save_state()
                        self.running = False

                    elif command == "help":
                        self.print_help()

                    elif command == "talk":
                        self.handle_talk(args)

                    elif command == "teach":
                        self.handle_teach(args)

                    elif command == "correct":
                        self.handle_correct(args)

                    elif command == "remember":
                        self.handle_remember()

                    elif command == "emotion":
                        self.handle_emotion()

                    elif command == "status":
                        self.handle_status()

                    elif command == "avatar":
                        self.handle_avatar()

                    else:
                        print(f"\n💡 Astuce: tape 'talk {user_input}'\n")

                time.sleep(0.01)

            except KeyboardInterrupt:
                print("\n👋 Interruption, sauvegarde...")
                self.consciousness.save_state()
                break
