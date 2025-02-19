from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Author(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    written_books: List[str] = []
    birthdate: date = None
    nationality: Optional[str] = Field(..., min_length=3, max_length=100)
    fav_category: Optional[str] = None


class AuthorResponse(BaseModel):
    id: str
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    written_books: Optional[List[str]] = []
    birthdate: Optional[date] = None
    nationality: Optional[str] = Field(..., min_length=3, max_length=100)
    fav_category: Optional[str] = None


class UpdateAuthorSchema(BaseModel):
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    birthdate: Optional[date] = None
    nationality: Optional[str] = Field(..., min_length=3, max_length=100)
    fav_category: Optional[str] = None

