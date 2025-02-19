from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class User(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    readed_books: List[str] = []
    rental_books: List[str] = []
    birthdate: date = None
    fav_library: str = None
    fav_category: str = None
    fav_author: str = None
    

class UserResponse(BaseModel):
    id: str
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    readed_books: Optional[List[str]] = []
    rental_books: Optional[List[str]] = []
    birthdate: Optional[date] = None
    fav_library: Optional[str] = None
    fav_category: Optional[str] = None
    fav_author: Optional[str] = None


class UpdateUserSchema(BaseModel):
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    birthdate: Optional[date] = None
    fav_library: Optional[str] = None
    fav_category: Optional[str] = None
    fav_author: Optional[str] = None

