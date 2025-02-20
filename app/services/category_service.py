from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..models.category import Category, CategoryResponse, UpdateCategorySchema
from ..configuration.database import db
from datetime import datetime

collection = db.categories

async def get_all_categories(
    page: int,
    limit: int,
    name: Optional[str] = None,
    status: Optional[bool] = None,
    min_popularity: Optional[float] = None,
    parent_category: Optional[str] = None
) -> List[CategoryResponse]:
    try:
        query = {}

        if name:
            query["name"] = {"$regex": name, "$options": "i"}

        if status is not None:
            query["status"] = status

        if min_popularity is not None:
            query["popularity_score"] = {"$gte": min_popularity}

        if parent_category and ObjectId.is_valid(parent_category):
            query["parent_category"] = ObjectId(parent_category)

        categories = await collection.find(query).skip((page - 1) * limit).limit(limit).to_list(limit)

        return [
            CategoryResponse(id=str(cat["_id"]), **{k: v for k, v in cat.items() if k != "_id"})
            for cat in categories
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_category_by_id(category_id: str) -> Optional[CategoryResponse]:
    try:
        if not ObjectId.is_valid(category_id):
            raise ValueError("Invalid ObjectId format")

        category = await collection.find_one({"_id": ObjectId(category_id)})
        if category:
            return CategoryResponse(id=str(category["_id"]), **{k: v for k, v in category.items() if k != "_id"})

        return JSONResponse(status_code=204, content=None)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def create_category(category: Category) -> Optional[CategoryResponse]:
    try:
        new_category = category.dict()
        new_category["created_at"] = new_category["updated_at"] = datetime.utcnow()
        
        if not ObjectId.is_valid(new_category["parent_category"]):
            del new_category["parent_category"]
        
        result = await collection.insert_one(new_category)
    
        return CategoryResponse(id=str(result.inserted_id), **new_category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating category: {str(e)}")


async def update_category(category_id: str, category: UpdateCategorySchema) -> Optional[CategoryResponse]:
    try:
        if not ObjectId.is_valid(category_id):
            raise ValueError("Invalid ObjectId format")
        
        updated_category = category.dict(exclude_unset=True)
        updated_category["updated_at"] = datetime.utcnow()
        
        if not ObjectId.is_valid(updated_category["parent_category"]):
            del updated_category["parent_category"]
        
        result = await collection.update_one({"_id": ObjectId(category_id)}, {"$set": updated_category})
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Category not found or no update performed")
        
        return await get_category_by_id(category_id)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")


async def delete_category(category_id: str) -> dict:
    try:
        if not ObjectId.is_valid(category_id):
            raise ValueError("Invalid ObjectId format")

        result = await collection.delete_one({"_id": ObjectId(category_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")

        return {"message": "Category deleted successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")

