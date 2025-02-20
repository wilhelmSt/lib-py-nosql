from fastapi import APIRouter, Query
from typing import List, Optional
from ..models.category import Category, CategoryResponse, UpdateCategorySchema
from ..services.category_service import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
)

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    page: int = Query(1, description="Page number, starting from 1", ge=1),
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    name: Optional[str] = Query(None, description="Filter by category name"),
    status: Optional[bool] = Query(None, description="Filter by status"),
    min_popularity: Optional[float] = Query(None, description="Minimum popularity score"),
    parent_category: Optional[str] = Query(None, description="Filter by parent category")
):
    return await get_all_categories(
        page=page,
        limit=limit,
        name=name,
        status=status,
        min_popularity=min_popularity,
        parent_category=parent_category
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    return await get_category_by_id(category_id)


@router.post("/", response_model=CategoryResponse)
async def add_category(category: Category):
    return await create_category(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def edit_category(category_id: str, category: UpdateCategorySchema):
    return await update_category(category_id, category)


@router.delete("/{category_id}")
async def remove_category(category_id: str):
    return await delete_category(category_id)
