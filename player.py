import threading
import time
from pathlib import Path
from typing import List

import vlc
from librosa import load as LiLoad

from programation import Programation


class Player:
    """Lecteur audio pour une programmation radio avec deux séquences préchargées."""

    AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

    def __init__(self, programation: Programation, volume: int = 100):
        self.prog = programation
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(volume)
        self.buffers: List[List[vlc.Media]] = [[], []]
        self.error_record = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._play_thread = None
        self._prepare_buffers()

    def _prepare_buffers(self) -> None:
        """Charge la première et la deuxième séquence en RAM."""
        self._load_next_buffer(0)
        self._load_next_buffer(1)

    def start(self) -> None:
        """Démarre la lecture automatique de la programmation."""
        if self._play_thread and self._play_thread.is_alive():
            return
        self._stop_event.clear()
        self._play_thread = threading.Thread(target=self._play_loop, daemon=True)
        self._play_thread.start()

    def stop(self) -> None:
        """Arrête la lecture et libère le thread de lecture."""
        self._stop_event.set()
        if self.player.is_playing():
            self.player.stop()
        if self._play_thread:
            self._play_thread.join(timeout=5)
            self._play_thread = None

    def next(self) -> None:
        """Passe immédiatement à la séquence suivante."""
        with self._lock:
            self.buffers[0] = self.buffers[1]
            self.buffers[1] = []
        self._load_next_buffer(1)

    def get_buffer_status(self) -> List[int]:
        """Retourne la taille des deux buffers actifs."""
        with self._lock:
            return [len(self.buffers[0]), len(self.buffers[1])]

    def _play_loop(self) -> None:
        while not self._stop_event.is_set():
            self._ensure_buffers()
            with self._lock:
                if not self.buffers[0]:
                    time.sleep(0.5)
                    continue
                current_sequence = list(self.buffers[0])
                self.buffers[0] = []

            for media in current_sequence:
                if self._stop_event.is_set():
                    break
                self.player.set_media(media)
                self.player.play()
                self._wait_until_end_or_stop()
                self.player.stop()

            if self._stop_event.is_set():
                break

            with self._lock:
                self.buffers[0] = self.buffers[1]
                self.buffers[1] = []
            self._load_next_buffer(1)

    def _ensure_buffers(self) -> None:
        with self._lock:
            if not self.buffers[0]:
                self._load_next_buffer(0)
            if not self.buffers[1]:
                self._load_next_buffer(1)

    def _load_next_buffer(self, buffer_index: int) -> None:
        event_paths = self.prog.get_next_event()
        media_list: List[vlc.Media] = []
        for path in event_paths:
            file_path = Path(path)
            if not file_path.is_file():
                self.error_record[str(file_path)] = "Fichier introuvable"
                continue
            if not self._is_audio_valid(file_path):
                self.error_record[str(file_path)] = "Fichier audio invalide"
                continue
            media_list.append(self.instance.media_new(str(file_path.resolve())))
        with self._lock:
            self.buffers[buffer_index] = media_list

    def _is_audio_valid(self, path: Path) -> bool:
        if path.suffix.lower() not in self.AUDIO_EXTENSIONS:
            return False
        try:
            LiLoad(str(path))
            return True
        except Exception:
            return False

    def _wait_until_end_or_stop(self) -> None:
        timeout = time.time() + 60 * 10
        while not self._stop_event.is_set():
            state = self.player.get_state()
            if state in {vlc.State.Ended, vlc.State.Stopped, vlc.State.Error}:
                break
            if time.time() >= timeout:
                break
            time.sleep(0.2)

    def get_current_title(self) -> str:
        """Retourne le titre du fichier en cours de lecture."""
        media = self.player.get_media()
        if media:
            return media.get_mrl().split('/')[-1]  # Nom du fichier
        return ""

    def get_next_title(self) -> str:
        """Retourne le titre du prochain fichier à jouer."""
        with self._lock:
            if self.buffers[0]:
                media = self.buffers[0][0]
                return media.get_mrl().split('/')[-1]
        return ""

    def get_next_sequence(self) -> List[str]:
        """Retourne la prochaine séquence de fichiers."""
        return self.prog.peek_next_event()

    def get_remaining_time(self) -> int:
        """Retourne le temps restant en millisecondes pour le fichier en cours."""
        length = self.player.get_length()
        time = self.player.get_time()
        if length > 0 and time >= 0:
            return length - time
        return 0


if __name__ == "__main__":
    prog = Programation()
    player = Player(prog)
    print("Lecteur prêt. Utilisez player.start() pour lancer la lecture.")