# visualize.py
# Generates graphs from the patent database for extra marks

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

DB_PATH    = "patents.db"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)




# ── Graph 2: Top 10 Countries Bar Chart ─────────────────────────────────────
countries = pd.read_sql("""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS total
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL
    GROUP BY i.country
    ORDER BY total DESC
    LIMIT 10
""", conn)

plt.figure(figsize=(10, 5))
sns.barplot(data=countries, x="country", y="total", palette="Blues_d")
plt.title("Top 10 Countries by Patent Count", fontsize=14)
plt.xlabel("Country")
plt.ylabel("Patents")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "top_countries.png"), dpi=150)
plt.close()
print("Saved: top_countries.png")


# ── Graph 3: Top 10 Companies ────────────────────────────────────────────────
companies = pd.read_sql("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS total
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL AND c.name != ''
    GROUP BY c.company_id, c.name
    ORDER BY total DESC
    LIMIT 10
""", conn)

plt.figure(figsize=(12, 5))
sns.barplot(data=companies, x="total", y="name", palette="Greens_d")
plt.title("Top 10 Companies by Patent Count", fontsize=14)
plt.xlabel("Patents")
plt.ylabel("Company")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "top_companies_chart.png"), dpi=150)
plt.close()
print("Saved: top_companies_chart.png")


# ── Graph 4: Patent Categories (CPC sections) ────────────────────────────────
# This requires g_cpc_current — load it separately
try:
    cpc = pd.read_csv(
        "data/g_cpc_current.tsv.zip",
        sep="\t", compression="zip",
        usecols=["patent_id", "cpc_section"],
        nrows=200000, low_memory=False, on_bad_lines="skip"
    )

    cpc_counts = cpc.groupby("cpc_section")["patent_id"].count().reset_index()
    cpc_counts.columns = ["cpc_section", "total"]
    cpc_counts = cpc_counts.sort_values("total", ascending=False).head(10)

    # CPC section labels
    labels = {
        "A": "A - Human Necessities",
        "B": "B - Operations & Transport",
        "C": "C - Chemistry",
        "D": "D - Textiles",
        "E": "E - Construction",
        "F": "F - Mechanical Engineering",
        "G": "G - Physics",
        "H": "H - Electricity",
        "Y": "Y - Emerging Tech"
    }
    cpc_counts["label"] = cpc_counts["cpc_section"].map(labels).fillna(cpc_counts["cpc_section"])

    plt.figure(figsize=(10, 6))
    plt.pie(cpc_counts["total"], labels=cpc_counts["label"],
            autopct="%1.1f%%", startangle=140, colors=sns.color_palette("Set2"))
    plt.title("Patent Distribution by Technology Category (CPC)", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "patent_categories.png"), dpi=150)
    plt.close()
    print("Saved: patent_categories.png")

except Exception as e:
    print(f"Skipped CPC chart: {e}")

conn.close()
print("\nAll charts saved to /output/")