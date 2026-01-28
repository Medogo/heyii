# 📋 Schémas de Données API

Documentation des schémas Pydantic utilisés dans l'API.

## Schémas Call

### CallBase
Schéma de base pour un appel.

```python
class CallBase(BaseModel):
    phone_number: str
```

### CallCreate
Schéma pour créer un appel.

```python
class CallCreate(CallBase):
    pass
```

### CallResponse
Schéma de réponse pour un appel.

```python
class CallResponse(CallBase):
    id: int
    call_id: str
    status: str
    duration_seconds: Optional[int]
    confidence_global: Optional[float]
    audio_recording_url: Optional[str]
    agent_version: str
    started_at: datetime
    ended_at: Optional[datetime]
```

### CallStats
Statistiques des appels.

```python
class CallStats(BaseModel):
    total_calls: int
    active_calls: int
    completed_calls: int
    failed_calls: int
    average_duration: float
    average_confidence: float
```

## Schémas Order

### OrderItemBase
Schéma de base pour un item de commande.

```python
class OrderItemBase(BaseModel):
    product_cip: str
    quantity: int
    unit: str = "boites"
```

### OrderItemCreate
Schéma pour créer un item.

```python
class OrderItemCreate(OrderItemBase):
    audio_transcript: Optional[str]
    confidence_score: Optional[float]
```

### OrderItemResponse
Schéma de réponse pour un item.

```python
class OrderItemResponse(OrderItemBase):
    id: int
    product_name: str
    unit_price: float
    line_total: float
    status: str
    extracted_at: datetime
```

### OrderBase
Schéma de base pour une commande.

```python
class OrderBase(BaseModel):
    pharmacy_id: int
    delivery_notes: Optional[str]
```

### OrderCreate
Schéma pour créer une commande.

```python
class OrderCreate(OrderBase):
    call_id: str
    items: List[OrderItemCreate]
```

### OrderResponse
Schéma de réponse pour une commande.

```python
class OrderResponse(OrderBase):
    id: int
    order_id: str
    call_id: int
    status: str
    total_amount: float
    delivery_date: Optional[date]
    required_human_review: bool
    erp_created: bool
    erp_order_id: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]
```

### OrderStats
Statistiques des commandes.

```python
class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_amount: float
    average_items_per_order: float
```

## Schémas Product

### ProductBase
Schéma de base pour un produit.

```python
class ProductBase(BaseModel):
    cip13: str  # 13 caractères
    name: str
    category: Optional[str]
    unit_price: float
```

### ProductCreate
Schéma pour créer un produit.

```python
class ProductCreate(ProductBase):
    ean: str
    supplier_code: Optional[str]
    stock_available: int = 0
```

### ProductResponse
Schéma de réponse pour un produit.

```python
class ProductResponse(ProductBase):
    id: int
    ean: str
    supplier_code: Optional[str]
    stock_available: int
    stock_reserved: int
    created_at: datetime
    updated_at: datetime
```

### ProductSearch
Résultat de recherche de produit.

```python
class ProductSearch(BaseModel):
    product: ProductResponse
    score: float  # 0.0 à 1.0
    match_type: str  # "exact", "fuzzy", "semantic"
```

### StockCheckRequest
Requête de vérification de stock.

```python
class StockCheckRequest(BaseModel):
    cip13: str
    quantity: int
```

### StockCheckResponse
Réponse de vérification de stock.

```python
class StockCheckResponse(BaseModel):
    cip13: str
    requested: int
    available: int
    is_available: bool
```

## Validation

Tous les schémas utilisent Pydantic pour la validation :

- **Types** : Validation automatique des types
- **Contraintes** : Validation des contraintes (min, max, etc.)
- **Required** : Champs obligatoires
- **Optional** : Champs optionnels

## Exemples

### Créer une commande

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

### Réponse d'une commande

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
