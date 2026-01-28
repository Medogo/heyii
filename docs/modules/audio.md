# 🎤 Module Audio

Le module Audio gère le traitement du signal audio, la détection de voix (VAD), et la conversion de formats.

## Vue d'ensemble

Le module Audio est composé de 5 composants :
- **AudioStreamProcessor** : Processeur principal de stream
- **VAD** : Voice Activity Detection
- **AudioBuffer** : Buffer pour accumulation audio
- **AudioRecorder** : Enregistrement audio
- **AudioFormatConverter** : Conversion de formats

## Composants

### 1. AudioStreamProcessor

**Fichier** : `src/audio/stream_processor.py`

**Responsabilité** : Traite les streams audio en temps réel

#### Méthodes principales

##### `start()`
Démarre le traitement du stream.

##### `process_audio_chunk(chunk: str)`
Traite un chunk audio (base64 mu-law depuis Twilio).

##### `stop() -> str`
Arrête le traitement et retourne le chemin de l'enregistrement.

#### Exemple d'utilisation

```python
from src.audio.stream_processor import AudioStreamProcessor

processor = AudioStreamProcessor("call_123")
await processor.start()

# Traiter les chunks
await processor.process_audio_chunk(base64_audio)

# Arrêter et récupérer l'enregistrement
recording_path = await processor.stop()
```

### 2. VAD (Voice Activity Detection)

**Fichier** : `src/audio/vad.py`

**Responsabilité** : Détecte la présence de voix dans l'audio

#### Méthodes principales

##### `is_speech(audio_data: bytes) -> bool`
Détecte si l'audio contient de la parole.

```python
from src.audio.vad import VAD

vad = VAD(aggressiveness=2)
is_speech = vad.is_speech(audio_data)
```

#### Paramètres

- `aggressiveness` : Niveau d'agressivité (0-3)
  - 0 : Moins agressif (plus de faux positifs)
  - 3 : Plus agressif (moins de faux positifs)

### 3. AudioBuffer

**Fichier** : `src/audio/buffer.py`

**Responsabilité** : Accumule les chunks audio

#### Méthodes principales

##### `add_chunk(chunk: bytes)`
Ajoute un chunk au buffer.

##### `get_buffer() -> bytes`
Récupère tout le buffer.

##### `clear()`
Vide le buffer.

##### `is_full() -> bool`
Vérifie si le buffer est plein.

#### Exemple

```python
from src.audio.buffer import AudioBuffer

buffer = AudioBuffer(max_size=32000)
buffer.add_chunk(chunk1)
buffer.add_chunk(chunk2)

if buffer.is_full():
    audio_data = buffer.get_buffer()
    buffer.clear()
```

### 4. AudioRecorder

**Fichier** : `src/audio/recorder.py`

**Responsabilité** : Enregistre l'audio dans des fichiers

#### Méthodes principales

##### `start_recording(call_id: str)`
Démarre l'enregistrement.

##### `record_chunk(chunk: bytes)`
Enregistre un chunk.

##### `stop_recording() -> str`
Arrête l'enregistrement et retourne le chemin du fichier.

#### Exemple

```python
from src.audio.recorder import AudioRecorder

recorder = AudioRecorder()
recorder.start_recording("call_123")

recorder.record_chunk(chunk1)
recorder.record_chunk(chunk2)

file_path = recorder.stop_recording()
```

### 5. AudioFormatConverter

**Fichier** : `src/audio/format_converter.py`

**Responsabilité** : Convertit entre différents formats audio

#### Formats supportés

- **PCM** : Format non compressé
- **mu-law** : Format compressé (Twilio)
- **Base64** : Encodage pour transmission

#### Méthodes principales

##### `mulaw_to_pcm(mulaw_data: bytes) -> bytes`
Convertit mu-law vers PCM.

##### `pcm_to_mulaw(pcm_data: bytes) -> bytes`
Convertit PCM vers mu-law.

##### `encode_base64_audio(audio_data: bytes) -> str`
Encode l'audio en base64.

##### `decode_base64_audio(base64_data: str) -> bytes`
Décode l'audio depuis base64.

#### Exemple

```python
from src.audio.format_converter import AudioFormatConverter

converter = AudioFormatConverter()

# Twilio → PCM
mulaw_audio = converter.decode_base64_audio(twilio_payload)
pcm_audio = converter.mulaw_to_pcm(mulaw_audio)

# PCM → Twilio
mulaw_audio = converter.pcm_to_mulaw(pcm_audio)
base64_audio = converter.encode_base64_audio(mulaw_audio)
```

## Flux de traitement audio

```
Twilio Media Stream (mu-law base64)
    ↓
AudioFormatConverter.decode_base64_audio()
    ↓
AudioFormatConverter.mulaw_to_pcm()
    ↓
VAD.is_speech() (détection de voix)
    ↓
AudioBuffer.add_chunk() (accumulation)
    ↓
AudioRecorder.record_chunk() (enregistrement)
    ↓
DeepgramSTTClient.send_audio() (transcription)
```

## Configuration

Les paramètres audio sont dans `src/core/config.py` :

```python
audio_buffer_size: int = 320        # Taille du buffer
vad_aggressiveness: int = 2          # Agressivité VAD
```

## Performance

- **Traitement asynchrone** : Tous les traitements sont async
- **Buffer optimisé** : Buffer de taille configurable
- **Format efficace** : Utilisation de mu-law pour Twilio

## Tests

Les tests du module Audio sont dans `tests/unit/test_audio/`.

```bash
pytest tests/unit/test_audio/ -v
```
