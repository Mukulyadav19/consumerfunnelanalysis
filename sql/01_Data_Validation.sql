-- ==============================================================================
-- File: 01_Data_Validation.sql
-- Description: Diagnostic data profiling and quality verification queries
-- Database Flavor: Microsoft SQL Server (T-SQL)
-- ==============================================================================

USE shopeasy;
GO

-- 1. Table Row Counts and Critical Column NULL Audits
SELECT 
    'customer_journey_raw' AS TableName, 
    COUNT(*) AS TotalRows, 
    SUM(CASE WHEN Duration IS NULL THEN 1 ELSE 0 END) AS NullDurationCount,
    SUM(CASE WHEN Stage IS NULL THEN 1 ELSE 0 END) AS NullStageCount
FROM customer_journey_raw
UNION ALL
SELECT 
    'engagement_data_raw', 
    COUNT(*), 
    SUM(CASE WHEN ViewsClicksCombined IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN ContentType IS NULL THEN 1 ELSE 0 END)
FROM engagement_data_raw
UNION ALL
SELECT 
    'customer_reviews_raw', 
    COUNT(*), 
    SUM(CASE WHEN ReviewText IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN Rating IS NULL THEN 1 ELSE 0 END)
FROM customer_reviews_raw
UNION ALL
SELECT 'customers', COUNT(*), SUM(CASE WHEN CustomerID IS NULL THEN 1 ELSE 0 END), 0 FROM customers
UNION ALL
SELECT 'products', COUNT(*), SUM(CASE WHEN ProductID IS NULL THEN 1 ELSE 0 END), 0 FROM products
UNION ALL
SELECT 'geography', COUNT(*), SUM(CASE WHEN GeographyID IS NULL THEN 1 ELSE 0 END), 0 FROM geography;

-- 2. Detect Inconsistent Casing & Unstandardized Stage/Action Enums
SELECT 
    Stage, 
    Action, 
    COUNT(*) AS Frequency
FROM customer_journey_raw
GROUP BY Stage, Action
ORDER BY Frequency DESC;

SELECT 
    ContentType, 
    COUNT(*) AS Frequency
FROM engagement_data_raw
GROUP BY ContentType;

-- 3. Detect Logical Duplicates in Customer Journey
-- (Flagging re-transmissions on double-clicks with identical user, product, timestamp, stage, and action)
WITH DuplicateCheck AS (
    SELECT 
        JourneyID, CustomerID, ProductID, VisitDate, Stage, Action,
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, ProductID, VisitDate, UPPER(TRIM(Stage)), UPPER(TRIM(Action))
            ORDER BY JourneyID
        ) AS RowNum
    FROM customer_journey_raw
)
SELECT 
    COUNT(*) AS LogicalDuplicatesCount
FROM DuplicateCheck
WHERE RowNum > 1;

-- 4. Audit Combined Metric Format in Engagement Data
-- (Verify that string contains exactly one hyphen delimiter between Views and Clicks)
SELECT 
    ContentID,
    ViewsClicksCombined,
    CHARINDEX('-', ViewsClicksCombined) AS DelimiterPosition
FROM engagement_data_raw
WHERE CHARINDEX('-', ViewsClicksCombined) = 0;

-- 5. Audit Review Text Formatting for Leading/Trailing and Multiple Internal Spaces
SELECT 
    ReviewID, 
    ReviewText 
FROM customer_reviews_raw 
WHERE ReviewText LIKE ' %' 
   OR ReviewText LIKE '% ' 
   OR ReviewText LIKE '%  %';
