from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Author(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    written_books: List[str] = []
    birthdate: str = None
    nationality: Optional[str] = Field(..., min_length=3, max_length=100)
    fav_category: Optional[str] = None
    
    def __init__(self, **data):
        if "birthdate" in data and isinstance(data["birthdate"], date):
            data["birthdate"] = data["birthdate"].strftime("%Y-%m-%d")
        super().__init__(**data)


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

