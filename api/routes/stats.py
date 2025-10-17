from fastapi import APIRouter

from api.services.insights import (
    compute_categories_stats,
    compute_overview,
    load_books_dataframe,
)

router = APIRouter(tags=["stats"])

@router.get("/stats/overview")
def stats_overview():
    df = load_books_dataframe()
    return compute_overview(df)

@router.get("/stats/categories")
def stats_by_category():
    df = load_books_dataframe()
    return compute_categories_stats(df)
