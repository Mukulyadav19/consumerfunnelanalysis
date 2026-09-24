-- ==============================================================================
-- File: 03_Funnel_Diagnostics_Master.sql
-- Description: Master analytical queries diagnosing funnel friction & sentiment
-- Database Flavor: Microsoft SQL Server (T-SQL)
-- ==============================================================================

USE shopeasy;
GO

-- ------------------------------------------------------------------------------
-- 1. TOUCHPOINT STAGE DISTRIBUTION
-- ------------------------------------------------------------------------------
SELECT 
    Stage,
    COUNT(JourneyID) AS TouchpointCount,
    ROUND(100.0 * COUNT(JourneyID) / (SELECT COUNT(*) FROM dbo.customer_journey_cleaned), 2) AS ShareOfTotalTouchpointsPct
FROM dbo.customer_journey_cleaned
GROUP BY Stage
ORDER BY TouchpointCount DESC;

-- ------------------------------------------------------------------------------
-- 2. ISOLATE CRITICAL DROP-OFF STAGE (QUANTIFYING CHECKOUT FRICTION)
--    Business Finding: 96% of all abandonments occur at the Checkout stage!
-- ------------------------------------------------------------------------------
SELECT 
    Stage,
    COUNT(*) AS AbandonedCount,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS DropOffSharePct
FROM dbo.customer_journey_cleaned
WHERE Action = 'ABANDONED' OR Stage = 'DROP-OFF'
GROUP BY Stage
ORDER BY AbandonedCount DESC;

-- ------------------------------------------------------------------------------
-- 3. CONVERSION RATES & FUNNEL GAP ANALYSIS
--    - View-to-Click: 50.3%
--    - Click-to-Purchase: 19.1%
--    - Overall Conversion Rate: 9.60% (220 purchases / 2,292 impressions)
-- ------------------------------------------------------------------------------
WITH FunnelMetrics AS (
    SELECT 
        SUM(CASE WHEN Stage = 'IMPRESSIONS' THEN 1 ELSE 0 END) AS TotalImpressions,
        SUM(CASE WHEN Stage = 'CLICK' THEN 1 ELSE 0 END) AS TotalClicks,
        SUM(CASE WHEN Stage = 'CART' THEN 1 ELSE 0 END) AS TotalCartAdditions,
        SUM(CASE WHEN Stage = 'CHECKOUT' AND Action = 'PURCHASED' THEN 1 ELSE 0 END) AS TotalPurchases
    FROM dbo.customer_journey_cleaned
)
SELECT 
    TotalImpressions,
    TotalClicks,
    TotalCartAdditions,
    TotalPurchases,
    ROUND(100.0 * TotalClicks / NULLIF(TotalImpressions, 0), 2) AS View_To_Click_Pct,
    ROUND(100.0 * TotalPurchases / NULLIF(TotalClicks, 0), 2) AS Click_To_Purchase_Pct,
    ROUND(100.0 * TotalPurchases / NULLIF(TotalImpressions, 0), 2) AS Overall_Conversion_Rate_Pct
FROM FunnelMetrics;

-- ------------------------------------------------------------------------------
-- 4. CATEGORY PERFORMANCE SUMMARY (REVENUE & PURCHASE VOLUME)
-- ------------------------------------------------------------------------------
SELECT 
    p.Category,
    COUNT(DISTINCT cj.JourneyID) AS CompletedOrders,
    ROUND(SUM(p.Price), 2) AS TotalRevenue,
    ROUND(AVG(p.Price), 2) AS AverageOrderValue
FROM dbo.customer_journey_cleaned cj
INNER JOIN dbo.products p 
    ON cj.ProductID = p.ProductID
WHERE cj.Stage = 'CHECKOUT' AND cj.Action = 'PURCHASED'
GROUP BY p.Category
ORDER BY TotalRevenue DESC;

-- ------------------------------------------------------------------------------
-- 5. COMPLAINT DRIVERS ANALYSIS (FROM SENTIMENT-ENRICHED REVIEWS)
-- ------------------------------------------------------------------------------
SELECT 
    IssueCategory,
    COUNT(*) AS ComplaintCount,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS ComplaintSharePct
FROM dbo.customer_reviews_sentiment_enriched
WHERE IssueCategory <> 'None'
GROUP BY IssueCategory
ORDER BY ComplaintCount DESC;
