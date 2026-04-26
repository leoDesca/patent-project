-- queries.sql
-- All SQL queries for the patent analysis assignment

-- Q1: Top Inventors (who has the most patents?)
SELECT
    i.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 20;


-- Q2: Top Companies (which companies own the most patents?)
SELECT
    c.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
WHERE c.name IS NOT NULL AND c.name != ''
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 20;


-- Q3: Countries (which countries produce the most patents?)
SELECT
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country IS NOT NULL
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 20;


-- Q4: Trends Over Time (how many patents per year?)
SELECT
    year,
    COUNT(patent_id) AS patents_filed
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year ASC;


-- Q5: JOIN Query (combine patents with inventors and companies)
SELECT
    p.patent_id,
    p.title,
    p.year,
    i.name  AS inventor_name,
    i.country,
    c.name  AS company_name
FROM patents p
LEFT JOIN relationships r ON p.patent_id = r.patent_id
LEFT JOIN inventors i     ON r.inventor_id = i.inventor_id
LEFT JOIN companies c     ON r.company_id = c.company_id
LIMIT 100;


-- Q6: CTE Query (top companies, broken into steps)
WITH patent_counts AS (
    -- Step 1: count patents per company
    SELECT
        c.company_id,
        c.name,
        COUNT(DISTINCT r.patent_id) AS total_patents
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL AND c.name != ''
    GROUP BY c.company_id, c.name
),
ranked AS (
    -- Step 2: keep only companies with more than 5 patents
    SELECT * FROM patent_counts
    WHERE total_patents > 5
)
-- Step 3: show top 10
SELECT name, total_patents
FROM ranked
ORDER BY total_patents DESC
LIMIT 10;


-- Q7: Ranking Query (rank inventors using window functions)
SELECT
    i.name,
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count,
    RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) AS inventor_rank
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name, i.country
ORDER BY inventor_rank
LIMIT 20;