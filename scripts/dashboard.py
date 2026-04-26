# dashboard.py
# Simple interactive dashboard — run with: streamlit run scripts/dashboard.py

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = "patents.db"

st.set_page_config(page_title="Patent Intelligence Dashboard", layout="wide")
st.title("🔬 Global Patent Intelligence Dashboard")
st.markdown("Built from PatentsView USPTO data — a data pipeline project")

conn = sqlite3.connect(DB_PATH)

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")
top_n = st.sidebar.slider("Number of top results to show", 5, 20, 10)
min_year, max_year = st.sidebar.slider("Year range", 1990, 2025, (2000, 2025))

# ── Summary metrics ──────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
total = pd.read_sql("SELECT COUNT(*) AS n FROM patents", conn).iloc[0]["n"]
num_inv = pd.read_sql("SELECT COUNT(*) AS n FROM inventors", conn).iloc[0]["n"]
num_comp = pd.read_sql("SELECT COUNT(*) AS n FROM companies", conn).iloc[0]["n"]

col1.metric("Total Patents", f"{int(total):,}")
col2.metric("Unique Inventors", f"{int(num_inv):,}")
col3.metric("Unique Companies", f"{int(num_comp):,}")

# ...existing code...

# ── Top 10 Companies ────────────────────────────────────────────────────────
st.subheader("🏢 Top 10 Companies")

companies = pd.read_sql("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS total
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    WHERE c.name IS NOT NULL AND c.name != ''
    GROUP BY c.company_id, c.name
    ORDER BY total DESC
    LIMIT 10
""", conn)

fig3, ax3 = plt.subplots(figsize=(12, 5))
sns.barplot(data=companies, x="total", y="name", palette="Greens_d", ax=ax3)
ax3.set_title("Top 10 Companies by Patent Count", fontsize=14)
ax3.set_xlabel("Patents")
ax3.set_ylabel("Company")
st.pyplot(fig3)


# ── Top Inventors and Companies side by side ─────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("🥇 Top Inventors")
    inv = pd.read_sql(f"""
        SELECT i.name, COUNT(DISTINCT r.patent_id) AS patents
        FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name ORDER BY patents DESC LIMIT {top_n}
    """, conn)
    st.dataframe(inv, use_container_width=True)

with right:
    st.subheader("🏢 Top Companies")
    comp = pd.read_sql(f"""
        SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents
        FROM companies c JOIN relationships r ON c.company_id = r.company_id
        WHERE c.name IS NOT NULL AND c.name != ''
        GROUP BY c.company_id, c.name ORDER BY patents DESC LIMIT {top_n}
    """, conn)
    st.dataframe(comp, use_container_width=True)

# ── Top Countries ─────────────────────────────────────────────────────────────
st.subheader("🌍 Top Countries")
countries = pd.read_sql(f"""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS patents
    FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL
    GROUP BY i.country ORDER BY patents DESC LIMIT {top_n}
""", conn)

fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.barplot(data=countries, x="country", y="patents", palette="Blues_d", ax=ax2)
ax2.set_xlabel("Country"); ax2.set_ylabel("Patents")
st.pyplot(fig2)

# ── Raw data explorer ─────────────────────────────────────────────────────────
st.subheader("🔎 Search Patents")
search = st.text_input("Search by title keyword")
if search:
    results = pd.read_sql(f"""
        SELECT patent_id, title, year, filing_date
        FROM patents
        WHERE title LIKE '%{search}%'
        LIMIT 50
    """, conn)
    st.dataframe(results, use_container_width=True)

conn.close()