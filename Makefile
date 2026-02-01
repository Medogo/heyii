.PHONY: help install dev test lint format clean docker-up docker-down

help:
	@echo "Commandes disponibles:"
	@echo "  make install     - Installer les dépendances"
	@echo "  make dev         - Lancer en mode développement"
	@echo "  make test        - Lancer les tests"
	@echo "  make lint        - Vérifier le code"
	@echo "  make format      - Formater le code"
	@echo "  make clean       - Nettoyer les fichiers temporaires"
	@echo "  make docker-up   - Démarrer les services Docker"
	@echo "  make docker-down - Arrêter les services Docker"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	black --check src tests
	isort --check-only src tests
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
