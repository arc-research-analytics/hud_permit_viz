import os
import pandas as pd
from datetime import datetime

# Note: this script only runs the data filter & export. It reads the two raw
# master CSVs produced by fetch_permits.py (in Data/raw/) and rebuilds the four
# dashboard CSVs in Data/. The GitHub Actions workflow (.github/workflows/
# refresh-data.yml) chains fetch_permits.py -> this script -> git commit/push,
# which triggers the Heroku redeploy.

# Resolve paths relative to this file so the script works from any cwd.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(REPO_ROOT, 'Data', 'raw')

county_list = [
    'Cherokee',
    'Clayton',
    'Cobb',
    'DeKalb',
    'Douglas',
    'Fayette',
    'Forsyth',
    'Fulton',
    'Gwinnett',
    'Henry',
    'Rockdale'
]

# FIPS-keyed dictionaries used by the annual pipeline. county_dict covers the 11
# metro counties; city_dict covers the cities in city_list PLUS the 11
# unincorporated county balances, which appear only in the annual viz.
county_dict = {
    '13057': 'Cherokee',
    '13063': 'Clayton',
    '13067': 'Cobb',
    '13089': 'DeKalb',
    '13097': 'Douglas',
    '13113': 'Fayette',
    '13117': 'Forsyth',
    '13121': 'Fulton',
    '13135': 'Gwinnett',
    '13151': 'Henry',
    '13247': 'Rockdale',
}

city_dict = {
    '13067003000': 'Acworth',
    '13121019000': 'Alpharetta',
    '13121038000': 'Atlanta',
    '13067043000': 'Austell',
    '13089047000': 'Avondale Estates',
    '13057055000': 'Ball Ground',
    '13135066000': 'Berkeley Lake',
    '13089098700': 'Brookhaven',
    '13135108000': 'Buford',
    '13057126000': 'Canton',
    '13089139000': 'Chamblee',
    '13121144900': 'Chattahoochee Hills',
    '13089152000': 'Clarkston',
    '13121169000': 'College Park',
    '13247178000': 'Conyers',
    '13117192000': 'Cumming',
    '13135195000': 'Dacula',
    '13089213000': 'Decatur',
    '13089225000': 'Doraville',
    '13097229000': 'Douglasville',
    '13135233000': 'Duluth',
    '13089233500': 'Dunwoody',
    '13121237000': 'East Point',
    '13121256000': 'Fairburn',
    '13113260000': 'Fayetteville',
    '13063268000': 'Forest Park',
    '13135301000': 'Grayson',
    '13151315000': 'Hampton',
    '13121317000': 'Hapeville',
    '13057341000': 'Holly Springs',
    '13121369300': 'Johns Creek',
    '13063371000': 'Jonesboro',
    '13067373000': 'Kennesaw',
    '13063381000': 'Lake City',
    '13135388000': 'Lawrenceville',
    '13135396000': 'Lilburn',
    '13089401000': 'Lithonia',
    '13151402000': 'Locust Grove',
    '13063409000': 'Lovejoy',
    '13067430000': 'Marietta',
    '13151439000': 'McDonough',
    '13121457300': 'Milton',
    '13063472000': 'Morrow',
    '13121480000': 'Mountain Park',
    '13063057500': 'Mountain View',
    '13057485000': 'Nelson',
    '13135494000': 'Norcross',
    '13121515000': 'Palmetto',
    '13113523000': 'Peachtree City',
    '13135523500': 'Peachtree Corners',
    '13089533000': 'Pine Lake',
    '13067546000': 'Powder Springs',
    '13063575000': 'Riverdale',
    '13121585000': 'Roswell',
    '13121592700': 'Sandy Springs',
    '13067613000': 'Smyrna',
    '13135614000': 'Snellville',
    '13121617800': 'South Fulton',
    '13151629000': 'Stockbridge',
    '13089630000': 'Stone Mountain',
    '13089629500': 'Stonecrest',
    '13135631000': 'Sugar Hill',
    '13135638000': 'Suwanee',
    '13089677800': 'Tucker',
    '13113685000': 'Tyrone',
    '13121687000': 'Union City',
    '13057742000': 'Woodstock',
    '13057147000': 'Unincorporated Cherokee County',
    '13063156000': 'Unincorporated Clayton County',
    '13067161000': 'Unincorporated Cobb County',
    '13089210000': 'Unincorporated DeKalb County',
    '13097228000': 'Unincorporated Douglas County',
    '13113259000': 'Unincorporated Fayette County',
    '13117270000': 'Unincorporated Forsyth County',
    '13121278000': 'Unincorporated Fulton County',
    '13135309000': 'Unincorporated Gwinnett County',
    '13151332000': 'Unincorporated Henry County',
    '13247579000': 'Unincorporated Rockdale County',
}

city_list = [
    'Acworth',
    'Alpharetta',
    'Atlanta',
    'Austell',
    'Avondale Estates',
    'Ball Ground',
    'Berkeley Lake',
    'Brookhaven',
    'Buford',
    'Canton',
    'Chamblee',
    'Chattahoochee Hills',
    'Clarkston',
    'College Park',
    'Conyers',
    'Cumming',
    'Dacula',
    'Decatur',
    'Doraville',
    'Douglasville',
    'Duluth',
    'Dunwoody',
    'East Point',
    'Fairburn',
    'Fayetteville',
    'Forest Park',
    'Grayson',
    'Hampton',
    'Hapeville',
    'Holly Springs',
    'Johns Creek',
    'Jonesboro',
    'Kennesaw',
    'Lake City',
    'Lawrenceville',
    'Lilburn',
    'Lithonia',
    'Locust Grove',
    'Lovejoy',
    'Marietta',
    'McDonough',
    'Milton',
    'Morrow',
    'Mountain Park',
    'Mountain View',
    'Nelson',
    'Norcross',
    'Palmetto',
    'Peachtree City',
    'Peachtree Corners',
    'Pine Lake',
    'Powder Springs',
    'Riverdale',
    'Roswell',
    'Sandy Springs',
    'Smyrna',
    'Snellville',
    'South Fulton',
    'Stockbridge',
    'Stone Mountain',
    'Stonecrest',
    'Sugar Hill',
    'Suwanee',
    'Tucker',
    'Tyrone',
    'Union City',
    'Woodstock',
]

# step 1: filter dataset, export to Streamlit app
df_master = pd.read_csv(os.path.join(RAW_DIR, 'BPS_GA.csv'))
df = df_master[((df_master['Level'] == 'County') & (df_master['Name'].isin(county_list)))
               | ((df_master['Level'] == 'City/Other') & (df_master['Name'].isin(city_list)))]

# Melt the dataframe to create rows for 'SF_permits' and 'MF_permits'
df_melted = pd.melt(
    df,
    id_vars=['year_month', 'date', 'Level', 'Name'],
    value_vars=['SF_permits', 'MF_permits'],
    var_name='Series',
    value_name='Permits'
)

# Map the 'Series' values to meaningful names
df_melted['Series'] = df_melted['Series'].map({
    'SF_permits': 'Single-Family',
    'MF_permits': 'Multi-Family'
})

# create the Metro total
metro_totals = (
    df_melted[df_melted['Level'] == 'County']
    .groupby(['year_month', 'date', 'Series'], as_index=False)['Permits']
    .sum()
)

# Add "Metro" as the 'Name' and 'Level'
metro_totals['Name'] = 'Metro'
metro_totals['Level'] = 'County'

# Append the Metro totals to the melted dataframe & export
df_final = pd.concat([df_melted, metro_totals], ignore_index=True)
df_final.to_csv(os.path.join(REPO_ROOT, 'Data', 'monthly_master.csv'), index=False)


# -----------------------------------------------------------------------------
# Step 2: build the annual dashboard CSVs.
#
# Replaces the standalone annual_update.ipynb. Each monthly run:
#   - pulls benchmarked annual rows for years where the BPS annual file exists
#     (from BPS_GA_annual.csv, produced by data_pull.py::annual_permits_fetch)
#   - fills gaps (current year, prior year pre-May-14) with summed monthlies,
#     marking those rows provisional=True
#   - preserves pre-window rows from the existing dashboard CSVs
#     (history before the rolling 3-year window never changes)
# -----------------------------------------------------------------------------

ROLLING_WINDOW = 3
ANNUAL_MASTER = os.path.join(RAW_DIR, 'BPS_GA_annual.csv')
DASHBOARD_DIR = os.path.join(REPO_ROOT, 'Data')

current_year = datetime.now().year
window_years = list(range(current_year - (ROLLING_WINDOW - 1), current_year + 1))
window_start = window_years[0]


def reformat_unincorporated(name):
    # BPS reports these as "<County> County Unincorporated Area"; convert to the
    # canonical "Unincorporated <County> County" the dashboard already uses.
    if isinstance(name, str) and 'Unincorporated Area' in name:
        return 'Unincorporated ' + name.replace(' Unincorporated Area', '').strip()
    return name


# ---- Prepare the monthly master for provisional roll-ups --------------------
df_monthly = df_master.copy()
df_monthly['Year'] = df_monthly['year_month'].astype(str).str[:4].astype(int)

# A provisional year is only emitted once it's fully complete (December monthly
# data is in hand). Otherwise a partial year — e.g. Jan-only in April — would
# render as a cliff-edge drop on the annual charts.
_months_seen = (
    df_monthly['year_month'].astype(str).str[-2:]
    .groupby(df_monthly['Year']).apply(set)
)
complete_years = {int(y) for y, months in _months_seen.items() if '12' in months}

# ---- Load the annual master (benchmarked), if available ---------------------
if os.path.exists(ANNUAL_MASTER):
    df_ann = pd.read_csv(ANNUAL_MASTER, dtype={'FIPS': str})
    df_ann['Year'] = df_ann['Year'].astype(int)
else:
    df_ann = pd.DataFrame(columns=[
        'Year', 'Level', 'Name', 'FIPS', 'SF_permits', 'MF_permits'
    ])


# ---- Counties: assemble rows for the rolling window -------------------------
county_frames = []

# benchmarked rows from the annual master
df_ann_c = df_ann[(df_ann['Level'] == 'County') &
                  (df_ann['FIPS'].isin(county_dict.keys()))].copy()
if not df_ann_c.empty:
    df_ann_c['county_name'] = df_ann_c['FIPS'].map(county_dict)
    df_ann_c['provisional'] = False
    county_frames.append(
        df_ann_c[['county_name', 'Year', 'SF_permits', 'MF_permits', 'provisional']]
    )

years_with_annual_c = set(df_ann_c['Year'].tolist()) if not df_ann_c.empty else set()

# provisional rows summed from monthlies for window years not yet benchmarked
df_m_c = df_monthly[(df_monthly['Level'] == 'County') &
                    (df_monthly['Name'].isin(county_dict.values()))].copy()
for yr in window_years:
    if yr in years_with_annual_c:
        continue
    if yr not in complete_years:
        continue
    df_yr = df_m_c[df_m_c['Year'] == yr]
    if df_yr.empty:
        continue
    agg = df_yr.groupby('Name', as_index=False)[['SF_permits', 'MF_permits']].sum()
    agg = agg.rename(columns={'Name': 'county_name'})
    agg['Year'] = yr
    agg['provisional'] = True
    county_frames.append(
        agg[['county_name', 'Year', 'SF_permits', 'MF_permits', 'provisional']]
    )

county_new = pd.concat(county_frames, ignore_index=True) if county_frames else \
    pd.DataFrame(columns=['county_name', 'Year', 'SF_permits', 'MF_permits', 'provisional'])


# ---- Cities/places: same shape ---------------------------------------------
city_frames = []

df_ann_p = df_ann[(df_ann['Level'] == 'City/Other') &
                  (df_ann['FIPS'].isin(city_dict.keys()))].copy()
if not df_ann_p.empty:
    df_ann_p['City'] = df_ann_p['FIPS'].map(city_dict)
    df_ann_p['provisional'] = False
    city_frames.append(
        df_ann_p[['City', 'Year', 'SF_permits', 'MF_permits', 'provisional']]
    )

years_with_annual_p = set(df_ann_p['Year'].tolist()) if not df_ann_p.empty else set()

df_m_p = df_monthly[df_monthly['Level'] == 'City/Other'].copy()
df_m_p['Name'] = df_m_p['Name'].apply(reformat_unincorporated)
df_m_p = df_m_p[df_m_p['Name'].isin(city_dict.values())]
for yr in window_years:
    if yr in years_with_annual_p:
        continue
    if yr not in complete_years:
        continue
    df_yr = df_m_p[df_m_p['Year'] == yr]
    if df_yr.empty:
        continue
    agg = df_yr.groupby('Name', as_index=False)[['SF_permits', 'MF_permits']].sum()
    agg = agg.rename(columns={'Name': 'City'})
    agg['Year'] = yr
    agg['provisional'] = True
    city_frames.append(
        agg[['City', 'Year', 'SF_permits', 'MF_permits', 'provisional']]
    )

city_new = pd.concat(city_frames, ignore_index=True) if city_frames else \
    pd.DataFrame(columns=['City', 'Year', 'SF_permits', 'MF_permits', 'provisional'])


# ---- Build Atlanta / Metro / Fulton-less-Atlanta pseudo-county rows --------
if not city_new.empty:
    atl = city_new[city_new['City'] == 'Atlanta'].copy()
    if not atl.empty:
        atl = atl.rename(columns={'City': 'county_name'})
        county_new = pd.concat([county_new, atl], ignore_index=True)

if not county_new.empty:
    real_counties = county_new[county_new['county_name'].isin(county_dict.values())]
    metro = (
        real_counties
        .groupby(['Year', 'provisional'], as_index=False)[['SF_permits', 'MF_permits']]
        .sum()
    )
    metro['county_name'] = 'Metro'
    county_new = pd.concat([county_new, metro], ignore_index=True)

    fulton = county_new[county_new['county_name'] == 'Fulton'] \
        .set_index('Year')[['SF_permits', 'MF_permits', 'provisional']]
    atlanta = county_new[county_new['county_name'] == 'Atlanta'] \
        .set_index('Year')[['SF_permits', 'MF_permits']]
    if not fulton.empty and not atlanta.empty:
        fla = fulton[['SF_permits', 'MF_permits']].subtract(atlanta, fill_value=0)
        fla['provisional'] = fulton['provisional']
        fla = fla.reset_index()
        fla['county_name'] = 'Fulton less Atlanta'
        county_new = pd.concat([county_new, fla], ignore_index=True)


# ---- Compute 'All' series for counties and melt to long form ---------------
if not county_new.empty:
    county_new['All'] = county_new['SF_permits'] + county_new['MF_permits']
    county_long = pd.melt(
        county_new,
        id_vars=['county_name', 'Year', 'provisional'],
        value_vars=['SF_permits', 'MF_permits', 'All'],
        var_name='Series',
        value_name='Permits'
    )
    county_long['Series'] = county_long['Series'].map({
        'SF_permits': 'Single-family',
        'MF_permits': 'Multi-family',
        'All': 'All',
    })
else:
    county_long = pd.DataFrame(
        columns=['county_name', 'Year', 'provisional', 'Series', 'Permits']
    )

if not city_new.empty:
    city_long = pd.melt(
        city_new,
        id_vars=['City', 'Year', 'provisional'],
        value_vars=['SF_permits', 'MF_permits'],
        var_name='Series',
        value_name='Permits'
    )
    city_long['Series'] = city_long['Series'].map({
        'SF_permits': 'Single-family',
        'MF_permits': 'Multi-family',
    })
else:
    city_long = pd.DataFrame(columns=['City', 'Year', 'provisional', 'Series', 'Permits'])


# ---- Merge with preserved pre-window history and write ---------------------
def _merge_preserved(new_df, existing_path, key_col):
    if os.path.exists(existing_path):
        old = pd.read_csv(existing_path)
        if 'provisional' not in old.columns:
            old['provisional'] = False
        old_pre = old[old['Year'] < window_start]
        combined = pd.concat([old_pre, new_df], ignore_index=True)
    else:
        combined = new_df.copy()
    combined['Permits'] = combined['Permits'].astype(int)
    return combined.sort_values(by=[key_col, 'Year', 'Series']).reset_index(drop=True)


county_final = _merge_preserved(
    county_long, os.path.join(DASHBOARD_DIR, 'annual_county.csv'), 'county_name')
city_final = _merge_preserved(
    city_long, os.path.join(DASHBOARD_DIR, 'annual_city.csv'), 'City')

# metro_total_annual is derived from the Metro "All" row in county_final
metro_src = county_final[(county_final['county_name'] == 'Metro') &
                         (county_final['Series'] == 'All')]
metro_final = metro_src[['Year', 'Permits', 'provisional']] \
    .sort_values('Year').reset_index(drop=True)

county_final.to_csv(os.path.join(DASHBOARD_DIR, 'annual_county.csv'), index=False)
city_final.to_csv(os.path.join(DASHBOARD_DIR, 'annual_city.csv'), index=False)
metro_final.to_csv(os.path.join(DASHBOARD_DIR, 'metro_total_annual.csv'), index=False)
