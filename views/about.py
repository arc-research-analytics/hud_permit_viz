import streamlit as st
from st_screen_stats import ScreenData

# using react component
screenD = ScreenData(setTimeout=200)
screen_d = screenD.st_screen_data()
screen_width = screen_d['innerWidth']


# heading variables
heading_font_size = 25
heading_margin_bottom = 15
heading_font_weight = 700
heading_font_color = '#00BFFF'

# desktop / tablet view
if screen_width >= 500:
    heading_margin_top = 0
# mobile view
else:
    heading_margin_top = -40

paragraph_font_size = 16
paragraph_font_weight = 100
paragraph_font_color = '#d9d9d9'

# set about block
st.markdown(
    f"""
    <div style='margin-top: {heading_margin_top}px; margin-bottom: {heading_margin_bottom}px; text-align: left;'>
        <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {heading_font_color}'>About us</span><br/>
        <span style='font-size: {paragraph_font_size}px; font-weight: {paragraph_font_weight}; color: {paragraph_font_color}'>The Research & Analytics Department (RAD) of the Atlanta Regional Commission developed and maintains this dashboard. RAD additionally provides bespoke data tools to support informed decision-making by local governments and leaders around the metro Atlanta region. For more analysis and visuals, please visit our 33N blog <b><a href="https://33n.atlantaregional.com/" style="text-decoration: underline; color: inherit;">here</a></b>.  
        <br/><br/> 
        RAD not only produces “the numbers” but also curates current and historical information necessary for accurate representation of the past and reasonable assessments of the future. The department focuses on leveraging partnerships in the development and deployment of online tools, developing innovative and interactive visualizations to facilitate understanding of the data, and performing detailed custom analyses that include narrative “storytelling” to inform application of the data.
</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")

# set source block
st.markdown(
    f"""
    <div style='margin-top: {heading_margin_top}px; margin-bottom: {heading_margin_bottom}px; text-align: left;'>
        <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {heading_font_color}'>Source</span><br/>
        <span style='font-size: {paragraph_font_size}px; font-weight: {paragraph_font_weight}; color: {paragraph_font_color}'>The data for this dashboard were collected from the State of the Cities Data Systems (SOCDS) which is maintained by the Office of Policy Development and Research. Click <b><a href="https://socds.huduser.gov/permits/index.html?" style="text-decoration: underline; color: {paragraph_font_color}">here</a></b> to access this data source.</span>
    </div>
    """,
    unsafe_allow_html=True
)

# desktop / tablet view
if screen_width >= 500:
    hide_default_format = """
            <style>
                [data-testid="stAppViewBlockContainer"] {
                    padding-top: 100px;
                    padding-left: 50px;
                    padding-right: 50px;
                    height: 100%;
                    width: 100%;
                }
                .main {
                    overflow: hidden
                }
            </style>
        """
# mobile view
else:
    hide_default_format = """
            <style>
                [data-testid="stAppViewBlockContainer"] {
                    padding-top: 100px;
                    padding-left: 50px;
                    padding-right: 50px;
                    height: 100%;
                    width: 100%;
                }
            </style>
        """

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
