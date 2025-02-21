from typing import List, Optional
from bson import ObjectId
from datetime import date
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.book import Book, BookResponse, UpdateBookSchema, BookAuthorResponse, BAuthorResponse
from ..configuration.database import db

collection = db.books

async def get_all_books(
    page: int = 1,
    limit: int = 10,
    title: Optional[str] = None,
    author: Optional[str] = None,
    library: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[BookResponse]:
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="Page and limit must be greater than zero")

        skip = (page - 1) * limit
        query = {}
        
        if title:
            query["title"] = {"$regex": title, "$options": "i"}
            
        if author and ObjectId.is_valid(author):
            query["author"] = ObjectId(author)
            
        if library and ObjectId.is_valid(library):
            query["libraries"] = {"$in": [ObjectId(library)]}
        
        if start_date:
            query["published_date"] = {"$gte": start_date}
            
        if end_date:
            if "published_date" not in query:
                query["published_date"] = {}
            query["published_date"]["$lte"] = end_date
            
        books = await collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        
        return [
            BookResponse(id=str(book["_id"]), **{k: v for k, v in book.items() if k != "_id"})
            for book in books
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_book_by_id(book_id: str) -> Optional[BookResponse]:
    try:
        if not ObjectId.is_valid(book_id):
            raise ValueError("Invalid ObjectId format")

        book = await collection.find_one({"_id": ObjectId(book_id)})
        if book:
            return BookResponse(id=str(book["_id"]), **{k: v for k, v in book.items() if k != "_id"})

        return JSONResponse(status_code=204, content=None)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
            
    
async def create_book(book: Book) -> Optional[BookResponse]:
    try:
        new_book = book.dict()
        
        author_id = new_book.get("author")
        if author_id and ObjectId.is_valid(author_id):
            new_book["author"] = ObjectId(author_id)
            
        category_id = new_book.get("category")
        if category_id and ObjectId.is_valid(category_id):
            new_book["category"] = ObjectId(category_id)
            
        library_ids = new_book.get("libraries", [])
        new_book["libraries"] = [
            ObjectId(lib_id) for lib_id in library_ids if ObjectId.is_valid(lib_id)
        ]
        
        result = await collection.insert_one(new_book)
        book_id = result.inserted_id
        
        if author_id and ObjectId.is_valid(author_id):
            await db.authors.update_one(
                {"_id": ObjectId(author_id)},
                {"$addToSet": {"written_books": book_id}}
            )
            
        if library_ids:
            await db.libraries.update_many(
                {"_id": {"$in": new_book["libraries"]}},
                {"$addToSet": {"books": book_id}}
            )
        
        return BookResponse(id=str(book_id), **new_book)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating book: {str(e)}")


async def update_book(book_id: str, book: UpdateBookSchema) -> Optional[BookResponse]:
    try:
        if not ObjectId.is_valid(book_id):
            raise ValueError("Invalid ObjectId format")
        
        updated_book = book.dict(exclude_unset=True)
        
        result = await collection.update_one({"_id": ObjectId(book_id)}, {"$set": updated_book})
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Book not found or no update performed")
        
        return await get_book_by_id(book_id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating book: {str(e)}")


async def delete_book(book_id: str) -> dict:
    try:
        if not ObjectId.is_valid(book_id):
            raise ValueError("Invalid ObjectId format")

        result = await collection.delete_one({"_id": ObjectId(book_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Book not found")

        return {"message": "Book deleted successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid book ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating book: {str(e)}")


async def add_libraries_to_book(book_id: str, library_ids: List[str]) -> dict:
    try:
        if not ObjectId.is_valid(book_id):
            raise ValueError("Invalid ObjectId format")
        
        valid_library_ids = [ObjectId(lib_id) for lib_id in library_ids if ObjectId.is_valid(lib_id)]
        
        if not valid_library_ids:
            raise ValueError("No valid ObjectId in library_ids")
        
        result = await collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$addToSet": {"library": {"$each": valid_library_ids}}},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Book not found or no update was performed")

        return {"message": "Libraries added successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating book: {str(e)}")
    

async def list_books_with_authors(page: int = 1, limit: int = 10) -> List[BookAuthorResponse]:
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="Page and limit must be greater than zero")

        skip = (page - 1) * limit

        books_with_authors = await collection.aggregate([
            {
                "$lookup": {
                    "from": "authors",
                    "localField": "author",
                    "foreignField": "_id",
                    "as": "author_details"
                }
            },
            {
                "$unwind": {
                    "path": "$author_details",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$skip": skip
            },
            {
                "$limit": limit
            }
        ]).to_list(length=limit)

        return [
            BookAuthorResponse(
                id=str(book["_id"]),
                title=book.get("title"),
                author=BAuthorResponse(
                    id=str(book.get("author_details", {}).get("_id")),
                    name=str(book.get("author_details").get("name")),
                    nationality=str(book.get("author_details").get("nationality"))
                ) if book.get("author_details") else None,
                published_date=book.get("published_date"),
                isbn=book.get("isbn"),
                libraries=book.get("libraries", [])
            )
            for book in books_with_authors
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
