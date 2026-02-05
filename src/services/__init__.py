"""Services externes."""
from src.services.llm import (
    OpenAIClient,
    BaseLLMClient,
    SYSTEM_PROMPTS,
    get_extraction_prompt,
    get_dialogue_prompt,
    FUNCTION_SCHEMAS,
)
from src.services.stt import DeepgramSTTClient, BaseSTTClient
from src.services.tts import ElevenLabsTTSClient, BaseTTSClient, TTSCache, tts_cache
from src.services.vector_db import (
    qdrant_client,
    QdrantClient,
    EmbeddingGenerator,
    embedding_generator,
    ProductIndexer,
    product_indexer,
)
# Telephony services removed (Twilio)

__all__ = [
    # LLM
    "OpenAIClient",
    "BaseLLMClient",
    "SYSTEM_PROMPTS",
    "get_extraction_prompt",
    "get_dialogue_prompt",
    "FUNCTION_SCHEMAS",
    # STT
    "DeepgramSTTClient",
    "BaseSTTClient",
    # TTS
    "ElevenLabsTTSClient",
    "BaseTTSClient",
    "TTSCache",
    "tts_cache",
    # Vector DB
    "qdrant_client",
    "QdrantClient",
    "EmbeddingGenerator",
    "embedding_generator",
    "ProductIndexer",
    "product_indexer",
    # Telephony - removed (Twilio)
]
