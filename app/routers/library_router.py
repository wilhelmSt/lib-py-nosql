from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.library import Library, LibraryResponse, UpdateLibrarySchema
from app.services.library_service import (
    get_all_libraries,
    get_library_by_id,
    create_library,
    update_library,
    delete_library
)

router = APIRouter()

@router.get("/", response_model=List[LibraryResponse])
async def get_libraries(
    page: int = Query(1, description="Page number, starting from 1", ge=1),
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    name: Optional[str] = Query(None, description="Filter by library name"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private library"),
    location: Optional[str] = Query(None, description="Filter by location"),
    establish_year: Optional[int] = Query(None, description="Filter by establishment year"),
    book_id: Optional[str] = Query(None, description="Filter by book ID inside library")
):
    return await get_all_libraries(
        page=page,
        limit=limit,
        name=name,
        is_public=is_public,
        location=location,
        establish_year=establish_year,
        book_id=book_id
    )


@router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(library_id: str):
    return await get_library_by_id(library_id)


@router.post("/", response_model=LibraryResponse)
async def add_library(library: Library):
    return await create_library(library)


@router.put("/{library_id}", response_model=LibraryResponse)
async def edit_library(library_id: str, library: UpdateLibrarySchema):
    return await update_library(library_id, library)


@router.delete("/{library_id}")
async def remove_library(library_id: str):
    return await delete_library(library_id)
