

import pandas as pd
import os

DATA_DIR = "data"  

def load_tsv_zip(filename, usecols, nrows=3000000):
    """Helper function to load a TSV zip file with selected columns"""
    path = os.path.join(DATA_DIR, filename)
    print(f"Loading {filename}...")
    df = pd.read_csv(
        path,
        sep="\t",
        compression="zip",
        usecols=usecols,
        nrows=nrows,
        low_memory=False,
        on_bad_lines="skip"
    )
    print(f"  -> Loaded {len(df):,} rows, columns: {list(df.columns)}")
    return df


def load_patents():
    return load_tsv_zip(
        "g_patent.tsv.zip",
        usecols=["patent_id", "patent_title", "patent_date", "patent_type"]
    )

def load_abstracts():
    return load_tsv_zip(
        "g_patent_abstract.tsv.zip",
        usecols=["patent_id", "patent_abstract"]
    )

def load_inventors():
    return load_tsv_zip(
        "g_inventor_disambiguated.tsv.zip",
        usecols=["patent_id", "inventor_id", "disambig_inventor_name_first",
                 "disambig_inventor_name_last", "location_id"]
    )

def load_assignees():
    return load_tsv_zip(
        "g_assignee_disambiguated.tsv.zip",
        usecols=["patent_id", "assignee_id", "disambig_assignee_organization",
                 "disambig_assignee_individual_name_first",
                 "disambig_assignee_individual_name_last", "location_id"]
    )

def load_locations():
    return load_tsv_zip(
        "g_location_disambiguated.tsv.zip",
        usecols=["location_id", "disambig_city", "disambig_state", "disambig_country"]
    )

def load_applications():
    return load_tsv_zip(
        "g_application.tsv.zip",
        usecols=["patent_id", "filing_date"]
    )

def load_cpc():
    return load_tsv_zip(
        "g_cpc_current.tsv.zip",
        usecols=["patent_id", "cpc_section", "cpc_class", "cpc_subclass", "cpc_group"]
    )


if __name__ == "__main__":

    patents    = load_patents()
    abstracts  = load_abstracts()
    inventors  = load_inventors()
    assignees  = load_assignees()
    locations  = load_locations()
    apps       = load_applications()
    cpc        = load_cpc()

    print("\nAll files loaded successfully!")