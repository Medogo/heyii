# 👨‍💻 Guide de Développement

Guide complet pour développer sur HEYI.

## Prérequis

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose
- Git

## Installation

### 1. Cloner le projet

```bash
git clone <repository-url>
cd heyi
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Configuration

Créer un fichier `.env` :

```bash
cp .env.example .env
```

Éditer `.env` avec vos credentials :

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/heyi

# Redis
REDIS_URL=redis://localhost:6379/0

# Deepgram
DEEPGRAM_API_KEY=your_key

# OpenAI
OPENAI_API_KEY=your_key

# ElevenLabs
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice_id

# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# ERP
ERP_API_URL=https://erp.example.com
ERP_API_KEY=your_key

# Security
SECRET_KEY=your_secret_key

# Mode Démo (optionnel)
DEMO_MODE=false
DEMO_NOTIFICATION_EMAILS=admin@example.com
DEMO_NOTIFICATION_WHATSAPP=+22900000000
```

### 5. Démarrer les services

```bash
docker-compose up -d
```

### 6. Initialiser la base de données

```bash
alembic upgrade head
```

### 7. Lancer l'application

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur `http://localhost:8000`

## Structure du code

```
src/
├── api/              # API FastAPI
├── agent/            # Orchestrateur agent
├── audio/            # Traitement audio
├── business/         # Logique métier
├── core/             # Configuration
├── data/             # Modèles et repositories
├── demo/             # Mode démo
├── integrations/     # Intégrations externes
├── monitoring/       # Monitoring
├── services/         # Services externes
└── utils/            # Utilitaires
```

## Workflow de développement

### 1. Créer une branche

```bash
git checkout -b feature/ma-feature
```

### 2. Développer

- Écrire le code
- Ajouter des tests
- Vérifier le linting

### 3. Tests

```bash
# Tests unitaires
pytest tests/unit -v

# Tests d'intégration
pytest tests/integration -v

# Coverage
pytest --cov=src --cov-report=html
```

### 4. Linting

```bash
# Formater le code
black src tests
isort src tests

# Vérifier le linting
flake8 src tests
mypy src
```

### 5. Commit

```bash
git add .
git commit -m "feat: ajouter ma feature"
```

### 6. Push et Pull Request

```bash
git push origin feature/ma-feature
```

## Standards de code

### Formatage

- **Black** : Formatage automatique
- **isort** : Tri des imports
- **Line length** : 100 caractères max

### Naming

- **Classes** : `PascalCase` (ex: `OrderService`)
- **Fonctions/Méthodes** : `snake_case` (ex: `create_order`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `MAX_RETRIES`)
- **Variables** : `snake_case` (ex: `order_id`)

### Docstrings

Utiliser des docstrings pour toutes les fonctions et classes :

```python
def create_order(self, call_id: str, items: List[Dict]) -> Order:
    """
    Crée une nouvelle commande.

    Args:
        call_id: ID de l'appel
        items: Liste des produits commandés

    Returns:
        Objet Order créé

    Raises:
        ValueError: Si produit non trouvé
    """
    pass
```

### Type Hints

Toujours utiliser les type hints :

```python
from typing import List, Dict, Optional

def process_items(items: List[Dict[str, Any]]) -> Optional[Order]:
    pass
```

## Tests

### Structure des tests

```
tests/
├── unit/           # Tests unitaires
├── integration/    # Tests d'intégration
├── e2e/            # Tests end-to-end
└── load/           # Tests de charge
```

### Écrire des tests

```python
import pytest
from src.business.order_service import OrderService

@pytest.mark.asyncio
async def test_create_order(db_session):
    service = OrderService(db_session)
    
    order = await service.create_order(
        call_id="call_123",
        pharmacy_id="PHARM_001",
        items=[{"product_cip": "3400930000000", "quantity": 10}],
        confidence=0.95
    )
    
    assert order.order_id is not None
    assert order.total_amount > 0
```

### Exécuter les tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/unit/test_order_service.py

# Avec coverage
pytest --cov=src --cov-report=html

# Mode verbose
pytest -v
```

## Migrations de base de données

### Créer une migration

```bash
alembic revision --autogenerate -m "ajouter champ X"
```

### Appliquer les migrations

```bash
alembic upgrade head
```

### Revenir en arrière

```bash
alembic downgrade -1
```

## Debugging

### Logs

Les logs sont dans `logs/` :

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Erreur", exc_info=True)
```

### Debugger

Utiliser `ipdb` pour le debugging :

```python
import ipdb; ipdb.set_trace()
```

## Pre-commit hooks

Installer les pre-commit hooks :

```bash
pre-commit install
```

Les hooks vérifient automatiquement :
- Formatage (black, isort)
- Linting (flake8)
- Type checking (mypy)

## CI/CD

Le projet utilise GitHub Actions pour :
- Tests automatiques
- Linting
- Déploiement

Voir `.github/workflows/` pour les configurations.

## Ressources

- [Architecture](./../architecture/overview.md)
- [Documentation API](./../api/rest-api.md)
- [Modules](./../modules/)
