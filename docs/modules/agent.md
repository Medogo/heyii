# 🤖 Module Agent

Le module Agent est le cœur de l'orchestration conversationnelle. Il coordonne tous les services pour gérer les conversations vocales avec les pharmaciens.

## Vue d'ensemble

Le module Agent est composé de 5 composants principaux :
- **AgentOrchestrator** : Orchestrateur principal
- **StateMachine** : Machine à états de conversation
- **DialogueManager** : Gestionnaire de dialogue
- **SessionManager** : Gestionnaire de sessions
- **CallManager** : Gestionnaire d'appels

## Composants

### 1. AgentOrchestrator

**Fichier** : `src/agent/orchestrator.py`

**Responsabilité** : Coordonne tous les services (STT, LLM, TTS, Vector DB, Services métier)

#### Méthodes principales

##### `handle_call_start(call_id: str) -> str`
Gère le début d'un appel. Crée une session et génère un message d'accueil.

```python
greeting = await orchestrator.handle_call_start("call_123")
```

##### `handle_audio_chunk(call_id: str, audio_chunk: bytes)`
Traite un chunk audio entrant. L'envoie au service STT.

```python
await orchestrator.handle_audio_chunk("call_123", audio_data)
```

##### `handle_transcript(call_id: str, transcript: str, is_final: bool, confidence: float) -> Optional[str]`
Gère une transcription (partielle ou finale). Analyse l'intention et génère une réponse.

```python
response = await orchestrator.handle_transcript(
    "call_123",
    "Je voudrais 10 boites de Doliprane",
    is_final=True,
    confidence=0.95
)
```

##### `handle_call_end(call_id: str)`
Gère la fin d'un appel. Nettoie les ressources et sauvegarde les données.

#### Flux de traitement

1. **Réception audio** → `handle_audio_chunk()`
2. **Transcription** → `handle_transcript()`
3. **Analyse intention** → LLM
4. **Recherche produits** → Vector DB (si nécessaire)
5. **Génération réponse** → LLM
6. **Synthèse vocale** → TTS
7. **Création commande** → OrderService (si validation)

### 2. StateMachine

**Fichier** : `src/agent/state_machine.py`

**Responsabilité** : Gère les états de conversation et les transitions

#### États de conversation

```python
class ConversationState(str, Enum):
    IDLE = "idle"              # État initial
    GREETING = "greeting"       # Salutation
    COLLECTING = "collecting"   # Collecte de produits
    CLARIFYING = "clarifying"   # Clarification nécessaire
    CONFIRMING = "confirming"   # Confirmation de commande
    PROCESSING = "processing"  # Traitement de la commande
    COMPLETED = "completed"    # Commande terminée
    ERROR = "error"            # Erreur
    TRANSFERRING = "transferring"  # Transfert vers humain
```

#### Transitions d'état

```
IDLE → GREETING → COLLECTING → CONFIRMING → PROCESSING → COMPLETED
                                    ↓
                              CLARIFYING
                                    ↓
                                 ERROR
```

#### Méthodes principales

##### `transition(new_state: ConversationState, reason: str)`
Effectue une transition d'état.

```python
state_machine.transition(ConversationState.COLLECTING, "Produit ajouté")
```

##### `can_transition_to(new_state: ConversationState) -> bool`
Vérifie si une transition est possible.

### 3. ConversationContext

**Fichier** : `src/agent/state_machine.py`

**Responsabilité** : Stocke le contexte de la conversation

#### Propriétés

- `call_id` : ID de l'appel
- `pharmacy_id` : ID de la pharmacie
- `state` : État actuel
- `items` : Liste des produits commandés
- `conversation_history` : Historique des messages
- `confidence_scores` : Scores de confiance
- `metadata` : Métadonnées supplémentaires

#### Méthodes

##### `add_item(item: Dict[str, Any])`
Ajoute un produit à la commande.

##### `add_message(role: str, content: str)`
Ajoute un message à l'historique.

##### `get_average_confidence() -> float`
Calcule la confiance moyenne.

### 4. DialogueManager

**Fichier** : `src/agent/dialogue_manager.py`

**Responsabilité** : Génère les réponses conversationnelles selon l'état

#### Méthodes principales

##### `generate_response(state: ConversationState, context: Dict[str, Any] = None) -> str`
Génère une réponse selon l'état.

```python
response = dialogue_manager.generate_response(
    ConversationState.GREETING,
    {"company": "votre grossiste"}
)
```

#### Réponses par état

- **GREETING** : "Bonjour, je suis votre assistant vocal..."
- **COLLECTING** : "D'accord, 10 boites de Doliprane. Autre chose ?"
- **CLARIFYING** : "Je n'ai pas bien compris. Vous voulez Spasfon ?"
- **CONFIRMING** : "Parfait, je récapitule : 5 Efferalgan, 10 Doliprane. Je valide ?"
- **COMPLETED** : "Commande créée avec succès. Numéro : CMD-20240128120000"

### 5. SessionManager

**Fichier** : `src/agent/session.py`

**Responsabilité** : Gère les sessions d'appel

#### Méthodes principales

##### `create_session(call_id: str) -> ConversationContext`
Crée une nouvelle session.

##### `get_session(call_id: str) -> Optional[ConversationContext]`
Récupère une session existante.

##### `end_session(call_id: str)`
Termine une session.

##### `get_active_sessions_count() -> int`
Retourne le nombre de sessions actives.

### 6. CallManager

**Fichier** : `src/agent/call_manager.py`

**Responsabilité** : Gère les appels actifs

#### Méthodes principales

##### `start_call(call_id: str, phone_number: str) -> bool`
Démarre un nouvel appel.

##### `end_call(call_id: str)`
Termine un appel.

##### `get_active_calls_count() -> int`
Retourne le nombre d'appels actifs.

##### `is_call_active(call_id: str) -> bool`
Vérifie si un appel est actif.

## Exemple d'utilisation

```python
from src.agent.orchestrator import AgentOrchestrator
from src.services.stt.deepgram_client import DeepgramSTTClient
from src.services.llm.openai_client import OpenAIClient
from src.services.tts.elevenlabs_client import ElevenLabsTTSClient
from src.services.vector_db.qcadrant_client import QdrantClient
from src.business.product_service import ProductService
from src.business.order_service import OrderService

# Initialisation
stt_client = DeepgramSTTClient()
llm_client = OpenAIClient()
tts_client = ElevenLabsTTSClient()
qdrant_client = QdrantClient()
product_service = ProductService(db)
order_service = OrderService(db)

orchestrator = AgentOrchestrator(
    stt_client=stt_client,
    llm_client=llm_client,
    tts_client=tts_client,
    qdrant_client=qdrant_client,
    product_service=product_service,
    order_service=order_service,
)

# Début d'appel
greeting = await orchestrator.handle_call_start("call_123")

# Traitement audio
await orchestrator.handle_audio_chunk("call_123", audio_data)

# Traitement transcription
response = await orchestrator.handle_transcript(
    "call_123",
    "Je voudrais 10 boites de Doliprane",
    is_final=True,
    confidence=0.95
)
```

## Gestion des erreurs

Le module Agent gère les erreurs à plusieurs niveaux :

1. **Erreurs STT** : Retry automatique ou fallback
2. **Erreurs LLM** : Message d'excuse et retry
3. **Erreurs TTS** : Fallback vers texte
4. **Erreurs métier** : Transition vers état ERROR

## Performance

- **Async/Await** : Toutes les opérations sont asynchrones
- **Session caching** : Sessions mises en cache en mémoire
- **Connection pooling** : Pool de connexions pour services externes

## Tests

Les tests du module Agent sont dans `tests/unit/test_agent/`.

```bash
pytest tests/unit/test_agent/ -v
```
