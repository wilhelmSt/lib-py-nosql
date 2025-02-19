from fastapi import APIRouter
from typing import List
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
async def get_books():
    return await get_all_books()


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
