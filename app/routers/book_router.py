from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.book import Book, BookResponse, UpdateBookSchema
from app.services.book_service import (
    get_all_books,
    get_book_by_id,
    create_book,
    update_book,
    delete_book
)

router = APIRouter()

@router.get("/", response_model=List[BookResponse])
async def get_books(
    page: int = Query(1, description="Page number, starting from 1", ge=1),
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    title: Optional[str] = Query(None, description="Filter by book title"),
    author: Optional[str] = Query(None, description="Filter by author ID"),
    library: Optional[str] = Query(None, description="Filter by library ID")
):
    return await get_all_books(
        page=page,
        limit=limit,
        title=title,
        author=author,
        library=library
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    return await get_book_by_id(book_id)
    

@router.post("/", response_model=BookResponse)
async def add_book(book: Book):
    return await create_book(book)


@router.put("/{book_id}", response_model=BookResponse)
async def edit_book(book_id: str, book: UpdateBookSchema):
    return await update_book(book_id, book)


@router.delete("/{book_id}")
async def remove_book(book_id: str):
    return await delete_book(book_id)
