from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategorySchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    status: bool = True
    popularity_score: float = 0.0
    parent_category: Optional[str] = None


class CategoryResponse(BaseModel):
    id: str
    name: Optional[str] = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    status: Optional[bool] = True
    popularity_score: Optional[float] = 0.0
    parent_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UpdateCategorySchema(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    status: Optional[bool] = True
    popularity_score: Optional[float] = 0.0
    parent_category: Optional[str] = None

