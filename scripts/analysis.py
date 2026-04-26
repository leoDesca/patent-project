import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")
q1 = """
SELECT i.name, COUNT(r.patent_id) AS total_patents
FROM relationships r
JOIN inventors i ON r.inventor_id = i.inventor_id
GROUP BY i.name
ORDER BY total_patents DESC
LIMIT 10;
"""

top_inventors = pd.read_sql(q1, conn)
print(top_inventors)


q2 = """
SELECT country, COUNT(*) as total
FROM inventors
GROUP BY country
ORDER BY total DESC;
"""

countries = pd.read_sql(q2, conn)
print(countries)

q3 = """
SELECT year, COUNT(*) as total
FROM patents
GROUP BY year
ORDER BY year;
"""

trends = pd.read_sql(q3, conn)
print(trends)

q4 = """
SELECT p.title, i.name
FROM patents p
JOIN relationships r ON p.patent_id = r.patent_id
JOIN inventors i ON r.inventor_id = i.inventor_id
LIMIT 20;
"""

join_result = pd.read_sql(q4, conn)
print(join_result)

q5 = """
WITH inventor_counts AS (
    SELECT inventor_id, COUNT(*) AS total
    FROM relationships
    GROUP BY inventor_id
)
SELECT * FROM inventor_counts
ORDER BY total DESC;
"""

cte_result = pd.read_sql(q5, conn)
print(cte_result)

q6 = """
SELECT name, total_patents,
RANK() OVER (ORDER BY total_patents DESC) as rank
FROM (
    SELECT i.name, COUNT(r.patent_id) AS total_patents
    FROM relationships r
    JOIN inventors i ON r.inventor_id = i.inventor_id
    GROUP BY i.name
);
"""

ranking = pd.read_sql(q6, conn)
print(ranking)

conn.close()