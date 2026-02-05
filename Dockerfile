FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout=1000 --retries=10 -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; print('📥 Téléchargement modèle...'); model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2'); print('✅ Modèle téléchargé et en cache')"

COPY src/ ./src/
COPY alembic.ini ./
COPY pyproject.toml ./

RUN mkdir -p /app/logs /app/recordings

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
