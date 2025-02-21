from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.user import User, UserResponse, UpdateUserSchema
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


async def get_users_with_rental_books_and_libraries(page: int = 1, limit: int = 10) -> List[UserResponse]:
    try:
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="Page and limit must be greater than zero")

        skip = (page - 1) * limit

        users_with_books_and_libraries = await collection.aggregate([
            {
                "$lookup": {
                    "from": "books", 
                    "localField": "rental_books",
                    "foreignField": "_id",
                    "as": "rented_books"
                }
            },
            {
                "$unwind": {
                    "path": "$rented_books",
                    "preserveNullAndEmptyArrays": True
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
                "$unwind": {
                    "path": "$book_libraries",
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
            UserResponse(
                id=str(user["_id"]),
                name=user["name"],
                rented_books=[{
                    "book_title": user["rented_books"]["title"],
                    "library_name": user["book_libraries"]["name"]
                }]
            )
            for user in users_with_books_and_libraries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
