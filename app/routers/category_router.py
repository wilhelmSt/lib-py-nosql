from fastapi import APIRouter
from typing import List
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
async def get_categories():
    return await get_all_categories()


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
