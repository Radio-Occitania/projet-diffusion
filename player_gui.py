"""Interface graphique pour le lecteur audio."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from player import Player
from programation import Programation


class PlayerGUI:
    """Interface graphique pour contrôler le lecteur audio."""

    def __init__(self, root: tk.Tk, programation: Optional[Programation] = None):
        """Initialise l'interface graphique du lecteur.
        
        Args:
            root: La fenêtre tkinter principale
            programation: Instance de Programation (optionnelle)
        """
        self.root = root
        self.root.title("🎙️ Lecteur Radio - Diffusion")
        self.root.geometry("600x500")
        self.root.resizable(True, False)
        
        # Initialiser la programmation et le lecteur
        self.prog = programation or Programation()
        self.player = Player(self.prog)
        self.is_playing = False
        
        self._create_widgets()
        self._update_display()

    def _create_widgets(self) -> None:
        """Crée les éléments de l'interface graphique."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        title_label = ttk.Label(
            main_frame,
            text="🎙️ Lecteur Audio",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Frame pour le statut
        status_frame = ttk.LabelFrame(main_frame, text="Statut de lecture", padding="10")
        status_frame.pack(fill=tk.X, pady=10)

        ttk.Label(status_frame, text="En cours:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.current_title_var = tk.StringVar(value="Aucun fichier")
        ttk.Label(status_frame, textvariable=self.current_title_var, foreground="green").grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(status_frame, text="Suivant:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.next_title_var = tk.StringVar(value="Aucun fichier")
        ttk.Label(status_frame, textvariable=self.next_title_var, foreground="blue").grid(row=1, column=1, sticky="w", padx=10, pady=(10, 0))

        ttk.Label(status_frame, text="Temps restant:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.time_var = tk.StringVar(value="0s")
        ttk.Label(status_frame, textvariable=self.time_var, foreground="orange").grid(row=2, column=1, sticky="w", padx=10, pady=(10, 0))

        # Frame pour les buffers
        buffer_frame = ttk.LabelFrame(main_frame, text="État des buffers", padding="10")
        buffer_frame.pack(fill=tk.X, pady=10)

        ttk.Label(buffer_frame, text="Buffer 1:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.buffer1_var = tk.StringVar(value="0 fichiers")
        ttk.Label(buffer_frame, textvariable=self.buffer1_var).grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(buffer_frame, text="Buffer 2:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.buffer2_var = tk.StringVar(value="0 fichiers")
        ttk.Label(buffer_frame, textvariable=self.buffer2_var).grid(row=1, column=1, sticky="w", padx=10, pady=(10, 0))

        # Frame pour les contrôles
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles", padding="10")
        control_frame.pack(fill=tk.X, pady=10)

        self.play_button = ttk.Button(
            control_frame,
            text="▶️ Démarrer",
            command=self._on_start,
            width=15
        )
        self.play_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(
            control_frame,
            text="⏹️ Arrêter",
            command=self._on_stop,
            width=15,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.next_button = ttk.Button(
            control_frame,
            text="⏭️ Suivant",
            command=self._on_next,
            width=15
        )
        self.next_button.grid(row=0, column=2, padx=5, pady=5)

        # Frame pour le volume
        volume_frame = ttk.LabelFrame(main_frame, text="Volume", padding="10")
        volume_frame.pack(fill=tk.X, pady=10)

        self.volume_slider = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_volume_change,
            length=300
        )
        self.volume_slider.set(100)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        self.volume_label = ttk.Label(volume_frame, text="100%", width=5)
        self.volume_label.pack(side=tk.LEFT, padx=10)

        # Frame pour les informations
        info_frame = ttk.LabelFrame(main_frame, text="Informations", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.info_text = tk.Text(info_frame, height=6, width=70, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar pour le texte
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)

    def _on_start(self) -> None:
        """Démarre la lecture."""
        try:
            self.player.start()
            self.is_playing = True
            self.play_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self._add_info("▶️ Lecture démarrée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur au démarrage: {e}")

    def _on_stop(self) -> None:
        """Arrête la lecture."""
        try:
            self.player.stop()
            self.is_playing = False
            self.play_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self._add_info("⏹️ Lecture arrêtée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur à l'arrêt: {e}")

    def _on_next(self) -> None:
        """Passe à la séquence suivante."""
        try:
            self.player.next()
            self._add_info("⏭️ Passage à la séquence suivante")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")

    def _on_volume_change(self, value: str) -> None:
        """Change le volume."""
        volume = int(float(value))
        self.player.player.audio_set_volume(volume)
        self.volume_label.config(text=f"{volume}%")

    def _add_info(self, message: str) -> None:
        """Ajoute un message aux informations."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)

    def _update_display(self) -> None:
        """Met à jour l'affichage en temps réel."""
        try:
            # Mise à jour du titre en cours
            current = self.player.get_current_title()
            self.current_title_var.set(current or "En attente...")

            # Mise à jour du titre suivant
            next_title = self.player.get_next_title()
            self.next_title_var.set(next_title or "Aucun")

            # Mise à jour du temps restant
            remaining = self.player.get_remaining_time()
            remaining_seconds = remaining // 1000
            self.time_var.set(f"{remaining_seconds}s")

            # Mise à jour des buffers
            buffer_status = self.player.get_buffer_status()
            self.buffer1_var.set(f"{buffer_status[0]} fichiers")
            self.buffer2_var.set(f"{buffer_status[1]} fichiers")

        except Exception as e:
            self._add_info(f"⚠️ Erreur de mise à jour: {e}")

        # Planifier la prochaine mise à jour
        self.root.after(1000, self._update_display)

    def run(self) -> None:
        """Lance l'interface graphique."""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    gui = PlayerGUI(root)
    gui.run()
