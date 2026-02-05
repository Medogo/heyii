# 🔌 WebSocket API - Appels Vocaux

Documentation de l'API WebSocket pour la gestion des streams audio des appels vocaux.

## Connexion

### Endpoint WebSocket

```
ws://localhost:8000/ws/voice
```

**Paramètres** :
- Aucun paramètre dans l'URL (l'ID d'appel est transmis dans les messages)

## Protocole WebSocket

Le protocole utilise des messages JSON pour échanger des données.

### Messages entrants (Client → Serveur)

#### START
Message envoyé au début du stream.

```json
{
  "event": "start",
  "start": {
    "callSid": "CA...",
    "streamSid": "MZ...",
    "customParameters": {
      "From": "+1234567890"
    }
  }
}
```

#### MEDIA
Chunk audio (mu-law base64).

```json
{
  "event": "media",
  "media": {
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
    "callSid": "CA...",
    "streamSid": "MZ..."
  }
}
```

### Messages sortants (Serveur → Client)

#### MEDIA
Envoyer de l'audio.

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
   - Envoi MEDIA
   ↓
4. Réception STOP → Nettoyage
```

## Exemple d'utilisation

### Client JavaScript

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/voice`);

ws.onopen = () => {
  console.log("WebSocket connecté");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.event === "media") {
    // Audio reçu depuis le serveur
    // Traiter l'audio...
  }
};

// Envoyer un message START
ws.send(JSON.stringify({
  event: "start",
  start: {
    callSid: "CA...",
    streamSid: "MZ...",
    customParameters: {
      From: "+1234567890"
    }
  }
}));

// Envoyer un chunk audio
ws.send(JSON.stringify({
  event: "media",
  media: {
    payload: "base64_audio_data"
  }
}));
```

### Python

```python
import asyncio
import websockets
import json

async def connect_websocket():
    uri = "ws://localhost:8000/ws/voice"
    
    async with websockets.connect(uri) as websocket:
        # Envoyer START
        start_message = {
            "event": "start",
            "start": {
                "callSid": "CA...",
                "streamSid": "MZ...",
                "customParameters": {
                    "From": "+1234567890"
                }
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
  "message": "Invalid request"
}
```

### Timeout

Si aucune activité pendant 30 secondes, la connexion est fermée.

## Performance

- **Latence** : < 500ms pour traitement complet (STT → LLM → TTS)
- **Throughput** : Supporte jusqu'à 10 appels simultanés
- **Buffer** : Buffer audio de 320 bytes

## Sécurité

- **Authentification** : Vérification des paramètres d'appel
- **Rate Limiting** : Limite de connexions par IP
- **Validation** : Validation de tous les messages entrants

## Monitoring

Les métriques WebSocket sont disponibles via :
- `/health/metrics` : Nombre de connexions actives
- Prometheus : Métriques détaillées
