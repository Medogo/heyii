# 🔌 WebSocket API - Twilio Media Streams

Documentation de l'API WebSocket pour la gestion des streams audio Twilio.

## Connexion

### Endpoint WebSocket

```
ws://localhost:8000/ws/twilio/{call_id}
```

**Paramètres** :
- `call_id` (string) : ID de l'appel

## Protocole Twilio Media Streams

Twilio Media Streams utilise un protocole basé sur JSON pour échanger des messages.

### Messages entrants (Twilio → Serveur)

#### START
Message envoyé au début du stream.

```json
{
  "event": "start",
  "start": {
    "accountSid": "AC...",
    "callSid": "CA...",
    "streamSid": "MZ...",
    "tracks": ["inbound", "outbound"]
  }
}
```

#### MEDIA
Chunk audio (mu-law base64).

```json
{
  "event": "media",
  "media": {
    "track": "inbound",
    "chunk": "1",
    "timestamp": "1234567890",
    "payload": "base64_encoded_audio"
  }
}
```

#### STOP
Fin du stream.

```json
{
  "event": "stop",
  "stop": {
    "accountSid": "AC...",
    "callSid": "CA...",
    "streamSid": "MZ..."
  }
}
```

### Messages sortants (Serveur → Twilio)

#### MEDIA
Envoyer de l'audio vers Twilio.

```json
{
  "event": "media",
  "streamSid": "MZ...",
  "media": {
    "payload": "base64_encoded_audio"
  }
}
```

#### MARK
Marquer un point dans le stream.

```json
{
  "event": "mark",
  "streamSid": "MZ...",
  "mark": {
    "name": "sentence_end"
  }
}
```

#### CLEAR
Vider le buffer audio.

```json
{
  "event": "clear",
  "streamSid": "MZ..."
}
```

## Flux de traitement

```
1. Connexion WebSocket
   ↓
2. Réception START → Initialisation orchestrateur
   ↓
3. Réception MEDIA → Traitement audio
   ↓
   - Décodage base64 → mu-law
   ↓
   - Conversion mu-law → PCM
   ↓
   - VAD (détection de voix)
   ↓
   - Envoi à Deepgram STT
   ↓
   - Transcription reçue
   ↓
   - Analyse LLM
   ↓
   - Recherche produits (si nécessaire)
   ↓
   - Génération réponse LLM
   ↓
   - Synthèse TTS
   ↓
   - Conversion PCM → mu-law
   ↓
   - Encodage base64
   ↓
   - Envoi MEDIA vers Twilio
   ↓
4. Réception STOP → Nettoyage
```

## Exemple d'utilisation

### Client JavaScript

```javascript
const callId = "call_123";
const ws = new WebSocket(`ws://localhost:8000/ws/twilio/${callId}`);

ws.onopen = () => {
  console.log("WebSocket connecté");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.event === "media") {
    // Audio reçu depuis le serveur
    // À envoyer à Twilio Media Streams
    sendToTwilio(message);
  }
};

// Envoyer un message START simulé
ws.send(JSON.stringify({
  event: "start",
  start: {
    accountSid: "AC...",
    callSid: "CA...",
    streamSid: "MZ...",
    tracks: ["inbound", "outbound"]
  }
}));

// Envoyer un chunk audio
ws.send(JSON.stringify({
  event: "media",
  media: {
    track: "inbound",
    chunk: "1",
    timestamp: Date.now().toString(),
    payload: "base64_audio_data"
  }
}));
```

### Python

```python
import asyncio
import websockets
import json

async def connect_websocket(call_id: str):
    uri = f"ws://localhost:8000/ws/twilio/{call_id}"
    
    async with websockets.connect(uri) as websocket:
        # Envoyer START
        start_message = {
            "event": "start",
            "start": {
                "accountSid": "AC...",
                "callSid": "CA...",
                "streamSid": "MZ...",
                "tracks": ["inbound", "outbound"]
            }
        }
        await websocket.send(json.dumps(start_message))
        
        # Écouter les messages
        async for message in websocket:
            data = json.loads(message)
            
            if data["event"] == "media":
                # Audio reçu
                audio_payload = data["media"]["payload"]
                # Traiter l'audio...
```

## Gestion des erreurs

### Erreurs de connexion

Si la connexion échoue, le serveur retourne un message d'erreur :

```json
{
  "error": "Connection failed",
  "message": "Call ID not found"
}
```

### Timeout

Si aucune activité pendant 30 secondes, la connexion est fermée.

## Performance

- **Latence** : < 500ms pour traitement complet (STT → LLM → TTS)
- **Throughput** : Supporte jusqu'à 10 appels simultanés
- **Buffer** : Buffer audio de 320 bytes

## Sécurité

- **Authentification** : Vérification du call_id
- **Rate Limiting** : Limite de connexions par IP
- **Validation** : Validation de tous les messages entrants

## Monitoring

Les métriques WebSocket sont disponibles via :
- `/health/metrics` : Nombre de connexions actives
- Prometheus : Métriques détaillées
