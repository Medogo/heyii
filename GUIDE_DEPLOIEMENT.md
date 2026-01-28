# 🚀 GUIDE DE DÉPLOIEMENT INFRASTRUCTURE - HEYI

## 📋 Vue d'ensemble

Cette infrastructure déploie HEYI sur AWS avec:
- **VPC** multi-AZ avec subnets publics/privés
- **EKS** (Kubernetes) pour l'orchestration
- **RDS PostgreSQL** pour la base de données
- **ElastiCache Redis** pour le cache
- **S3** pour le stockage des enregistrements audio
- **Monitoring** avec Prometheus & Grafana

---

## 📦 STRUCTURE DES FICHIERS

```
infrastructure/
├── terraform/
│   ├── main.tf                    # Configuration principale
│   ├── variables.tf               # Variables
│   ├── outputs.tf                 # Outputs
│   ├── modules/
│   │   ├── vpc/                   # Module VPC
│   │   ├── eks/                   # Module EKS
│   │   ├── rds/                   # Module RDS
│   │   ├── redis/                 # Module Redis
│   │   └── s3/                    # Module S3
│   └── environments/
│       ├── dev/
│       │   └── terraform.tfvars
│       ├── staging/
│       │   └── terraform.tfvars
│       └── production/
│           └── terraform.tfvars
│
└── kubernetes/
    ├── base/
    │   ├── namespace.yaml
    │   ├── configmap.yaml
    │   ├── secrets.yaml
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── ingress.yaml
    │   └── hpa.yaml
    ├── monitoring/
    │   ├── prometheus.yaml
    │   └── grafana.yaml
    └── overlays/
        ├── dev/
        ├── staging/
        └── production/
```

---

## 🔧 PRÉREQUIS

### Outils nécessaires
```bash
# Terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Kustomize
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
sudo mv kustomize /usr/local/bin/

# Helm (optionnel)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Configuration AWS
```bash
# Configurer AWS CLI
aws configure

# Vérifier
aws sts get-caller-identity
```

---

## 🏗️ ÉTAPE 1 : DÉPLOYER L'INFRASTRUCTURE (TERRAFORM)

### 1.1 Initialiser Terraform

```bash
cd infrastructure/terraform

# Dev
terraform init -backend-config="key=dev/terraform.tfstate"

# Production
terraform init -backend-config="key=prod/terraform.tfstate"
```

### 1.2 Créer le backend S3 (première fois uniquement)

```bash
# Créer bucket S3 pour state
aws s3api create-bucket \
  --bucket heyi-terraform-state \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1

# Activer versioning
aws s3api put-bucket-versioning \
  --bucket heyi-terraform-state \
  --versioning-configuration Status=Enabled

# Créer table DynamoDB pour locks
aws dynamodb create-table \
  --table-name heyi-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region eu-west-1
```

### 1.3 Déployer l'infrastructure

```bash
# Développement
terraform workspace new dev
terraform plan -var-file="environments/dev/terraform.tfvars"
terraform apply -var-file="environments/dev/terraform.tfvars"

# Production
terraform workspace new production
terraform plan -var-file="environments/production/terraform.tfvars"
terraform apply -var-file="environments/production/terraform.tfvars"
```

### 1.4 Récupérer les outputs

```bash
# Endpoint EKS
terraform output eks_cluster_endpoint

# Endpoint RDS
terraform output rds_endpoint

# Endpoint Redis
terraform output redis_endpoint

# Bucket S3
terraform output s3_audio_bucket
```

---

## ☸️ ÉTAPE 2 : DÉPLOYER SUR KUBERNETES

### 2.1 Configurer kubectl

```bash
# Récupérer le nom du cluster
CLUSTER_NAME=$(terraform output -raw eks_cluster_name)

# Configurer kubectl
aws eks update-kubeconfig \
  --region eu-west-1 \
  --name $CLUSTER_NAME

# Vérifier
kubectl get nodes
```

### 2.2 Créer les secrets

```bash
cd infrastructure/kubernetes

# Éditer les secrets avec les vraies valeurs
kubectl create secret generic heyi-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://user:password@rds-endpoint:5432/heyi_db" \
  --from-literal=REDIS_URL="redis://redis-endpoint:6379/0" \
  --from-literal=DEEPGRAM_API_KEY="your_key" \
  --from-literal=OPENAI_API_KEY="your_key" \
  --from-literal=ELEVENLABS_API_KEY="your_key" \
  --from-literal=ELEVENLABS_VOICE_ID="your_voice_id" \
  --from-literal=TWILIO_ACCOUNT_SID="your_sid" \
  --from-literal=TWILIO_AUTH_TOKEN="your_token" \
  --from-literal=TWILIO_PHONE_NUMBER="+1234567890" \
  --from-literal=BREVO_API_KEY="your_key" \
  --from-literal=BREVO_SENDER_EMAIL="noreply@heyi.com" \
  --from-literal=ERP_API_URL="https://erp.example.com/api" \
  --from-literal=ERP_API_KEY="your_key" \
  --from-literal=SECRET_KEY="your-super-secret-key" \
  --namespace=heyi
```

### 2.3 Déployer avec Kustomize

```bash
# Développement
kubectl apply -k overlays/dev/

# Production
kubectl apply -k overlays/production/

# Vérifier le déploiement
kubectl get all -n heyi
kubectl get pods -n heyi -w
```

### 2.4 Vérifier les services

```bash
# API
kubectl get svc heyi-api-service -n heyi

# Qdrant
kubectl get svc qdrant-service -n heyi

# Prometheus
kubectl get svc prometheus-service -n heyi

# Grafana
kubectl get svc grafana-service -n heyi
```

---

## 🌐 ÉTAPE 3 : CONFIGURER LE DOMAINE & TLS

### 3.1 Installer cert-manager

```bash
# Ajouter le repo Helm
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Installer cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.crds.yaml

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0
```

### 3.2 Configurer Let's Encrypt

```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@heyi.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 3.3 Configurer le DNS

```bash
# Récupérer l'IP du Load Balancer
kubectl get svc -n ingress-nginx

# Créer un enregistrement DNS A
# api.heyi.com -> IP_DU_LOAD_BALANCER
```

---

## 📊 ÉTAPE 4 : ACCÉDER AU MONITORING

### 4.1 Port-forward Grafana

```bash
kubectl port-forward -n heyi svc/grafana-service 3000:3000
```

Accéder à: http://localhost:3000
- Username: `admin`
- Password: `admin` (à changer)

### 4.2 Configurer Prometheus comme source

1. Aller dans Configuration > Data Sources
2. Ajouter Prometheus
3. URL: `http://prometheus-service:9090`
4. Sauvegarder & Tester

### 4.3 Importer des dashboards

- Kubernetes Cluster Monitoring: Dashboard ID `7249`
- Node Exporter: Dashboard ID `1860`
- Custom HEYI metrics

---

## 🔍 ÉTAPE 5 : VÉRIFICATION & TESTS

### 5.1 Health checks

```bash
# API health
kubectl exec -n heyi deployment/heyi-api -- curl http://localhost:8000/health

# Logs
kubectl logs -n heyi deployment/heyi-api -f

# Métriques
kubectl exec -n heyi deployment/heyi-api -- curl http://localhost:8000/metrics
```

### 5.2 Test de charge

```bash
# Port-forward l'API
kubectl port-forward -n heyi svc/heyi-api-service 8000:80

# Tester
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### 5.3 Vérifier l'autoscaling

```bash
# Voir HPA
kubectl get hpa -n heyi

# Voir les métriques
kubectl top nodes
kubectl top pods -n heyi
```

---

## 🔄 MISE À JOUR DE L'APPLICATION

### Build & Push de l'image

```bash
# Build
docker build -t heyi/api:v1.0.1 .

# Tag
docker tag heyi/api:v1.0.1 YOUR_REGISTRY/heyi/api:v1.0.1

# Push
docker push YOUR_REGISTRY/heyi/api:v1.0.1
```

### Déploiement

```bash
# Mettre à jour l'image
kubectl set image deployment/heyi-api \
  heyi-api=YOUR_REGISTRY/heyi/api:v1.0.1 \
  -n heyi

# Vérifier le rollout
kubectl rollout status deployment/heyi-api -n heyi

# Rollback si nécessaire
kubectl rollout undo deployment/heyi-api -n heyi
```

---

## 🗑️ NETTOYAGE

### Supprimer Kubernetes

```bash
kubectl delete namespace heyi
kubectl delete -k overlays/production/
```

### Supprimer Terraform

```bash
cd infrastructure/terraform
terraform destroy -var-file="environments/production/terraform.tfvars"
```

---

## 📊 COÛTS ESTIMÉS (AWS)

### Développement (~300€/mois)
- EKS: ~70€
- RDS (t3.small): ~30€
- ElastiCache (t3.micro): ~15€
- EC2 (2x t3.medium): ~60€
- NAT Gateway: ~45€
- S3 + Data Transfer: ~80€

### Production (~1200€/mois)
- EKS: ~70€
- RDS (t3.large, Multi-AZ): ~200€
- ElastiCache (t3.medium, 3 nodes): ~150€
- EC2 (5x t3.large): ~400€
- NAT Gateway (3x): ~135€
- S3 + Data Transfer: ~245€

---

## 🆘 TROUBLESHOOTING

### Pods ne démarrent pas

```bash
kubectl describe pod POD_NAME -n heyi
kubectl logs POD_NAME -n heyi
```

### Problème de connexion DB

```bash
# Vérifier le security group
# Vérifier les secrets
kubectl get secret heyi-secrets -n heyi -o yaml
```

### HPA ne scale pas

```bash
# Vérifier metrics-server
kubectl get deployment metrics-server -n kube-system

# Installer si nécessaire
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## ✅ CHECKLIST PRODUCTION

- [ ] Secrets correctement configurés
- [ ] TLS/HTTPS activé
- [ ] Monitoring opérationnel
- [ ] Alertes configurées
- [ ] Backups RDS activés
- [ ] Multi-AZ activé
- [ ] Auto-scaling configuré
- [ ] Logs centralisés
- [ ] Documentation à jour
- [ ] Plan de disaster recovery testé

---

**Votre infrastructure HEYI est prête ! 🎉**
