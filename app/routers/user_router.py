from fastapi import APIRouter
from typing import List
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
async def get_users():
    return await get_all_users()


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
