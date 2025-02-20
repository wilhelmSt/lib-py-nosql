from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.library import Library, LibraryResponse, UpdateLibrarySchema
from ..configuration.database import db

collection = db.libraries

async def get_all_libraries(
    page: int,
    limit: int,
    name: Optional[str] = None,
    is_public: Optional[bool] = None,
    location: Optional[str] = None,
    establish_year: Optional[int] = None,
    book_id: Optional[str] = None
) -> List[LibraryResponse]:
    try:
        query = {}

        if name:
            query["name"] = {"$regex": name, "$options": "i"}

        if is_public is not None:
            query["is_public"] = is_public

        if location:
            query["location"] = {"$regex": location, "$options": "i"}

        if establish_year is not None:
            query["establish_year"] = establish_year

        if book_id and ObjectId.is_valid(book_id):
            query["books"] = {"$in": [ObjectId(book_id)]}

        libraries = await collection.find(query).skip((page - 1) * limit).limit(limit).to_list(limit)

        return [
            LibraryResponse(id=str(library["_id"]), **{k: v for k, v in library.items() if k != "_id"})
            for library in libraries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_library_by_id(library_id: str) -> Optional[LibraryResponse]:
    try:
        if not ObjectId.is_valid(library_id):
            raise ValueError("Invalid ObjectId format")

        library = await collection.find_one({"_id": ObjectId(library_id)})
        if library:
            return LibraryResponse(id=str(library["_id"]), **{k: v for k, v in library.items() if k != "_id"})

        return JSONResponse(status_code=204, content=None)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid library ID format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
            
    
async def create_library(library: Library) -> Optional[LibraryResponse]:
    try:
        new_library = library.dict()
        
        if new_library.get("books"):
            new_library["books"] = [
                ObjectId(book_id) for book_id in new_library["books"] if ObjectId.is_valid(book_id)
            ]
        
        result = await collection.insert_one(new_library)
        
        return LibraryResponse(id=str(result.inserted_id), **new_library)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating library: {str(e)}")


async def update_library(library_id: str, library: UpdateLibrarySchema) -> Optional[LibraryResponse]:
    try:
        if not ObjectId.is_valid(library_id):
            raise ValueError("Invalid ObjectId format")
        
        updated_library = library.dict(exclude_unset=True)
        
        result = await collection.update_one({"_id": ObjectId(library_id)}, {"$set": updated_library})
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Library not found or no update performed")
        
        return await get_library_by_id(library_id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid library ID format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating library: {str(e)}")


async def delete_library(library_id: str) -> dict:
    try:
        if not ObjectId.is_valid(library_id):
            raise ValueError("Invalid ObjectId format")

        result = await collection.delete_one({"_id": ObjectId(library_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Library not found")

        return {"message": "Library deleted successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid library ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating library: {str(e)}")


async def add_book_to_library(library_id: str, books_ids: List[str]) -> dict:
    try:
        if not ObjectId.is_valid(library_id):
            raise ValueError("Invalid ObjectId format")
        
        valid_book_ids = [ObjectId(book_id) for book_id in books_ids if ObjectId.is_valid(book_id)]
        
        if not valid_book_ids:
            raise ValueError("No valid ObjectId in books_ids")
        
        result = await collection.update_one(
            {"_id": ObjectId(library_id)},
            {"$addToSet": {"books": {"$each": valid_book_ids}}},
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Library not found or no update was performed")

        return {"message": "Books added successfully"}
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating library: {str(e)}")