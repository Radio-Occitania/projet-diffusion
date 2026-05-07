"""Interface graphique pour la programmation radio."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, List, Optional
from programation import Programation


class ProgramationGUI:
    """Interface graphique pour gérer la programmation radio."""

    def __init__(self, root: tk.Tk, programation: Optional[Programation] = None):
        """Initialise l'interface graphique de la programmation.
        
        Args:
            root: La fenêtre tkinter principale
            programation: Instance de Programation (optionnelle)
        """
        self.root = root
        self.root.title("📻 Programmation Radio")
        self.root.geometry("800x800")
        self.root.resizable(True, True)
        
        # Initialiser la programmation
        self.prog = programation or Programation()
        self.current_time_selected = 0
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")

        self._create_widgets()
        self._load_schedule()

    def _create_widgets(self) -> None:
        """Crée les éléments de l'interface graphique."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        title_label = ttk.Label(
            main_frame,
            text="📻 Programmation Radio",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Frame pour la source
        source_frame = ttk.LabelFrame(main_frame, text="Configuration source", padding="10")
        source_frame.pack(fill=tk.X, pady=10)

        ttk.Label(source_frame, text="Dossier source:").grid(row=0, column=0, sticky="w")
        self.source_var = tk.StringVar(value=str(self.prog.source_folder))
        ttk.Entry(source_frame, textvariable=self.source_var, width=50, state=tk.DISABLED).grid(row=0, column=1, padx=10)

        browse_button = ttk.Button(
            source_frame,
            text="📁 Parcourir",
            command=self._on_browse_folder
        )
        browse_button.grid(row=0, column=2, padx=5)

        reload_button = ttk.Button(
            source_frame,
            text="🔄 Recharger",
            command=self._on_reload_library
        )
        reload_button.grid(row=0, column=3, padx=5)

        # Frame pour les horaires
        hours_frame = ttk.LabelFrame(main_frame, text="Sélectionner un horaire", padding="10")
        hours_frame.pack(fill=tk.X, pady=10)

        ttk.Label(hours_frame, text="Heure:").grid(row=0, column=0, sticky="w")
        self.hour_spin = tk.Spinbox(
            hours_frame,
            from_=0,
            to=23,
            textvariable=self.hour_var,
            width=3,
            format="%02.0f",
        )
        self.hour_spin.grid(row=0, column=1, padx=(5, 0))

        ttk.Label(hours_frame, text=":").grid(row=0, column=2)
        self.minute_spin = tk.Spinbox(
            hours_frame,
            from_=0,
            to=59,
            textvariable=self.minute_var,
            width=3,
            format="%02.0f",
        )
        self.minute_spin.grid(row=0, column=3, padx=(0, 5))

        ttk.Button(hours_frame, text="⏱️ Choisir", command=self._on_time_selected).grid(row=0, column=4, padx=5)
        ttk.Button(hours_frame, text="➕ Ajouter fichier", command=self._on_add_file).grid(row=0, column=5, padx=5)
        ttk.Button(hours_frame, text="❌ Effacer le créneau", command=self._on_clear_time).grid(row=0, column=6, padx=5)

        # Frame pour la liste des fichiers
        files_frame = ttk.LabelFrame(main_frame, text="Fichiers pour l'heure sélectionnée", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Treeview pour afficher les fichiers
        self.files_tree = ttk.Treeview(files_frame, columns=("Fichier", "Chemin"), height=10)
        self.files_tree.column("#0", width=50)
        self.files_tree.heading("#0", text="N°")
        self.files_tree.column("Fichier", width=150)
        self.files_tree.heading("Fichier", text="Nom du fichier")
        self.files_tree.column("Chemin", width=500)
        self.files_tree.heading("Chemin", text="Chemin complet")

        self.files_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar pour le treeview
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_tree.config(yscrollcommand=scrollbar.set)

        # Frame pour les actions
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            action_frame,
            text="🗑️ Supprimer sélection",
            command=self._on_remove_file
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="⬆️ Monter",
            command=self._on_move_up
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="⬇️ Descendre",
            command=self._on_move_down
        ).pack(side=tk.LEFT, padx=5)

        # Frame pour les boutons d'action
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            bottom_frame,
            text="💾 Enregistrer",
            command=self._on_save
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            bottom_frame,
            text="📊 Afficher statistiques",
            command=self._on_show_stats
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            bottom_frame,
            text="❓ À propos",
            command=self._on_about
        ).pack(side=tk.LEFT, padx=5)

    def _on_browse_folder(self) -> None:
        """Ouvre le dialogue de sélection de dossier."""
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.prog.configure_source_folder(folder)
            self.source_var.set(str(self.prog.source_folder))
            self._on_reload_library()

    def _on_reload_library(self) -> None:
        """Recharge la bibliothèque."""
        self.prog.reload_library()
        messagebox.showinfo("Succès", f"Bibliothèque rechargée: {len(self.prog.media_library)} fichiers trouvés")

    def _on_time_selected(self) -> None:
        """Met à jour la liste des fichiers pour l'horaire sélectionné."""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Attention", "Veuillez entrer un horaire valide (HH:MM)")
            return

        self.current_time_selected = hour * 60 + minute
        self._load_files_for_time()

    def _load_files_for_time(self) -> None:
        """Charge les fichiers pour l'horaire sélectionné."""
        self.files_tree.delete(*self.files_tree.get_children())
        sequence = self.prog.get_sequence_for_time(self.current_time_selected)
        for i, file_path in enumerate(sequence, 1):
            path_obj = Path(file_path)
            self.files_tree.insert("", tk.END, text=str(i), values=(path_obj.name, file_path))

    def _on_add_file(self) -> None:
        """Ajoute un fichier à l'horaire sélectionné."""
        if self.current_time_selected is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un horaire")
            return

        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier audio",
            filetypes=[("Fichiers audio", "*.mp3 *.wav *.flac *.ogg *.m4a"), ("Tous", "*")]
        )
        
        if file_path:
            sequence = list(self.prog.get_sequence_for_time(self.current_time_selected))
            sequence.append(file_path)
            self.prog.set_sequence_for_time(self.current_time_selected, sequence)
            self._load_files_for_time()

    def _on_remove_file(self) -> None:
        """Supprime le fichier sélectionné."""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un fichier à supprimer")
            return

        sequence = list(self.prog.get_sequence_for_time(self.current_time_selected))
        for item in selection:
            index = int(self.files_tree.item(item)["text"]) - 1
            if 0 <= index < len(sequence):
                sequence.pop(index)

        self.prog.set_sequence_for_time(self.current_time_selected, sequence)
        self._load_files_for_time()

    def _on_move_up(self) -> None:
        """Remonte le fichier sélectionné."""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un fichier")
            return

        item = selection[0]
        index = int(self.files_tree.item(item)["text"]) - 1
        
        if index > 0:
            sequence = list(self.prog.get_sequence_for_time(self.current_time_selected))
            sequence[index], sequence[index - 1] = sequence[index - 1], sequence[index]
            self.prog.set_sequence_for_time(self.current_time_selected, sequence)
            self._load_files_for_time()

    def _on_move_down(self) -> None:
        """Descend le fichier sélectionné."""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un fichier")
            return

        item = selection[0]
        index = int(self.files_tree.item(item)["text"]) - 1
        sequence = list(self.prog.get_sequence_for_time(self.current_time_selected))
        
        if index < len(sequence) - 1:
            sequence[index], sequence[index + 1] = sequence[index + 1], sequence[index]
            self.prog.set_sequence_for_time(self.current_time_selected, sequence)
            self._load_files_for_time()

    def _on_clear_time(self) -> None:
        """Efface tous les fichiers de l'horaire sélectionné."""
        if self.current_time_selected is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un horaire")
            return

        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir effacer ce créneau?"):
            self.prog.set_sequence_for_time(self.current_time_selected, [])
            self._load_files_for_time()

    def _on_save(self) -> None:
        """Enregistre la programmation."""
        try:
            self.prog.save_schedule()
            messagebox.showinfo("Succès", "Programmation enregistrée avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {e}")

    def _on_show_stats(self) -> None:
        """Affiche les statistiques."""
        stats = f"""📊 Statistiques de programmation:

Bibliothèque: {len(self.prog.media_library)} fichiers
Dossier: {self.prog.source_folder}

Programmation horaire:
"""
        for minute in sorted(self.prog.daily_schedule.keys()):
            seq = self.prog.daily_schedule[minute]
            stats += f"\n{self.prog._format_time_key(minute)} → {len(seq)} fichier(s)"

        messagebox.showinfo("Statistiques", stats)

    def _on_about(self) -> None:
        """Affiche l'à propos."""
        messagebox.showinfo(
            "À propos",
            "📻 Programmation Radio v1.0\n\n"
            "Interface de gestion de la programmation radio\n"
            "pour Radio Occitania\n\n"
            "© 2026"
        )

    def _load_schedule(self) -> None:
        """Charge la programmation initiale."""
        if self.prog.daily_schedule:
            first_time = sorted(self.prog.daily_schedule)[0]
        else:
            first_time = 0
        self.current_time_selected = first_time
        self.hour_var.set(f"{first_time // 60:02d}")
        self.minute_var.set(f"{first_time % 60:02d}")
        self._load_files_for_time()

    def run(self) -> None:
        """Lance l'interface graphique."""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    gui = ProgramationGUI(root)
    gui.run()
