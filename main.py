import streamlit as st
from utils import *


# - - - PAGE SETUP - - -
overview = st.Page(
    page='views/1_overview.py',
    title='Overview',
    icon=':material/home:',
    default=True
)

jurisdiction_compare = st.Page(
    page='views/2_jurisdiction_compare.py',
    title='Compare',
    icon=':material/stacked_line_chart:'
)

permit_types_annual = st.Page(
    page='views/3_annual_trends.py',
    title='Annual Trends',
    icon=':material/calendar_today:'
)

permit_types_monthly = st.Page(
    page='views/4_monthly_trends.py',
    title='Monthly Trends',
    icon=':material/timer:'
)

about_page = st.Page(
    page='views/5_about.py',
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
