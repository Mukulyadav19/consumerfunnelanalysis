# 🛒 ShopEasy E-Commerce Funnel & Sentiment Intelligence

![SQL Server](https://img.shields.io/badge/Database-SQL%20Server-CC292B?logo=microsoft-sql-server&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python%203.11-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Library-Pandas-150458?logo=pandas&logoColor=white)
![Power BI](https://img.shields.io/badge/BI-Power%20BI-F2C811?logo=power-bi&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-blue)

An end-to-end data analytics and business intelligence project diagnosing e-commerce funnel drop-offs, identifying purchase friction, and enriching customer sentiment telemetry to unlock stagnant revenue growth.

---

## 📌 Executive Summary

ShopEasy experienced a common e-commerce dilemma: **marketing impressions and top-funnel ad views were growing, but top-line revenue was flat.** 

By architecting a robust SQL data cleaning pipeline, an explainable rule-based Python sentiment classifier, and a 2-page interactive Power BI dashboard, this project uncovered:
* **The Root Cause**: Top-of-funnel acquisition was performing strongly (**50.3% View-to-Click Rate**), but **96.15% (~96%) of all session drop-offs were concentrated exclusively at the Checkout stage**.
* **The Revenue Bottleneck**: Only **19.1%** of users who clicked into a product completed a purchase (Overall Session Conversion Rate: **9.60%**).
* **The Qualitative Driver**: **31%** of customer review complaints stemmed from **"Unmet Expectations"** (misleading product descriptions) and **21%** from **"Product Cost"** (surprise shipping fees / hidden checkout costs).

---

## 🏗️ Relational Architecture & Star Schema

The data model connects 6 relational tables through a Star Schema centered on a shared date dimension:

```
                       ┌────────────────┐
                       │    dim_date    │
                       │ (Calendar Date)│
                       └───────┬────────┘
                               │ 1:N
          ┌────────────────────┼────────────────────┐
          │ 1:N                │ 1:N                │ 1:N
┌─────────┴──────────┐ ┌───────┴──────────┐ ┌───────┴──────────┐
│customer_journey_cl │ │engagement_data_cl│ │customer_reviews_ │
│ (VisitDate)        │ │ (Date)           │ │ sentiment        │
└─────────┬──────────┘ └───────┬──────────┘ └───────┬──────────┘
          │ N:1                │                    │ N:1
          └───────────────────►│    products      │◄┘
                               │   (ProductID)    │
                               └────────┬─────────┘
                                        │
                               ┌────────┴─────────┐
                               │    customers     │◄─── geography
                               │   (CustomerID)   │
                               └──────────────────┘
```

---

## 🔍 Key Metrics & Analytical Findings

| Funnel Stage | Event Count | Step Conversion Rate | Drop-off Share | Strategic Takeaway |
| :--- | :--- | :--- | :--- | :--- |
| **Impressions** | 2,292 | Baseline (100%) | - | Strong creative reach & audience targeting |
| **Clicks** | 1,152 | **50.3%** (View-to-Click) | 2.5% | High initial user interest & intent |
| **Cart Additions** | 480 | **41.7%** (Click-to-Cart) | 1.3% | Strong product consideration |
| **Completed Purchases** | 220 | **45.8%** (Cart-to-Purchase) | **96.2%** | **Massive checkout friction & drop-off (575 sessions lost)** |

* **Click-to-Purchase Rate**: **19.10%** (220 orders / 1,152 clicks)
* **Overall Conversion Rate**: **9.60%** (220 orders / 2,292 impressions)
* **Average Star Rating**: **3.7 / 5.0**

---

## 📁 Repository Structure

```
shopeasy-funnel-analysis/
│
├── data/
│   ├── raw/                            # 6 raw datasets with injected real-world anomalies
│   │   ├── customer_journey_raw.csv
│   │   ├── engagement_data_raw.csv
│   │   ├── customer_reviews_raw.csv
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   └── geography.csv
│   └── cleaned/                        # Fully normalized, deduplicated & enriched CSVs
│       ├── customer_journey_cleaned.csv
│       ├── engagement_data_cleaned.csv
│       ├── customer_reviews_sentiment_enriched.csv
│       ├── customers.csv
│       ├── products.csv
│       └── geography.csv
│
├── sql/
│   ├── 01_Data_Validation.sql          # Diagnostic profiling, null checks & duplicate detection
│   ├── 02_Cleaning_Transformation.sql   # Production pipeline (ROW_NUMBER(), CHARINDEX, nested REPLACE)
│   └── 03_Funnel_Diagnostics_Master.sql# Funnel drop-offs (96% checkout proof), conversions & category stats
│
├── python/
│   ├── clean_and_enrich.py             # Automated Pandas cleaning & rule-based sentiment tagging
│   └── generate_mock_data.py           # Synthetic dataset generator for reproduction
│
├── power_bi/
│   ├── DAX_Measures.dax                # 13 verified DAX measures with zero table mismatches
│   └── README_PowerBI.md               # 2-Page dashboard layout specifications & visual guides
│
├── docs/
│   ├── Executive_Summary_and_Recommendations.md # Strategic business action plan
│   └── Interview_STAR_Guide.md         # Full & concise interview responses + defense strategies
│
├── .gitignore
└── README.md
```

---

## 🛠️ Step-by-Step Implementation

### 1. SQL Pipeline & Transformation
* **Deduplication**: Handled re-transmitted double-click events using `ROW_NUMBER() OVER(PARTITION BY CustomerID, ProductID, VisitDate, UPPER(TRIM(Stage)), UPPER(TRIM(Action)) ORDER BY JourneyID)`.
* **String Parsing**: Replaced fragile hacks with standard `SUBSTRING` and `CHARINDEX` to parse combined metrics like `"45000-9000"`.
* **Whitespace Scrubbing**: Handled double and triple whitespace in customer feedback using nested `REPLACE(REPLACE(ReviewText, '   ', ' '), '  ', ' ')`.

### 2. Python Rule-Based Sentiment Analysis
* Avoided black-box NLP packages in favor of a **100% explainable, auditable Pandas rule-engine**.
* Mapped star ratings and review text keywords to issue categories:
  * **Unmet Expectations (31%)**: Cues like `"expect"`, `"average"`, `"misleading"`.
  * **Product Cost (21%)**: Cues like `"price"`, `"expensive"`, `"shipping"`, `"cheaper"`.
  * **Product Performance (18%)**: Cues like `"performance"`, `"bad experience"`, `"glitch"`.
  * **Delivery Issues (17%)**: Cues like `"late"`, `"delivery"`, `"shipping time"`.

### 3. Power BI 2-Page Dashboard Blueprint
* **Page 1: Executive Overview**:
  * 4 KPI Banner Cards: *Overall Conversion Rate (9.6%)*, *Click-to-Purchase Rate (19.1%)*, *Total Impressions (2,292)*, *Avg Rating (3.7)*.
  * Dual-Axis Reach vs Conversion Trend Chart.
  * Category Revenue Summary Table.
* **Page 2: Funnel & Sentiment Diagnostics (Split Screen)**:
  * **Left**: 4-Stage Funnel Chart + Drop-off stage bar chart highlighting the **96% checkout abandonment**.
  * **Right**: Sentiment distribution donut chart + Top complaint drivers bar chart.

---

## 💡 Strategic Recommendations

1. **Eliminate Checkout Cost Shock**: Display transparent shipping costs, taxes, and estimated delivery dates upfront on the Product Detail Page and Cart to eliminate surprise fees.
2. **Implement 1-Click & Guest Checkout**: Reduce drop-offs by removing mandatory account creation and offering modern payment wallets (Apple Pay, Google Pay).
3. **Realign PDP Expectations**: Audit imagery, dimensions, and specifications on high-traffic PDPs to curb the 31% "Unmet Expectations" complaint share.

---

## 👤 Author & Portfolio
* **Project**: ShopEasy Consumer Intelligence Funnel & Sentiment Analysis
* **Tools**: SQL Server (T-SQL), Python (Pandas), Power BI (DAX), Git
