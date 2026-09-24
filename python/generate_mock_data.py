"""
==============================================================================
Script: generate_mock_data.py
Description: Generates the 6 relational datasets with realistic e-commerce 
             telemetry, including intentional quality anomalies for testing.
==============================================================================
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'data', 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)

date_start = datetime(2023, 1, 1)

def generate_geography():
    df = pd.DataFrame([
        [1, 'United States', 'New York'], [2, 'United States', 'Los Angeles'],
        [3, 'United States', 'Chicago'], [4, 'United Kingdom', 'London'],
        [5, 'Canada', 'Toronto'], [6, 'Australia', 'Sydney'],
        [7, 'Germany', 'Berlin'], [8, 'United States', 'Houston'],
        [9, 'United Kingdom', 'Manchester'], [10, 'Canada', 'Vancouver']
    ], columns=['GeographyID', 'Country', 'City'])
    df.to_csv(os.path.join(OUTPUT_DIR, 'geography.csv'), index=False)
    print("-> Generated geography.csv")

def generate_customers():
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    genders = ['Male', 'Female', 'Non-Binary']
    
    cust_data = [
        [i, f"{random.choice(first_names)} {random.choice(last_names)}", 
         f"user{i}@example.com", random.choice(genders), random.randint(18, 70), random.randint(1, 10)] 
        for i in range(1, 301)
    ]
    df = pd.DataFrame(cust_data, columns=['CustomerID', 'CustomerName', 'Email', 'Gender', 'Age', 'GeographyID'])
    df.to_csv(os.path.join(OUTPUT_DIR, 'customers.csv'), index=False)
    print("-> Generated customers.csv")

def generate_products():
    df = pd.DataFrame([
        [1, 'Running Shoes', 'Footwear', 120.0], [2, 'Leather Jacket', 'Apparel', 250.0],
        [3, 'Yoga Mat', 'Fitness', 35.0], [4, 'Wireless Earbuds', 'Electronics', 99.0],
        [5, 'Smart Watch', 'Electronics', 199.0], [6, 'Backpack', 'Accessories', 65.0],
        [7, 'Sunglasses', 'Accessories', 45.0], [8, 'Water Bottle', 'Fitness', 25.0],
        [9, 'Gym Duffel', 'Accessories', 55.0], [10, 'Trail Hiking Boots', 'Footwear', 140.0],
        [11, 'Football Helmet', 'Sports Gear', 150.0], [12, 'Hockey Stick', 'Sports Gear', 110.0],
        [13, 'Baseball Glove', 'Sports Gear', 85.0], [14, 'Swim Goggles', 'Fitness', 30.0],
        [15, 'Tennis Racket', 'Sports Gear', 130.0], [16, 'Fitness Tracker', 'Electronics', 89.0],
        [17, 'Cycling Helmet', 'Sports Gear', 75.0], [18, 'Compression Tights', 'Apparel', 48.0],
        [19, 'Resistance Bands', 'Fitness', 20.0], [20, 'Insulated Jacket', 'Apparel', 180.0]
    ], columns=['ProductID', 'ProductName', 'Category', 'Price'])
    df.to_csv(os.path.join(OUTPUT_DIR, 'products.csv'), index=False)
    print("-> Generated products.csv")

def generate_journey():
    journey_rows = []
    for i in range(1, 5001):
        c_id, p_id = random.randint(1, 300), random.randint(1, 20)
        v_date = date_start + timedelta(days=random.randint(0, 730))
        r = random.random()
        if r < 0.45:
            stage, action, duration = random.choice(['Impressions', 'IMPRESSIONS']), random.choice(['Viewed', 'VIEWED']), round(random.uniform(5.0, 45.0), 2)
        elif r < 0.72:
            stage, action, duration = random.choice(['Click', 'click']), random.choice(['Clicked', 'CLICKED']), round(random.uniform(15.0, 90.0), 2)
        elif r < 0.85:
            stage, action, duration = random.choice(['Cart', 'CART']), 'Added to Cart', round(random.uniform(30.0, 150.0), 2)
        elif r < 0.95:
            stage, action, duration = random.choice(['Checkout', 'checkout', 'Drop-off']), 'Abandoned', None
        else:
            stage, action, duration = random.choice(['Checkout', 'checkout']), 'Purchased', round(random.uniform(45.0, 300.0), 2)
        journey_rows.append([i, c_id, p_id, v_date.strftime('%Y-%m-%d'), stage, action, duration])

    df = pd.DataFrame(journey_rows, columns=['JourneyID', 'CustomerID', 'ProductID', 'VisitDate', 'Stage', 'Action', 'Duration'])
    # Inject 120 logical duplicates
    dups = df.sample(n=120, random_state=42)
    df = pd.concat([df, dups], ignore_index=True)
    df.to_csv(os.path.join(OUTPUT_DIR, 'customer_journey_raw.csv'), index=False)
    print("-> Generated customer_journey_raw.csv")

def generate_engagement():
    channels = ['Video', 'VIDEO', 'Social Media', 'social media', 'Blog', 'BLOG', 'Newsletter', 'newsletter']
    eng_rows = []
    for i in range(1, 1001):
        c_type = random.choice(channels)
        camp = f"Campaign_{random.choice(['SummerSale', 'BlackFriday', 'SpringLaunch', 'HolidaySpecial', 'InfluencerBoost'])}"
        views = random.randint(5000, 100000)
        clicks = int(views * random.uniform(0.02, 0.18))
        combined = f"{views}-{clicks}"
        likes = int(clicks * random.uniform(0.1, 0.4))
        e_date = date_start + timedelta(days=random.randint(0, 730))
        eng_rows.append([i, c_type, camp, combined, likes, e_date.strftime('%Y-%m-%d')])
        
    df = pd.DataFrame(eng_rows, columns=['ContentID', 'ContentType', 'Campaign', 'ViewsClicksCombined', 'Likes', 'Date'])
    df.to_csv(os.path.join(OUTPUT_DIR, 'engagement_data_raw.csv'), index=False)
    print("-> Generated engagement_data_raw.csv")

def generate_reviews():
    pos_texts = [
        "Great quality, absolutely loved it!",
        "Excellent product, matches description perfectly.",
        "Very fast shipping and high durability. 5 stars.",
        "Super comfortable and fits true to size.",
        "Worth every penny, exceeded expectations."
    ]
    neg_texts = [
        "Did not meet expectations. The photo was misleading.",
        "Way too expensive for this level of quality.",
        "Average product, not worth the full price.",
        "Poor performance, started glitching after 2 days.",
        "Delivery took over 3 weeks. Very disappointed.",
        "Stopped working within a week of moderate use.",
        "Expected better build quality for the cost."
    ]
    
    rev_rows = []
    for i in range(1, 1001):
        c_id, p_id = random.randint(1, 300), random.randint(1, 20)
        r_date = date_start + timedelta(days=random.randint(0, 730))
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.15, 0.12, 0.15, 0.28, 0.30])[0]
        if rating >= 4:
            txt = random.choice(pos_texts)
        else:
            txt = random.choice(neg_texts)
        
        # Inject intentional double space formatting
        if random.random() < 0.25:
            txt = txt.replace(' ', '  ')
            
        rev_rows.append([i, c_id, p_id, r_date.strftime('%Y-%m-%d'), rating, txt])
        
    df = pd.DataFrame(rev_rows, columns=['ReviewID', 'CustomerID', 'ProductID', 'ReviewDate', 'Rating', 'ReviewText'])
    df.to_csv(os.path.join(OUTPUT_DIR, 'customer_reviews_raw.csv'), index=False)
    print("-> Generated customer_reviews_raw.csv")

if __name__ == '__main__':
    generate_geography()
    generate_customers()
    generate_products()
    generate_journey()
    generate_engagement()
    generate_reviews()
    print("SUCCESS: Mock datasets generated in data/raw/")
