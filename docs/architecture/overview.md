# 🏗️ Architecture Générale - HEYI

## Vue d'ensemble

HEYI est un agent IA vocal conversationnel pour automatiser la prise de commande pharmaceutique 24h/24. Le système est conçu avec une architecture modulaire et scalable.

## Architecture en couches

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │   REST   │  │ WebSocket │  │ Middleware│  │ Schemas ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  Agent Orchestration Layer               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │Orchestrator│ │StateMachine│ │DialogueMgr│ │SessionMgr││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    Business Logic Layer                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │  Order   │  │ Product  │  │ Pharmacy │  │Validation││
│  │ Service  │  │ Service  │  │ Service  │  │ Service ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    Services Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │   STT    │  │   LLM    │  │   TTS    │  │ VectorDB││
│  │(Deepgram)│  │ (OpenAI) │  │(ElevenLabs)│ │(Qdrant) ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    Data Access Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │  Order   │  │  Product │  │ Pharmacy │  │  Call   ││
│  │Repository│  │Repository│  │Repository│  │Repository││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │PostgreSQL│  │  Redis   │  │  Qdrant  │  │ Telnyx  ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
```

## Composants principaux

### 1. API Layer (`src/api/`)

**Responsabilité** : Point d'entrée HTTP/WebSocket de l'application

- **REST API** : Endpoints pour la gestion des appels, commandes, produits
- **WebSocket** : Gestion des streams audio des appels vocaux
- **Middleware** : Auth, logging, rate limiting, error handling
- **Schemas** : Validation des données avec Pydantic

**Fichiers clés** :
- `src/api/main.py` - Application FastAPI principale
- `src/api/routes/` - Routes REST et WebSocket
- `src/api/middleware/` - Middlewares personnalisés
- `src/api/schemas/` - Schémas Pydantic

### 2. Agent Orchestration Layer (`src/agent/`)

**Responsabilité** : Orchestration de la conversation et gestion de l'état

- **AgentOrchestrator** : Coordonne tous les services (STT, LLM, TTS)
- **StateMachine** : Gère les états de conversation (GREETING, COLLECTING, PROCESSING, etc.)
- **DialogueManager** : Génère les réponses conversationnelles
- **SessionManager** : Gère les sessions d'appel
- **CallManager** : Gère les appels actifs

**Fichiers clés** :
- `src/agent/orchestrator.py` - Orchestrateur principal
- `src/agent/state_machine.py` - Machine à états
- `src/agent/dialogue_manager.py` - Gestion du dialogue
- `src/agent/session.py` - Gestion des sessions
- `src/agent/call_manager.py` - Gestion des appels

### 3. Business Logic Layer (`src/business/`)

**Responsabilité** : Logique métier de l'application

- **OrderService** : Création et gestion des commandes
- **ProductService** : Recherche et gestion des produits
- **PharmacyService** : Gestion des pharmacies
- **ValidationService** : Validation des données métier

**Fichiers clés** :
- `src/business/order_service.py` - Service de commandes
- `src/business/product_service.py` - Service de produits
- `src/business/pharmacy_service.py` - Service de pharmacies
- `src/business/validation_service.py` - Service de validation

### 4. Services Layer (`src/services/`)

**Responsabilité** : Intégration avec les services externes

#### STT (Speech-to-Text)
- **DeepgramSTTClient** : Transcription audio en temps réel
- **BaseSTTClient** : Interface abstraite pour STT

#### LLM (Large Language Model)
- **OpenAIClient** : Génération de réponses et extraction de commandes
- **BaseLLMClient** : Interface abstraite pour LLM
- **Prompts** : Templates de prompts pour différents contextes
- **Functions** : Schémas de function calling

#### TTS (Text-to-Speech)
- **ElevenLabsTTSClient** : Synthèse vocale
- **BaseTTSClient** : Interface abstraite pour TTS
- **TTSCache** : Cache des réponses audio

#### Vector DB
- **QdrantClient** : Base de données vectorielle pour recherche sémantique
- **EmbeddingGenerator** : Génération d'embeddings
- **ProductIndexer** : Indexation des produits

#### Telephony
- **Services de téléphonie** : Utilisation de Telnyx (Twilio supprimé)

**Fichiers clés** :
- `src/services/stt/deepgram_client.py`
- `src/services/llm/openai_client.py`
- `src/services/tts/elevenlabs_client.py`
- `src/services/vector_db/qcadrant_client.py`

### 5. Audio Processing Layer (`src/audio/`)

**Responsabilité** : Traitement du signal audio

- **AudioBuffer** : Buffer pour accumulation audio
- **VAD** : Voice Activity Detection
- **AudioRecorder** : Enregistrement audio
- **AudioFormatConverter** : Conversion de formats (PCM, mu-law, etc.)
- **AudioStreamProcessor** : Traitement de stream audio

**Fichiers clés** :
- `src/audio/stream_processor.py` - Processeur principal
- `src/audio/vad.py` - Détection de voix
- `src/audio/format_converter.py` - Conversion de formats

### 6. Data Access Layer (`src/data/`)

**Responsabilité** : Accès aux données

#### Models (`src/data/models/`)
- **Order** : Modèle de commande
- **OrderItem** : Ligne de commande
- **Product** : Modèle de produit
- **Pharmacy** : Modèle de pharmacie
- **Call** : Modèle d'appel

#### Repositories (`src/data/repositories/`)
- **BaseRepository** : Repository générique avec CRUD
- **OrderRepository** : Repository des commandes
- **ProductRepository** : Repository des produits
- **PharmacyRepository** : Repository des pharmacies
- **CallRepository** : Repository des appels

**Fichiers clés** :
- `src/data/database.py` - Configuration SQLAlchemy
- `src/data/models/` - Modèles SQLAlchemy
- `src/data/repositories/` - Repositories

### 7. Integrations Layer (`src/integrations/`)

**Responsabilité** : Intégrations externes

#### ERP (`src/integrations/erp/`)
- **ERPClient** : Client pour l'ERP
- **ERPMapper** : Mapping des données
- **BaseERPClient** : Interface abstraite
- **RetryStrategy** : Stratégie de retry

#### Notifications (`src/integrations/notifications/`)
- **EmailService** : Envoi d'emails
- **BrevoEmailService** : Service Brevo (ex-Sendinblue)
- **SlackService** : Notifications Slack
- **SMSService** : Envoi de SMS

**Fichiers clés** :
- `src/integrations/erp/client.py`
- `src/integrations/notifications/brevo_email.py`

### 8. Utils Layer (`src/utils/`)

**Responsabilité** : Utilitaires partagés

- **Cache** : Wrapper Redis
- **Formatters** : Formatage de données
- **Metrics** : Métriques Prometheus
- **Parsers** : Parsing de texte
- **Validators** : Validation de données

**Fichiers clés** :
- `src/utils/cache.py` - Wrapper Redis
- `src/utils/metrics.py` - Métriques Prometheus

## Flux de données

### Flux d'un appel entrant

```
1. Appel entrant → WebSocket
   ↓
2. AudioStreamProcessor → Traitement audio
   ↓
3. DeepgramSTTClient → Transcription
   ↓
4. AgentOrchestrator → Orchestration
   ↓
5. OpenAIClient → Analyse et génération de réponse
   ↓
6. ProductService → Recherche de produits (si nécessaire)
   ↓
7. OrderService → Création de commande (si validation)
   ↓
8. ERPClient → Envoi à l'ERP
   ↓
9. ElevenLabsTTSClient → Synthèse vocale
   ↓
10. WebSocket → Pharmacien
```

### Flux de création de commande

```
1. AgentOrchestrator → Validation de commande
   ↓
2. OrderService.create_order()
   ↓
3. ProductService → Vérification stocks
   ↓
4. OrderRepository → Création en base
   ↓
5. (Si mode démo) DemoOrderService → Mock ERP
   ↓
6. (Si production) ERPClient → Envoi ERP réel
   ↓
7. NotificationHandler → Notifications
```

## Technologies utilisées

### Backend
- **FastAPI** : Framework web async
- **SQLAlchemy** : ORM
- **Alembic** : Migrations DB
- **Pydantic** : Validation de données

### Services externes
- **Deepgram** : Speech-to-Text
- **OpenAI** : LLM (GPT-4)
- **ElevenLabs** : Text-to-Speech
- **Qdrant** : Vector Database
- **Telnyx** : Téléphonie
- **Brevo** : Emails

### Infrastructure
- **PostgreSQL** : Base de données principale
- **Redis** : Cache et sessions
- **Docker** : Containerisation
- **Kubernetes** : Orchestration
- **Terraform** : Infrastructure as Code

## Patterns architecturaux

### 1. Repository Pattern
Séparation entre logique métier et accès aux données.

### 2. Service Layer Pattern
Encapsulation de la logique métier dans des services.

### 3. Dependency Injection
Injection de dépendances via constructeurs.

### 4. State Machine Pattern
Gestion des états de conversation avec une machine à états.

### 5. Strategy Pattern
Interfaces abstraites pour services (BaseSTTClient, BaseLLMClient, etc.)

## Sécurité

- **JWT** : Authentification
- **Rate Limiting** : Protection contre les abus
- **Input Validation** : Validation avec Pydantic
- **SQL Injection Protection** : ORM SQLAlchemy
- **CORS** : Configuration CORS

## Performance

- **Async/Await** : Programmation asynchrone
- **Connection Pooling** : Pool de connexions DB
- **Redis Cache** : Cache des données fréquentes
- **TTS Cache** : Cache des réponses audio
- **Batch Processing** : Traitement par lots

## Monitoring

- **Prometheus** : Métriques
- **Grafana** : Dashboards
- **Health Checks** : Vérification de santé
- **Logging** : Logs structurés

## Mode Démo

Le système supporte un mode démo qui utilise un mock ERP au lieu de l'ERP réel. Voir [Mode Démo](./../development/demo-mode.md) pour plus de détails.
