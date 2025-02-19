from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Book(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    author: str = None
    published_date: date = None
    isbn: str = Field(..., min_length=10, max_length=13)
    libraries: List[str] = []
    

class BookResponse(BaseModel):
    id: str
    title: Optional[str] = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    published_date: Optional[date] = None
    isbn: Optional[str] = Field(..., min_length=10, max_length=13)
    libraries: Optional[str] = None


class UpdateBookSchema(BaseModel):
    title: Optional[str] = Field(..., min_length=3, max_length=100)
    author: Optional[str] = None
    isbn: Optional[str] = Field(..., min_length=10, max_length=13)
    libraries: Optional[str] = None

