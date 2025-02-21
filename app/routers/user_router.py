from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.user import User, UserResponse, UpdateUserSchema
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    page: int = Query(1, description="Page number, starting from 1", ge=1),
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    name: Optional[str] = Query(None, description="Filter by user name"),
    fav_library: Optional[str] = Query(None, description="Filter by favorite library"),
    fav_category: Optional[str] = Query(None, description="Filter by favorite category"),
    fav_author: Optional[str] = Query(None, description="Filter by favorite author"),
    readed_book: Optional[str] = Query(None, description="Filter by readed book"),
    rental_book: Optional[str] = Query(None, description="Filter by rented book")
):
    return await get_all_users(
        page=page,
        limit=limit,
        name=name,
        fav_library=fav_library,
        fav_category=fav_category,
        fav_author=fav_author,
        readed_book=readed_book,
        rental_book=rental_book
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    return await get_user_by_id(user_id)


@router.post("/", response_model=UserResponse)
async def add_user(user: User):
    return await create_user(user)


@router.put("/{user_id}", response_model=UserResponse)
async def edit_user(user_id: str, user: UpdateUserSchema):
    return await update_user(user_id, user)


@router.delete("/{user_id}")
async def remove_user(user_id: str):
    return await delete_user(user_id)
