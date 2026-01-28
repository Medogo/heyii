"""Routes pour la gestion des produits."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_db
from src.data.repositories.product_repository import ProductRepository
from src.api.schemas.product import (
    ProductResponse,
    ProductCreate,
    ProductSearch,
    StockCheckRequest,
    StockCheckResponse
)
from src.services.vector_db.qcadrant_client import qdrant_client
from src.business.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """Lister tous les produits."""
    repo = ProductRepository(db)
    products = await repo.get_all(skip=skip, limit=limit)
    return products


@router.get("/search", response_model=List[ProductSearch])
async def search_products(
        q: str = Query(..., min_length=2, description="Search query"),
        limit: int = Query(10, le=50),
        use_semantic: bool = Query(True, description="Use semantic search"),
        db: AsyncSession = Depends(get_db)
):
    """Rechercher des produits."""

    if use_semantic:
        # Recherche sémantique avec Qdrant
        results = await qdrant_client.search_product(q, limit=limit)
        return results
    else:
        # Recherche classique en base
        repo = ProductRepository(db)
        products = await repo.search(q, limit=limit)

        return [
            ProductSearch(
                product=p,
                score=1.0,
                match_type="database"
            )
            for p in products
        ]


@router.get("/{cip13}", response_model=ProductResponse)
async def get_product(
        cip13: str,
        db: AsyncSession = Depends(get_db)
):
    """Récupérer un produit par CIP."""
    repo = ProductRepository(db)
    product = await repo.get_by_cip(cip13)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("/", response_model=ProductResponse)
async def create_product(
        product_data: ProductCreate,
        db: AsyncSession = Depends(get_db)
):
    """Créer un nouveau produit."""
    from src.data.models import Product

    repo = ProductRepository(db)

    # Vérifier si existe déjà
    existing = await repo.get_by_cip(product_data.cip13)
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")

    product = Product(**product_data.model_dump())
    created = await repo.create(product)

    # Indexer dans Qdrant
    await qdrant_client.index_product(created)

    return created


@router.post("/check-stock", response_model=StockCheckResponse)
async def check_stock(
        request: StockCheckRequest,
        db: AsyncSession = Depends(get_db)
):
    """Vérifier la disponibilité d'un produit."""
    product_service = ProductService(db)

    is_available = await product_service.check_stock(
        request.cip13,
        request.quantity
    )

    repo = ProductRepository(db)
    product = await repo.get_by_cip(request.cip13)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return StockCheckResponse(
        cip13=request.cip13,
        requested=request.quantity,
        available=product.stock_available,
        is_available=is_available
    )