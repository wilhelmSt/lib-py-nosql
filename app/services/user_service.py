from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.user import User, UserResponse, UpdateUserSchema
from ..configuration.database import db

collection = db.users

async def get_all_users() -> List[UserResponse]:
    try:
        users = await collection.find().to_list(100)

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
