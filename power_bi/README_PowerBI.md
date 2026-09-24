# 📊 Power BI 2-Page Dashboard Blueprint & Architecture

This guide details the exact layout, visual configurations, slicers, and relationship topology required to build the **Shopeasy Consumer Intelligence Dashboard** in Power BI Desktop.

---

## 1. Data Model Relationships (Star Schema)

Import the 6 cleaned CSV files from `../data/cleaned/` into Power BI:
1. `customer_journey_cleaned` (Fact Table)
2. `engagement_data_cleaned` (Fact Table)
3. `customer_reviews_sentiment_enriched` (Fact Table)
4. `products` (Dimension Table)
5. `customers` (Dimension Table)
6. `geography` (Dimension Table)

### Relationships in Model View:
* **dim_date (Calendar)** `[Date]` (1) ───► (N) `customer_journey_cleaned[VisitDate]`
* **dim_date (Calendar)** `[Date]` (1) ───► (N) `engagement_data_cleaned[Date]`
* **dim_date (Calendar)** `[Date]` (1) ───► (N) `customer_reviews_sentiment_enriched[ReviewDate]`
* **products** `[ProductID]` (1) ───► (N) `customer_journey_cleaned[ProductID]`
* **products** `[ProductID]` (1) ───► (N) `customer_reviews_sentiment_enriched[ProductID]`
* **customers** `[CustomerID]` (1) ───► (N) `customer_journey_cleaned[CustomerID]`
* **customers** `[CustomerID]` (1) ───► (N) `customer_reviews_sentiment_enriched[CustomerID]`
* **geography** `[GeographyID]` (1) ───► (N) `customers[GeographyID]`

*(Note: Create a standard Date table using DAX: `dim_date = CALENDARAUTO()`)*

---

## 2. Dashboard Layout

### 📄 Page 1: Executive Overview
**Objective**: Provide leadership with a single-pane view of business conversion efficiency, marketing reach, and category revenue.

* **Top KPI Header (4 Cards)**:
  * **Card 1**: `Overall Conversion Rate` (Format: `0.0%` -> **9.6%**)
  * **Card 2**: `Click to Purchase Rate` (Format: `0.0%` -> **19.1%**)
  * **Card 3**: `Total Impressions` (Format: `#,##0` -> **2,292**)
  * **Card 4**: `Avg Rating` (Format: `0.0` -> **3.7 / 5.0**)
* **Dual-Axis Trend Chart (Center)**:
  * **Visual**: Line and Clustered Column Chart (or Dual-Axis Line)
  * **Shared X-Axis**: `dim_date[YearMonth]`
  * **Column / Primary Y-Axis**: `Marketing Ad Reach` (Total views)
  * **Line / Secondary Y-Axis**: `Overall Conversion Rate` (%)
* **Category Breakdown Matrix (Bottom)**:
  * **Rows**: `products[Category]`
  * **Values**: `Total Purchases`, `Total Revenue ($)`
* **Global Slicers**:
  * Date Range Slider (`dim_date[Date]`)
  * Geography Dropdown (`geography[Country]`)
  * Product Category Dropdown (`products[Category]`)

---

### 📄 Page 2: Funnel & Sentiment Diagnostics (Split Screen)
**Objective**: Diagnose *where* customer drop-offs occur and *why* customers are abandoning.

#### 👈 Left Screen (Funnel Diagnostics):
1. **Multi-Stage Funnel Chart**:
   * Stages: `Total Impressions (2,292)` ➔ `Journey Clicks (1,152)` ➔ `Cart Touchpoints (480)` ➔ `Total Purchases (220)`
2. **Drop-Off Stage Horizontal Bar Chart**:
   * **Y-Axis**: `customer_journey_cleaned[Stage]`
   * **X-Axis**: `Total Abandoned Sessions`
   * **Visual Callout Card**: 
     > **🚨 96.15% (~96%) of all session drop-offs occur at the Checkout Stage!**

#### 👉 Right Screen (Customer Sentiment & Feedback):
1. **Sentiment Breakdown Donut Chart**:
   * **Legend**: `customer_reviews_sentiment_enriched[SentimentCategory]`
   * **Values**: `Total Reviews`
   * **Percentages**: ~61.6% Positive, ~14.4% Mixed Negative, ~24.0% Negative
2. **Complaint Drivers Bar Chart**:
   * **Visual filter**: `IssueCategory <> "None"`
   * **Y-Axis**: `IssueCategory`
   * **X-Axis**: Count of Reviews / Share of Complaints
   * **Key Insights**: Unmet Expectations (31%), Product Cost (21%), Product Performance (18%), Delivery (17%)
