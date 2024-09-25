import streamlit as st
from utils import *

# - - - PAGE SETUP - - -
overview_page = st.Page(
    page='views/overview.py',
    title='Overview',
    icon=':material/home:',
    default=True
)

county_drilldown = st.Page(
    page='views/county_drilldown.py',
    title='County Compare',
    icon=':material/stacked_line_chart:'
)

type_drilldown = st.Page(
    page='views/permit_type_drilldown.py',
    title='Permit Types (Annual)',
    icon=':material/area_chart:'
)

trailing_lookback = st.Page(
    page='views/lookback_monthly.py',
    title='Permit Types (Monthly)',
    icon=':material/area_chart:'
)

about_page = st.Page(
    page='views/about.py',
    title='About',
    icon=':material/info:'
)

# - - - NAVIGATION SETUP - - -
pg = st.navigation(
    pages=[
        overview_page,
        county_drilldown,
        type_drilldown,
        trailing_lookback,
        about_page
    ])

# - - - SHARED ON ALL PAGES - - -
st.logo('assets/arc_bw.png')

# - - - RUN NAVIGATION - - -
pg.run()

# the custom CSS lives here:
hide_default_format = """
        <style>
            .reportview-container .main footer {visibility: hidden;}    
            #MainMenu, footer {visibility: hidden;}
            section.main > div:has(~ footer ) {
                padding-bottom: 1px;
                padding-top: 2px;
            }
            [data-testid="stDecoration"] {
                display: none;
                }
            [data-testid="stHeader"] {
                display: none;
            }
            [class="stDeployButton"] {
                display: none;
            } 
            [data-testid="manage-app-button"] {
                display: none;
            }
            div.stActionButton{visibility: hidden;}
        </style>
       """


# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
