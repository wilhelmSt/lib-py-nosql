from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..schemas.category import CategorySchema, CategoryResponse, UpdateCategorySchema
from ..configuration.database import db
from datetime import datetime

collection = db.categories

async def get_all_categories() -> List[CategoryResponse]:
    try:    
        categories = await collection.find().to_list(100)
        
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


async def create_category(category: CategorySchema) -> Optional[CategoryResponse]:
    try:
        new_category = category.dict()
        new_category["created_at"] = new_category["updated_at"] = datetime.utcnow()
        
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

