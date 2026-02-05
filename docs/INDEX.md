# 📑 Index de la Documentation

Index complet de toute la documentation HEYI.

## 🚀 Démarrage Rapide

- [README Principal](../README.md) - Vue d'ensemble du projet
- [Guide de Développement](./development/guide.md) - Setup et installation
- [Architecture Générale](./architecture/overview.md) - Comprendre l'architecture

## 📚 Documentation par Catégorie

### Architecture

- [Vue d'ensemble](./architecture/overview.md) - Architecture complète du système
- [Diagrammes](./architecture/diagrams/) - Schémas et diagrammes
- [ADR](./architecture/adr/) - Architecture Decision Records

### API

- [API REST](./api/rest-api.md) - Documentation complète de l'API REST
- [API WebSocket](./api/websocket-api.md) - Documentation WebSocket pour les appels vocaux
- [Schémas de Données](./api/schemas.md) - Modèles Pydantic

### Modules

#### Core Modules

- [Module Agent](./modules/agent.md) - Orchestration conversationnelle
- [Module Audio](./modules/audio.md) - Traitement audio et VAD
- [Module Business](./modules/business.md) - Services métier
- [Module Data](./modules/data.md) - Modèles et repositories

#### Services

- [Module Services](./modules/services.md) - Services externes (STT, LLM, TTS, Vector DB, Telephony)
- [Module Integrations](./modules/integrations.md) - ERP et notifications
- [Module Utils](./modules/utils.md) - Utilitaires partagés

### Développement

- [Guide de Développement](./development/guide.md) - Setup, workflow, standards
- [Guide des Tests](./development/testing.md) - Tests unitaires et d'intégration
- [Mode Démo](./development/demo-mode.md) - Utilisation du mode démo

### Déploiement

- [Guide de Déploiement](./deployment/guide.md) - Déploiement infrastructure
- [Kubernetes](./deployment/kubernetes/) - Configurations K8s
- [Terraform](./deployment/terraform/) - Infrastructure as Code

### Référence

- [Liste des Implémentations](./IMPLEMENTATIONS.md) - Liste complète de tous les fichiers

## 🔍 Recherche Rapide

### Par Sujet

#### Agent & Conversation

- [Module Agent](./modules/agent.md) - Orchestrateur, State Machine, Dialogue
- [API WebSocket](./api/websocket-api.md) - Gestion des appels

#### Audio & Speech

- [Module Audio](./modules/audio.md) - Traitement audio, VAD, Conversion
- [Module Services - STT](./modules/services.md#stt-speech-to-text) - Speech-to-Text
- [Module Services - TTS](./modules/services.md#tts-text-to-speech) - Text-to-Speech

#### Commandes & Produits

- [Module Business](./modules/business.md) - OrderService, ProductService
- [API REST - Orders](./api/rest-api.md#orders) - Endpoints commandes
- [API REST - Products](./api/rest-api.md#products) - Endpoints produits

#### Base de Données

- [Module Data](./modules/data.md) - Models, Repositories, Database
- [Schémas API](./api/schemas.md) - Schémas Pydantic

#### Intégrations

- [Module Integrations](./modules/integrations.md) - ERP et Notifications
- [Mode Démo](./development/demo-mode.md) - Mode démo avec mock ERP

#### Services Externes

- [Module Services](./modules/services.md) - STT, LLM, TTS, Vector DB, Telephony
- [Module Integrations](./modules/integrations.md) - ERP, Notifications

## 📖 Parcours Recommandés

### Pour les Développeurs

1. [Guide de Développement](./development/guide.md)
2. [Architecture Générale](./architecture/overview.md)
3. [Module Agent](./modules/agent.md)
4. [Guide des Tests](./development/testing.md)

### Pour les Intégrateurs

1. [API REST](./api/rest-api.md)
2. [API WebSocket](./api/websocket-api.md)
3. [Schémas de Données](./api/schemas.md)
4. [Module Integrations](./modules/integrations.md)

### Pour les DevOps

1. [Guide de Déploiement](./deployment/guide.md)
2. [Kubernetes](./deployment/kubernetes/)
3. [Terraform](./deployment/terraform/)
4. [Architecture](./architecture/overview.md)

### Pour les Product Owners

1. [Architecture Générale](./architecture/overview.md)
2. [Module Business](./modules/business.md)
3. [Mode Démo](./development/demo-mode.md)
4. [API REST](./api/rest-api.md)

## 🔗 Liens Utiles

- [GitHub Repository](https://github.com/your-org/heyi)
- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
- [Prometheus](http://localhost:9090)
- [Grafana](http://localhost:3000)

## 📝 Contribution

Pour contribuer à la documentation :

1. Créer une branche `docs/feature-name`
2. Modifier/ajouter la documentation
3. Créer une Pull Request

Voir [Guide de Développement](./development/guide.md) pour plus de détails.
