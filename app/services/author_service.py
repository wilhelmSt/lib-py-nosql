from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.author import Author, AuthorResponse, UpdateAuthorSchema
from ..configuration.database import db

collection = db.authors

async def get_all_authors(
    page: int = 1,
    limit: int = 10,
    name: Optional[str] = None,
    written_book: Optional[str] = None,
    nationality: Optional[str] = None
) -> List[AuthorResponse]:
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="Page and limit must be greater than zero")

        skip = (page - 1) * limit
        query = {}
        
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        
        if nationality:
            query["nationality"] = {"$regex": nationality, "$options": "i"}
            
        if written_book and ObjectId.is_valid(written_book):
            query["written_books"] = {"$in": [ObjectId(written_book)]}
        
        authors = await collection.find(query).skip(skip).limit(limit).to_list(length=limit)

        return [
            AuthorResponse(id=str(author["_id"]), **{k: v for k, v in author.items() if k != "_id"})
            for author in authors
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_author_by_id(author_id: str) -> Optional[AuthorResponse]:
    try:
        if not ObjectId.is_valid(author_id):
            raise ValueError("Invalid ObjectId format")

        author = await collection.find_one({"_id": ObjectId(author_id)})
        if author:
            return AuthorResponse(id=str(author["_id"]), **{k: v for k, v in author.items() if k != "_id"})

        return JSONResponse(status_code=204, content=None)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid author ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def create_author(author: Author) -> Optional[AuthorResponse]:
    try:
        new_author = author.dict()
        
        if new_author.get("written_books"):
            new_author["written_books"] = [
                ObjectId(book_id) for book_id in new_author["written_books"] if ObjectId.is_valid(book_id)
            ]
            
        result = await collection.insert_one(new_author)

        return AuthorResponse(id=str(result.inserted_id), **new_author)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating author: {str(e)}")


async def update_author(author_id: str, author: UpdateAuthorSchema) -> Optional[AuthorResponse]:
    try:
        if not ObjectId.is_valid(author_id):
            raise ValueError("Invalid ObjectId format")

        updated_author = author.dict(exclude_unset=True)

        result = await collection.update_one({"_id": ObjectId(author_id)}, {"$set": updated_author})

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Author not found or no update performed")

        return await get_author_by_id(author_id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid author ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating author: {str(e)}")


async def delete_author(author_id: str) -> dict:
    try:
        if not ObjectId.is_valid(author_id):
            raise ValueError("Invalid ObjectId format")

        result = await collection.delete_one({"_id": ObjectId(author_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Author not found")

        return {"message": "Author deleted successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid author ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting author: {str(e)}")


async def add_written_book(author_id: str, book_id: str) -> Optional[AuthorResponse]:
    try:
        if not ObjectId.is_valid(author_id) or not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")

        author = await collection.find_one({"_id": ObjectId(author_id)})

        if not author:
            raise HTTPException(status_code=404, detail="Author not found")

        result = await collection.update_one(
            {"_id": ObjectId(author_id)},
            {"$addToSet": {"written_books": ObjectId(book_id)}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Book already exists in written_books")

        updated_author = await collection.find_one({"_id": ObjectId(author_id)})

        return AuthorResponse(id=str(updated_author["_id"]), **{k: v for k, v in updated_author.items() if k != "_id"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating author: {str(e)}")