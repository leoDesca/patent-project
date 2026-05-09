
import gdown
import os

DB_PATH = "patents.db"
FILE_ID = "1jqeqVk_s34zC-5d3VZesqG5lJ9XQsbV9"

if not os.path.exists(DB_PATH):
    print("Downloading patents.db from Google Drive...")
    gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", DB_PATH, quiet=False)

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

DB_PATH = "patents.db"

st.set_page_config(page_title="Patent Intelligence", page_icon="🔬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 20px;
    }
    div[data-testid="metric-container"] label { color: #8b949e !important; font-size: 13px; }
    div[data-testid="metric-container"] div   { color: #58a6ff !important; font-size: 26px; font-weight: 700; }
    .block-title {
        font-size: 16px; font-weight: 600; color: #58a6ff;
        border-left: 4px solid #58a6ff;
        padding-left: 10px; margin: 28px 0 10px 0;
    }
    .stDataFrame { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

plt.rcParams.update({
    "figure.facecolor": "#161b22", "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d", "axes.labelcolor": "#c9d1d9",
    "xtick.color": "#8b949e", "ytick.color": "#8b949e",
    "text.color": "#c9d1d9", "grid.color": "#21262d",
    "grid.linestyle": "--", "grid.alpha": 0.5,
})
BLUE = "#58a6ff"; GREEN = "#3fb950"; RED = "#f78166"; PURPLE = "#d2a8ff"; ORANGE = "#ffa657"

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=300)
def query(sql):
    return pd.read_sql(sql, get_conn())

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 Patent Intelligence")
    st.markdown("**Data:** USPTO PatentsView")

    yr_info  = query("SELECT MIN(year) AS mn, MAX(year) AS mx FROM patents WHERE year IS NOT NULL")
    data_min = int(yr_info.iloc[0]["mn"])
    data_max = int(yr_info.iloc[0]["mx"])
    st.markdown(f"**Coverage:** {data_min} – {data_max}")
    st.markdown("---")

    top_n = st.slider("Top N results", 5, 25, 10)
    min_yr, max_yr = st.slider("Year range", data_min, data_max, (1990, data_max))
    country_filter = st.text_input("Filter inventors by country (e.g. US)", "")

# ── Page title ────────────────────────────────────────────────────────────────
st.markdown("# 🔬 Global Patent Intelligence Dashboard")
st.markdown(f"Showing data from **{min_yr}** to **{max_yr}** · Source: USPTO PatentsView ({data_min}–{data_max})")

# ── Summary metrics ───────────────────────────────────────────────────────────
total   = query("SELECT COUNT(*) AS n FROM patents").iloc[0]["n"]
num_inv = query("SELECT COUNT(*) AS n FROM inventors").iloc[0]["n"]
num_co  = query("SELECT COUNT(*) AS n FROM companies WHERE name IS NOT NULL AND name != ''").iloc[0]["n"]
num_cty = query("SELECT COUNT(DISTINCT country) AS n FROM inventors WHERE country IS NOT NULL").iloc[0]["n"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Patents",    f"{int(total):,}")
c2.metric("Unique Inventors", f"{int(num_inv):,}")
c3.metric("Unique Companies", f"{int(num_co):,}")
c4.metric("Countries",        f"{int(num_cty):,}")

# ── Patents per year ──────────────────────────────────────────────────────────
st.markdown('<div class="block-title">Patents Granted Per Year</div>', unsafe_allow_html=True)
yearly = query(f"""
    SELECT year, COUNT(patent_id) AS total FROM patents
    WHERE year BETWEEN {min_yr} AND {max_yr}
    GROUP BY year ORDER BY year
""")
fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(yearly["year"], yearly["total"], color=BLUE, linewidth=2.5)
ax.fill_between(yearly["year"], yearly["total"], alpha=0.12, color=BLUE)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlabel("Year"); ax.set_ylabel("Patents"); ax.grid(True)
st.pyplot(fig); plt.close()

# ── Year over year growth ─────────────────────────────────────────────────────
st.markdown('<div class="block-title">Year-over-Year Growth Rate (%)</div>', unsafe_allow_html=True)
yearly2 = query("""
    SELECT year, COUNT(patent_id) AS total FROM patents
    WHERE year IS NOT NULL AND year >= 1977
    GROUP BY year ORDER BY year
""")
yearly2["growth"] = yearly2["total"].pct_change() * 100
fig, ax = plt.subplots(figsize=(13, 3))
bar_colors = [GREEN if v >= 0 else RED for v in yearly2["growth"].fillna(0)]
ax.bar(yearly2["year"], yearly2["growth"].fillna(0), color=bar_colors, width=0.8, edgecolor="none")
ax.axhline(0, color="#c9d1d9", linewidth=0.8)
ax.set_xlabel("Year"); ax.set_ylabel("Growth %"); ax.grid(True, axis="y")
st.pyplot(fig); plt.close()

# ── Decade comparison ─────────────────────────────────────────────────────────
st.markdown('<div class="block-title">Total Patents by Decade</div>', unsafe_allow_html=True)
decade = query("""
    SELECT (year/10)*10 AS decade, COUNT(patent_id) AS total
    FROM patents WHERE year IS NOT NULL AND year >= 1980
    GROUP BY decade ORDER BY decade
""")
decade["label"] = decade["decade"].astype(str) + "s"
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(decade["label"], decade["total"], color=ORANGE, edgecolor="none", width=0.6)
for bar, val in zip(ax.patches, decade["total"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(decade["total"])*0.01,
            f"{int(val):,}", ha="center", fontsize=9, color="#c9d1d9")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlabel("Decade"); ax.set_ylabel("Patents"); ax.grid(True, axis="y")
st.pyplot(fig); plt.close()

# ── Top inventors + companies side by side ────────────────────────────────────
st.markdown('<div class="block-title">Top Inventors and Companies</div>', unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    country_clause = f"WHERE i.country = '{country_filter}'" if country_filter else ""
    inv = query(f"""
        SELECT i.name, i.country, COUNT(DISTINCT r.patent_id) AS patents,
               RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) AS rank
        FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
        {country_clause}
        GROUP BY i.inventor_id, i.name, i.country
        ORDER BY patents DESC LIMIT {top_n}
    """)
    st.markdown("**🥇 Top Inventors**")
    st.dataframe(inv, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh(inv["name"][::-1], inv["patents"][::-1], color=PURPLE, edgecolor="none", height=0.65)
    ax.set_xlabel("Patents"); ax.grid(True, axis="x")
    st.pyplot(fig); plt.close()

with right:
    comp = query(f"""
        SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents
        FROM companies c JOIN relationships r ON c.company_id = r.company_id
        WHERE c.name IS NOT NULL AND c.name != ''
        GROUP BY c.company_id, c.name ORDER BY patents DESC LIMIT {top_n}
    """)
    st.markdown("**🏢 Top Companies**")
    st.dataframe(comp, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh(comp["name"][::-1], comp["patents"][::-1], color=GREEN, edgecolor="none", height=0.65)
    ax.set_xlabel("Patents"); ax.grid(True, axis="x")
    st.pyplot(fig); plt.close()

# ── Countries ─────────────────────────────────────────────────────────────────
st.markdown('<div class="block-title">Top Countries by Patent Count</div>', unsafe_allow_html=True)
cntry = query(f"""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS patents,
           ROUND(COUNT(DISTINCT r.patent_id) * 100.0 / {int(total)}, 2) AS share_pct
    FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE i.country IS NOT NULL AND i.country != ''
    GROUP BY i.country ORDER BY patents DESC LIMIT {top_n}
""")
col1, col2 = st.columns([1, 1.4])
with col1:
    st.dataframe(cntry, use_container_width=True, hide_index=True)
with col2:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(cntry["country"][::-1], cntry["patents"][::-1], color=BLUE, edgecolor="none", height=0.65)
    ax.set_xlabel("Patents"); ax.grid(True, axis="x")
    st.pyplot(fig); plt.close()



# ── Patent search ─────────────────────────────────────────────────────────────
st.markdown('<div class="block-title">Search Patents by Keyword</div>', unsafe_allow_html=True)
keyword = st.text_input("Enter a keyword to search patent titles", placeholder="e.g. solar, battery, artificial intelligence")
if keyword:
    results = query(f"""
        SELECT patent_id, title, year, filing_date
        FROM patents WHERE title LIKE '%{keyword}%'
        ORDER BY year DESC LIMIT 100
    """)
    st.markdown(f"**{len(results)} results** for *{keyword}* (showing up to 100)")
    st.dataframe(results, use_container_width=True, hide_index=True)

    if not results.empty:
        yr_dist = results.groupby("year").size().reset_index(name="count")
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.bar(yr_dist["year"], yr_dist["count"], color=BLUE, edgecolor="none")
        ax.set_xlabel("Year"); ax.set_ylabel("Results"); ax.grid(True, axis="y")
        ax.set_title(f'"{keyword}" results by year')
        st.pyplot(fig); plt.close()