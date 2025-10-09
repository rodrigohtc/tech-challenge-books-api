from fastapi import APIRouter
import pandas as pd

router = APIRouter(tags=["categories"])

def _load_df() -> pd.DataFrame:
    return pd.read_csv("data/books.csv")

@router.get("/categories")
def categories():
    df = _load_df()
    cats = sorted([c for c in df["category"].dropna().unique() if str(c).strip() != ""])
    return {"categories": cats}
