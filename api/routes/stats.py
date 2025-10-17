from fastapi import APIRouter
import pandas as pd

router = APIRouter(tags=["stats"])

def _load_df() -> pd.DataFrame:
    df = pd.read_csv("data/books.csv")
    if "price" in df.columns:
        cleaned_price = (
            df["price"]
            .astype(str)
            .str.replace(r"[^\d.,-]", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df["price"] = pd.to_numeric(cleaned_price, errors="coerce")
    if "rating" in df.columns:
        map_rating = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        }
        df["rating"] = df["rating"].apply(
            lambda r: map_rating.get(str(r), r)
        )
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)
    return df

@router.get("/stats/overview")
def stats_overview():
    df = _load_df()
    total = len(df)
    avg_price_series = df["price"].dropna() if "price" in df.columns else pd.Series(dtype=float)
    avg_price = float(avg_price_series.mean()) if not avg_price_series.empty else 0.0
    rating_dist = df["rating"].value_counts().sort_index().to_dict() if "rating" in df.columns else {}
    return {
        "total_books": total,
        "avg_price": round(avg_price, 2),
        "rating_distribution": rating_dist,
    }

@router.get("/stats/categories")
def stats_by_category():
    df = _load_df()
    if "category" not in df.columns:
        return {}
    grouped = df.groupby("category").agg(
        count=("title", "count"),
        avg_price=("price", "mean"),
        max_price=("price", "max"),
        min_price=("price", "min"),
    ).reset_index()
    grouped["avg_price"] = grouped["avg_price"].round(2)
    grouped = grouped.where(pd.notnull(grouped), None)
    return grouped.to_dict(orient="records")
