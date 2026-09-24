"""
==============================================================================
Script: clean_and_enrich.py
Description: End-to-end Python pipeline executing data cleaning and
             transparent, rule-based sentiment enrichment via Pandas.
==============================================================================
"""

import os
import pandas as pd
import numpy as np

# Set base directories relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, '..', 'data', 'raw')
CLEAN_DIR = os.path.join(BASE_DIR, '..', 'data', 'cleaned')

os.makedirs(CLEAN_DIR, exist_ok=True)

def clean_customer_journey():
    print("-> Cleaning customer_journey...")
    df = pd.read_csv(os.path.join(RAW_DIR, 'customer_journey_raw.csv'))
    
    # Standardize casing & trim spaces
    df['Stage'] = df['Stage'].astype(str).str.strip().str.upper()
    df['Action'] = df['Action'].astype(str).str.strip().str.upper()
    
    # Deduplicate re-transmitted web clicks
    df_cleaned = df.drop_duplicates(
        subset=['CustomerID', 'ProductID', 'VisitDate', 'Stage', 'Action'],
        keep='first'
    ).reset_index(drop=True)
    
    # Re-index clean sequential JourneyID
    df_cleaned['JourneyID'] = range(1, len(df_cleaned) + 1)
    
    output_path = os.path.join(CLEAN_DIR, 'customer_journey_cleaned.csv')
    df_cleaned.to_csv(output_path, index=False)
    print(f"   Saved {len(df_cleaned)} rows to {output_path}")

def clean_engagement_data():
    print("-> Cleaning engagement_data...")
    df = pd.read_csv(os.path.join(RAW_DIR, 'engagement_data_raw.csv'))
    
    df['ContentType'] = df['ContentType'].astype(str).str.strip().str.upper()
    
    # Split ViewsClicksCombined e.g. "45000-9000" on '-'
    split_metrics = df['ViewsClicksCombined'].astype(str).str.split('-', expand=True)
    df['Views'] = split_metrics[0].astype(int)
    df['Clicks'] = split_metrics[1].astype(int)
    
    df_cleaned = df.drop(columns=['ViewsClicksCombined'])
    output_path = os.path.join(CLEAN_DIR, 'engagement_data_cleaned.csv')
    df_cleaned.to_csv(output_path, index=False)
    print(f"   Saved {len(df_cleaned)} rows to {output_path}")

def clean_and_enrich_reviews():
    print("-> Cleaning and enriching customer_reviews...")
    df = pd.read_csv(os.path.join(RAW_DIR, 'customer_reviews_raw.csv'))
    
    # Multi-pass whitespace cleaning (collapsing multiple spaces)
    def clean_text(text):
        if pd.isna(text):
            return ""
        t = str(text).strip()
        while '  ' in t:
            t = t.replace('  ', ' ')
        return t
    
    df['ReviewText'] = df['ReviewText'].apply(clean_text)
    
    # Rule-Based Sentiment Classification (Explainable & Auditable)
    def classify_sentiment(row):
        rating = row['Rating']
        text = str(row['ReviewText']).lower()
        if rating >= 4:
            return 'Positive'
        elif rating == 3:
            mixed_neg_cues = ['cheaper', 'average', 'not worth', 'disappointed', 'expected better']
            return 'Mixed Negative' if any(w in text for w in mixed_neg_cues) else 'Mixed Positive'
        else:
            return 'Negative'
    
    # Issue / Complaint Root Cause Classification
    def classify_issue(row):
        rating = row['Rating']
        text = str(row['ReviewText']).lower()
        if rating <= 3:
            if any(k in text for k in ['expect', 'average', 'misleading', 'description']):
                return 'Unmet Expectations'
            elif any(k in text for k in ['cost', 'price', 'cheaper', 'worth', 'expensive', 'shipping']):
                return 'Product Cost'
            elif any(k in text for k in ['performance', 'bad experience', 'slow', 'glitch']):
                return 'Product Performance'
            elif any(k in text for k in ['late', 'delivery', 'shipping time', 'carrier']):
                return 'Delivery'
            elif any(k in text for k in ['working', 'stopped', 'broke', 'durability']):
                return 'Durability'
            else:
                return 'General Dissatisfaction'
        return 'None'
    
    df['SentimentCategory'] = df.apply(classify_sentiment, axis=1)
    df['IssueCategory'] = df.apply(classify_issue, axis=1)
    
    output_path = os.path.join(CLEAN_DIR, 'customer_reviews_sentiment_enriched.csv')
    df.to_csv(output_path, index=False)
    print(f"   Saved {len(df)} enriched reviews to {output_path}")

def copy_dimension_tables():
    print("-> Syncing dimension tables...")
    for dim_file in ['customers.csv', 'products.csv', 'geography.csv']:
        src = os.path.join(RAW_DIR, dim_file)
        dst = os.path.join(CLEAN_DIR, dim_file)
        if os.path.exists(src):
            df = pd.read_csv(src)
            df.to_csv(dst, index=False)
            print(f"   Copied {dim_file}")

if __name__ == '__main__':
    print("Starting data pipeline execution...")
    clean_customer_journey()
    clean_engagement_data()
    clean_and_enrich_reviews()
    copy_dimension_tables()
    print("SUCCESS: Data pipeline execution finished.")
