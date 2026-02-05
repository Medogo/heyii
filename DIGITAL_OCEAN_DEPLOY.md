# 🚀 Guide de Déploiement Digital Ocean

## Problèmes d'accessibilité - Diagnostic

Si `http://138.68.236.116/docs` est inaccessible, vérifiez les points suivants :

### 1. Vérifier que l'application tourne

```bash
# Se connecter au serveur
ssh root@138.68.236.116

# Vérifier les conteneurs Docker
docker ps

# Vérifier les logs
docker logs heyi-app

# Vérifier que le port 8000 écoute
netstat -tulpn | grep 8000
# ou
ss -tulpn | grep 8000
```

### 2. Vérifier le Firewall (UFW)

```bash
# Vérifier le statut du firewall
ufw status

# Autoriser le port 8000 si nécessaire
ufw allow 8000/tcp
ufw reload
```

### 3. Vérifier les règles de sécurité Digital Ocean

Dans le **Digital Ocean Dashboard** :
1. Allez dans **Networking** → **Firewalls**
2. Créez ou modifiez un firewall
3. Ajoutez une règle **Inbound** :
   - **Type** : Custom
   - **Protocol** : TCP
   - **Port Range** : 8000
   - **Sources** : All IPv4, All IPv6

### 4. Tester l'accessibilité

```bash
# Depuis votre machine locale
curl http://138.68.236.116:8000/
curl http://138.68.236.116:8000/health/
curl http://138.68.236.116:8000/docs

# Vérifier depuis le serveur
curl http://localhost:8000/
curl http://localhost:8000/health/
```

### 5. Configuration Nginx (Recommandé pour production)

Si vous utilisez Nginx comme reverse proxy :

```nginx
# /etc/nginx/sites-available/heyi
server {
    listen 80;
    server_name 138.68.236.116;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Puis :
```bash
sudo ln -s /etc/nginx/sites-available/heyi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Vérifier les variables d'environnement

Assurez-vous que le fichier `.env` existe et contient :

```env
DATABASE_URL=postgresql+asyncpg://heyi:heyi_password@postgres:5432/heyi_db
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

### 7. Redémarrer les services

```bash
# Redémarrer Docker Compose
cd /path/to/heyi
docker compose down
docker compose up -d

# Vérifier les logs
docker compose logs -f app
```

## URLs à tester

Une fois l'application accessible, testez ces endpoints :

- **API Root** : `http://138.68.236.116:8000/`
- **Swagger Docs** : `http://138.68.236.116:8000/docs`
- **ReDoc** : `http://138.68.236.116:8000/redoc`
- **Health Check** : `http://138.68.236.116:8000/health/`
- **Readiness** : `http://138.68.236.116:8000/health/ready`
- **Metrics** : `http://138.68.236.116:8000/health/metrics`

## Problèmes courants

### Problème : "Connection refused"

**Cause** : L'application n'écoute pas sur `0.0.0.0` ou le port est fermé

**Solution** :
```bash
# Vérifier dans docker-compose.yml que le port est mappé
ports:
  - "8000:8000"

# Vérifier que l'application écoute sur 0.0.0.0
# Dans src/core/config.py :
app_host: str = "0.0.0.0"
```

### Problème : "Timeout" ou "Connection timeout"

**Cause** : Firewall bloque le port

**Solution** :
```bash
# Ouvrir le port dans UFW
ufw allow 8000/tcp

# Vérifier dans Digital Ocean Firewall
```

### Problème : "502 Bad Gateway" (si Nginx)

**Cause** : L'application n'est pas accessible depuis Nginx

**Solution** :
```bash
# Vérifier que l'application tourne
docker ps

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/error.log
```

### Problème : Les liens dans `/docs` ne fonctionnent pas

**Cause** : Problème de CORS ou de configuration FastAPI

**Solution** : Vérifier que CORS est bien configuré dans `src/api/main.py` :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Commandes utiles

```bash
# Voir tous les conteneurs
docker ps -a

# Logs en temps réel
docker compose logs -f

# Redémarrer un service
docker compose restart app

# Rebuild et redémarrer
docker compose up -d --build app

# Vérifier les ports ouverts
sudo netstat -tulpn
# ou
sudo ss -tulpn

# Tester depuis le serveur
curl -v http://localhost:8000/health/
```

## Configuration recommandée pour production

1. **Utiliser HTTPS** avec Let's Encrypt
2. **Configurer Nginx** comme reverse proxy
3. **Restreindre CORS** aux domaines autorisés
4. **Configurer un firewall** strict
5. **Activer les logs** et monitoring
