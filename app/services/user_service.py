from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.user import (
    User,
    UserResponse,
    UpdateUserSchema,
    PopulateBooksUserSchema,
    UserResponseAggregate,
    UBookAResponse,
    ULibraryAResponse
)
from ..configuration.database import db

collection = db.users

async def get_all_users(
    page: int,
    limit: int,
    name: Optional[str] = None,
    fav_library: Optional[str] = None,
    fav_category: Optional[str] = None,
    fav_author: Optional[str] = None,
    readed_book: Optional[str] = None,
    rental_book: Optional[str] = None
) -> List[UserResponse]:
    try:
        query = {}

        if name:
            query["name"] = {"$regex": name, "$options": "i"}

        if fav_library and ObjectId.is_valid(fav_library):
            query["fav_library"] = ObjectId(fav_library)

        if fav_category and ObjectId.is_valid(fav_category):
            query["fav_category"] = ObjectId(fav_category)

        if fav_author and ObjectId.is_valid(fav_author):
            query["fav_author"] = ObjectId(fav_author)

        if readed_book and ObjectId.is_valid(readed_book):
            query["readed_books"] = {"$in": [ObjectId(readed_book)]}

        if rental_book and ObjectId.is_valid(rental_book):
            query["rental_books"] = {"$in": [ObjectId(rental_book)]}

        users = await collection.find(query).skip((page - 1) * limit).limit(limit).to_list(limit)

        return [
            UserResponse(id=str(user["_id"]), **{k: v for k, v in user.items() if k != "_id"})
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    try:
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid ObjectId format")

        user = await collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserResponse(id=str(user["_id"]), **{k: v for k, v in user.items() if k != "_id"})

        return JSONResponse(status_code=204, content=None)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def create_user(user: User) -> Optional[UserResponse]:
    try:
        new_user = user.dict()

        result = await collection.insert_one(new_user)

        return UserResponse(id=str(result.inserted_id), **new_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


async def update_user(user_id: str, user: UpdateUserSchema) -> Optional[UserResponse]:
    try:
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid ObjectId format")

        updated_user = user.dict(exclude_unset=True)

        result = await collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_user})

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or no update performed")

        return await get_user_by_id(user_id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


async def delete_user(user_id: str) -> dict:
    try:
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid ObjectId format")

        result = await collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


async def get_users_with_rental_books_and_libraries(page: int = 1, limit: int = 10) -> List[UserResponseAggregate]:
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="Page and limit must be greater than zero")

        skip = (page - 1) * limit

        users_with_books_and_libraries = await collection.aggregate([
            {
                "$match": {  
                    "rental_books": {"$exists": True, "$not": {"$size": 0}}  
                }
            },
            {
                "$addFields": {
                    "rental_books": {
                        "$map": {
                            "input": { "$ifNull": ["$rental_books", []] },
                            "as": "book_id",
                            "in": {
                                "$cond": {
                                    "if": { "$eq": [{ "$type": "$$book_id" }, "string"] },  
                                    "then": { "$toObjectId": "$$book_id" },
                                    "else": "$$book_id" 
                                }
                            }
                        }
                    }
                }
            },
            {
                "$lookup": {
                    "from": "books", 
                    "localField": "rental_books",
                    "foreignField": "_id",
                    "as": "rented_books"
                }
            },
            {
                "$lookup": {
                    "from": "libraries",
                    "localField": "rented_books.libraries", 
                    "foreignField": "_id",
                    "as": "book_libraries"
                }
            },
            {
                "$skip": skip
            },
            {
                "$limit": limit
            }
        ]).to_list(length=limit)

        if not users_with_books_and_libraries:
            raise HTTPException(status_code=404, detail="No users found")

        return [
            UserResponseAggregate(
                id=str(user["_id"]),
                name=user.get("name", "Sem Nome"),
                readed_books=[str(book) for book in user.get("readed_books", [])],
                rental_books=[UBookAResponse(
                    id=str(book["_id"]),
                    title=book.get("title", "Título Desconhecido"),
                    libraries=[ULibraryAResponse(
                        id=str(library["_id"]),
                        name=library.get("name", "Biblioteca Desconhecida")
                    ) for library in user.get("book_libraries", [])]
                ) for book in user.get("rented_books", [])]
            )
            for user in users_with_books_and_libraries
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def populate_books(user_id: str, user: PopulateBooksUserSchema) -> dict:
    readed_books = user.readed_books or []
    rental_books = user.rental_books or []
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    valid_readed_books = [
        ObjectId(book_id) for book_id in readed_books if ObjectId.is_valid(book_id)
    ]

    valid_rental_books = [
        ObjectId(book_id) for book_id in rental_books if ObjectId.is_valid(book_id)
    ]

    if not valid_readed_books and not valid_rental_books:
        raise HTTPException(status_code=400, detail="Nenhum ID de livro válido fornecido")

    update_query = {"$addToSet": {}}

    if valid_readed_books:
        update_query["$addToSet"]["readed_books"] = {"$each": valid_readed_books}

    if valid_rental_books:
        update_query["$addToSet"]["rental_books"] = {"$each": valid_rental_books}

    result = await collection.update_one({"_id": ObjectId(user_id)}, update_query)

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou livros já adicionados")

    return {"message": "Livros adicionados com sucesso"}