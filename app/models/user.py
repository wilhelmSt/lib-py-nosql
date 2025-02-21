from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class User(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    readed_books: List[str] = []
    rental_books: List[str] = []
    birthdate: str = None
    fav_library: Optional[str] = None
    fav_category: Optional[str] = None
    fav_author: Optional[str] = None
    
    def __init__(self, **data):
        if "birthdate" in data and isinstance(data["birthdate"], date):
            data["birthdate"] = data["birthdate"].strftime("%Y-%m-%d")
        super().__init__(**data)


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


class PopulateBooksUserSchema(BaseModel):
    readed_books: Optional[List[str]] = []
    rental_books: Optional[List[str]] = []
    

class ULibraryAResponse(BaseModel):
    id: str
    name: str

class UBookAResponse(BaseModel):
    id: str
    title: str
    libraries: List[ULibraryAResponse]
class UserResponseAggregate(BaseModel):
    id: str
    name: str
    readed_books: List[str]
    rental_books: List[UBookAResponse]
    birthdate: Optional[str] = None
    fav_library: Optional[str] = None
    fav_category: Optional[str] = None
    fav_author: Optional[str] = None