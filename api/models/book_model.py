from pydantic import BaseModel, HttpUrl
from typing import Optional

class Book(BaseModel):
    id: int
    title: str
    price: float
    rating: int
    availability: str
    category: str
    link: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
