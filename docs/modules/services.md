# 🔌 Module Services

Le module Services contient les intégrations avec les services externes : STT, LLM, TTS, Vector DB, et Téléphonie.

## Vue d'ensemble

Le module Services est organisé en sous-modules :
- **STT** : Speech-to-Text (Deepgram)
- **LLM** : Large Language Model (OpenAI)
- **TTS** : Text-to-Speech (ElevenLabs)
- **Vector DB** : Base de données vectorielle (Qdrant)
- **Telephony** : Téléphonie (Twilio)

## STT (Speech-to-Text)

### DeepgramSTTClient

**Fichier** : `src/services/stt/deepgram_client.py`

**Responsabilité** : Transcription audio en temps réel

#### Méthodes principales

##### `start_streaming(on_transcript_callback)`
Démarre le streaming STT.

**Paramètres** :
- `on_transcript_callback` : Callback `(transcript, is_final, confidence) -> None`

**Exemple** :
```python
from src.services.stt.deepgram_client import DeepgramSTTClient

stt_client = DeepgramSTTClient()

async def on_transcript(transcript, is_final, confidence):
    print(f"Transcription: {transcript} (final: {is_final}, conf: {confidence})")

await stt_client.start_streaming(on_transcript)
```

##### `send_audio(audio_chunk: bytes)`
Envoie un chunk audio pour transcription.

##### `close()`
Ferme la connexion STT.

### BaseSTTClient

**Fichier** : `src/services/stt/base.py`

**Responsabilité** : Interface abstraite pour STT

Permet d'implémenter d'autres fournisseurs STT (Google, Azure, etc.)

## LLM (Large Language Model)

### OpenAIClient

**Fichier** : `src/services/llm/openai_client.py`

**Responsabilité** : Génération de réponses et extraction de commandes

#### Méthodes principales

##### `extract_order_items(transcript: str, context: Dict) -> str`
Extrait les produits et quantités d'une transcription.

**Retour** : JSON string avec les produits

**Exemple** :
```python
from src.services.llm.openai_client import OpenAIClient

llm_client = OpenAIClient()

result = await llm_client.extract_order_items(
    "Je voudrais 10 boites de Doliprane et 5 Efferalgan",
    {"conversation_history": [...]}
)
# Retourne: {"products": [{"name": "Doliprane", "quantity": 10, ...}]}
```

##### `generate_response(user_message: str, conversation_history: List) -> str`
Génère une réponse conversationnelle.

##### `analyze_intent(transcript: str) -> Dict`
Analyse l'intention du message.

### Prompts

**Fichier** : `src/services/llm/prompts.py`

**Responsabilité** : Templates de prompts

#### Prompts disponibles

- `SYSTEM_PROMPTS["extraction"]` : Prompt pour extraction de commandes
- `SYSTEM_PROMPTS["dialogue"]` : Prompt pour dialogue conversationnel
- `SYSTEM_PROMPTS["intent_analysis"]` : Prompt pour analyse d'intention

### Functions

**Fichier** : `src/services/llm/functions.py`

**Responsabilité** : Schémas de function calling

#### Fonctions disponibles

- `extract_order` : Extraction de produits
- `search_product` : Recherche de produit

### BaseLLMClient

**Fichier** : `src/services/llm/base.py`

**Responsabilité** : Interface abstraite pour LLM

## TTS (Text-to-Speech)

### ElevenLabsTTSClient

**Fichier** : `src/services/tts/elevenlabs_client.py`

**Responsabilité** : Synthèse vocale

#### Méthodes principales

##### `text_to_speech_stream(text: str) -> AsyncGenerator[bytes, None]`
Convertit texte en audio (streaming).

**Exemple** :
```python
from src.services.tts.elevenlabs_client import ElevenLabsTTSClient

tts_client = ElevenLabsTTSClient()

async for audio_chunk in tts_client.text_to_speech_stream("Bonjour"):
    # Envoyer audio_chunk à Twilio
    pass
```

##### `text_to_speech(text: str) -> bytes`
Convertit texte en audio (complet).

### TTSCache

**Fichier** : `src/services/tts/cache.py`

**Responsabilité** : Cache des réponses audio

#### Méthodes principales

##### `get(text: str, voice_id: str) -> Optional[bytes]`
Récupère l'audio depuis le cache.

##### `set(text: str, voice_id: str, audio_data: bytes)`
Met en cache l'audio.

**Exemple** :
```python
from src.services.tts.cache import tts_cache

# Vérifier le cache
cached_audio = await tts_cache.get("Bonjour", "voice_id")
if cached_audio:
    return cached_audio

# Générer et mettre en cache
audio = await tts_client.text_to_speech("Bonjour")
await tts_cache.set("Bonjour", "voice_id", audio)
```

### BaseTTSClient

**Fichier** : `src/services/tts/base.py`

**Responsabilité** : Interface abstraite pour TTS

## Vector DB

### QdrantClient

**Fichier** : `src/services/vector_db/qcadrant_client.py`

**Responsabilité** : Recherche vectorielle de produits

#### Méthodes principales

##### `search_products(query: str, limit: int = 5) -> List[Dict]`
Recherche sémantique de produits.

**Exemple** :
```python
from src.services.vector_db.qcadrant_client import qdrant_client

results = await qdrant_client.search_products("Doliprane", limit=5)
for result in results:
    print(f"{result['name']} - Score: {result['score']}")
```

##### `index_products_batch(products: List[Dict]) -> int`
Indexe une liste de produits.

##### `get_collection_info() -> Dict`
Récupère les informations de la collection.

### EmbeddingGenerator

**Fichier** : `src/services/vector_db/embeddings.py`

**Responsabilité** : Génération d'embeddings

#### Méthodes principales

##### `generate_embedding(text: str) -> List[float]`
Génère un embedding pour un texte.

##### `generate_embeddings_batch(texts: List[str]) -> List[List[float]]`
Génère des embeddings en batch.

### ProductIndexer

**Fichier** : `src/services/vector_db/indexer.py`

**Responsabilité** : Indexation de produits

#### Méthodes principales

##### `index_products(products: List[Dict]) -> int`
Indexe une liste de produits.

##### `reindex_all(products: List[Dict]) -> int`
Réindexe tous les produits.

## Telephony

### TwilioClient

**Fichier** : `src/services/telephony/twilio_client.py`

**Responsabilité** : Gestion des appels Twilio

#### Méthodes principales

##### `create_call(to: str, from_: str = None, url: str = None) -> Dict`
Crée un appel sortant.

##### `get_call_status(call_sid: str) -> str`
Récupère le statut d'un appel.

##### `end_call(call_sid: str) -> bool`
Termine un appel.

##### `generate_twiml_connect_stream(websocket_url: str) -> str`
Génère TwiML pour connecter à un WebSocket.

##### `send_sms(to: str, body: str) -> Dict`
Envoie un SMS.

### TwilioWebSocketHandler

**Fichier** : `src/services/telephony/websocket_handler.py`

**Responsabilité** : Handler WebSocket pour Twilio Media Streams

#### Méthodes principales

##### `handle_connection()`
Gère la connexion WebSocket.

##### `handle_start(data: dict)`
Gère l'événement START.

##### `handle_media(data: dict)`
Gère les chunks audio.

##### `send_audio(audio_data: bytes)`
Envoie de l'audio vers Twilio.

## Configuration

Les services sont configurés dans `src/core/config.py` :

```python
# Deepgram
deepgram_api_key: str
deepgram_model: str = "nova-2"
deepgram_language: str = "fr-FR"

# OpenAI
openai_api_key: str
openai_model: str = "gpt-4o"
openai_temperature: float = 0.3

# ElevenLabs
elevenlabs_api_key: str
elevenlabs_voice_id: str
elevenlabs_model: str = "eleven_turbo_v2_5"

# Qdrant
qdrant_host: str = "localhost"
qdrant_port: int = 6333
qdrant_collection: str = "products"

# Twilio
twilio_account_sid: str
twilio_auth_token: str
twilio_phone_number: str
```

## Gestion des erreurs

Tous les services gèrent les erreurs avec retry automatique :

- **STT** : Retry sur erreur de connexion
- **LLM** : Retry sur erreur API
- **TTS** : Fallback vers cache si erreur
- **Vector DB** : Retry sur erreur de recherche

## Tests

Les tests du module Services sont dans `tests/unit/test_services/`.

```bash
pytest tests/unit/test_services/ -v
```
