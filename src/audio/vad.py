
# ========================================
# src/audio/vad.py
# ========================================
"""Voice Activity Detection."""
import webrtcvad
from typing import List, Tuple


class VAD:
    """Détecteur d'activité vocale."""

    def __init__(self, aggressiveness: int = 2):
        """
        Initialiser le VAD.

        Args:
            aggressiveness: Niveau d'agressivité (0-3)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 8000  # Standard téléphonie (8kHz)
        self.frame_duration = 20  # ms

    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Détecter si le chunk contient de la parole.

        Args:
            audio_chunk: Audio en bytes (PCM 16-bit)

        Returns:
            True si parole détectée
        """
        try:
            return self.vad.is_speech(audio_chunk, self.sample_rate)
        except Exception as e:
            print(f"❌ Erreur VAD: {e}")
            return False

    def detect_speech_segments(
            self, audio_chunks: List[bytes], padding_duration_ms: int = 300
    ) -> List[Tuple[int, int]]:
        """
        Détecter les segments de parole dans une liste de chunks.

        Args:
            audio_chunks: Liste de chunks audio
            padding_duration_ms: Padding avant/après la parole (ms)

        Returns:
            Liste de tuples (start_idx, end_idx) des segments de parole
        """
        num_padding_frames = int(padding_duration_ms / self.frame_duration)
        ring_buffer = [0] * num_padding_frames
        triggered = False
        segments = []
        start_idx = 0

        for i, chunk in enumerate(audio_chunks):
            is_speech = self.is_speech(chunk)

            ring_buffer.pop(0)
            ring_buffer.append(1 if is_speech else 0)

            num_voiced = sum(ring_buffer)

            if not triggered:
                if num_voiced > 0.9 * num_padding_frames:
                    triggered = True
                    start_idx = max(0, i - num_padding_frames)
            else:
                if num_voiced < 0.1 * num_padding_frames:
                    triggered = False
                    segments.append((start_idx, i))

        # Si toujours triggered à la fin
        if triggered:
            segments.append((start_idx, len(audio_chunks)))

        return segments
