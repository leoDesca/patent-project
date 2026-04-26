# store_data.py
# Purpose: Create a SQLite database and load clean data into it

import sqlite3
import pandas as pd
import os
from load_data import (load_patents, load_abstracts, load_inventors,
                        load_assignees, load_locations, load_applications)
from clean_data import clean_patents, clean_inventors, clean_companies

DB_PATH = "patents.db"
OUTPUT_DIR = "output"


def build_database():
    print("Building database...")

    # Load and clean data
    patents_raw    = load_patents()
    abstracts_raw  = load_abstracts()
    inventors_raw  = load_inventors()
    assignees_raw  = load_assignees()
    locations_raw  = load_locations()
    apps_raw       = load_applications()

    patents_clean                       = clean_patents(patents_raw, abstracts_raw, apps_raw)
    inventors_clean, inventor_crosswalk = clean_inventors(inventors_raw, locations_raw)
    companies_clean, company_crosswalk  = clean_companies(assignees_raw, locations_raw)

    # Build relationships table
    relationships = inventor_crosswalk.merge(company_crosswalk, on="patent_id", how="outer")

    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop tables if they exist (so we can re-run cleanly)
    cursor.executescript("""
        DROP TABLE IF EXISTS relationships;
        DROP TABLE IF EXISTS inventors;
        DROP TABLE IF EXISTS companies;
        DROP TABLE IF EXISTS patents;
    """)

    # Create tables
    cursor.executescript("""
        CREATE TABLE patents (
            patent_id   TEXT PRIMARY KEY,
            title       TEXT,
            abstract    TEXT,
            filing_date TEXT,
            year        INTEGER
        );

        CREATE TABLE inventors (
            inventor_id TEXT PRIMARY KEY,
            name        TEXT,
            country     TEXT
        );

        CREATE TABLE companies (
            company_id  TEXT PRIMARY KEY,
            name        TEXT
        );

        CREATE TABLE relationships (
            patent_id   TEXT,
            inventor_id TEXT,
            company_id  TEXT
        );
    """)

    conn.commit()

    # Load data into tables
    patents_clean.to_sql("patents",       conn, if_exists="append", index=False)
    inventors_clean.to_sql("inventors",   conn, if_exists="append", index=False)
    companies_clean.to_sql("companies",   conn, if_exists="append", index=False)
    relationships.to_sql("relationships", conn, if_exists="append", index=False)

    conn.close()
    print(f"\nDatabase saved to {DB_PATH}")
    print(f"  Patents:       {len(patents_clean):,}")
    print(f"  Inventors:     {len(inventors_clean):,}")
    print(f"  Companies:     {len(companies_clean):,}")
    print(f"  Relationships: {len(relationships):,}")


if __name__ == "__main__":
    build_database()