# 📡 API REST - Documentation

Documentation complète de l'API REST de HEYI.

## Base URL

```
http://localhost:8000
```

## Authentification

L'API utilise JWT pour l'authentification. Inclure le token dans le header :

```
Authorization: Bearer <token>
```

## Endpoints

### Health

#### GET `/health/`
Health check basique.

**Réponse** :
```json
{
  "status": "healthy",
  "service": "heyi-api",
  "version": "1.0.0"
}
```

#### GET `/health/ready`
Readiness check (database + redis).

**Réponse** :
```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "redis": true
  }
}
```

#### GET `/health/metrics`
Métriques de l'application.

**Réponse** :
```json
{
  "active_calls": 5,
  "active_sessions": 5,
  "max_concurrent_calls": 10
}
```

### Calls

#### GET `/calls/`
Lister tous les appels.

**Paramètres de requête** :
- `skip` (int, default: 0) : Nombre d'éléments à sauter
- `limit` (int, default: 100) : Nombre d'éléments à retourner

**Réponse** : `List[CallResponse]`

**Exemple** :
```bash
curl http://localhost:8000/calls/?skip=0&limit=10
```

#### GET `/calls/{call_id}`
Récupérer un appel par ID.

**Paramètres** :
- `call_id` (string) : ID de l'appel

**Réponse** : `CallResponse`

**Exemple** :
```bash
curl http://localhost:8000/calls/call_123
```

#### GET `/calls/active/list`
Lister les appels actifs.

**Réponse** :
```json
{
  "active_calls": ["call_123", "call_456"],
  "count": 2
}
```

#### GET `/calls/stats`
Statistiques des appels.

**Réponse** : `CallStats`
```json
{
  "total_calls": 150,
  "active_calls": 5,
  "completed_calls": 140,
  "failed_calls": 5,
  "average_duration": 120.5,
  "average_confidence": 0.92
}
```

### Orders

#### GET `/orders/`
Lister toutes les commandes.

**Paramètres de requête** :
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `status` (string, optional) : Filtrer par statut

**Réponse** : `List[OrderResponse]`

**Exemple** :
```bash
curl http://localhost:8000/orders/?status=pending&limit=20
```

#### GET `/orders/{order_id}`
Récupérer une commande par ID.

**Paramètres** :
- `order_id` (string) : ID de la commande

**Réponse** : `OrderResponse`

#### POST `/orders/`
Créer une nouvelle commande.

**Body** : `OrderCreate`
```json
{
  "call_id": "call_123",
  "pharmacy_id": "PHARM_001",
  "items": [
    {
      "product_cip": "3400930000000",
      "quantity": 10,
      "unit": "boites",
      "audio_transcript": "10 boites de Doliprane",
      "confidence_score": 0.95
    }
  ],
  "delivery_notes": "Livraison urgente"
}
```

**Réponse** : `OrderResponse`

#### POST `/orders/{order_id}/validate`
Valider manuellement une commande.

**Body** :
```json
{
  "validated_by": "user_123"
}
```

**Réponse** : `OrderResponse`

#### GET `/orders/stats`
Statistiques des commandes.

**Réponse** : `OrderStats`
```json
{
  "total_orders": 500,
  "pending_orders": 10,
  "completed_orders": 480,
  "total_amount": 125000.50,
  "average_items_per_order": 3.5
}
```

### Products

#### GET `/products/`
Lister tous les produits.

**Paramètres de requête** :
- `skip` (int, default: 0)
- `limit` (int, default: 100)

**Réponse** : `List[ProductResponse]`

#### GET `/products/search`
Rechercher des produits.

**Paramètres de requête** :
- `q` (string, required) : Terme de recherche
- `limit` (int, default: 10, max: 50) : Nombre de résultats
- `use_semantic` (bool, default: true) : Utiliser la recherche sémantique

**Réponse** : `List[ProductSearch]`

**Exemple** :
```bash
curl "http://localhost:8000/products/search?q=Doliprane&limit=5&use_semantic=true"
```

**Réponse** :
```json
[
  {
    "product": {
      "id": 1,
      "cip13": "3400930000000",
      "name": "Doliprane 1000mg",
      "unit_price": 5.50
    },
    "score": 0.95,
    "match_type": "semantic"
  }
]
```

#### GET `/products/{product_id}`
Récupérer un produit par ID.

**Réponse** : `ProductResponse`

#### GET `/products/cip/{cip13}`
Récupérer un produit par code CIP13.

**Paramètres** :
- `cip13` (string) : Code CIP13

**Réponse** : `ProductResponse`

#### POST `/products/`
Créer un nouveau produit.

**Body** : `ProductCreate`
```json
{
  "cip13": "3400930000000",
  "ean": "3400930000000",
  "name": "Doliprane 1000mg",
  "category": "Antalgique",
  "unit_price": 5.50,
  "supplier_code": "SUP001",
  "stock_available": 100
}
```

**Réponse** : `ProductResponse`

#### POST `/products/check-stock`
Vérifier le stock d'un produit.

**Body** : `StockCheckRequest`
```json
{
  "cip13": "3400930000000",
  "quantity": 10
}
```

**Réponse** : `StockCheckResponse`
```json
{
  "cip13": "3400930000000",
  "requested": 10,
  "available": 100,
  "is_available": true
}
```

## Schémas de données

### CallResponse
```json
{
  "id": 1,
  "call_id": "call_123",
  "phone_number": "+22900000000",
  "status": "completed",
  "duration_seconds": 120,
  "confidence_global": 0.95,
  "audio_recording_url": "https://...",
  "agent_version": "1.0.0",
  "started_at": "2024-01-28T12:00:00Z",
  "ended_at": "2024-01-28T12:02:00Z"
}
```

### OrderResponse
```json
{
  "id": 1,
  "order_id": "CMD-20240128120000",
  "call_id": 1,
  "pharmacy_id": "PHARM_001",
  "status": "confirmed",
  "total_amount": 55.00,
  "delivery_date": "2024-01-30",
  "required_human_review": false,
  "erp_created": true,
  "erp_order_id": "ERP_123",
  "created_at": "2024-01-28T12:00:00Z",
  "items": [
    {
      "id": 1,
      "product_cip": "3400930000000",
      "product_name": "Doliprane 1000mg",
      "quantity": 10,
      "unit": "boites",
      "unit_price": 5.50,
      "line_total": 55.00,
      "status": "ok",
      "extracted_at": "2024-01-28T12:00:00Z"
    }
  ]
}
```

### ProductResponse
```json
{
  "id": 1,
  "cip13": "3400930000000",
  "ean": "3400930000000",
  "name": "Doliprane 1000mg",
  "category": "Antalgique",
  "unit_price": 5.50,
  "supplier_code": "SUP001",
  "stock_available": 100,
  "stock_reserved": 10,
  "created_at": "2024-01-28T12:00:00Z",
  "updated_at": "2024-01-28T12:00:00Z"
}
```

## Codes d'erreur

- `200` : Succès
- `201` : Créé
- `400` : Requête invalide
- `401` : Non authentifié
- `403` : Non autorisé
- `404` : Non trouvé
- `500` : Erreur serveur

## Rate Limiting

L'API applique un rate limiting :
- **100 requêtes/minute** par IP
- **1000 requêtes/heure** par IP

## Documentation interactive

La documentation interactive Swagger est disponible à :
```
http://localhost:8000/docs
```

La documentation ReDoc est disponible à :
```
http://localhost:8000/redoc
```
