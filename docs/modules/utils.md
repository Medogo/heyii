# 🛠️ Module Utils

Le module Utils contient les utilitaires partagés : cache, formatters, metrics, parsers, validators.

## Vue d'ensemble

Le module Utils est composé de :
- **Cache** : Wrapper Redis
- **Formatters** : Formatage de données
- **Metrics** : Métriques Prometheus
- **Parsers** : Parsing de texte
- **Validators** : Validation de données

## Cache

### Cache

**Fichier** : `src/utils/cache.py`

**Responsabilité** : Wrapper Redis pour le cache

#### Méthodes principales

##### `connect()`
Connecte au serveur Redis.

##### `disconnect()`
Déconnecte de Redis.

##### `get(key: str) -> Optional[str]`
Récupère une valeur depuis le cache.

##### `set(key: str, value: str, ttl: int = None)`
Met une valeur en cache.

##### `delete(key: str)`
Supprime une clé du cache.

##### `exists(key: str) -> bool`
Vérifie si une clé existe.

#### Exemple

```python
from src.utils.cache import cache

# Connecter
await cache.connect()

# Mettre en cache
await cache.set("key", "value", ttl=300)

# Récupérer
value = await cache.get("key")

# Supprimer
await cache.delete("key")
```

## Formatters

**Fichier** : `src/utils/formatters.py`

**Responsabilité** : Formatage de données

#### Fonctions

##### `format_currency(amount: float, currency: str = "€") -> str`
Formate un montant.

```python
from src.utils.formatters import format_currency

formatted = format_currency(1234.56)  # "1 234.56 €"
```

##### `format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str`
Formate une date.

```python
from src.utils.formatters import format_datetime

formatted = format_datetime(datetime.now())  # "28/01/2024 12:00"
```

##### `format_phone_display(phone: str) -> str`
Formate un numéro pour affichage.

```python
from src.utils.formatters import format_phone_display

formatted = format_phone_display("+22900000000")  # "+229 00 00 00 00"
```

##### `format_order_summary(order: Dict) -> str`
Formate le résumé d'une commande.

```python
from src.utils.formatters import format_order_summary

summary = format_order_summary({
    "order_id": "CMD-123",
    "items": [
        {"quantity": 10, "product_name": "Doliprane"}
    ],
    "total_amount": 55.00
})
```

## Metrics

**Fichier** : `src/utils/metrics.py`

**Responsabilité** : Métriques Prometheus

#### Métriques disponibles

##### Compteurs

- `calls_total` : Nombre total d'appels (par statut)
- `orders_total` : Nombre total de commandes (par statut)
- `errors_total` : Nombre total d'erreurs (par type)

##### Histogrammes

- `call_duration` : Durée des appels en secondes
- `api_latency` : Latence des requêtes API (par endpoint, méthode)
- `stt_latency` : Latence du STT
- `llm_latency` : Latence du LLM
- `tts_latency` : Latence du TTS

##### Gauges

- `active_calls` : Nombre d'appels actifs
- `active_sessions` : Nombre de sessions actives

#### Fonctions

##### `record_call_completed(duration: float, status: str)`
Enregistre un appel terminé.

##### `record_order_created(status: str)`
Enregistre une commande créée.

##### `record_error(error_type: str)`
Enregistre une erreur.

#### Exemple

```python
from src.utils.metrics import (
    record_call_completed,
    record_order_created,
    record_error,
    active_calls
)

# Enregistrer un appel
record_call_completed(duration=120.5, status="completed")

# Enregistrer une commande
record_order_created(status="confirmed")

# Enregistrer une erreur
record_error(error_type="stt_error")

# Mettre à jour un gauge
active_calls.set(5)
```

## Parsers

**Fichier** : `src/utils/parsers.py`

**Responsabilité** : Parsing de texte

#### Fonctions

##### `parse_quantity_from_text(text: str) -> Tuple[Optional[int], Optional[str]]`
Extrait quantité et unité depuis un texte.

```python
from src.utils.parsers import parse_quantity_from_text

quantity, unit = parse_quantity_from_text("10 boites de Doliprane")
# (10, "boites")

quantity, unit = parse_quantity_from_text("5 unités")
# (5, "unités")
```

##### `parse_product_name(text: str) -> str`
Nettoie et normalise un nom de produit.

```python
from src.utils.parsers import parse_product_name

cleaned = parse_product_name("euh donc Doliprane voilà")
# "doliprane"
```

## Validators

**Fichier** : `src/utils/validators.py`

**Responsabilité** : Validation de données

#### Fonctions

##### `validate_phone_number(phone: str) -> bool`
Valide un numéro de téléphone.

```python
from src.utils.validators import validate_phone_number

is_valid = validate_phone_number("+22900000000")  # True
is_valid = validate_phone_number("invalid")     # False
```

##### `validate_cip13(cip13: str) -> bool`
Valide un code CIP13.

```python
from src.utils.validators import validate_cip13

is_valid = validate_cip13("3400930000000")  # True (13 chiffres)
is_valid = validate_cip13("123")            # False
```

##### `validate_email(email: str) -> bool`
Valide une adresse email.

```python
from src.utils.validators import validate_email

is_valid = validate_email("test@example.com")  # True
is_valid = validate_email("invalid")            # False
```

##### `sanitize_text(text: str) -> str`
Nettoie un texte.

```python
from src.utils.validators import sanitize_text

cleaned = sanitize_text("Hello! @#$%^&*()")
# "Hello!"
```

## Configuration

Les utilitaires utilisent la configuration dans `src/core/config.py` :

```python
# Redis
redis_url: str
redis_ttl: int = 300
```

## Tests

Les tests du module Utils sont dans `tests/unit/test_utils/`.

```bash
pytest tests/unit/test_utils/ -v
```
