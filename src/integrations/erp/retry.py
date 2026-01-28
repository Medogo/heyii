
# ========================================
# src/integrations/erp/retry.py
# ========================================
"""Stratégie de retry pour les appels ERP."""
import asyncio
from typing import Callable, Any
from functools import wraps


def retry_on_error(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Décorateur pour retry avec backoff exponentiel.

    Args:
        max_attempts: Nombre max de tentatives
        delay: Délai initial (secondes)
        backoff: Facteur de backoff
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    if attempt == max_attempts:
                        print(
                            f"❌ Échec définitif après {max_attempts} tentatives: {e}"
                        )
                        raise

                    print(
                        f"⚠️  Tentative {attempt}/{max_attempts} échouée: {e}. "
                        f"Retry dans {current_delay}s..."
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator


class RetryStrategy:
    """Stratégie de retry configurable."""

    def __init__(
            self,
            max_attempts: int = 3,
            initial_delay: float = 1.0,
            max_delay: float = 10.0,
            backoff_factor: float = 2.0,
    ):
        """
        Initialiser la stratégie.

        Args:
            max_attempts: Nombre max de tentatives
            initial_delay: Délai initial
            max_delay: Délai maximum
            backoff_factor: Facteur de backoff
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécuter avec retry.

        Args:
            func: Fonction async à exécuter
            *args, **kwargs: Arguments

        Returns:
            Résultat de la fonction
        """
        current_delay = self.initial_delay

        for attempt in range(1, self.max_attempts + 1):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                if attempt == self.max_attempts:
                    raise

                print(
                    f"⚠️  Tentative {attempt}/{self.max_attempts} échouée. "
                    f"Retry dans {current_delay}s..."
                )

                await asyncio.sleep(current_delay)

                # Calculer le prochain délai
                current_delay = min(current_delay * self.backoff_factor, self.max_delay)
