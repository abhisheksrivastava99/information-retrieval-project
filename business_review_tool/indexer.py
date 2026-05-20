"""Index building, cache management, and query operations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import load_npz, save_npz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from .data import load_and_prepare
from .text_utils import build_search_text, make_snippet, normalize_name, top_terms


@dataclass
class SearchArtifacts:
    businesses: pd.DataFrame
    reviews: pd.DataFrame
    vectorizer: TfidfVectorizer
    matrix: object
    cache_dir: Path


def default_cache_dir() -> Path:
    return Path.cwd() / ".cache" / "business_review_tool"


def _metadata_path(cache_dir: Path) -> Path:
    return cache_dir / "metadata.json"


def _required_cache_files(cache_dir: Path) -> list[Path]:
    return [
        cache_dir / "businesses.pkl",
        cache_dir / "reviews.pkl",
        cache_dir / "tfidf_vectorizer.joblib",
        cache_dir / "review_matrix.npz",
        _metadata_path(cache_dir),
    ]


def cache_exists(cache_dir: Path) -> bool:
    return all(path.exists() for path in _required_cache_files(cache_dir))


def build_index(
    business_path: str | Path | None = None,
    review_path: str | Path | None = None,
    cache_dir: str | Path | None = None,
) -> dict[str, object]:
    cache_path = Path(cache_dir) if cache_dir else default_cache_dir()
    cache_path.mkdir(parents=True, exist_ok=True)

    businesses, reviews = load_and_prepare(business_path, review_path)
    merged = reviews.merge(
        businesses[["business_id", "categories"]],
        on="business_id",
        how="left",
    )
    merged["search_text"] = merged.apply(
        lambda row: build_search_text(row["text"], row["categories"]), axis=1
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.85,
        max_features=40000,
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(merged["search_text"].fillna(""))

    reviews_to_store = reviews[["review_id", "business_id", "stars", "text", "date"]].copy()
    businesses_to_store = businesses[
        [
            "business_id",
            "name",
            "city",
            "categories",
            "stars",
            "review_count",
            "is_open",
            "normalized_name",
            "normalized_categories",
        ]
    ].copy()

    reviews_to_store.to_pickle(cache_path / "reviews.pkl")
    businesses_to_store.to_pickle(cache_path / "businesses.pkl")
    joblib.dump(vectorizer, cache_path / "tfidf_vectorizer.joblib")
    save_npz(cache_path / "review_matrix.npz", matrix)

    metadata = {
        "business_path": str(business_path) if business_path else str(Path.cwd()),
        "review_path": str(review_path) if review_path else str(Path.cwd()),
        "review_rows": int(len(reviews_to_store)),
        "business_rows": int(len(businesses_to_store)),
        "matrix_shape": list(matrix.shape),
    }
    _metadata_path(cache_path).write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def load_artifacts(cache_dir: str | Path | None = None) -> SearchArtifacts:
    cache_path = Path(cache_dir) if cache_dir else default_cache_dir()
    if not cache_exists(cache_path):
        raise FileNotFoundError(
            f"Index cache not found in {cache_path}. Run `python app.py build-index` first."
        )
    return SearchArtifacts(
        businesses=pd.read_pickle(cache_path / "businesses.pkl"),
        reviews=pd.read_pickle(cache_path / "reviews.pkl"),
        vectorizer=joblib.load(cache_path / "tfidf_vectorizer.joblib"),
        matrix=load_npz(cache_path / "review_matrix.npz"),
        cache_dir=cache_path,
    )


def _filtered_businesses(
    businesses: pd.DataFrame,
    city: str | None = None,
    category: str | None = None,
    min_stars: float | None = None,
) -> pd.DataFrame:
    filtered = businesses
    if city:
        filtered = filtered[filtered["city"].str.casefold() == city.casefold()]
    if category:
        normalized_category = normalize_name(category)
        filtered = filtered[
            filtered["normalized_categories"].str.contains(normalized_category, regex=False)
        ]
    if min_stars is not None:
        filtered = filtered[filtered["stars"] >= min_stars]
    return filtered


def _theme_summary(
    reviews: pd.DataFrame,
    query: str | None = None,
    top_n: int = 4,
) -> tuple[list[str], list[str]]:
    positive_texts = reviews.loc[reviews["stars"] >= 4, "text"].tolist()
    negative_texts = reviews.loc[reviews["stars"] <= 2, "text"].tolist()
    praise = top_terms(positive_texts, top_n=top_n, exclude_terms=[query or ""])
    complaints = top_terms(negative_texts, top_n=top_n, exclude_terms=[query or ""])
    return praise, complaints


def search_businesses(
    artifacts: SearchArtifacts,
    query: str,
    city: str | None = None,
    category: str | None = None,
    min_stars: float | None = None,
    top_k: int = 5,
) -> list[dict[str, object]]:
    businesses = _filtered_businesses(artifacts.businesses, city, category, min_stars)
    if businesses.empty:
        return []

    allowed_ids = set(businesses["business_id"].tolist())
    query_vector = artifacts.vectorizer.transform([query])
    raw_scores = linear_kernel(query_vector, artifacts.matrix).ravel()

    review_business_ids = artifacts.reviews["business_id"].to_numpy()
    mask = np.isin(review_business_ids, list(allowed_ids))
    scores = raw_scores * mask

    nonzero_idx = np.flatnonzero(scores > 0)
    if len(nonzero_idx) == 0:
        return []

    candidate_count = min(max(top_k * 250, 500), len(nonzero_idx))
    candidate_idx = nonzero_idx[np.argpartition(scores[nonzero_idx], -candidate_count)[-candidate_count:]]
    candidate_scores = scores[candidate_idx]
    order = np.argsort(candidate_scores)[::-1]
    ordered_idx = candidate_idx[order]

    candidate_reviews = artifacts.reviews.iloc[ordered_idx].copy()
    candidate_reviews["score"] = scores[ordered_idx]

    business_lookup = artifacts.businesses.set_index("business_id")
    review_count_scale = np.log1p(max(float(artifacts.businesses["review_count"].max()), 1.0))

    grouped = []
    for business_id, group in candidate_reviews.groupby("business_id", sort=False):
        business = business_lookup.loc[business_id]
        top_score = float(group["score"].max())
        match_count = int(len(group))
        business_rating = float(business["stars"])
        review_count = float(business["review_count"])
        final_score = (
            (top_score * 0.70)
            + (min(np.log1p(match_count) / 5.0, 1.0) * 0.15)
            + ((business_rating / 5.0) * 0.10)
            + ((np.log1p(review_count) / review_count_scale) * 0.05)
        )
        top_review = group.sort_values("score", ascending=False).iloc[0]
        theme_reviews = group.sort_values("score", ascending=False).head(20)
        praise, complaints = _theme_summary(theme_reviews, query=query)
        grouped.append(
            {
                "business_id": business_id,
                "name": business["name"],
                "city": business["city"],
                "categories": business["categories"],
                "stars": business_rating,
                "review_count": int(review_count),
                "relevance_score": final_score,
                "matching_review_count": match_count,
                "snippet": make_snippet(top_review["text"]),
                "praise_terms": praise,
                "complaint_terms": complaints,
            }
        )

    grouped.sort(key=lambda item: item["relevance_score"], reverse=True)
    return grouped[:top_k]


def resolve_business(artifacts: SearchArtifacts, business_name: str) -> pd.Series:
    normalized = normalize_name(business_name)
    exact = artifacts.businesses[artifacts.businesses["normalized_name"] == normalized]
    if len(exact) == 1:
        return exact.iloc[0]
    if len(exact) > 1:
        return exact.sort_values("review_count", ascending=False).iloc[0]

    partial = artifacts.businesses[
        artifacts.businesses["normalized_name"].str.contains(normalized, regex=False)
    ]
    if partial.empty:
        raise LookupError(f"No business matched '{business_name}'.")
    return partial.sort_values("review_count", ascending=False).iloc[0]


def business_summary(artifacts: SearchArtifacts, business_name: str) -> dict[str, object]:
    business = resolve_business(artifacts, business_name)
    reviews = artifacts.reviews[artifacts.reviews["business_id"] == business["business_id"]].copy()
    if reviews.empty:
        raise LookupError(f"No reviews found for '{business['name']}'.")

    praise, complaints = _theme_summary(reviews)
    positives = reviews[reviews["stars"] >= 4].sort_values("stars", ascending=False)
    negatives = reviews[reviews["stars"] <= 2].sort_values("stars", ascending=True)
    return {
        "business": business.to_dict(),
        "review_total": int(len(reviews)),
        "average_review_stars": float(reviews["stars"].mean()),
        "praise_terms": praise,
        "complaint_terms": complaints,
        "positive_snippets": [make_snippet(text) for text in positives["text"].head(2).tolist()],
        "negative_snippets": [make_snippet(text) for text in negatives["text"].head(2).tolist()],
    }


def category_analysis(artifacts: SearchArtifacts, category: str) -> dict[str, object]:
    businesses = _filtered_businesses(artifacts.businesses, category=category)
    if businesses.empty:
        raise LookupError(f"No businesses matched category '{category}'.")

    business_ids = set(businesses["business_id"].tolist())
    reviews = artifacts.reviews[artifacts.reviews["business_id"].isin(business_ids)].copy()
    praise, complaints = _theme_summary(reviews, query=category)
    return {
        "category": category,
        "business_count": int(len(businesses)),
        "total_reviews": int(len(reviews)),
        "average_business_stars": float(businesses["stars"].mean()),
        "top_cities": businesses["city"].value_counts().head(5).to_dict(),
        "praise_terms": praise,
        "complaint_terms": complaints,
    }

