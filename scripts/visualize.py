

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

DB_PATH    = "patents.db"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global style
plt.rcParams.update({
    "figure.facecolor":  "#0f1117",
    "axes.facecolor":    "#1a1d27",
    "axes.edgecolor":    "#3a3d4d",
    "axes.labelcolor":   "#c9d1d9",
    "xtick.color":       "#c9d1d9",
    "ytick.color":       "#c9d1d9",
    "text.color":        "#c9d1d9",
    "grid.color":        "#2d2f3e",
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "font.family":       "DejaVu Sans",
})

ACCENT   = "#58a6ff"
ACCENT2  = "#3fb950"
ACCENT3  = "#f78166"
ACCENT4  = "#d2a8ff"

conn = sqlite3.connect(DB_PATH)
print("Connected to database. Generating charts...\n")


# Chart 1: Patents Per Year (line + shaded area)
print("1/7 Patents per year...")
yearly = pd.read_sql("""
    SELECT year, COUNT(patent_id) AS total
    FROM patents
    WHERE year IS NOT NULL AND year >= 1976
    GROUP BY year ORDER BY year
""", conn)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(yearly["year"], yearly["total"], color=ACCENT, linewidth=2.5, zorder=3)
ax.fill_between(yearly["year"], yearly["total"], alpha=0.15, color=ACCENT)
ax.set_title("US Patent Grants Per Year (1976 – Present)", fontsize=14, pad=15, color="white")
ax.set_xlabel("Year"); ax.set_ylabel("Patents Granted")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(True)
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "patents_per_year.png"), dpi=150, bbox_inches="tight")
plt.close()


# Chart 2: Top 15 Countries (horizontal bar) 
print("2/7 Top countries...")
countries = pd.read_sql("""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS total
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL AND i.country != ''
    GROUP BY i.country ORDER BY total DESC LIMIT 15
""", conn)

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(countries["country"][::-1], countries["total"][::-1],
               color=ACCENT, edgecolor="none", height=0.65)
for bar, val in zip(bars, countries["total"][::-1]):
    ax.text(bar.get_width() + max(countries["total"]) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(val):,}", va="center", fontsize=9, color="#c9d1d9")
ax.set_title("Top 15 Countries by Patent Count", fontsize=14, pad=15, color="white")
ax.set_xlabel("Number of Patents")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(True, axis="x")
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "top_countries.png"), dpi=150, bbox_inches="tight")
plt.close()


# Chart 3: Top 15 Companies (horizontal bar)
print("3/7 Top companies...")
companies = pd.read_sql("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS total
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL AND c.name != ''
    GROUP BY c.company_id, c.name ORDER BY total DESC LIMIT 15
""", conn)

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(companies["name"][::-1], companies["total"][::-1],
               color=ACCENT2, edgecolor="none", height=0.65)
for bar, val in zip(bars, companies["total"][::-1]):
    ax.text(bar.get_width() + max(companies["total"]) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(val):,}", va="center", fontsize=9, color="#c9d1d9")
ax.set_title("Top 15 Companies by Patent Count", fontsize=14, pad=15, color="white")
ax.set_xlabel("Number of Patents")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(True, axis="x")
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "top_companies_chart.png"), dpi=150, bbox_inches="tight")
plt.close()


# Chart 4: CPC Technology Categories (donut chart)
print("4/7 Patent categories...")
try:
    cpc = pd.read_csv(
        "data/g_cpc_current.tsv.zip",
        sep="\t", compression="zip",
        usecols=["patent_id", "cpc_section"],
        nrows=3000000, low_memory=False, on_bad_lines="skip"
    )
    cpc_counts = (cpc.groupby("cpc_section")["patent_id"]
                     .count().reset_index()
                     .rename(columns={"patent_id": "total"})
                     .sort_values("total", ascending=False))

    labels = {
        "A": "A · Human Necessities",
        "B": "B · Operations & Transport",
        "C": "C · Chemistry",
        "D": "D · Textiles",
        "E": "E · Construction",
        "F": "F · Mechanical Engineering",
        "G": "G · Physics",
        "H": "H · Electricity",
        "Y": "Y · Emerging Tech"
    }
    cpc_counts["label"] = cpc_counts["cpc_section"].map(labels).fillna(cpc_counts["cpc_section"])

    colors = [ACCENT, ACCENT2, ACCENT3, ACCENT4, "#ffa657", "#79c0ff",
              "#56d364", "#ff7b72", "#e3b341"]
    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts, autotexts = ax.pie(
        cpc_counts["total"], labels=cpc_counts["label"],
        autopct="%1.1f%%", startangle=140,
        colors=colors[:len(cpc_counts)],
        pctdistance=0.78, wedgeprops=dict(width=0.55)
    )
    for t in texts:   t.set_color("#c9d1d9")
    for t in autotexts: t.set_color("white"); t.set_fontsize(8)
    ax.set_title("Patent Distribution by Technology Category (CPC)",
                 fontsize=13, pad=20, color="white")
    fig.savefig(os.path.join(OUTPUT_DIR, "patent_categories.png"),
                dpi=150, bbox_inches="tight", facecolor="#0f1117")
    plt.close()
    print("   CPC chart saved.")
except Exception as e:
    print(f"   Skipped CPC chart: {e}")


# Chart 5: Patent growth decade by decade (grouped bar) 
print("5/7 Decade comparison...")
decade = pd.read_sql("""
    SELECT
        (year / 10) * 10 AS decade,
        COUNT(patent_id) AS total
    FROM patents
    WHERE year IS NOT NULL AND year >= 1980
    GROUP BY decade ORDER BY decade
""", conn)
decade["label"] = decade["decade"].astype(str) + "s"

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(decade["label"], decade["total"], color=ACCENT3, edgecolor="none", width=0.6)
for bar, val in zip(bars, decade["total"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(decade["total"]) * 0.01,
            f"{int(val):,}", ha="center", fontsize=9, color="#c9d1d9")
ax.set_title("Total Patents Granted by Decade", fontsize=14, pad=15, color="white")
ax.set_xlabel("Decade"); ax.set_ylabel("Patents Granted")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(True, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "patents_by_decade.png"), dpi=150, bbox_inches="tight")
plt.close()


# Chart 6: Top 10 inventors bar chart
print("6/7 Top inventors...")
inventors = pd.read_sql("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS total
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name ORDER BY total DESC LIMIT 10
""", conn)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(inventors["name"][::-1], inventors["total"][::-1],
               color=ACCENT4, edgecolor="none", height=0.65)
for bar, val in zip(bars, inventors["total"][::-1]):
    ax.text(bar.get_width() + max(inventors["total"]) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            str(int(val)), va="center", fontsize=9, color="#c9d1d9")
ax.set_title("Top 10 Inventors by Patent Count", fontsize=14, pad=15, color="white")
ax.set_xlabel("Number of Patents")
ax.grid(True, axis="x")
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "top_inventors_chart.png"), dpi=150, bbox_inches="tight")
plt.close()


# Chart 7: Year-over-year growth rate 
print("7/7 Growth rate...")
yearly2 = pd.read_sql("""
    SELECT year, COUNT(patent_id) AS total
    FROM patents WHERE year IS NOT NULL AND year >= 1977
    GROUP BY year ORDER BY year
""", conn)
yearly2["growth"] = yearly2["total"].pct_change() * 100

fig, ax = plt.subplots(figsize=(14, 5))
colors_bar = [ACCENT2 if v >= 0 else ACCENT3 for v in yearly2["growth"].fillna(0)]
ax.bar(yearly2["year"], yearly2["growth"].fillna(0), color=colors_bar, edgecolor="none", width=0.8)
ax.axhline(0, color="#c9d1d9", linewidth=0.8, linestyle="--")
ax.set_title("Year-over-Year Patent Growth Rate (%)", fontsize=14, pad=15, color="white")
ax.set_xlabel("Year"); ax.set_ylabel("Growth Rate (%)")
ax.grid(True, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "patent_growth_rate.png"), dpi=150, bbox_inches="tight")
plt.close()

conn.close()
print("\nAll 7 charts saved to /output/")
