"""Interfaces pour les composants principaux de la radio."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union


class PlayerInterface(ABC):
    """Interface pour le lecteur audio."""

    @abstractmethod
    def start(self) -> None:
        """Démarre la lecture automatique de la programmation."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Arrête la lecture et libère le thread de lecture."""
        pass

    @abstractmethod
    def next(self) -> None:
        """Passe immédiatement à la séquence suivante."""
        pass

    @abstractmethod
    def get_buffer_status(self) -> List[int]:
        """Retourne la taille des deux buffers actifs."""
        pass

    @abstractmethod
    def get_current_title(self) -> str:
        """Retourne le titre du fichier en cours de lecture."""
        pass

    @abstractmethod
    def get_next_title(self) -> str:
        """Retourne le titre du prochain fichier à jouer."""
        pass

    @abstractmethod
    def get_next_sequence(self) -> List[str]:
        """Retourne la prochaine séquence de fichiers."""
        pass

    @abstractmethod
    def get_remaining_time(self) -> int:
        """Retourne le temps restant en millisecondes pour le fichier en cours."""
        pass


class ProgramationInterface(ABC):
    """Interface pour la programmation radio."""

    @abstractmethod
    def reload_library(self) -> None:
        """Recharge la bibliothèque audio depuis le dossier source."""
        pass

    @abstractmethod
    def set_daily_schedule(self, daily_schedule: Dict[int, List[str]]) -> None:
        """Définit une grille horaire quotidienne par heure."""
        pass

    @abstractmethod
    def get_sequence_for_hour(self, hour: int) -> List[str]:
        """Retourne la séquence pour une heure donnée."""
        pass

    @abstractmethod
    def configure_source_folder(self, folder_path: Union[str, Path]) -> None:
        """Configure le dossier source pour les médias."""
        pass

    @abstractmethod
    def reset(self, start_time: Optional[datetime] = None) -> None:
        """Réinitialise la programmation à l'heure suivante ou à un instant donné."""
        pass

    @abstractmethod
    def get_next_event(self) -> List[str]:
        """Retourne la séquence audio à jouer pour la prochaine heure et passe à l'heure suivante."""
        pass

    @abstractmethod
    def peek_next_event(self) -> List[str]:
        """Retourne la prochaine séquence sans avancer la programmation."""
        pass
