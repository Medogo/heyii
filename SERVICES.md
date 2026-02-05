# 🌐 Services & URLs - HEYI

Documentation complète des URLs et accès aux différents services du projet HEYI.

## 📱 Application Principale

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | API FastAPI principale |
| Swagger UI | http://localhost:8000/docs | Documentation interactive de l'API |
| ReDoc | http://localhost:8000/redoc | Documentation alternative de l'API |
| Health Check | http://localhost:8000/health/ | Vérification de santé basique |
| Readiness | http://localhost:8000/health/ready | Vérification de disponibilité (DB + Redis) |
| Métriques | http://localhost:8000/health/metrics | Métriques de l'application |

## 📊 Monitoring & Observabilité

| Service | URL | Credentials | Description |
|---------|-----|-------------|-------------|
| **Grafana** | http://localhost:3000 | `admin` / `admin` | Tableaux de bord et visualisations |
| **Prometheus** | http://localhost:9090 | - | Collecte et stockage de métriques |

> **Note Grafana** : La source de données Prometheus est automatiquement configurée avec l'URL `http://prometheus:9090` (accessible depuis le réseau Docker). Si vous configurez manuellement, utilisez cette URL depuis Grafana.
| Prometheus Graph | http://localhost:9090/graph | - | Interface de requêtes PromQL |
| Prometheus Metrics | http://localhost:9090/metrics | - | Endpoint de métriques Prometheus |

## 🗄️ Bases de Données & Services

| Service | URL/Port | Credentials | Description |
|---------|----------|-------------|-------------|
| **PostgreSQL** | `localhost:5432` | `heyi` / `heyi_password` | Base de données principale |
| **Redis** | `localhost:6379` | - | Cache et sessions |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | - | Interface web de Qdrant |
| **Qdrant API** | http://localhost:6333 | - | API REST de Qdrant |
| **Qdrant gRPC** | `localhost:6334` | - | API gRPC de Qdrant |

## 🔗 Accès depuis le réseau Docker

Depuis un conteneur dans le réseau `heyi-network`, utilisez les noms de services :

- **PostgreSQL**: `postgres:5432`
- **Redis**: `redis:6379`
- **Qdrant**: `qdrant:6333` (REST) ou `qdrant:6334` (gRPC)
- **Prometheus**: `prometheus:9090`
- **Grafana**: `grafana:3000`
- **App**: `app:8000`

## 🚀 Commandes Utiles

### Vérifier l'état des services
```bash
docker compose ps
```

### Voir les logs d'un service
```bash
docker compose logs -f app
docker compose logs -f grafana
docker compose logs -f prometheus
```

### Accéder à un conteneur
```bash
docker compose exec app bash
docker compose exec postgres psql -U heyi -d heyi_db
docker compose exec redis redis-cli
```

### Redémarrer un service
```bash
docker compose restart app
docker compose restart grafana
```

## 📝 Notes

- Tous les services sont accessibles sur `localhost` depuis votre machine hôte
- Les ports peuvent être modifiés dans `docker-compose.yml` si nécessaire
- Les credentials par défaut doivent être changés en production
- Les services communiquent entre eux via le réseau Docker `heyi-network`
