# 📚 Documentation HEYI

Documentation complète du projet HEYI - Agent IA de Prise de Commande Pharmaceutique H24.

## 📖 Table des matières

### Architecture
- [Architecture générale](./architecture/overview.md) - Vue d'ensemble du système
- [Diagrammes d'architecture](./architecture/diagrams/) - Schémas et diagrammes
- [Décisions d'architecture (ADR)](./architecture/adr/) - Architecture Decision Records

### API
- [Documentation API REST](./api/rest-api.md) - Endpoints REST
- [Documentation WebSocket](./api/websocket-api.md) - API WebSocket pour Twilio
- [Schémas de données](./api/schemas.md) - Modèles Pydantic

### Modules
- [Module Agent](./modules/agent.md) - Orchestrateur et gestion de conversation
- [Module Audio](./modules/audio.md) - Traitement audio et VAD
- [Module Business](./modules/business.md) - Services métier
- [Module Services](./modules/services.md) - Services externes (STT, LLM, TTS)
- [Module Data](./modules/data.md) - Modèles et repositories
- [Module Intégrations](./modules/integrations.md) - ERP et notifications
- [Module Utils](./modules/utils.md) - Utilitaires

### Développement
- [Guide de développement](./development/guide.md) - Setup et workflow
- [Guide des tests](./development/testing.md) - Tests unitaires et d'intégration
- [Mode Démo](./development/demo-mode.md) - Utilisation du mode démo

### Déploiement
- [Guide de déploiement](./deployment/guide.md) - Déploiement infrastructure
- [Kubernetes](./deployment/kubernetes/) - Configurations K8s
- [Terraform](./deployment/terraform/) - Infrastructure as Code

## 🚀 Démarrage rapide

Pour commencer rapidement, consultez :
1. [Architecture générale](./architecture/overview.md)
2. [Guide de développement](./development/guide.md)
3. [Documentation API REST](./api/rest-api.md)

## 📝 Contribution

Pour contribuer à la documentation :
1. Créer une branche `docs/feature-name`
2. Ajouter/modifier la documentation
3. Créer une Pull Request
