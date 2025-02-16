from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Category(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    status: bool = True
    popularity_score: float = 0.0
    parent_category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
