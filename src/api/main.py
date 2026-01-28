"""Point d'entrée principal de l'API FastAPI."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.utils.cache import cache
from src.api.routes import health, calls, orders, products, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    # Startup
    print("🚀 Démarrage de l'application...")
    await cache.connect()
    print("✅ Redis connecté")

    yield

    # Shutdown
    print("🛑 Arrêt de l'application...")
    await cache.disconnect()
    print("✅ Redis déconnecté")


app = FastAPI(
    title=settings.app_name,
    description="Agent IA de Prise de Commande Pharmaceutique H24",
    version="1.0.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(calls.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Endpoint racine."""
    return {
        "message": "HEYI API - Agent IA Pharmaceutique",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )