-- ==============================================================================
-- File: 02_Cleaning_Transformation.sql
-- Description: Production data cleaning & transformation pipeline
-- Database Flavor: Microsoft SQL Server (T-SQL)
-- ==============================================================================

USE shopeasy;
GO

-- ------------------------------------------------------------------------------
-- 1. CLEAN customer_journey
--    - Standardize casing to UPPER
--    - Strip whitespace
--    - Deduplicate re-transmitted web clicks using ROW_NUMBER() window function
-- ------------------------------------------------------------------------------
IF OBJECT_ID('dbo.customer_journey_cleaned', 'U') IS NOT NULL 
    DROP TABLE dbo.customer_journey_cleaned;
GO

WITH DeduplicationCTE AS (
    SELECT 
        JourneyID,
        CustomerID,
        ProductID,
        CAST(VisitDate AS DATE) AS VisitDate,
        UPPER(TRIM(Stage)) AS Stage,
        UPPER(TRIM(Action)) AS Action,
        Duration,
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, ProductID, VisitDate, UPPER(TRIM(Stage)), UPPER(TRIM(Action))
            ORDER BY JourneyID
        ) AS RowNum
    FROM customer_journey_raw
)
SELECT 
    ROW_NUMBER() OVER(ORDER BY VisitDate, JourneyID) AS JourneyID,
    CustomerID,
    ProductID,
    VisitDate,
    Stage,
    Action,
    Duration
INTO dbo.customer_journey_cleaned
FROM DeduplicationCTE
WHERE RowNum = 1;
GO

-- ------------------------------------------------------------------------------
-- 2. CLEAN engagement_data
--    - Split ViewsClicksCombined (e.g. "45000-9000") into separate Views and Clicks
--    - Robust splitting using SUBSTRING and CHARINDEX (defensible in interviews)
--    - Standardize ContentType casing
-- ------------------------------------------------------------------------------
IF OBJECT_ID('dbo.engagement_data_cleaned', 'U') IS NOT NULL 
    DROP TABLE dbo.engagement_data_cleaned;
GO

SELECT 
    ContentID,
    UPPER(TRIM(ContentType)) AS ContentType,
    Campaign,
    CAST(SUBSTRING(ViewsClicksCombined, 1, CHARINDEX('-', ViewsClicksCombined) - 1) AS INT) AS Views,
    CAST(SUBSTRING(ViewsClicksCombined, CHARINDEX('-', ViewsClicksCombined) + 1, LEN(ViewsClicksCombined)) AS INT) AS Clicks,
    Likes,
    CAST(Date AS DATE) AS Date
INTO dbo.engagement_data_cleaned
FROM engagement_data_raw;
GO

-- ------------------------------------------------------------------------------
-- 3. CLEAN customer_reviews
--    - Multi-pass nested REPLACE to remove double & triple internal whitespace
--    - Trim outer leading and trailing spaces
-- ------------------------------------------------------------------------------
IF OBJECT_ID('dbo.customer_reviews_cleaned', 'U') IS NOT NULL 
    DROP TABLE dbo.customer_reviews_cleaned;
GO

SELECT 
    ReviewID,
    CustomerID,
    ProductID,
    CAST(ReviewDate AS DATE) AS ReviewDate,
    Rating,
    TRIM(REPLACE(REPLACE(ReviewText, '   ', ' '), '  ', ' ')) AS ReviewText
INTO dbo.customer_reviews_cleaned
FROM customer_reviews_raw;
GO
