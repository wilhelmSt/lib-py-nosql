from fastapi import APIRouter, Query
from typing import List, Optional
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
async def get_authors(
    page: int = Query(1, description="Page number, starting from 1", ge=1),
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    name: Optional[str] = Query(None, description="Filter by author name"),
    written_book: Optional[str] = Query(None, description="Filter by author written books"),
    nationality: Optional[str] = Query(None, description="Filter by nationality")
):
    return await get_all_authors(
        page=page,
        limit=limit,
        name=name,
        written_book=written_book,
        nationality=nationality
    )


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


@router.patch("/{author_id}/add_book/{book_id}", response_model=AuthorResponse)
async def add_written_book(author_id: str, book_id: str):
    return await add_written_book(author_id, book_id)