import streamlit as st
from st_screen_stats import ScreenData

# using react component
screenD = ScreenData(setTimeout=200)
screen_d = screenD.st_screen_data()
screen_width = screen_d['innerWidth']


# text variables that are NOT screensize specific
heading_font_size = 25
heading_margin_bottom = 25
heading_font_weight = 700
paragraph_font_size = 16
paragraph_font_weight = 100
heading_font_color = '#00BFFF'
paragraph_font_color = '#d9d9d9'

# desktop / tablet view
if screen_width >= 500:
    heading_margin_top = 0
    margin_side = 20
    text_alignment = 'left'
# mobile view
else:
    heading_margin_top = -20
    margin_side = 20
    text_alignment = 'left'


# "About us" text blocks
st.markdown(
    f"""
    <div style='margin-top: {heading_margin_top}px; margin-bottom: {heading_margin_bottom}px; text-align: {text_alignment}; padding-left: {margin_side}px; padding-right: {margin_side}px;'>
        <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {heading_font_color}'>About us</span><br/>
        <span style='font-size: {paragraph_font_size}px; font-weight: {paragraph_font_weight}; color: {paragraph_font_color}'>The Research & Innovation Team of the Atlanta Regional Commission developed and maintains this web application. The team additionally provides bespoke data tools to support informed decision-making by local governments and leaders around the metro Atlanta region. For more analysis and visuals, please visit our 33N blog <b><a href="https://33n.atlantaregional.com/" style="text-decoration: underline; color: inherit;">here</a></b>.  
        <br/><br/> 
        Research & Innovation not only produces “the numbers” but also curates current and historical information necessary for accurate representation of the past and reasonable assessments of the future. The department focuses on leveraging partnerships in the development and deployment of online tools, developing innovative and interactive visualizations to facilitate understanding of the data, and performing detailed custom analyses that include narrative “storytelling” to inform application of the data.
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")

# "Source" text block
st.markdown(
    f"""
    <div style='margin-top: {heading_margin_top}px; margin-bottom: {heading_margin_bottom}px; text-align: {text_alignment}; padding-left: {margin_side}px; padding-right: {margin_side}px;'>
        <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {heading_font_color}'>Source</span><br/>
        <span style='font-size: {paragraph_font_size}px; font-weight: {paragraph_font_weight}; color: {paragraph_font_color}'>The data for this dashboard were collected from the U.S. Census Building Permits Survey. Click <b><a href="https://www2.census.gov/econ/bps/" style="text-decoration: underline; color: {paragraph_font_color}">here</a></b> to access this data source.</span>
    </div>
    """,
    unsafe_allow_html=True
)
