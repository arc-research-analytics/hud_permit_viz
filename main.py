import streamlit as st
from utils import *


# - - - PAGE SETUP - - -
overview = st.Page(
    page='views/overview.py',
    title='Overview',
    icon=':material/home:',
    default=True
)

jurisdiction_compare = st.Page(
    page='views/jurisdiction_compare.py',
    title='Compare',
    icon=':material/stacked_line_chart:'
)

permit_types_annual = st.Page(
    page='views/annual_trends.py',
    title='Annual Trends',
    icon=':material/area_chart:'
)

permit_types_monthly = st.Page(
    page='views/monthly_trends.py',
    title='Monthly Trends',
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
        overview,
        jurisdiction_compare,
        permit_types_annual,
        permit_types_monthly,
        about_page
    ])

# - - - SHARED ON ALL PAGES - - -
st.logo('assets/arc_bw.png')

# - - - RUN NAVIGATION - - -
pg.run()

# the custom CSS lives here:
hide_default_format = """
        <style>
            [data-testid="stAppViewBlockContainer"] {
                background-color: #292929;
            }
            MainMenu, footer {
                visibility: hidden;
                height: 0%;
            }
            [data-testid="stHeader"] {
                display: none;
            }
            section.main > div:has(~ footer ) {
                padding-bottom: 1px;
                padding-top: 2px;
            }
            [data-testid="stDecoration"] {
                display: none;
                }
            [class="stDeployButton"] {
                display: none;
            }
            .stActionButton {
                visibility: hidden;
            }
        </style>
       """


# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
