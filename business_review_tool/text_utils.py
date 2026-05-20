"""Text cleaning and lightweight keyword extraction utilities."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

STOP_WORDS = set(ENGLISH_STOP_WORDS) | {
    "ve",
    "ll",
    "did",
    "don",
    "just",
    "really",
    "got",
    "going",
    "said",
    "like",
    "good",
    "great",
}

TOKEN_RE = re.compile(r"[a-z0-9']+")
NON_WORD_RE = re.compile(r"[^a-z0-9\s']")
SPACE_RE = re.compile(r"\s+")


def normalize_text(value: object) -> str:
    """Return a normalized ASCII-friendly text string."""
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = text.replace("&amp;", " and ")
    text = NON_WORD_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()


def tokenize(value: object) -> list[str]:
    """Tokenize text and remove stop words and low-value tokens."""
    text = normalize_text(value)
    tokens = []
    for token in TOKEN_RE.findall(text):
        if len(token) < 3:
            continue
        if token.isdigit():
            continue
        if token in STOP_WORDS:
            continue
        tokens.append(token)
    return tokens


def normalize_name(value: object) -> str:
    """Normalize a business or category name for matching."""
    return " ".join(tokenize(value))


def build_search_text(review_text: object, categories: object) -> str:
    """Combine review text and category words for indexing."""
    review_part = str(review_text or "")
    category_part = str(categories or "")
    return f"{review_part} {category_part}".strip()


def top_terms(
    texts: Iterable[object],
    top_n: int = 5,
    exclude_terms: Iterable[str] | None = None,
) -> list[str]:
    """Extract top unigram and bigram themes from a group of texts."""
    exclude = set(tokenize(" ".join(exclude_terms or [])))
    counts: Counter[str] = Counter()
    for text in texts:
        tokens = [token for token in tokenize(text) if token not in exclude]
        for token in tokens:
            counts[token] += 1
        for left, right in zip(tokens, tokens[1:]):
            if left == right:
                continue
            counts[f"{left} {right}"] += 1
    ranked = []
    for term, count in counts.most_common():
        if count < 2 and len(counts) > 10:
            continue
        ranked.append(term)
        if len(ranked) >= top_n:
            break
    return ranked


def make_snippet(text: object, max_len: int = 180) -> str:
    """Create a readable single-line snippet."""
    snippet = SPACE_RE.sub(" ", str(text or "").strip())
    if len(snippet) <= max_len:
        return snippet
    return snippet[: max_len - 3].rstrip() + "..."

