

import sqlite3
import pandas as pd
import json
import os

DB_PATH    = "patents.db"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)


#Run all queries 

total_patents = pd.read_sql("SELECT COUNT(*) AS n FROM patents", conn).iloc[0]["n"]

top_inventors = pd.read_sql("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)

top_companies = pd.read_sql("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL AND c.name != ''
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)

top_countries = pd.read_sql("""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL
    GROUP BY i.country
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)

yearly_trends = pd.read_sql("""
    SELECT year, COUNT(patent_id) AS patents_filed
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year ASC
""", conn)

ranked_inventors = pd.read_sql("""
    SELECT
        i.name,
        i.country,
        COUNT(DISTINCT r.patent_id) AS patent_count,
        RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) AS inventor_rank
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name, i.country
    ORDER BY inventor_rank
    LIMIT 20
""", conn)

conn.close()


# Console Report 

print("=" * 55)
print("           GLOBAL PATENT INTELLIGENCE REPORT")
print("=" * 55)

print(f"\nTotal Patents in Database: {int(total_patents):,}\n")

print("TOP 10 INVENTORS")
print("-" * 40)
for i, row in top_inventors.iterrows():
    print(f"  {i+1}. {row['name']} — {int(row['patent_count'])} patents")

print("\nTOP 10 COMPANIES")
print("-" * 40)
for i, row in top_companies.iterrows():
    print(f"  {i+1}. {row['name']} — {int(row['patent_count'])} patents")

print("\nTOP 10 COUNTRIES")
print("-" * 40)
for i, row in top_countries.iterrows():
    print(f"  {i+1}. {row['country']} — {int(row['patent_count'])} patents")

print("\nPATENTS BY YEAR (last 10 years shown)")
print("-" * 40)
for _, row in yearly_trends.tail(10).iterrows():
    print(f"  {int(row['year'])}: {int(row['patents_filed']):,} patents")

print("\nINVENTOR RANKINGS (Window Function)")
print("-" * 40)
for _, row in ranked_inventors.head(10).iterrows():
    print(f"  Rank {int(row['inventor_rank'])}: {row['name']} ({row['country']}) — {int(row['patent_count'])} patents")

print("\n" + "=" * 55)


# CSV Exports

top_inventors.to_csv(os.path.join(OUTPUT_DIR, "top_inventors.csv"), index=False)
top_companies.to_csv(os.path.join(OUTPUT_DIR, "top_companies.csv"), index=False)
top_countries.to_csv(os.path.join(OUTPUT_DIR, "country_trends.csv"), index=False)
yearly_trends.to_csv(os.path.join(OUTPUT_DIR, "yearly_trends.csv"), index=False)

print("\nCSV files saved to /output/")


#JSON Report

report = {
    "total_patents": int(total_patents),
    "top_inventors": [
        {"rank": i+1, "name": row["name"], "patents": int(row["patent_count"])}
        for i, row in top_inventors.iterrows()
    ],
    "top_companies": [
        {"rank": i+1, "name": row["name"], "patents": int(row["patent_count"])}
        for i, row in top_companies.iterrows()
    ],
    "top_countries": [
        {
            "country": row["country"],
            "patents": int(row["patent_count"]),
            "share": round(int(row["patent_count"]) / int(total_patents), 4)
        }
        for _, row in top_countries.iterrows()
    ],
    "patents_by_year": [
        {"year": int(row["year"]), "patents": int(row["patents_filed"])}
        for _, row in yearly_trends.iterrows()
    ]
}

with open(os.path.join(OUTPUT_DIR, "report.json"), "w") as f:
    json.dump(report, f, indent=2)

print("JSON report saved to /output/report.json")
print("\nDone!")