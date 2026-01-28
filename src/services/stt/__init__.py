"""Service Speech-to-Text."""
from src.services.stt.deepgram_client import DeepgramSTTClient
from src.services.stt.base import BaseSTTClient

__all__ = ["DeepgramSTTClient", "BaseSTTClient"]
