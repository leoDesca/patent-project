

import pandas as pd
import os
from load_data import (load_patents, load_abstracts, load_inventors,
                        load_assignees, load_locations, load_applications, load_cpc)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_patents(patents_df, abstracts_df, apps_df):
    """
    Build the patents table:
      patent_id | title | abstract | filing_date | year
    """
    print("\nCleaning patents...")
 
    patents_df["patent_id"] = patents_df["patent_id"].astype(str)
    abstracts_df["patent_id"] = abstracts_df["patent_id"].astype(str)
    apps_df["patent_id"] = apps_df["patent_id"].astype(str)

    patents_df = patents_df.rename(columns={
        "patent_title": "title",
        "patent_date":  "grant_date"
    })

    
    df = patents_df.merge(abstracts_df, on="patent_id", how="left")

    
    df = df.merge(apps_df[["patent_id", "filing_date"]], on="patent_id", how="left")


    df = df.rename(columns={"patent_abstract": "abstract"})

    
    df = df.dropna(subset=["title"])

    
    df["title"] = df["title"].str.strip()

    
    df["year"] = pd.to_datetime(df["grant_date"], errors="coerce").dt.year

    # Keep only the columns we need
    df = df[["patent_id", "title", "abstract", "filing_date", "year"]].copy()


    df = df.drop_duplicates(subset="patent_id")

    print(f"  -> Clean patents: {len(df):,} rows")
    df.to_csv(os.path.join(OUTPUT_DIR, "clean_patents.csv"), index=False)
    return df


def clean_inventors(inventors_df, locations_df):
    """
    Build the inventors table:
      inventor_id | name | country
    """
    print("Cleaning inventors...")

    # Combine first and last name
    inventors_df["name"] = (
        inventors_df["disambig_inventor_name_first"].fillna("") + " " +
        inventors_df["disambig_inventor_name_last"].fillna("")
    ).str.strip()

    #location
    df = inventors_df.merge(
        locations_df[["location_id", "disambig_country"]],
        on="location_id",
        how="left"
    )
    df = df.rename(columns={"disambig_country": "country"})

    
    inventors_clean = df[["inventor_id", "name", "country"]].drop_duplicates(subset="inventor_id")
    inventors_clean = inventors_clean.dropna(subset=["inventor_id"])

    
    crosswalk = df[["patent_id", "inventor_id"]].drop_duplicates()

    print(f"  -> Unique inventors: {len(inventors_clean):,}")
    inventors_clean.to_csv(os.path.join(OUTPUT_DIR, "clean_inventors.csv"), index=False)
    return inventors_clean, crosswalk


def clean_companies(assignees_df, locations_df):
    """
    Build the companies (assignees) table:
      company_id | name
    """
    print("Cleaning companies...")

    
    assignees_df["name"] = assignees_df["disambig_assignee_organization"].fillna(
        assignees_df["disambig_assignee_individual_name_first"].fillna("") + " " +
        assignees_df["disambig_assignee_individual_name_last"].fillna("")
    ).str.strip()

    # Merge location for country
    df = assignees_df.merge(
        locations_df[["location_id", "disambig_country"]],
        on="location_id",
        how="left"
    )

    # Unique companies
    companies_clean = df[["assignee_id", "name"]].rename(
        columns={"assignee_id": "company_id"}
    ).drop_duplicates(subset="company_id")
    companies_clean = companies_clean.dropna(subset=["company_id"])

    
    crosswalk = df[["patent_id", "assignee_id"]].rename(
        columns={"assignee_id": "company_id"}
    ).drop_duplicates()

    print(f"  -> Unique companies: {len(companies_clean):,}")
    companies_clean.to_csv(os.path.join(OUTPUT_DIR, "clean_companies.csv"), index=False)
    return companies_clean, crosswalk


if __name__ == "__main__":
    
    patents_raw   = load_patents()
    abstracts_raw = load_abstracts()
    inventors_raw = load_inventors()
    assignees_raw = load_assignees()
    locations_raw = load_locations()
    apps_raw      = load_applications()

    
    patents_clean                      = clean_patents(patents_raw, abstracts_raw, apps_raw)
    inventors_clean, inventor_crosswalk = clean_inventors(inventors_raw, locations_raw)
    companies_clean, company_crosswalk  = clean_companies(assignees_raw, locations_raw)

    print("\nAll data cleaned and saved to /output!")