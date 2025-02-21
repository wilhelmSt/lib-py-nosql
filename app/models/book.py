from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Book(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    published_date: str = None
    isbn: str = Field(..., min_length=10, max_length=13)
    libraries: List[str] = []
    
    def __init__(self, **data):
        if "published_date" in data and isinstance(data["published_date"], date):
            data["published_date"] = data["published_date"].strftime("%Y-%m-%d")
        super().__init__(**data)
    

class BookResponse(BaseModel):
    id: str
    title: Optional[str] = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    published_date: Optional[date] = None
    isbn: Optional[str] = Field(..., min_length=10, max_length=13)
    libraries: Optional[List[str]] = None


class UpdateBookSchema(BaseModel):
    title: Optional[str] = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    isbn: Optional[str] = Field(..., min_length=10, max_length=13)
    libraries: Optional[str] = None

