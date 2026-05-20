"""Dataset loading and normalization."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .text_utils import normalize_name

BUSINESS_REQUIRED_COLUMNS = {
    "business_id",
    "name",
    "city",
    "categories",
    "stars",
    "review_count",
}
REVIEW_REQUIRED_COLUMNS = {
    "review_id",
    "business_id",
    "stars",
    "text",
    "date",
}


def discover_input_file(patterns: Iterable[str]) -> Path | None:
    cwd = Path.cwd()
    for pattern in patterns:
        matches = sorted(cwd.glob(pattern))
        if matches:
            return matches[0]
    return None


def default_business_path() -> Path:
    path = discover_input_file(
        [
            "data/businesses*.csv",
            "data/businesses*.xlsx",
            "businesses*.csv",
            "businesses*.xlsx",
        ]
    )
    if path is None:
        raise FileNotFoundError("Could not find a business dataset file in the current directory.")
    return path


def default_review_path() -> Path:
    path = discover_input_file(
        [
            "data/reviews*.csv",
            "data/reviews*.xlsx",
            "reviews*.csv",
            "reviews*.xlsx",
        ]
    )
    if path is None:
        raise FileNotFoundError("Could not find a reviews dataset file in the current directory.")
    return path


def read_table(path: str | Path) -> pd.DataFrame:
    table_path = Path(path)
    suffix = table_path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(table_path)
        except UnicodeDecodeError:
            return pd.read_csv(table_path, encoding="latin1")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(table_path)
    raise ValueError(f"Unsupported file type: {table_path.suffix}")


def ensure_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def prepare_businesses(df: pd.DataFrame) -> pd.DataFrame:
    ensure_columns(df, BUSINESS_REQUIRED_COLUMNS, "Business dataset")
    businesses = df.copy()
    businesses["name"] = businesses["name"].fillna("").astype(str)
    businesses["city"] = businesses["city"].fillna("").astype(str).str.strip()
    businesses["categories"] = businesses["categories"].fillna("").astype(str)
    businesses["stars"] = pd.to_numeric(businesses["stars"], errors="coerce").fillna(0.0)
    businesses["review_count"] = pd.to_numeric(
        businesses["review_count"], errors="coerce"
    ).fillna(0)
    if "is_open" in businesses.columns:
        businesses["is_open"] = pd.to_numeric(
            businesses["is_open"], errors="coerce"
        ).fillna(0).astype(int)
    else:
        businesses["is_open"] = 0
    businesses["normalized_name"] = businesses["name"].map(normalize_name)
    businesses["normalized_categories"] = businesses["categories"].map(normalize_name)
    return businesses


def prepare_reviews(df: pd.DataFrame) -> pd.DataFrame:
    ensure_columns(df, REVIEW_REQUIRED_COLUMNS, "Review dataset")
    reviews = df.copy()
    reviews["text"] = reviews["text"].fillna("").astype(str)
    reviews["stars"] = pd.to_numeric(reviews["stars"], errors="coerce").fillna(0).astype(int)
    reviews["date"] = pd.to_datetime(reviews["date"], errors="coerce")
    return reviews


def load_and_prepare(
    business_path: str | Path | None = None,
    review_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    business_file = Path(business_path) if business_path else default_business_path()
    review_file = Path(review_path) if review_path else default_review_path()
    businesses = prepare_businesses(read_table(business_file))
    reviews = prepare_reviews(read_table(review_file))
    return businesses, reviews
