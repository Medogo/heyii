"""Routes API."""
# Import direct des modules pour éviter les imports circulaires
import src.api.routes.health as health
import src.api.routes.calls as calls
import src.api.routes.orders as orders
import src.api.routes.products as products
import src.api.routes.websocket as websocket

__all__ = ["health", "calls", "orders", "products", "websocket"]
