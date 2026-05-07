from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import sqlite3
import json


class Programation:
    """Génère une programmation radio et retourne la séquence à jouer pour le prochain créneau."""

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
                    start_time TEXT PRIMARY KEY,
                    files TEXT NOT NULL
                )
            """)
            conn.commit()

    def _load_from_db(self) -> None:
        """Charge la programmation depuis la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT start_time, files FROM sequences")
            for time_text, files_json in cursor:
                minute = self._normalize_time_key(time_text)
                self.daily_schedule[minute] = json.loads(files_json)

    def _save_to_db(self) -> None:
        """Sauvegarde la programmation dans la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sequences")
            for minute, files in self.daily_schedule.items():
                conn.execute(
                    "INSERT INTO sequences (start_time, files) VALUES (?, ?)",
                    (self._format_time_key(minute), json.dumps(files)),
                )
            conn.commit()

    def reload_library(self) -> None:
        """Recharge la bibliothèque audio depuis le dossier source."""
        self.media_library = []
        if not self.source_folder.exists():
            return

        for path in sorted(self.source_folder.iterdir()):
            if path.is_file() and path.suffix.lower() in self.AUDIO_EXTENSIONS:
                self.media_library.append(str(path.resolve()))

    @staticmethod
    def _normalize_time_key(time_key: Union[int, str]) -> int:
        if isinstance(time_key, int):
            if 0 <= time_key <= 23:
                return time_key * 60
            if 0 <= time_key < 1440:
                return time_key
            raise ValueError("La clé de temps doit être un entier entre 0 et 1439 ou une heure entre 0 et 23")

        parts = time_key.split(":")
        if len(parts) == 1:
            hour = int(parts[0])
            minute = 0
        elif len(parts) == 2:
            hour = int(parts[0])
            minute = int(parts[1])
        else:
            raise ValueError("Format de temps invalide, attendu HH:MM")

        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError("L'heure doit être entre 00:00 et 23:59")
        return hour * 60 + minute

    @staticmethod
    def _format_time_key(minute_of_day: int) -> str:
        hour = minute_of_day // 60
        minute = minute_of_day % 60
        return f"{hour:02d}:{minute:02d}"

    def set_daily_schedule(self, daily_schedule: Dict[Union[int, str], List[str]]) -> None:
        """Définit une grille horaire quotidienne à minutes près."""
        sanitized: Dict[int, List[str]] = {}
        for time_key, playlist in daily_schedule.items():
            minute = self._normalize_time_key(time_key)
            sanitized[minute] = [str(Path(item).expanduser()) for item in playlist]
        self.daily_schedule = sanitized
        self._save_to_db()
        self.reset()

    def get_sequence_for_time(self, time_key: Union[int, str]) -> List[str]:
        """Retourne la séquence pour une heure/minute donnée."""
        minute = self._normalize_time_key(time_key)
        return list(self.daily_schedule.get(minute, []))

    def set_sequence_for_time(self, time_key: Union[int, str], files: List[str]) -> None:
        """Définit et sauvegarde la séquence pour un horaire précis."""
        minute = self._normalize_time_key(time_key)
        self.daily_schedule[minute] = [str(Path(f).expanduser()) for f in files]
        self._save_to_db()

    def save_schedule(self) -> None:
        """Sauvegarde la programmation actuelle dans la base de données."""
        self._save_to_db()

    def configure_source_folder(self, folder_path: Union[str, Path]) -> None:
        """Configure le dossier source pour les médias."""
        self.source_folder = Path(folder_path).expanduser()
        self.reload_library()

    def reset(self, start_time: Optional[datetime] = None) -> None:
        """Réinitialise la programmation au prochain créneau planifié."""
        now = start_time or datetime.now()
        self._next_event_time = self._next_schedule_time(now)
        self._event_counter = 0

    def get_next_event(self) -> List[str]:
        """Retourne la séquence audio à jouer pour le prochain créneau et avance."""
        _, event = self.get_next_event_with_time()
        return event

    def get_next_event_with_time(self) -> tuple[datetime, List[str]]:
        """Retourne la prochaine séquence programmée et son horaire, puis avance."""
        if self._next_event_time is None:
            self.reset()

        event_time = self._next_event_time
        event = self.__generate_next_event_content__(event_time)
        self._next_event_time = self._next_schedule_time(event_time + timedelta(seconds=1))
        self._event_counter += 1
        return event_time, event

    def peek_next_event(self) -> List[str]:
        """Retourne la prochaine séquence sans avancer la programmation."""
        if self._next_event_time is None:
            self.reset()
        return self.__generate_next_event_content__(self._next_event_time)

    def peek_next_event_time(self) -> datetime:
        """Retourne l'heure du prochain créneau sans avancer."""
        if self._next_event_time is None:
            self.reset()
        return self._next_event_time

    def get_schedule_times(self) -> List[str]:
        """Retourne les horaires programmés au format HH:MM."""
        return [self._format_time_key(minute) for minute in sorted(self.daily_schedule.keys())]

    def _next_schedule_time(self, now: datetime) -> datetime:
        if not self.daily_schedule:
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_hour

        today_minutes = now.hour * 60 + now.minute
        keys = sorted(self.daily_schedule.keys())
        next_minute = None
        for minute in keys:
            if minute > today_minutes or (minute == today_minutes and now.second == 0 and now.microsecond == 0):
                next_minute = minute
                break

        if next_minute is None:
            # Aucune séquence future aujourd'hui, jouer immédiatement la dernière séquence passée
            past_minutes = [m for m in keys if m <= today_minutes]
            if past_minutes:
                next_minute = max(past_minutes)  # Jouer immédiatement la dernière séquence passée
            else:
                next_minute = keys[0]  # Aucune séquence passée, prendre la première demain
                now = now + timedelta(days=1)

        return now.replace(hour=next_minute // 60, minute=next_minute % 60, second=0, microsecond=0)

    def __generate_next_event_content__(self, event_time: datetime) -> List[str]:
        """Génère le contenu du prochain créneau programmé."""
        minute = event_time.hour * 60 + event_time.minute
        if minute in self.daily_schedule:
            return list(self.daily_schedule[minute])

        if self.media_library:
            index = (minute + self._event_counter) % len(self.media_library)
            return [self.media_library[index]]

        return []
