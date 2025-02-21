from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from bson import ObjectId

class Book(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    category: Optional[str] = None
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
    category: Optional[str] = None
    published_date: Optional[str] = None
    isbn: Optional[str] = Field(..., min_length=10, max_length=13)
    libraries: Optional[List[str]] = None
    
    def __init__(self, **data):
        if "published_date" in data and isinstance(data["published_date"], date):
            data["published_date"] = data["published_date"].strftime("%Y-%m-%d")
        if "author" in data and isinstance(data["author"], ObjectId):
            data["author"] = str(data["author"])
        if "category" in data and isinstance(data["category"], ObjectId):
            data["category"] = str(data["category"])
        if "libraries" in data and isinstance(data["libraries"], list):
            data["libraries"] = [str(lib) for lib in data["libraries"]]
        super().__init__(**data)


class BAuthorResponse(BaseModel):
    id: str
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    nationality: Optional[str] = Field(..., min_length=3, max_length=100)


class BookAuthorResponse(BookResponse):
    author: Optional[BAuthorResponse] = None


class UpdateBookSchema(BaseModel):
    title: Optional[str] = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    category: Optional[str] = None
    isbn: Optional[str] = Field(..., min_length=10, max_length=13)
    libraries: Optional[str] = None

