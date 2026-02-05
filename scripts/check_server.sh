#!/bin/bash
# Script de diagnostic pour vérifier l'accessibilité du serveur

echo "🔍 Diagnostic du serveur HEYI"
echo "================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Vérifier Docker
echo "1. Vérification Docker..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker installé${NC}"
    docker --version
else
    echo -e "${RED}❌ Docker non installé${NC}"
fi
echo ""

# 2. Vérifier les conteneurs
echo "2. Vérification des conteneurs..."
if docker ps | grep -q heyi-app; then
    echo -e "${GREEN}✅ Conteneur heyi-app en cours d'exécution${NC}"
    docker ps | grep heyi-app
else
    echo -e "${RED}❌ Conteneur heyi-app non trouvé${NC}"
    echo "Conteneurs actifs:"
    docker ps
fi
echo ""

# 3. Vérifier les ports
echo "3. Vérification des ports..."
if netstat -tuln 2>/dev/null | grep -q ":8000" || ss -tuln 2>/dev/null | grep -q ":8000"; then
    echo -e "${GREEN}✅ Port 8000 en écoute${NC}"
    netstat -tuln 2>/dev/null | grep ":8000" || ss -tuln 2>/dev/null | grep ":8000"
else
    echo -e "${RED}❌ Port 8000 non en écoute${NC}"
fi
echo ""

# 4. Vérifier le firewall UFW
echo "4. Vérification du firewall UFW..."
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status | head -n 1)
    echo "Statut UFW: $UFW_STATUS"
    if ufw status | grep -q "8000/tcp"; then
        echo -e "${GREEN}✅ Port 8000 autorisé dans UFW${NC}"
    else
        echo -e "${YELLOW}⚠️  Port 8000 non explicitement autorisé dans UFW${NC}"
        echo "Pour autoriser: sudo ufw allow 8000/tcp"
    fi
else
    echo -e "${YELLOW}⚠️  UFW non installé${NC}"
fi
echo ""

# 5. Tester localhost
echo "5. Test de l'application sur localhost..."
if curl -s -f http://localhost:8000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Application accessible sur localhost:8000${NC}"
    curl -s http://localhost:8000/health/ | head -n 5
else
    echo -e "${RED}❌ Application non accessible sur localhost:8000${NC}"
    echo "Vérifiez les logs: docker logs heyi-app"
fi
echo ""

# 6. Vérifier l'IP publique
echo "6. Vérification de l'IP publique..."
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com)
echo "IP publique détectée: $PUBLIC_IP"
echo ""

# 7. Vérifier les logs récents
echo "7. Derniers logs de l'application..."
if docker ps | grep -q heyi-app; then
    echo "---"
    docker logs --tail 20 heyi-app
    echo "---"
else
    echo -e "${RED}❌ Impossible de récupérer les logs (conteneur non trouvé)${NC}"
fi
echo ""

# 8. Résumé
echo "================================"
echo "📋 Résumé"
echo "================================"
echo ""
echo "Pour tester depuis l'extérieur:"
echo "  curl http://$PUBLIC_IP:8000/health/"
echo "  curl http://$PUBLIC_IP:8000/docs"
echo ""
echo "Si les tests échouent, vérifiez:"
echo "  1. Firewall Digital Ocean (Networking → Firewalls)"
echo "  2. Firewall UFW: sudo ufw allow 8000/tcp"
echo "  3. Logs: docker logs heyi-app"
echo "  4. Status: docker compose ps"
echo ""
