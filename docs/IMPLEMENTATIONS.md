# 📝 Implémentations - Liste Complète

Liste complète de toutes les implémentations du projet HEYI.

## Structure du Projet

```
src/
├── __init__.py
├── agent/                    # Orchestration conversationnelle
├── api/                      # API FastAPI
├── audio/                    # Traitement audio
├── business/                 # Logique métier
├── core/                     # Configuration
├── data/                     # Accès aux données
├── demo/                     # Mode démo
├── integrations/             # Intégrations externes
├── monitoring/               # Monitoring
├── services/                 # Services externes
└── utils/                    # Utilitaires
```

## Module Agent (`src/agent/`)

### Fichiers

- **`orchestrator.py`** : Orchestrateur principal qui coordonne tous les services
  - `AgentOrchestrator` : Classe principale
  - Méthodes : `handle_call_start()`, `handle_audio_chunk()`, `handle_transcript()`, `handle_call_end()`

- **`state_machine.py`** : Machine à états de conversation
  - `ConversationState` : Enum des états
  - `ConversationContext` : Contexte de conversation
  - `StateMachine` : Machine à états

- **`dialogue_manager.py`** : Gestionnaire de dialogue
  - `DialogueManager` : Génère les réponses selon l'état

- **`session.py`** : Gestionnaire de sessions
  - `SessionManager` : Gère les sessions d'appel
  - `session_manager` : Instance globale

- **`call_manager.py`** : Gestionnaire d'appels
  - `CallManager` : Gère les appels actifs
  - `call_manager` : Instance globale

## Module API (`src/api/`)

### Fichiers

- **`main.py`** : Application FastAPI principale
  - `app` : Instance FastAPI
  - `lifespan` : Lifecycle events

### Routes (`src/api/routes/`)

- **`health.py`** : Health checks
  - `GET /health/` : Health check basique
  - `GET /health/ready` : Readiness check
  - `GET /health/metrics` : Métriques

- **`calls.py`** : Gestion des appels
  - `GET /calls/` : Lister les appels
  - `GET /calls/{call_id}` : Récupérer un appel
  - `GET /calls/active/list` : Appels actifs
  - `GET /calls/stats` : Statistiques

- **`orders.py`** : Gestion des commandes
  - `GET /orders/` : Lister les commandes
  - `GET /orders/{order_id}` : Récupérer une commande
  - `POST /orders/` : Créer une commande
  - `POST /orders/{order_id}/validate` : Valider une commande
  - `GET /orders/stats` : Statistiques

- **`products.py`** : Gestion des produits
  - `GET /products/` : Lister les produits
  - `GET /products/search` : Rechercher des produits
  - `GET /products/{product_id}` : Récupérer un produit
  - `GET /products/cip/{cip13}` : Récupérer par CIP13
  - `POST /products/` : Créer un produit
  - `POST /products/check-stock` : Vérifier le stock

- **`websocket.py`** : WebSocket pour Twilio Media Streams
  - `WS /ws/twilio/{call_id}` : Connexion WebSocket

### Middleware (`src/api/middleware/`)

- **`auth.py`** : Authentification
  - `AuthMiddleware` : Middleware d'authentification

- **`error_handler.py`** : Gestion des erreurs
  - Gestion centralisée des erreurs

- **`logging.py`** : Logging
  - `LoggingMiddleware` : Middleware de logging

- **`rate_limit.py`** : Rate limiting
  - `RateLimiter` : Rate limiter

### Schemas (`src/api/schemas/`)

- **`call.py`** : Schémas pour les appels
  - `CallBase`, `CallCreate`, `CallResponse`, `CallStats`

- **`order.py`** : Schémas pour les commandes
  - `OrderItemBase`, `OrderItemCreate`, `OrderItemResponse`
  - `OrderBase`, `OrderCreate`, `OrderResponse`, `OrderStats`

- **`product.py`** : Schémas pour les produits
  - `ProductBase`, `ProductCreate`, `ProductResponse`
  - `ProductSearch`, `StockCheckRequest`, `StockCheckResponse`

## Module Audio (`src/audio/`)

### Fichiers

- **`stream_processor.py`** : Processeur de stream audio
  - `AudioStreamProcessor` : Traite les streams audio

- **`vad.py`** : Voice Activity Detection
  - `VAD` : Détection de voix

- **`buffer.py`** : Buffer audio
  - `AudioBuffer` : Accumulation audio

- **`recorder.py`** : Enregistrement audio
  - `AudioRecorder` : Enregistre l'audio

- **`format_converter.py`** : Conversion de formats
  - `AudioFormatConverter` : Conversion PCM/mu-law/base64

## Module Business (`src/business/`)

### Fichiers

- **`order_service.py`** : Service de commandes
  - `OrderService` : Création et gestion des commandes
  - Support du mode démo

- **`product_service.py`** : Service de produits
  - `ProductService` : Recherche et gestion des produits

- **`pharmacy_service.py`** : Service de pharmacies
  - `PharmacyService` : Gestion des pharmacies

- **`validation_service.py`** : Service de validation
  - `ValidationService` : Validation des données métier

## Module Core (`src/core/`)

### Fichiers

- **`config.py`** : Configuration centralisée
  - `Settings` : Classe de configuration Pydantic
  - `settings` : Instance globale

## Module Data (`src/data/`)

### Models (`src/data/models/`)

- **`order.py`** : Modèles Order et OrderItem
  - `Order` : Modèle de commande
  - `OrderItem` : Modèle de ligne de commande

- **`product.py`** : Modèle Product
  - `Product` : Modèle de produit

- **`pharmacy.py`** : Modèle Pharmacy
  - `Pharmacy` : Modèle de pharmacie

- **`call.py`** : Modèle Call
  - `Call` : Modèle d'appel

### Repositories (`src/data/repositories/`)

- **`base.py`** : Repository de base
  - `BaseRepository` : Repository générique

- **`order_repository.py`** : Repository des commandes
  - `OrderRepository` : Repository des commandes
  - `OrderItemRepository` : Repository des items

- **`product_repository.py`** : Repository des produits
  - `ProductRepository` : Repository des produits

- **`pharmacy_repository.py`** : Repository des pharmacies
  - `PharmacyRepository` : Repository des pharmacies

- **`call_repository.py`** : Repository des appels
  - `CallRepository` : Repository des appels

### Database

- **`database.py`** : Configuration SQLAlchemy
  - `engine` : Engine async
  - `AsyncSessionLocal` : Session factory
  - `Base` : Base class
  - `get_db()` : Dependency injection

## Module Demo (`src/demo/`)

### Fichiers

- **`demo_order_service.py`** : Service de commande démo
  - `DemoOrderService` : Service démo

- **`mock_erp_client.py`** : Mock ERP
  - `MockERPClient` : Client ERP simulé

- **`notification_handler.py`** : Handler de notifications
  - `DemoNotificationHandler` : Gestionnaire de notifications

## Module Integrations (`src/integrations/`)

### ERP (`src/integrations/erp/`)

- **`client.py`** : Client ERP
  - `ERPClient` : Client pour l'ERP

- **`mapper.py`** : Mapper ERP
  - `ERPMapper` : Mapping des données

- **`base.py`** : Interface ERP
  - `BaseERPClient` : Interface abstraite

- **`retry.py`** : Stratégie de retry
  - `retry_on_error` : Décorateur retry
  - `RetryStrategy` : Stratégie de retry

### Notifications (`src/integrations/notifications/`)

- **`brevo_email.py`** : Service Brevo
  - `BrevoEmailService` : Service d'emails Brevo

- **`email.py`** : Service email générique
  - `EmailService` : Interface email

- **`slack.py`** : Service Slack
  - `SlackService` : Service Slack

- **`sms.py`** : Service SMS
  - `SMSService` : Service SMS

## Module Monitoring (`src/monitoring/`)

### Fichiers

- **`health_checker.py`** : Health checker
  - `HealthChecker` : Vérificateur de santé
  - `health_checker` : Instance globale

## Module Services (`src/services/`)

### STT (`src/services/stt/`)

- **`deepgram_client.py`** : Client Deepgram
  - `DeepgramSTTClient` : Client STT Deepgram

- **`base.py`** : Interface STT
  - `BaseSTTClient` : Interface abstraite

### LLM (`src/services/llm/`)

- **`openai_client.py`** : Client OpenAI
  - `OpenAIClient` : Client LLM OpenAI

- **`base.py`** : Interface LLM
  - `BaseLLMClient` : Interface abstraite

- **`prompts.py`** : Templates de prompts
  - `SYSTEM_PROMPTS` : Prompts système
  - `get_extraction_prompt()` : Prompt d'extraction
  - `get_dialogue_prompt()` : Prompt de dialogue

- **`functions.py`** : Schémas de function calling
  - `FUNCTION_SCHEMAS` : Schémas de fonctions

### TTS (`src/services/tts/`)

- **`elevenlabs_client.py`** : Client ElevenLabs
  - `ElevenLabsTTSClient` : Client TTS ElevenLabs

- **`base.py`** : Interface TTS
  - `BaseTTSClient` : Interface abstraite

- **`cache.py`** : Cache TTS
  - `TTSCache` : Cache des réponses audio
  - `tts_cache` : Instance globale

### Vector DB (`src/services/vector_db/`)

- **`qcadrant_client.py`** : Client Qdrant
  - `QdrantClient` : Client Qdrant
  - `qdrant_client` : Instance globale

- **`embeddings.py`** : Générateur d'embeddings
  - `EmbeddingGenerator` : Générateur d'embeddings
  - `embedding_generator` : Instance globale

- **`indexer.py`** : Indexeur de produits
  - `ProductIndexer` : Indexeur de produits
  - `product_indexer` : Instance globale

### Telephony (`src/services/telephony/`)

- **`twilio_client.py`** : Client Twilio
  - `TwilioClient` : Client Twilio
  - `twilio_client` : Instance globale

- **`websocket_handler.py`** : Handler WebSocket
  - `TwilioWebSocketHandler` : Handler WebSocket Twilio

## Module Utils (`src/utils/`)

### Fichiers

- **`cache.py`** : Wrapper Redis
  - `Cache` : Wrapper Redis
  - `cache` : Instance globale

- **`formatters.py`** : Formateurs
  - `format_currency()` : Formatage monétaire
  - `format_datetime()` : Formatage date
  - `format_phone_display()` : Formatage téléphone
  - `format_order_summary()` : Formatage résumé commande

- **`metrics.py`** : Métriques Prometheus
  - Compteurs, histogrammes, gauges
  - Fonctions d'enregistrement

- **`parsers.py`** : Parseurs
  - `parse_quantity_from_text()` : Extraction quantité
  - `parse_product_name()` : Nettoyage nom produit

- **`validators.py`** : Validateurs
  - `validate_phone_number()` : Validation téléphone
  - `validate_cip13()` : Validation CIP13
  - `validate_email()` : Validation email
  - `sanitize_text()` : Nettoyage texte

## Statistiques

- **Total fichiers Python** : ~95 fichiers
- **Modules principaux** : 10
- **Services externes** : 5 (STT, LLM, TTS, Vector DB, Telephony)
- **Endpoints API** : ~20
- **Modèles de données** : 5
- **Repositories** : 5

## Documentation

Toute la documentation est dans `docs/` :

- Architecture : `docs/architecture/`
- API : `docs/api/`
- Modules : `docs/modules/`
- Développement : `docs/development/`
- Déploiement : `docs/deployment/`
