
# ========================================
# src/utils/metrics.py
# ========================================
"""Métriques Prometheus."""
from prometheus_client import Counter, Histogram, Gauge

# Compteurs
calls_total = Counter("heyi_calls_total", "Nombre total d'appels", ["status"])

orders_total = Counter("heyi_orders_total", "Nombre total de commandes", ["status"])

errors_total = Counter("heyi_errors_total", "Nombre total d'erreurs", ["type"])

# Histogrammes (latence)
call_duration = Histogram(
    "heyi_call_duration_seconds", "Durée des appels en secondes"
)

api_latency = Histogram(
    "heyi_api_latency_seconds", "Latence des requêtes API", ["endpoint", "method"]
)

stt_latency = Histogram("heyi_stt_latency_seconds", "Latence du STT")

llm_latency = Histogram("heyi_llm_latency_seconds", "Latence du LLM")

tts_latency = Histogram("heyi_tts_latency_seconds", "Latence du TTS")

# Gauges (valeurs actuelles)
active_calls = Gauge("heyi_active_calls", "Nombre d'appels actifs")

active_sessions = Gauge("heyi_active_sessions", "Nombre de sessions actives")


def record_call_completed(duration: float, status: str):
    """Enregistrer un appel terminé."""
    calls_total.labels(status=status).inc()
    call_duration.observe(duration)


def record_order_created(status: str):
    """Enregistrer une commande créée."""
    orders_total.labels(status=status).inc()


def record_error(error_type: str):
    """Enregistrer une erreur."""
    errors_total.labels(type=error_type).inc()