# Global Patent Intelligence Data Pipeline

This project builds a data pipeline on top of real USPTO patent data from PatentsView.
The idea was to work like a data engineer — pulling in raw bulk files, cleaning them,
storing them in a database, running queries, and producing reports and charts.

---

## What the project does

The pipeline reads large TSV zip files from the USPTO PatentsView bulk download,
cleans the data using pandas, stores everything in a SQLite database, runs seven
SQL queries against it, and produces a console report, CSV files, a JSON summary,
seven charts, and an interactive Streamlit dashboard.

---

## Project structure

- data/ — where the raw zip files go (not uploaded to GitHub, too large)
- scripts/load_data.py — reads the zip files into pandas DataFrames
- scripts/clean_data.py — fixes missing values, renames columns, saves clean CSVs
- scripts/store_data.py — builds the SQLite database with four tables
- scripts/check_db.py — prints all tables and columns so you can verify the schema
- scripts/schema.sql — the CREATE TABLE statements for the database
- scripts/queries.sql — all seven required SQL queries
- scripts/report.py — generates the console report, CSV exports, and JSON file
- scripts/visualize.py — generates seven charts saved as PNG files
- scripts/dashboard.py — interactive Streamlit dashboard
- output/ — all generated files end up here after running the scripts
- requirements.txt — Python libraries needed to run the project
- README.md — this file

---

## How to run this project

First, clone the repo and install the dependencies:

```bash
git clone https://github.com/leoDesca/patent-project.git
cd patent-project
pip install -r requirements.txt
```

Then download the following seven zip files from the USPTO PatentsView bulk download
at https://data.uspto.gov/bulkdata/datasets/pvgpatdis and place them inside the data/ folder:

- g_patent.tsv.zip
- g_patent_abstract.tsv.zip
- g_inventor_disambiguated.tsv.zip
- g_assignee_disambiguated.tsv.zip
- g_location_disambiguated.tsv.zip
- g_application.tsv.zip
- g_cpc_current.tsv.zip

These files are not included in the repository because they are several hundred MB each
and exceed GitHub's file size limits. See the limitations section for more on this.

Once the files are in place, run the scripts in this order:

```bash
python scripts/load_data.py
python scripts/clean_data.py
python scripts/store_data.py
python scripts/report.py
python scripts/visualize.py
streamlit run scripts/dashboard.py
```

To verify the database tables and columns match the assignment schema:

```bash
python scripts/check_db.py
```

---

## Database

The SQLite database file is called patents.db and gets created in the project root
when you run store_data.py. It contains four tables.

The patents table stores patent_id, title, abstract, filing_date, and year.

The inventors table stores inventor_id, name, and country.

The companies table stores company_id and name.

The relationships table links everything together using patent_id, inventor_id,
and company_id as a bridge between the three main tables.

---

## SQL queries

All seven queries are written in scripts/queries.sql. They cover the top inventors
by patent count, top companies by patent count, countries producing the most patents,
patents grouped by year, a JOIN across all four tables, a CTE query that breaks a
company ranking into named steps, and a window function query that ranks inventors
using RANK().

---

## Output files

After running the full pipeline the output/ folder will contain the following:

- clean_patents.csv, clean_inventors.csv, clean_companies.csv — the cleaned data tables
- top_inventors.csv, top_companies.csv, country_trends.csv, yearly_trends.csv — query results
- report.json — a full JSON summary of the analysis
- seven PNG chart files from visualize.py

---

## Data source

The data comes from the PatentsView Granted Patent Disambiguated dataset published
by the USPTO. It covers granted US patents from 1976 through September 2025.
PatentsView uses machine learning to resolve inventor and assignee identities across
millions of records. The dataset is published under CC BY 4.0.

---

## Limitations and challenges

The biggest issue encountered was GitHub rejecting the push because of file sizes.
The patents.db file came out at 103 MB and clean_patents.csv was 73 MB, both over
GitHub's 100 MB hard limit. The push failed with error GH001 even after using
git rm --cached to stop tracking them. The files had already been committed to history
in an earlier commit, so removing them required rewriting the entire commit history
using git filter-branch and then doing a force push. The .gitignore file was added
afterwards to make sure they would never be committed again. This is why the database
and large CSVs are not in the repository — they get generated locally when you run
the scripts.

Another issue was that the column names in the PatentsView files changed after a
major revision in October 2022. The older documentation showed column names like
title and date but the actual files use patent_title and patent_date. This caused
a ValueError about missing columns early on, which was fixed by checking the actual
column names from the data dictionary PDF on the USPTO website.

Loading files with several million rows each was slow and caused memory pressure on
a standard laptop. The nrows parameter in pandas read_csv was set to 3 million as a
balance between loading enough data to be meaningful and not running out of memory
or waiting too long.

The raw data also had inconsistencies typical of real-world datasets — some patents
had no abstract, some inventors had no country, and some assignee entries were blank
or used individual names instead of organisation names. The cleaning script handles
these cases by merging name fields and filling missing values.

---

## Extra features

dark-themed charts are generated by visualize.py covering annual patent volume,
top countries, top companies, technology categories by CPC section, decade comparison,
top inventors, and year-over-year growth rate.

The Streamlit dashboard is a single-page layout showing all analysis and charts together
with sidebar filters for year range, top N results, and country. It also includes a
patent keyword search at the bottom.

## Deployment

The dashboard is deployed on Streamlit Community Cloud at:
https://nwqz6xd96sp5zxsmycdqre.streamlit.app/#global-patent-intelligence-dashboard

To redeploy or update it, push any change to the main branch on GitHub and
Streamlit Cloud will automatically detect it and reboot the app.

The database file is hosted on Google Drive and downloaded automatically by the
dashboard on first startup using gdown. This was necessary because the file
exceeds GitHub's size limits and cannot be stored in the repository.

To deploy your own copy:
- Fork the repository on GitHub
- Upload patents.db to Google Drive and set sharing to anyone with the link
- Copy the file ID from the share URL and paste it into the FILE_ID variable
  at the top of scripts/dashboard.py
- Go to share.streamlit.io, connect your GitHub account, select the repository,
  set the main file path to scripts/dashboard.py, and click Deploy

---

## Author

Namitto Maria Leodesca 23/U/14617/PS
GitHub: https://github.com/leoDesca/patent-project
Dashbord link:https://nwqz6xd96sp5zxsmycdqre.streamlit.app/#global-patent-intelligence-dashboard