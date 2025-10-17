from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.services.insights import (
    filter_books_by_price,
    get_top_rated_books,
    load_books_dataframe,
)

router = APIRouter(tags=["books"])

@router.get("/books")
def list_books(skip: int = 0, limit: int = Query(100, le=500)):
    df = load_books_dataframe()
    data = df.iloc[skip: skip + limit].to_dict(orient="records")
    return data

@router.get("/books/search")
def search_books(
    title: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[int] = None,
):
    df = load_books_dataframe()
    if title:
        df = df[df["title"].str.contains(title, case=False, na=False)]
    if category:
        df = df[df["category"].str.contains(category, case=False, na=False)]
    if min_price is not None:
        df = df[df["price"] >= min_price]
    if max_price is not None:
        df = df[df["price"] <= max_price]
    if min_rating is not None:
        df = df[df["rating"] >= min_rating]
    return df.to_dict(orient="records")

@router.get("/books/top-rated")
def top_rated(limit: int = Query(10, le=100)):
    df = load_books_dataframe()
    return get_top_rated_books(df, limit=limit)

@router.get("/books/price-range")
def price_range(min: float, max: float):
    df = load_books_dataframe()
    return filter_books_by_price(df, min_price=min, max_price=max)

@router.get("/books/{book_id}")
def get_book(book_id: int):
    df = load_books_dataframe()
    row = df[df["id"] == book_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Book not found")
    return row.iloc[0].to_dict()
