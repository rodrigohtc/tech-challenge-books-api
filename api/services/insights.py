import os
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

BOOKS_CSV_PATH = Path(os.getenv("BOOKS_CSV_PATH", "data/books.csv"))

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}

DEFAULT_COLUMNS = [
    "id",
    "title",
    "category",
    "price",
    "rating",
    "availability",
    "link",
    "image",
]


def load_books_dataframe() -> pd.DataFrame:
    if not BOOKS_CSV_PATH.exists():
        return pd.DataFrame(columns=DEFAULT_COLUMNS)

    df = pd.read_csv(BOOKS_CSV_PATH)

    if "price" in df.columns:
        cleaned_price = (
            df["price"]
            .astype(str)
            .str.replace(r"[^\d.,-]", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df["price"] = pd.to_numeric(cleaned_price, errors="coerce")

    if "rating" in df.columns:
        df["rating"] = df["rating"].apply(lambda r: RATING_MAP.get(str(r), r))
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

    if "id" not in df.columns:
        df = df.reset_index(drop=True).reset_index().rename(columns={"index": "id"})

    for column in DEFAULT_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df = df.replace({pd.NA: None, np.nan: None})
    return df[DEFAULT_COLUMNS + [col for col in df.columns if col not in DEFAULT_COLUMNS]]


def compute_overview(df: pd.DataFrame) -> Dict[str, object]:
    total_books = int(len(df))
    avg_price_series = df["price"].dropna() if "price" in df.columns else pd.Series(dtype=float)
    avg_price = float(avg_price_series.mean()) if not avg_price_series.empty else 0.0

    rating_distribution: Dict[str, int] = {}
    if "rating" in df.columns:
        rating_distribution = (
            df["rating"].value_counts().sort_index().astype(int).to_dict()
        )

    availability_total = (
        df["availability"].value_counts().to_dict() if "availability" in df.columns else {}
    )

    return {
        "total_books": total_books,
        "avg_price": round(avg_price, 2),
        "rating_distribution": rating_distribution,
        "availability": availability_total,
    }


def compute_categories_stats(df: pd.DataFrame) -> List[Dict[str, object]]:
    if "category" not in df.columns or df["category"].dropna().empty:
        return []

    grouped = (
        df.groupby("category")
        .agg(
            books=("title", "count"),
            avg_price=("price", "mean"),
            max_price=("price", "max"),
            min_price=("price", "min"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
    )

    grouped["avg_price"] = grouped["avg_price"].round(2)
    grouped["avg_rating"] = grouped["avg_rating"].round(2)
    grouped = grouped.where(pd.notnull(grouped), None)
    return grouped.to_dict(orient="records")


def get_top_rated_books(df: pd.DataFrame, limit: int) -> List[Dict[str, object]]:
    if df.empty:
        return []

    ordered = (
        df.sort_values(by=["rating", "price"], ascending=[False, True])
        .head(limit)
        .replace({pd.NA: None, np.nan: None})
    )
    return ordered.to_dict(orient="records")


def filter_books_by_price(
    df: pd.DataFrame, min_price: float, max_price: float
) -> List[Dict[str, object]]:
    if df.empty or "price" not in df.columns:
        return []

    filtered = df[
        (df["price"].astype(float) >= float(min_price))
        & (df["price"].astype(float) <= float(max_price))
    ]
    return filtered.replace({pd.NA: None, np.nan: None}).to_dict(orient="records")
