from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Library(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    books: List[str] = []
    is_public: bool = True
    location: str = Field(..., min_length=3, max_length=200)
    establish_year: Optional[int] = None
    

class LibraryResponse(BaseModel):
    id: str
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    books: Optional[List[str]] = []
    is_public: Optional[bool] = True
    location: Optional[str] = Field(..., min_length=3, max_length=200)
    establish_year: Optional[int] = None


class UpdateLibrarySchema(BaseModel):
    name: Optional[str] = Field(..., min_length=3, max_length=100)
    is_public: Optional[bool] = True
    location: Optional[str] = Field(..., min_length=3, max_length=200)
    establish_year: Optional[int] = None

