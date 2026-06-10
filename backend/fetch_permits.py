"""Fetch BPS building-permit data from the Census Bureau and write the two
"master" CSVs the dashboard pipeline consumes.

This is the in-repo replacement for the building-permit half of the external
`Monthly Data Pull/data_pull.py`. It pulls from public Census endpoints (no API
key required), so it runs unattended in GitHub Actions.

Outputs (relative to the repo root):
  Data/raw/BPS_GA.csv         - rolling 18-month monthly master
  Data/raw/BPS_GA_annual.csv  - rolling 3-year benchmarked annual master

Run `python backend/fetch_permits.py`, then `python backend/backend_query.py`
to rebuild the four dashboard CSVs in Data/.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Resolve output paths relative to this file so the script works from any cwd.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(REPO_ROOT, 'Data', 'raw')
MONTHLY_MASTER = os.path.join(RAW_DIR, 'BPS_GA.csv')
ANNUAL_MASTER = os.path.join(RAW_DIR, 'BPS_GA_annual.csv')


# Building permits -$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$-$
def get_relevant_months():
    months_back = 18
    today = datetime.today()

    # Determine the most recent available data month
    if today.day > 27:  # After the 27th, last month's data is available
        most_recent = today.replace(day=1) - timedelta(days=1)  # last month
    else:  # On or before the 27th, the latest data is two months ago
        most_recent = today.replace(day=1) - timedelta(days=1)
        most_recent = most_recent.replace(
            day=1) - timedelta(days=1)  # two months ago

    # Generate the past x-number of months as 4-digit strings
    months = [(most_recent - relativedelta(months=i)).strftime('%y%m')
              for i in range(months_back)]

    return months


# Helper function to convert 'yymm' month code to readable label (e.g., '2602' -> 'February 2026')
def month_code_to_label(code):
    year = 2000 + int(code[:2])
    month = int(code[2:])
    return datetime(year, month, 1).strftime('%B %Y')


# Helper function to convert 'year_month' code to formatted date string for line charts
def code_to_date(code):
    # Ensure code is a string, then extract year and month parts
    code = str(code)
    year = int(code[:4])
    month = int(code[4:])

    # Create a datetime object and format to "Abbr Month Full Year" (e.g., "Sept 2024")
    return datetime(year, month, 1).strftime('%b %Y')


# Function to load and process county data
def load_county_data(url):
    df = pd.read_csv(url, skiprows=1)
    df = df.rename(columns={
        'Date': 'year_month',
        'Units': 'SF_permits',
        'Value': 'SF_value',
        'Units.1': '2U_permits',
        'Value.1': '2U_value',
        'Units.2': '3-4U_permits',
        'Value.2': '3-4U_value',
        'Units.3': '5+U_permits',
        'Value.3': '5+U_value',
    })

    # Create FIPS and county_name columns
    df['FIPS'] = df['State'].astype(str).str.zfill(
        2) + df['County'].astype(str).str.zfill(3)
    df['Name'] = df['Name'].str.replace(' County', '')

    # Apply code_to_date function to year_month and add as date column
    df['date'] = df['year_month'].apply(code_to_date)

    df['Level'] = 'County'
    df['MF_permits'] = df['2U_permits'] + \
        df['3-4U_permits'] + df['5+U_permits']
    df['MF_value'] = df['2U_value'] + \
        df['3-4U_value'] + df['5+U_value']

    # Filter and rearrange columns
    df = df[df['FIPS'].astype(str).str.startswith('13')]
    df = df[[
        'year_month',
        'date',
        'Level',
        'Name',
        'SF_permits',
        'SF_value',
        'MF_permits',
        'MF_value',
        '2U_permits',
        '2U_value',
        '3-4U_permits',
        '3-4U_value',
        '5+U_permits',
        '5+U_value'
    ]]

    return df


# Function to load and process place (i.e., city) data
def load_place_data(url):
    df = pd.read_csv(url, skiprows=1)
    df = df.rename(columns={
        'Date': 'year_month',
        'Code': 'State',
        'Code.1': 'County',
        'Units': 'SF_permits',
        'Value': 'SF_value',
        'Units.1': '2U_permits',
        'Value.1': '2U_value',
        'Units.2': '3-4U_permits',
        'Value.2': '3-4U_value',
        'Units.3': '5+U_permits',
        'Value.3': '5+U_value'
    })

    # Create FIPS column and filter on it
    df['FIPS'] = df['State'].astype(str).str.zfill(
        2) + df['County'].astype(str).str.zfill(3)
    df = df[df['FIPS'].astype(str).str.startswith('13')]

    # Remove instances of "town" if it exists
    df['Name'] = df['Name'].str.replace(' town', '')

    # Apply code_to_date function to year_month and add as date column
    df['date'] = df['year_month'].apply(code_to_date)

    df['Level'] = 'City/Other'
    df['MF_permits'] = df['2U_permits'] + \
        df['3-4U_permits'] + df['5+U_permits']
    df['MF_value'] = df['2U_value'] + \
        df['3-4U_value'] + df['5+U_value']

    # Select and arrange columns
    df = df[[
        'year_month',
        'date',
        'Level',
        'Name',
        'SF_permits',
        'SF_value',
        'MF_permits',
        'MF_value',
        '2U_permits',
        '2U_value',
        '3-4U_permits',
        '3-4U_value',
        '5+U_permits',
        '5+U_value'
    ]]

    return df


# Function to load and process annual county data
def load_county_annual(url, year):
    df = pd.read_csv(url, skiprows=1)
    df = df.rename(columns={
        'Date': 'Year',
        'Units': 'SF_permits',
        'Value': 'SF_value',
        'Units.1': '2U_permits',
        'Value.1': '2U_value',
        'Units.2': '3-4U_permits',
        'Value.2': '3-4U_value',
        'Units.3': '5+U_permits',
        'Value.3': '5+U_value',
    })
    df['FIPS'] = df['State'].astype(str).str.zfill(2) + df['County'].astype(str).str.zfill(3)
    df = df[df['FIPS'].str.startswith('13')]
    df['Name'] = df['Name'].str.strip().str.replace(' County', '')
    df['Level'] = 'County'
    df['MF_permits'] = df['2U_permits'] + df['3-4U_permits'] + df['5+U_permits']
    df['MF_value'] = df['2U_value'] + df['3-4U_value'] + df['5+U_value']
    df['Year'] = int(year)
    return df[['Year', 'Level', 'Name', 'FIPS',
               'SF_permits', 'SF_value', 'MF_permits', 'MF_value',
               '2U_permits', '2U_value', '3-4U_permits', '3-4U_value',
               '5+U_permits', '5+U_value']]


# Function to load and process annual place data
def load_place_annual(url, year):
    df = pd.read_csv(url, skiprows=1)
    df = df.rename(columns={
        'Date': 'Year',
        'Code': 'State',
        'Code.1': 'County',
        'Units': 'SF_permits',
        'Value': 'SF_value',
        'Units.1': '2U_permits',
        'Value.1': '2U_value',
        'Units.2': '3-4U_permits',
        'Value.2': '3-4U_value',
        'Units.3': '5+U_permits',
        'Value.3': '5+U_value',
    })
    df['FIPS'] = (
        df['State'].astype(str).str.zfill(2)
        + df['County'].astype(str).str.zfill(3)
        + df['ID'].astype(str).str.zfill(6)
    )
    df = df[df['FIPS'].str.startswith('13')]
    df['Name'] = df['Name'].str.strip().str.replace(' town', '')
    df['Level'] = 'City/Other'
    df['MF_permits'] = df['2U_permits'] + df['3-4U_permits'] + df['5+U_permits']
    df['MF_value'] = df['2U_value'] + df['3-4U_value'] + df['5+U_value']
    df['Year'] = int(year)
    return df[['Year', 'Level', 'Name', 'FIPS',
               'SF_permits', 'SF_value', 'MF_permits', 'MF_value',
               '2U_permits', '2U_value', '3-4U_permits', '3-4U_value',
               '5+U_permits', '5+U_value']]


def annual_permits_fetch():
    # rolling 3-year window: current year + 2 previous. Files for the current year
    # and for the prior year (before May 14 of the following year) won't exist —
    # those gaps are filled by summed monthlies in backend_query.py.
    today = datetime.today()
    years = [today.year - 2, today.year - 1, today.year]
    frames = []

    print('gathering annual building permits...')

    for year in years:
        county_url = f"https://www2.census.gov/econ/bps/County/co{year}a.txt"
        print(f"Searching for {year} annual county data...")
        try:
            frames.append(load_county_annual(county_url, year))
        except Exception:
            print(f"  {year} annual county file not yet published; skipping.")

        place_url = f"https://www2.census.gov/econ/bps/Place/South%20Region/so{year}a.txt"
        print(f"Searching for {year} annual place data...")
        try:
            frames.append(load_place_annual(place_url, year))
        except Exception:
            print(f"  {year} annual place file not yet published; skipping.")

    if not frames:
        # The current year's annual files won't exist until the following May, so
        # an empty window is only expected very early in a calendar year. Raise so
        # a transient Census outage can't silently blank the committed master.
        raise RuntimeError('no annual files available in window; aborting without write.')

    df_annual = pd.concat(frames, ignore_index=True)
    df_annual['Name'] = df_annual['Name'].str.strip()
    df_annual = df_annual.sort_values(by=['Name', 'Year']).reset_index(drop=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    df_annual.to_csv(ANNUAL_MASTER, index=False)
    print('annual building permit script successful!')


def building_permits_fetch():
    months = get_relevant_months()
    county_dfs = []
    place_dfs = []

    print('gathering building permits...')

    # Load and append data for county endpoint
    for i, month in enumerate(months):
        month_label = month_code_to_label(month)
        print(f"Searching for {month_label} county data...")
        url = f"https://www2.census.gov/econ/bps/County/co{month}c.txt"
        try:
            county_dfs.append(load_county_data(url))
        except Exception:
            if i + 1 < len(months):
                next_label = month_code_to_label(months[i + 1])
                print(f"Unable to find {month_label} county data, looking for {next_label} county data...")
            else:
                print(f"Unable to find {month_label} county data.")

    # Load and append data for place endpoint
    for i, month in enumerate(months):
        month_label = month_code_to_label(month)
        print(f"Searching for {month_label} place data...")
        url = f"https://www2.census.gov/econ/bps/Place/South%20Region/so{month}c.txt"
        try:
            place_dfs.append(load_place_data(url))
        except Exception:
            if i + 1 < len(months):
                next_label = month_code_to_label(months[i + 1])
                print(f"Unable to find {month_label} place data, looking for {next_label} place data...")
            else:
                print(f"Unable to find {month_label} place data.")

    # Guard against a Census outage overwriting the good master with empty data.
    if not county_dfs or not place_dfs:
        raise RuntimeError(
            'no monthly county/place data fetched; aborting without write.')

    # Concatenate all data
    print("Concatenating data...")
    county_dfs = pd.concat(county_dfs, ignore_index=True)
    place_dfs = pd.concat(place_dfs, ignore_index=True)
    df_master = pd.concat([county_dfs, place_dfs], ignore_index=True)
    df_master['Name'] = df_master['Name'].str.strip()
    df_master = df_master.sort_values(by=['Name', 'year_month'])
    os.makedirs(RAW_DIR, exist_ok=True)
    df_master.to_csv(MONTHLY_MASTER, index=False)
    print('building permit script successful!')


def main():
    building_permits_fetch()
    annual_permits_fetch()
    print('all permit fetches complete!')


if __name__ == '__main__':
    main()
