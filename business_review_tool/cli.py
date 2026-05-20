"""Command-line interface for the business review tool."""

from __future__ import annotations

import argparse
from pathlib import Path

from .indexer import (
    build_index,
    business_summary,
    category_analysis,
    default_cache_dir,
    load_artifacts,
    search_businesses,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local Business Review Search and Sentiment Insight Tool"
    )
    parser.add_argument(
        "--cache-dir",
        default=str(default_cache_dir()),
        help="Directory used for cached indexes and cleaned data.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_cmd = subparsers.add_parser("build-index", help="Build the TF-IDF search index.")
    build_cmd.add_argument("--business-file", help="Path to the business CSV or workbook.")
    build_cmd.add_argument("--review-file", help="Path to the review CSV or workbook.")

    search_cmd = subparsers.add_parser("search", help="Search for relevant businesses.")
    search_cmd.add_argument("--query", required=True, help="Natural-language search query.")
    search_cmd.add_argument("--city", help="Exact city filter.")
    search_cmd.add_argument("--category", help="Category filter.")
    search_cmd.add_argument("--min-stars", type=float, help="Minimum business star rating.")
    search_cmd.add_argument("--top-k", type=int, default=5, help="Number of results to show.")

    summary_cmd = subparsers.add_parser(
        "business-summary", help="Summarize praise and complaints for a business."
    )
    summary_cmd.add_argument("--business", required=True, help="Business name to summarize.")

    category_cmd = subparsers.add_parser(
        "category-analysis", help="Summarize one business category."
    )
    category_cmd.add_argument("--category", required=True, help="Category name to analyze.")
    return parser


def _print_list(label: str, values: list[str]) -> None:
    pretty = ", ".join(values) if values else "None found"
    print(f"{label}: {pretty}")


def run_cli() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cache_dir = Path(args.cache_dir)

    if args.command == "build-index":
        metadata = build_index(args.business_file, args.review_file, cache_dir)
        print(f"Index built successfully in: {cache_dir}")
        print(f"Businesses indexed: {metadata['business_rows']}")
        print(f"Reviews indexed: {metadata['review_rows']}")
        print(f"Matrix shape: {tuple(metadata['matrix_shape'])}")
        return 0

    artifacts = load_artifacts(cache_dir)

    if args.command == "search":
        results = search_businesses(
            artifacts,
            query=args.query,
            city=args.city,
            category=args.category,
            min_stars=args.min_stars,
            top_k=args.top_k,
        )
        if not results:
            print("No businesses matched the query and filters.")
            return 0
        for idx, result in enumerate(results, start=1):
            print(f"{idx}. {result['name']} ({result['city']})")
            print(
                f"   Stars: {result['stars']:.1f} | Reviews: {result['review_count']} "
                f"| Relevance: {result['relevance_score']:.4f}"
            )
            print(f"   Categories: {result['categories']}")
            print(f"   Matching review count: {result['matching_review_count']}")
            print(f"   Snippet: {result['snippet']}")
            _print_list("   Top praise", result["praise_terms"])
            _print_list("   Top complaints", result["complaint_terms"])
            print()
        return 0

    if args.command == "business-summary":
        summary = business_summary(artifacts, args.business)
        business = summary["business"]
        print(f"{business['name']} ({business['city']})")
        print(
            f"Business stars: {float(business['stars']):.1f} | "
            f"Business review count: {int(business['review_count'])}"
        )
        print(f"Categories: {business['categories']}")
        print(
            f"Indexed review count: {summary['review_total']} | "
            f"Average review stars: {summary['average_review_stars']:.2f}"
        )
        _print_list("Top praise", summary["praise_terms"])
        _print_list("Top complaints", summary["complaint_terms"])
        print("Positive snippets:")
        for snippet in summary["positive_snippets"]:
            print(f"- {snippet}")
        print("Negative snippets:")
        for snippet in summary["negative_snippets"]:
            print(f"- {snippet}")
        return 0

    if args.command == "category-analysis":
        report = category_analysis(artifacts, args.category)
        print(f"Category: {report['category']}")
        print(f"Business count: {report['business_count']}")
        print(f"Total reviews: {report['total_reviews']}")
        print(f"Average business stars: {report['average_business_stars']:.2f}")
        top_cities = ", ".join(
            f"{city} ({count})" for city, count in report["top_cities"].items()
        )
        print(f"Top cities: {top_cities}")
        _print_list("Top praise", report["praise_terms"])
        _print_list("Top complaints", report["complaint_terms"])
        return 0

    parser.error("Unknown command")
    return 2

