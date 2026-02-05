# 🏥 HEYI - Agent IA de Prise de Commande Pharmaceutique H24

Agent IA vocal conversationnel pour automatiser la prise de commande pharmaceutique 24h/24, 7j/7.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd heyi
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Pour le développement
```

4. **Configuration**
```bash
cp .env .env
# Éditer .env avec vos credentials
```

5. **Démarrer avec Docker Compose**
```bash
docker-compose up -d
```

6. **Initialiser la base de données**
```bash
alembic upgrade head
```

7. **Lancer l'application**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Structure du Projet

```
heyi/
├── src/               # Code source
│   ├── api/          # API FastAPI
│   ├── agent/        # Agent IA orchestrator
│   ├── audio/        # Traitement audio
│   ├── services/     # Services externes (STT, LLM, TTS)
│   ├── business/     # Logique métier
│   └── data/         # Couche données
├── tests/            # Tests
├── infrastructure/   # IaC (Terraform, Kubernetes)
├── docs/             # Documentation
└── scripts/          # Scripts utilitaires
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/unit -v

# Tests d'intégration
pytest tests/integration -v

# Coverage
pytest --cov=src --cov-report=html
```

## 📊 Services & URLs

### Application
- **API principale**: http://localhost:8000
- **Documentation API (Swagger)**: http://localhost:8000/docs
- **Documentation API (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health/
- **Readiness Check**: http://localhost:8000/health/ready
- **Métriques**: http://localhost:8000/health/metrics

### Monitoring & Observabilité
- **Grafana**: http://localhost:3000
  - Utilisateur: `admin`
  - Mot de passe: `admin`
- **Prometheus**: http://localhost:9090
  - Interface de requêtes: http://localhost:9090/graph
  - Métriques: http://localhost:9090/metrics

### Bases de données & Services
- **PostgreSQL**: `localhost:5432`
  - Base de données: `heyi_db`
  - Utilisateur: `heyi`
  - Mot de passe: `heyi_password`
- **Redis**: `localhost:6379`
- **Qdrant (Vector DB)**:
  - Dashboard: http://localhost:6333/dashboard
  - API REST: http://localhost:6333
  - gRPC: `localhost:6334`

## 🔧 Développement

### Formater le code
```bash
black src tests
isort src tests
```

### Linter
```bash
flake8 src tests
mypy src
```

### Pre-commit hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 📚 Documentation

Documentation complète disponible dans `docs/`

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

[Votre License]

## 👥 Équipe

- Chef de Projet: [Nom]
- Lead Dev: [Nom]
- DevOps: [Nom]
