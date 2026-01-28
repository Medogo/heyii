# 💾 Module Data

Le module Data gère l'accès aux données avec SQLAlchemy (ORM) et les repositories.

## Vue d'ensemble

Le module Data est composé de :
- **Models** : Modèles SQLAlchemy
- **Repositories** : Pattern Repository pour l'accès aux données
- **Database** : Configuration de la base de données
- **Migrations** : Migrations Alembic

## Models

### Order

**Fichier** : `src/data/models/order.py`

**Table** : `orders`

**Champs** :
- `id` : ID primaire
- `order_id` : ID métier unique
- `call_id` : ID de l'appel
- `pharmacy_id` : ID de la pharmacie
- `status` : Statut (pending, confirmed, demo, etc.)
- `total_amount` : Montant total
- `delivery_date` : Date de livraison
- `delivery_notes` : Notes de livraison
- `required_human_review` : Nécessite validation humaine
- `review_reason` : Raison de la review
- `confidence_global` : Confiance globale
- `erp_created` : Créé dans l'ERP
- `erp_order_id` : ID ERP
- `validated_by_human` : Validé par
- `validated_at` : Date de validation
- `created_at` : Date de création
- `updated_at` : Date de mise à jour

**Relations** :
- `items` : Liste des `OrderItem`

### OrderItem

**Fichier** : `src/data/models/order.py`

**Table** : `order_items`

**Champs** :
- `id` : ID primaire
- `order_id` : ID de la commande
- `product_id` : ID du produit
- `audio_transcript` : Transcription audio
- `quantity_asked` : Quantité demandée
- `quantity_unit` : Unité (boites, unités)
- `unit_price` : Prix unitaire
- `line_total` : Total ligne
- `confidence_score` : Score de confiance
- `status` : Statut (ok, out_of_stock)
- `extracted_at` : Date d'extraction

**Relations** :
- `order` : Commande parente
- `product` : Produit

### Product

**Fichier** : `src/data/models/product.py`

**Table** : `products`

**Champs** :
- `id` : ID primaire
- `cip13` : Code CIP13 (unique)
- `ean` : Code EAN
- `name` : Nom du produit
- `category` : Catégorie
- `unit_price` : Prix unitaire
- `supplier_code` : Code fournisseur
- `stock_available` : Stock disponible
- `stock_reserved` : Stock réservé
- `created_at` : Date de création
- `updated_at` : Date de mise à jour

### Pharmacy

**Fichier** : `src/data/models/pharmacy.py`

**Table** : `pharmacies`

**Champs** :
- `id` : ID primaire
- `pharmacy_id` : ID métier unique
- `name` : Nom de la pharmacie
- `phone_number` : Numéro de téléphone (unique)
- `address` : Adresse
- `city` : Ville
- `is_active` : Actif
- `created_at` : Date de création
- `updated_at` : Date de mise à jour

### Call

**Fichier** : `src/data/models/call.py`

**Table** : `calls`

**Champs** :
- `id` : ID primaire
- `call_id` : ID métier unique
- `phone_number` : Numéro de téléphone
- `status` : Statut (active, completed, failed)
- `duration_seconds` : Durée en secondes
- `confidence_global` : Confiance globale
- `audio_recording_url` : URL de l'enregistrement
- `agent_version` : Version de l'agent
- `started_at` : Date de début
- `ended_at` : Date de fin

## Repositories

### BaseRepository

**Fichier** : `src/data/repositories/base.py`

**Responsabilité** : Repository générique avec CRUD de base

#### Méthodes

##### `get(id: int) -> Optional[ModelType]`
Récupère un élément par ID.

##### `get_all(skip: int = 0, limit: int = 100) -> List[ModelType]`
Récupère tous les éléments avec pagination.

##### `create(model: ModelType) -> ModelType`
Crée un nouvel élément.

##### `update(model: ModelType) -> ModelType`
Met à jour un élément.

##### `delete(id: int) -> bool`
Supprime un élément.

### OrderRepository

**Fichier** : `src/data/repositories/order_repository.py`

**Méthodes supplémentaires** :

##### `get_by_order_id(order_id: str) -> Optional[Order]`
Récupère une commande par ID métier.

##### `get_by_status(status: str, skip: int = 0, limit: int = 100) -> List[Order]`
Récupère les commandes par statut.

##### `get_by_pharmacy_id(pharmacy_id: str, skip: int = 0, limit: int = 100) -> List[Order]`
Récupère les commandes d'une pharmacie.

### ProductRepository

**Fichier** : `src/data/repositories/product_repository.py`

**Méthodes supplémentaires** :

##### `get_by_cip(cip13: str) -> Optional[Product]`
Récupère un produit par code CIP13.

##### `search(query: str, limit: int = 10) -> List[Product]`
Recherche de produits par nom.

### PharmacyRepository

**Fichier** : `src/data/repositories/pharmacy_repository.py`

**Méthodes supplémentaires** :

##### `get_by_pharmacy_id(pharmacy_id: str) -> Optional[Pharmacy]`
Récupère une pharmacie par ID métier.

##### `get_by_phone(phone_number: str) -> Optional[Pharmacy]`
Récupère une pharmacie par numéro de téléphone.

### CallRepository

**Fichier** : `src/data/repositories/call_repository.py`

**Méthodes supplémentaires** :

##### `get_by_call_id(call_id: str) -> Optional[Call]`
Récupère un appel par ID métier.

##### `get_by_status(status: str, skip: int = 0, limit: int = 100) -> List[Call]`
Récupère les appels par statut.

## Database

**Fichier** : `src/data/database.py`

**Responsabilité** : Configuration SQLAlchemy

### Configuration

```python
from src.data.database import engine, AsyncSessionLocal, Base, get_db

# Engine async
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class
class Base(DeclarativeBase):
    pass
```

### Dependency Injection

```python
from src.data.database import get_db

@router.get("/")
async def endpoint(db: AsyncSession = Depends(get_db)):
    # Utiliser db...
    pass
```

## Migrations

**Fichier** : `src/data/migrations/`

**Outil** : Alembic

### Commandes

```bash
# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

## Exemple d'utilisation

```python
from src.data.database import get_db
from src.data.repositories.order_repository import OrderRepository
from src.data.models import Order

# Dans une route
@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    repo = OrderRepository(db)
    order = await repo.get_by_order_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order
```

## Performance

- **Connection Pooling** : Pool de connexions configurable
- **Async/Await** : Toutes les opérations sont asynchrones
- **Lazy Loading** : Chargement paresseux des relations
- **Eager Loading** : Chargement anticipé avec `selectinload()`

## Tests

Les tests du module Data sont dans `tests/unit/test_data/`.

```bash
pytest tests/unit/test_data/ -v
```
