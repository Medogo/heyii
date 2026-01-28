# 🧪 Guide des Tests

Guide complet pour écrire et exécuter les tests de HEYI.

## Structure des tests

```
tests/
├── conftest.py          # Fixtures partagées
├── unit/                # Tests unitaires
│   ├── test_agent/
│   ├── test_audio/
│   ├── test_business/
│   ├── test_data/
│   ├── test_services/
│   └── test_utils/
├── integration/         # Tests d'intégration
│   ├── test_api/
│   └── test_erp/
├── e2e/                 # Tests end-to-end
└── load/                # Tests de charge
```

## Types de tests

### Tests unitaires

Testent des unités isolées (fonctions, classes).

**Exemple** :
```python
# tests/unit/test_business/test_order_service.py
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

### Tests d'intégration

Testent l'intégration entre plusieurs composants.

**Exemple** :
```python
# tests/integration/test_api/test_orders.py
import pytest
from fastapi.testclient import TestClient

def test_create_order_api(client):
    response = client.post("/orders/", json={
        "call_id": "call_123",
        "pharmacy_id": "PHARM_001",
        "items": [{"product_cip": "3400930000000", "quantity": 10}]
    })
    
    assert response.status_code == 201
    assert response.json()["order_id"] is not None
```

### Tests E2E

Testent le flux complet de bout en bout.

**Exemple** :
```python
# tests/e2e/test_call_flow.py
@pytest.mark.asyncio
async def test_complete_call_flow():
    # 1. Démarrer un appel
    # 2. Envoyer de l'audio
    # 3. Recevoir une transcription
    # 4. Créer une commande
    # 5. Vérifier la commande
    pass
```

## Fixtures

### conftest.py

Les fixtures partagées sont dans `tests/conftest.py` :

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.data.database import Base

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
```

### Fixtures disponibles

- `db_session` : Session de base de données
- `client` : Client FastAPI pour tests
- `mock_stt_client` : Mock du client STT
- `mock_llm_client` : Mock du client LLM
- `mock_tts_client` : Mock du client TTS

## Exécuter les tests

### Tous les tests

```bash
pytest
```

### Tests spécifiques

```bash
# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Fichier spécifique
pytest tests/unit/test_order_service.py

# Fonction spécifique
pytest tests/unit/test_order_service.py::test_create_order
```

### Avec options

```bash
# Verbose
pytest -v

# Avec coverage
pytest --cov=src --cov-report=html

# Parallèle
pytest -n auto

# Arrêter au premier échec
pytest -x

# Afficher les print
pytest -s
```

## Coverage

### Générer le rapport

```bash
pytest --cov=src --cov-report=html
```

Le rapport HTML est dans `htmlcov/index.html`.

### Objectif de coverage

- **Minimum** : 80%
- **Recommandé** : 90%+

## Mocking

### Mock de services externes

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    with patch('src.services.stt.deepgram_client.DeepgramSTTClient') as mock:
        mock.return_value.send_audio = AsyncMock()
        
        # Test...
        pass
```

### Mock de base de données

```python
@pytest.mark.asyncio
async def test_with_db_mock(db_session):
    # Utiliser db_session (fixture)
    pass
```

## Best Practices

### 1. Nommer les tests

```python
def test_create_order_with_valid_items():
    pass

def test_create_order_fails_with_invalid_product():
    pass
```

### 2. Arrange-Act-Assert

```python
def test_example():
    # Arrange
    service = OrderService(db_session)
    items = [{"product_cip": "3400930000000", "quantity": 10}]
    
    # Act
    order = await service.create_order(...)
    
    # Assert
    assert order.order_id is not None
```

### 3. Tests isolés

Chaque test doit être indépendant.

### 4. Tests rapides

Les tests unitaires doivent être rapides (< 1s).

### 5. Tests clairs

Les tests doivent être faciles à comprendre.

## CI/CD

Les tests sont exécutés automatiquement dans CI/CD :

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml
```

## Ressources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
