from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import sqlite3
import json


class Programation:
    """Génère une programmation radio horaire et retourne la séquence à jouer pour la prochaine heure."""

    AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

    def __init__(
        self,
        source_folder: Optional[Union[str, Path]] = None,
        db_path: Optional[Union[str, Path]] = None,
    ):
        self.source_folder = Path(source_folder) if source_folder else Path.cwd()
        self.source_folder = self.source_folder.expanduser()
        self.db_path = Path(db_path) if db_path else Path.cwd() / "programation.db"
        self.daily_schedule: Dict[int, List[str]] = {}
        self.media_library: List[str] = []
        self._next_event_time: Optional[datetime] = None
        self._event_counter: int = 0
        self._init_db()
        self._load_from_db()
        self.reload_library()
        self.reset()

    def _init_db(self) -> None:
        """Initialise la base de données SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sequences (
                    hour INTEGER PRIMARY KEY,
                    files TEXT NOT NULL
                )
            """)
            conn.commit()

    def _load_from_db(self) -> None:
        """Charge la programmation depuis la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT hour, files FROM sequences")
            for hour, files_json in cursor:
                self.daily_schedule[hour] = json.loads(files_json)

    def _save_to_db(self) -> None:
        """Sauvegarde la programmation dans la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sequences")
            for hour, files in self.daily_schedule.items():
                conn.execute("INSERT INTO sequences (hour, files) VALUES (?, ?)",
                           (hour, json.dumps(files)))
            conn.commit()

    def reload_library(self) -> None:
        """Recharge la bibliothèque audio depuis le dossier source."""
        self.media_library = []
        if not self.source_folder.exists():
            return

        for path in sorted(self.source_folder.iterdir()):
            if path.is_file() and path.suffix.lower() in self.AUDIO_EXTENSIONS:
                self.media_library.append(str(path.resolve()))

    def set_daily_schedule(self, daily_schedule: Dict[int, List[str]]) -> None:
        """Définit une grille horaire quotidienne par heure."""
        sanitized: Dict[int, List[str]] = {}
        for hour, playlist in daily_schedule.items():
            if not isinstance(hour, int) or hour < 0 or hour > 23:
                raise ValueError("Les clés de la programmation quotidienne doivent être des heures entre 0 et 23")
            sanitized[hour] = [str(Path(item).expanduser()) for item in playlist]
        self.daily_schedule = sanitized
        self._save_to_db()
        self.reset()

    def get_sequence_for_hour(self, hour: int) -> List[str]:
        """Retourne la séquence pour une heure donnée."""
        return self.daily_schedule.get(hour, [])

    def get_sequence_for_hour(self, hour: int) -> List[str]:
        """Retourne la séquence pour une heure donnée."""
        return self.daily_schedule.get(hour, [])

    def configure_source_folder(self, folder_path: Union[str, Path]) -> None:
        """Configure le dossier source pour les médias."""
        self.source_folder = Path(folder_path).expanduser()
        self.reload_library()

    def reset(self, start_time: Optional[datetime] = None) -> None:
        """Réinitialise la programmation à l'heure suivante ou à un instant donné."""
        self._next_event_time = self._first_next_program_hour(start_time)
        self._event_counter = 0

    def get_next_event(self) -> List[str]:
        """Retourne la séquence audio à jouer pour la prochaine heure et passe à l'heure suivante."""
        event = self.__generate_next_event_content__(self._next_event_time)
        self._next_event_time += timedelta(hours=1)
        self._event_counter += 1
        return event

    def peek_next_event(self) -> List[str]:
        """Retourne la prochaine séquence sans avancer la programmation."""
        if self._next_event_time is None:
            self.reset()
        return self.__generate_next_event_content__(self._next_event_time)

    def __generate_next_event_content__(self, event_time: datetime) -> List[str]:
        """Génère le contenu du prochain créneau horaire."""
        if event_time.hour in self.daily_schedule:
            return list(self.daily_schedule[event_time.hour])

        if self.media_library:
            index = (event_time.hour + self._event_counter) % len(self.media_library)
            return [self.media_library[index]]

        return []

    @staticmethod
    def _first_next_program_hour(start_time: Optional[datetime] = None) -> datetime:
        now = start_time or datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return next_hour
