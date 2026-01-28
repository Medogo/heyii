

# ========================================
# src/audio/recorder.py
# ========================================
"""Enregistreur audio pour sauvegarder les appels."""
import wave
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional


class AudioRecorder:
    """Enregistreur audio pour les appels."""

    def __init__(self, output_dir: str = "recordings"):
        """
        Initialiser l'enregistreur.

        Args:
            output_dir: Répertoire de sortie
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.sample_rate = 8000
        self.sample_width = 2  # 16-bit
        self.channels = 1  # Mono

        self.is_recording = False
        self.current_file: Optional[wave.Wave_write] = None
        self.current_filename: Optional[str] = None
        self.audio_buffer = []

    def start_recording(self, call_id: str) -> str:
        """
        Démarrer l'enregistrement.

        Args:
            call_id: ID de l'appel

        Returns:
            Nom du fichier
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{call_id}_{timestamp}.wav"
        filepath = self.output_dir / filename

        self.current_filename = str(filepath)
        self.current_file = wave.open(str(filepath), "wb")
        self.current_file.setnchannels(self.channels)
        self.current_file.setsampwidth(self.sample_width)
        self.current_file.setframerate(self.sample_rate)

        self.is_recording = True
        self.audio_buffer = []

        print(f"🎙️  Enregistrement démarré: {filename}")

        return filename

    def add_audio_chunk(self, audio_chunk: bytes):
        """
        Ajouter un chunk audio.

        Args:
            audio_chunk: Données audio
        """
        if self.is_recording:
            self.audio_buffer.append(audio_chunk)

            # Écrire périodiquement (tous les 10 chunks)
            if len(self.audio_buffer) >= 10:
                self._flush_buffer()

    def _flush_buffer(self):
        """Écrire le buffer sur disque."""
        if self.current_file and self.audio_buffer:
            combined = b"".join(self.audio_buffer)
            self.current_file.writeframes(combined)
            self.audio_buffer = []

    def stop_recording(self) -> Optional[str]:
        """
        Arrêter l'enregistrement.

        Returns:
            Chemin du fichier ou None
        """
        if not self.is_recording:
            return None

        # Écrire le reste du buffer
        self._flush_buffer()

        if self.current_file:
            self.current_file.close()

        self.is_recording = False
        filename = self.current_filename
        self.current_file = None
        self.current_filename = None

        print(f"⏹️  Enregistrement arrêté: {filename}")

        return filename

    async def upload_to_s3(self, filename: str, s3_bucket: str) -> str:
        """
        Uploader vers S3 (placeholder).

        Args:
            filename: Nom du fichier
            s3_bucket: Nom du bucket S3

        Returns:
            URL S3
        """
        # TODO: Implémenter l'upload S3
        # Pour l'instant, retourner juste le chemin local
        return f"file://{filename}"
