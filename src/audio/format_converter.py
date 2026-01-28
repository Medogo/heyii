
# ========================================
# src/audio/format_converter.py
# ========================================
"""Conversion de formats audio."""
import base64
import audioop


class AudioFormatConverter:
    """Convertisseur de formats audio."""

    @staticmethod
    def mulaw_to_pcm(mulaw_data: bytes, sample_width: int = 2) -> bytes:
        """
        Convertir mu-law en PCM.

        Args:
            mulaw_data: Données mu-law
            sample_width: Largeur d'échantillon (bytes)

        Returns:
            Données PCM
        """
        return audioop.ulaw2lin(mulaw_data, sample_width)

    @staticmethod
    def pcm_to_mulaw(pcm_data: bytes, sample_width: int = 2) -> bytes:
        """
        Convertir PCM en mu-law.

        Args:
            pcm_data: Données PCM
            sample_width: Largeur d'échantillon (bytes)

        Returns:
            Données mu-law
        """
        return audioop.lin2ulaw(pcm_data, sample_width)

    @staticmethod
    def decode_base64_audio(base64_audio: str) -> bytes:
        """
        Décoder audio base64.

        Args:
            base64_audio: Audio encodé en base64

        Returns:
            Audio en bytes
        """
        return base64.b64decode(base64_audio)

    @staticmethod
    def encode_base64_audio(audio_bytes: bytes) -> str:
        """
        Encoder audio en base64.

        Args:
            audio_bytes: Audio en bytes

        Returns:
            Audio encodé en base64
        """
        return base64.b64encode(audio_bytes).decode("utf-8")

    @staticmethod
    def resample_audio(
            audio_data: bytes,
            orig_rate: int,
            new_rate: int,
            sample_width: int = 2,
    ) -> bytes:
        """
        Ré-échantillonner l'audio.

        Args:
            audio_data: Données audio
            orig_rate: Fréquence d'origine
            new_rate: Nouvelle fréquence
            sample_width: Largeur d'échantillon

        Returns:
            Audio ré-échantillonné
        """
        return audioop.ratecv(
            audio_data, sample_width, 1, orig_rate, new_rate, None
        )[0]
