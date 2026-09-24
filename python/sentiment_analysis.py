"""
========================================================================================
Project: ShopEasy Consumer Intelligence & Funnel Analysis
Script: sentiment_analysis.py
Description: Explainable, rule-based customer sentiment analysis and complaint driver
             categorization using Python and Pandas.
========================================================================================
"""

import pandas as pd
import numpy as np


def clean_review_text(text: str) -> str:
    """
    Cleans unstructured customer review text:
    - Normalizes nulls
    - Trims leading and trailing whitespace
    - Collapses consecutive internal spaces (handling double/triple spaces)
    """
    if pd.isna(text):
        return ""
    cleaned = str(text).strip()
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    return cleaned


def classify_sentiment(rating: int, text: str) -> str:
    """
    Classifies review sentiment into auditable categories based on star ratings
    and qualitative linguistic markers:
    - 4 to 5 Stars: Positive
    - 3 Stars: Mixed Negative if expressing disappointment/value concerns, else Mixed Positive
    - 1 to 2 Stars: Negative
    """
    text_lower = str(text).lower()
    if rating >= 4:
        return "Positive"
    elif rating == 3:
        negative_cues = ["cheaper", "average", "not worth", "disappointed", "expected better", "slow", "poor"]
        if any(cue in text_lower for cue in negative_cues):
            return "Mixed Negative"
        return "Mixed Positive"
    else:
        return "Negative"


def classify_issue_category(rating: int, text: str) -> str:
    """
    Extracts specific complaint drivers for negative and mixed reviews (Rating <= 3).
    Categorizes feedback into actionable operational buckets:
    - Unmet Expectations: Misleading descriptions, sizing, look-and-feel mismatches
    - Product Cost: Pricing concerns, surprise shipping fees, value-for-money complaints
    - Product Performance: Glitches, poor build, malfunctions
    - Delivery: Shipping delays, carrier problems, damaged packaging
    - Durability: Early wear-and-tear, breaking within days
    """
    if rating > 3:
        return "None"

    text_lower = str(text).lower()

    if any(k in text_lower for k in ["expect", "average", "misleading", "description", "photo", "picture"]):
        return "Unmet Expectations"
    elif any(k in text_lower for k in ["cost", "price", "cheaper", "worth", "expensive", "shipping fee", "hidden"]):
        return "Product Cost"
    elif any(k in text_lower for k in ["performance", "bad experience", "slow", "glitch", "quality"]):
        return "Product Performance"
    elif any(k in text_lower for k in ["late", "delivery", "shipping time", "carrier", "delay"]):
        return "Delivery"
    elif any(k in text_lower for k in ["working", "stopped", "broke", "durability", "tear"]):
        return "Durability"
    else:
        return "General Dissatisfaction"


def analyze_reviews(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Executes the full sentiment and complaint diagnostic workflow on a DataFrame of reviews.
    Expected columns: ['ReviewID', 'CustomerID', 'ProductID', 'Rating', 'ReviewText']
    """
    df = df_reviews.copy()

    # Step 1: Text Cleaning
    df["CleanedReviewText"] = df["ReviewText"].apply(clean_review_text)

    # Step 2: Sentiment Classification
    df["SentimentCategory"] = df.apply(
        lambda row: classify_sentiment(row["Rating"], row["CleanedReviewText"]), 
        axis=1
    )

    # Step 3: Issue Theme Tagging
    df["IssueCategory"] = df.apply(
        lambda row: classify_issue_category(row["Rating"], row["CleanedReviewText"]), 
        axis=1
    )

    return df


def generate_sentiment_diagnostics(df_enriched: pd.DataFrame):
    """
    Prints executive-level diagnostic summaries from the enriched reviews dataset.
    """
    total_reviews = len(df_enriched)
    print("=" * 70)
    print(f"📊 CUSTOMER SENTIMENT & COMPLAINT DIAGNOSTICS (Total Reviews: {total_reviews:,})")
    print("=" * 70)

    # 1. Sentiment Distribution
    sentiment_dist = df_enriched["SentimentCategory"].value_counts(normalize=True) * 100
    print("\n1. Sentiment Distribution:")
    for category, pct in sentiment_dist.items():
        count = (df_enriched["SentimentCategory"] == category).sum()
        print(f"   - {category:<16}: {pct:>5.1f}% ({count:,} reviews)")

    # 2. Complaint Driver Distribution (Filtered to Rating <= 3)
    negative_reviews = df_enriched[df_enriched["IssueCategory"] != "None"]
    print(f"\n2. Top Complaint Drivers (Dissatisfied Reviews: {len(negative_reviews):,}):")
    complaint_dist = negative_reviews["IssueCategory"].value_counts(normalize=True) * 100
    for issue, pct in complaint_dist.items():
        count = (negative_reviews["IssueCategory"] == issue).sum()
        print(f"   - {issue:<24}: {pct:>5.1f}% ({count:,} reviews)")

    # 3. Average Rating by Sentiment Category
    print("\n3. Rating Benchmark by Sentiment Category:")
    avg_ratings = df_enriched.groupby("SentimentCategory")["Rating"].mean()
    for category, avg_r in avg_ratings.items():
        print(f"   - {category:<16}: {avg_r:.2f} / 5.0")
    print("=" * 70)


if __name__ == "__main__":
    import os
    
    # Example file path (can be customized or loaded from database / CSV)
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned", "customer_reviews_sentiment_enriched.csv")
    raw_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "customer_reviews_raw.csv")
    
    target_path = raw_path if os.path.exists(raw_path) else data_path
    
    if os.path.exists(target_path):
        df_raw = pd.read_csv(target_path)
        df_result = analyze_reviews(df_raw)
        generate_sentiment_diagnostics(df_result)
    else:
        # Mock sample demonstration if standalone
        mock_data = pd.DataFrame([
            {"ReviewID": 1, "CustomerID": 101, "ProductID": 1, "Rating": 5, "ReviewText": "Loved it! Excellent quality."},
            {"ReviewID": 2, "CustomerID": 102, "ProductID": 2, "Rating": 1, "ReviewText": "Did not meet expectations. Misleading photo."},
            {"ReviewID": 3, "CustomerID": 103, "ProductID": 4, "Rating": 2, "ReviewText": "Way too expensive for what you get, hidden shipping fees."},
            {"ReviewID": 4, "CustomerID": 104, "ProductID": 5, "Rating": 3, "ReviewText": "Average product, cheaper alternatives are better."},
            {"ReviewID": 5, "CustomerID": 105, "ProductID": 10, "Rating": 4, "ReviewText": "Very good, arrived quickly."}
        ])
        df_result = analyze_reviews(mock_data)
        generate_sentiment_diagnostics(df_result)
