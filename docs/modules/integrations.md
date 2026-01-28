# 🔗 Module Integrations

Le module Integrations gère les intégrations externes : ERP et Notifications.

## Vue d'ensemble

Le module Integrations est composé de :
- **ERP** : Intégration avec l'ERP
- **Notifications** : Emails, SMS, Slack

## ERP

### ERPClient

**Fichier** : `src/integrations/erp/client.py`

**Responsabilité** : Client pour communiquer avec l'ERP

#### Méthodes principales

##### `create_order(order_data: Dict) -> Dict`
Crée une commande dans l'ERP.

**Paramètres** :
```python
order_data = {
    "pharmacy_id": "PHARM_001",
    "order_date": "2024-01-28T12:00:00Z",
    "items": [
        {
            "product_cip13": "3400930000000",
            "quantity": 10,
            "unit_price": 5.50,
            "line_total": 55.00
        }
    ],
    "delivery_date": "2024-01-30",
    "notes": "Livraison urgente",
    "source": "agent_ia_v1",
    "external_order_id": "CMD-20240128120000",
    "total_amount": 55.00
}
```

**Retour** :
```python
{
    "order_id": "ERP_123",
    "status": "created"
}
```

##### `search_product(query: str, fuzzy: bool = True) -> List[Dict]`
Recherche un produit dans le catalogue ERP.

##### `check_availability(items: List[Dict]) -> Dict`
Vérifie la disponibilité des produits.

##### `get_order_status(erp_order_id: str) -> Dict`
Récupère le statut d'une commande dans l'ERP.

##### `sync_stock(cip13: str) -> int`
Synchronise le stock d'un produit depuis l'ERP.

#### Retry Strategy

**Fichier** : `src/integrations/erp/retry.py`

Le client ERP utilise une stratégie de retry avec backoff exponentiel :

```python
from src.integrations.erp.retry import retry_on_error

@retry_on_error(max_attempts=3, delay=1.0, backoff=2.0)
async def create_order(self, order_data):
    # ...
```

### ERPMapper

**Fichier** : `src/integrations/erp/mapper.py`

**Responsabilité** : Mapping des données entre HEYI et l'ERP

#### Méthodes

##### `order_to_erp(order: Order) -> Dict`
Convertit une commande HEYI vers format ERP.

##### `order_item_to_erp(item: OrderItem) -> Dict`
Convertit un item de commande vers format ERP.

##### `erp_product_to_heyi(erp_product: Dict) -> Dict`
Convertit un produit ERP vers format HEYI.

### BaseERPClient

**Fichier** : `src/integrations/erp/base.py`

**Responsabilité** : Interface abstraite pour les clients ERP

Permet d'implémenter d'autres fournisseurs ERP.

## Notifications

### BrevoEmailService

**Fichier** : `src/integrations/notifications/brevo_email.py`

**Responsabilité** : Envoi d'emails via Brevo (ex-Sendinblue)

#### Méthodes principales

##### `send_email(to, subject, html_content, text_content, ...) -> bool`
Envoie un email.

**Paramètres** :
- `to` : Liste de destinataires `[{"email": "...", "name": "..."}]`
- `subject` : Sujet
- `html_content` : Contenu HTML
- `text_content` : Contenu texte (fallback)
- `cc`, `bcc`, `reply_to` : Options
- `tags` : Tags pour tracking
- `params` : Paramètres de personnalisation

##### `send_order_notification(order_id, pharmacy_name, total_amount, items_count, to_emails) -> bool`
Envoie une notification de nouvelle commande.

##### `send_validation_required(order_id, reason, amount, to_emails) -> bool`
Envoie une alerte de validation humaine requise.

##### `send_error_alert(error_message, call_id, to_emails) -> bool`
Envoie une alerte d'erreur système.

##### `send_daily_report(date, total_calls, total_orders, total_amount, success_rate, to_emails) -> bool`
Envoie un rapport quotidien.

#### Exemple

```python
from src.integrations.notifications.brevo_email import BrevoEmailService

email_service = BrevoEmailService(
    api_key=settings.brevo_api_key,
    sender_email=settings.brevo_sender_email,
    sender_name="HEYI"
)

await email_service.send_order_notification(
    order_id="CMD-20240128120000",
    pharmacy_name="Pharmacie Centrale",
    total_amount=55.00,
    items_count=2,
    to_emails=["admin@example.com"]
)
```

### EmailService

**Fichier** : `src/integrations/notifications/email.py`

**Responsabilité** : Service d'email générique (interface)

### SlackService

**Fichier** : `src/integrations/notifications/slack.py`

**Responsabilité** : Envoi de notifications Slack

#### Méthodes principales

##### `send_message(channel: str, message: str) -> bool`
Envoie un message Slack.

##### `send_order_notification(order_id: str, order_data: Dict) -> bool`
Envoie une notification de commande.

### SMSService

**Fichier** : `src/integrations/notifications/sms.py`

**Responsabilité** : Envoi de SMS

#### Méthodes principales

##### `send_sms(to: str, message: str) -> bool`
Envoie un SMS.

## Configuration

Les intégrations sont configurées dans `src/core/config.py` :

```python
# ERP
erp_api_url: str
erp_api_key: str
erp_timeout: int = 5

# Brevo
brevo_api_key: str
brevo_sender_email: str
brevo_sender_name: str = "HEYI"
```

## Gestion des erreurs

### ERP

- **Retry automatique** : 3 tentatives avec backoff exponentiel
- **Timeout** : 5 secondes par défaut
- **Fallback** : Commande créée en base mais pas dans l'ERP

### Notifications

- **Retry** : 2 tentatives pour emails
- **Logging** : Toutes les erreurs sont loggées
- **Non-bloquant** : Les erreurs de notification n'empêchent pas le traitement

## Tests

Les tests du module Integrations sont dans `tests/integration/test_erp/`.

```bash
pytest tests/integration/test_erp/ -v
```
