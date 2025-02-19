from fastapi import APIRouter
from typing import List
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
async def get_libraries():
    return await get_all_libraries()


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
