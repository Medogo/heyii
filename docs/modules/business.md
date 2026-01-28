# 💼 Module Business

Le module Business contient la logique métier de l'application. Il encapsule les règles métier et coordonne les opérations entre les repositories et les intégrations.

## Vue d'ensemble

Le module Business est composé de 4 services :
- **OrderService** : Gestion des commandes
- **ProductService** : Gestion des produits
- **PharmacyService** : Gestion des pharmacies
- **ValidationService** : Validation des données métier

## Services

### 1. OrderService

**Fichier** : `src/business/order_service.py`

**Responsabilité** : Création et gestion des commandes

#### Méthodes principales

##### `create_order(call_id, pharmacy_id, items, confidence, delivery_notes) -> Order`
Crée une nouvelle commande.

**Paramètres** :
- `call_id` : ID de l'appel
- `pharmacy_id` : ID de la pharmacie
- `items` : Liste des produits commandés
- `confidence` : Score de confiance global
- `delivery_notes` : Notes de livraison (optionnel)

**Retour** : Objet `Order`

**Exemple** :
```python
from src.business.order_service import OrderService

order_service = OrderService(db)

order = await order_service.create_order(
    call_id="call_123",
    pharmacy_id="PHARM_001",
    items=[
        {
            "product_cip": "3400930000000",
            "quantity": 10,
            "unit": "boites",
            "transcript": "10 boites de Doliprane",
            "confidence": 0.95
        }
    ],
    confidence=0.95,
    delivery_notes="Livraison urgente"
)
```

**Fonctionnalités** :
- Vérification des stocks
- Calcul du total
- Détection de besoin de validation humaine
- Support du mode démo
- Envoi à l'ERP (si pas de review nécessaire)

##### `send_to_erp(order: Order) -> str`
Envoie une commande à l'ERP.

**Retour** : ID de commande ERP

##### `validate_order(order_id: str, validated_by: str) -> Order`
Valide manuellement une commande.

**Paramètres** :
- `order_id` : ID de la commande
- `validated_by` : Identifiant du validateur

#### Mode Démo

Si `settings.demo_mode = True`, le service utilise `DemoOrderService` au lieu de l'ERP réel :

```python
# Dans create_order()
if settings.demo_mode:
    demo_service = DemoOrderService(...)
    return await demo_service.create_order(...)
```

Voir [Mode Démo](../development/demo-mode.md) pour plus de détails.

#### Validation humaine

Une commande nécessite une validation humaine si :
- Montant > 10 000€
- Confiance < 0.85
- Produits en rupture de stock

### 2. ProductService

**Fichier** : `src/business/product_service.py`

**Responsabilité** : Recherche et gestion des produits

#### Méthodes principales

##### `search_product(query: str, limit: int = 5) -> List[ProductSearch]`
Recherche un produit par nom.

**Paramètres** :
- `query` : Nom du produit à rechercher
- `limit` : Nombre de résultats max

**Retour** : Liste de `ProductSearch` (produit + score)

**Exemple** :
```python
from src.business.product_service import ProductService

product_service = ProductService(db)

results = await product_service.search_product("Doliprane", limit=5)
for result in results:
    print(f"{result.product.name} - Score: {result.score}")
```

##### `get_by_cip(cip13: str) -> Optional[Product]`
Récupère un produit par code CIP13.

##### `check_stock(cip13: str, quantity: int) -> bool`
Vérifie si le stock est suffisant.

##### `reserve_stock(cip13: str, quantity: int)`
Réserve du stock pour une commande.

##### `update_stock(cip13: str, quantity: int)`
Met à jour le stock d'un produit.

### 3. PharmacyService

**Fichier** : `src/business/pharmacy_service.py`

**Responsabilité** : Gestion des pharmacies

#### Méthodes principales

##### `get_by_phone(phone_number: str) -> Optional[Pharmacy]`
Récupère une pharmacie par numéro de téléphone.

##### `get_by_pharmacy_id(pharmacy_id: str) -> Optional[Pharmacy]`
Récupère une pharmacie par ID métier.

##### `authenticate_caller(phone_number: str) -> Optional[Pharmacy]`
Authentifie un appelant par son numéro.

**Retour** : `Pharmacy` si authentifié, `None` sinon

**Exemple** :
```python
from src.business.pharmacy_service import PharmacyService

pharmacy_service = PharmacyService(db)

pharmacy = await pharmacy_service.authenticate_caller("+22900000000")
if pharmacy:
    print(f"Pharmacie authentifiée: {pharmacy.name}")
else:
    print("Pharmacie non reconnue")
```

### 4. ValidationService

**Fichier** : `src/business/validation_service.py`

**Responsabilité** : Validation des données métier

#### Méthodes principales

##### `validate_order_items(items: List[Dict]) -> Tuple[bool, List[str]]`
Valide les items d'une commande.

**Retour** : `(is_valid, errors)`

##### `validate_phone_number(phone: str) -> bool`
Valide un numéro de téléphone.

##### `validate_cip13(cip13: str) -> bool`
Valide un code CIP13.

## Flux de création de commande

```
1. AgentOrchestrator → Validation commande
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

## Gestion des erreurs

Les services métier gèrent les erreurs suivantes :

- **Produit non trouvé** : `ValueError("Product not found: {cip13}")`
- **Stock insuffisant** : Item marqué `out_of_stock`
- **Commande non trouvée** : `ValueError("Order not found: {order_id}")`
- **Erreur ERP** : Commande créée mais pas envoyée à l'ERP

## Tests

Les tests du module Business sont dans `tests/unit/test_business/`.

```bash
pytest tests/unit/test_business/ -v
```
