from typing import Dict, List

import pandas as pd

from api.services.insights import load_books_dataframe


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with NaNs replaced and minimal columns for ML."""
    return df.replace({pd.NA: None})


def prepare_feature_matrix() -> List[Dict[str, object]]:
    """Return feature-ready rows prioritising numeric/categorical fields."""
    df = load_books_dataframe()
    if df.empty:
        return []

    features = df[
        [
            "id",
            "title",
            "category",
            "price",
            "rating",
            "availability",
        ]
    ].copy()
    features["in_stock"] = features["availability"].astype(str).str.contains("In stock", case=False)
    features["category"] = features["category"].fillna("unknown")

    features = features.drop(columns=["availability"])
    return _clean_dataframe(features).to_dict(orient="records")


def prepare_training_dataset() -> Dict[str, List[Dict[str, object]]]:
    """Return a simplified dataset suitable for model training."""
    df = load_books_dataframe()
    if df.empty:
        return {"records": [], "feature_columns": [], "target": None}

    dataset = df[
        [
            "id",
            "title",
            "category",
            "price",
            "rating",
            "availability",
            "link",
        ]
    ].copy()
    dataset["in_stock"] = dataset["availability"].astype(str).str.contains("In stock", case=False)

    feature_columns = ["category", "price", "rating", "in_stock"]
    target = "price"

    return {
        "records": _clean_dataframe(dataset).to_dict(orient="records"),
        "feature_columns": feature_columns,
        "target": target,
    }


def summarize_predictions(predictions: List[Dict[str, object]]) -> Dict[str, object]:
    """Return a simple acknowledgement payload for received predictions."""
    total = len(predictions)
    sources = sorted({item.get("model", "unknown") for item in predictions})
    avg_score = None
    scores = [
        float(item["score"])
        for item in predictions
        if isinstance(item, dict) and "score" in item and isinstance(item["score"], (int, float, str))
    ]
    if scores:
        avg_score = round(sum(scores) / len(scores), 4)

    return {
        "received": total,
        "models": sources,
        "average_score": avg_score,
    }
