from fastapi import APIRouter
from typing import List
from app.models.author import Author, AuthorResponse, UpdateAuthorSchema
from app.services.author_service import (
    get_all_authors,
    get_author_by_id,
    create_author,
    update_author,
    delete_author
)

router = APIRouter()

@router.get("/", response_model=List[AuthorResponse])
async def get_authors():
    return await get_all_authors()


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: str):
    return await get_author_by_id(author_id)


@router.post("/", response_model=AuthorResponse)
async def add_author(author: Author):
    return await create_author(author)


@router.put("/{author_id}", response_model=AuthorResponse)
async def edit_author(author_id: str, author: UpdateAuthorSchema):
    return await update_author(author_id, author)


@router.delete("/{author_id}")
async def remove_author(author_id: str):
    return await delete_author(author_id)
