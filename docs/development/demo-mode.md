# 🎭 Mode Démo

Documentation du mode démo de HEYI.

## Vue d'ensemble

Le mode démo permet de tester l'application sans connexion à un ERP réel. Il utilise un mock ERP et envoie des notifications par email/WhatsApp.

## Activation

### Configuration

Dans le fichier `.env` :

```env
DEMO_MODE=true
DEMO_NOTIFICATION_EMAILS=admin@example.com,dev@example.com
DEMO_NOTIFICATION_WHATSAPP=+22900000000
```

### Variables

- `DEMO_MODE` : Activer le mode démo (true/false)
- `DEMO_NOTIFICATION_EMAILS` : Liste d'emails séparés par virgules
- `DEMO_NOTIFICATION_WHATSAPP` : Numéro WhatsApp pour notifications

## Fonctionnement

### OrderService

Quand `DEMO_MODE=true`, le `OrderService` utilise `DemoOrderService` au lieu de l'ERP réel :

```python
# Dans OrderService.create_order()
if settings.demo_mode:
    demo_service = DemoOrderService(...)
    return await demo_service.create_order(...)
```

### DemoOrderService

**Fichier** : `src/demo/demo_order_service.py`

**Responsabilité** : Création de commandes en mode démo

#### Fonctionnalités

1. **Mock ERP** : Utilise `MockERPClient` au lieu de l'ERP réel
2. **Notifications** : Envoie des notifications par email/WhatsApp
3. **Traçabilité** : Crée quand même l'ordre en base avec statut "demo"

#### Méthodes

##### `create_order(call_id, pharmacy_id, pharmacy_name, items, confidence) -> Dict`
Crée une commande en mode démo.

**Retour** :
```python
{
    "success": True,
    "order_id": "DEMO-CMD-20240128120000",
    "total_amount": 55.00,
    "erp_response": {
        "order_id": "DEMO-ERP-123",
        "status": "created"
    },
    "notifications_sent": {
        "email": True,
        "whatsapp": True
    },
    "mode": "DEMO",
    "message": "✅ Commande créée en mode DÉMO (aucune connexion ERP réelle)"
}
```

### MockERPClient

**Fichier** : `src/demo/mock_erp_client.py`

**Responsabilité** : Mock de l'ERP

#### Fonctionnalités

- Simule la création de commandes
- Stocke les commandes en mémoire
- Retourne des réponses réalistes

#### Méthodes

##### `create_order(order_data: Dict) -> Dict`
Crée une commande simulée.

##### `get_all_orders() -> List[Dict]`
Récupère toutes les commandes simulées.

### DemoNotificationHandler

**Fichier** : `src/demo/notification_handler.py`

**Responsabilité** : Gestion des notifications en mode démo

#### Fonctionnalités

- Envoie des emails de notification
- Envoie des messages WhatsApp (si configuré)
- Formate les messages de manière lisible

#### Méthodes

##### `send_order_notification(order_id, pharmacy_name, items, total_amount, ...) -> Dict`
Envoie une notification de nouvelle commande.

## Exemple d'utilisation

### 1. Activer le mode démo

```env
DEMO_MODE=true
DEMO_NOTIFICATION_EMAILS=admin@example.com
```

### 2. Créer une commande

L'API fonctionne normalement, mais utilise le mock ERP :

```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_123",
    "pharmacy_id": "PHARM_001",
    "items": [
      {
        "product_cip": "3400930000000",
        "quantity": 10,
        "unit": "boites"
      }
    ],
    "confidence": 0.95
  }'
```

### 3. Vérifier les notifications

Les notifications sont envoyées aux emails configurés.

### 4. Vérifier les commandes démo

```bash
curl http://localhost:8000/orders/
```

Les commandes ont le statut `"demo"` et `erp_created=true`.

## Différences avec le mode production

| Aspect | Mode Démo | Mode Production |
|--------|-----------|-----------------|
| ERP | MockERPClient | ERPClient réel |
| Notifications | Email/WhatsApp | Email/Slack/SMS |
| Statut commande | "demo" | "pending"/"confirmed" |
| Traçabilité | Oui (en base) | Oui (en base) |
| Stock réel | Non vérifié | Vérifié |

## Avantages

- **Tests sans ERP** : Tester sans connexion ERP
- **Développement** : Développer sans dépendances externes
- **Démonstrations** : Présenter le système sans risque
- **Formation** : Former les utilisateurs

## Limitations

- **Pas de stock réel** : Le stock n'est pas vérifié
- **Pas d'ERP réel** : Les commandes ne sont pas dans l'ERP
- **Notifications limitées** : Seulement email/WhatsApp

## Tests

Les tests du mode démo sont dans `tests/unit/test_demo/` :

```bash
pytest tests/unit/test_demo/ -v
```

## Scripts

### Test du mode démo

```bash
python scripts/test_demo_mode.py
```

Ce script :
1. Active le mode démo
2. Crée une commande test
3. Vérifie les notifications
4. Affiche les résultats
