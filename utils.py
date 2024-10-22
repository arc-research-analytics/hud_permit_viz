import streamlit as st

# Create a custom color palette to map onto all counties
county_color_map = {
    "Cherokee": "#FF4500",
    "Clayton": "#9370DB",
    "Cobb": "#00BFFF",
    "DeKalb": "#FFD700",
    "Douglas": "#008000",
    "Fayette": "#00FFFF",
    "Forsyth": "#FF8C00",
    "Fulton": "#FF6F61",
    "Gwinnett": "#32CD32",
    "Henry": "#FF1493",
    "Rockdale": "#87CEEB",
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
    # 'Unincorporated Cherokee County',
    # 'Unincorporated Clayton County',
    # 'Unincorporated Cobb County',
    # 'Unincorporated DeKalb County',
    # 'Unincorporated Douglas County',
    # 'Unincorporated Fayette County',
    # 'Unincorporated Forsyth County',
    # 'Unincorporated Fulton County',
    # 'Unincorporated Gwinnett County',
    # 'Unincorporated Henry County',
    # 'Unincorporated Rockdale County'
]


# Function to apply the text color to selected multiselect options
def colorize_multiselect_options(selected_counties: list[str]) -> None:
    rules = ""
    for i, county in enumerate(selected_counties):
        # Default to black if county not in map
        color = county_color_map.get(county, "#000000")
        rules += f""".stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({i + 1}){{color: {color};}}"""

    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)


# Callback functions for each widget to update session state
def update_permit_type():
    st.session_state['permit_type'] = st.session_state['permit_type_input']
    st.query_params["permit_type"] = st.session_state['permit_type']


def update_county():
    st.session_state['county'] = st.session_state['county_input']


def update_starting_year():
    st.session_state['starting_year'] = st.session_state['starting_year_input']
    st.query_params["starting_year"] = st.session_state['starting_year']
