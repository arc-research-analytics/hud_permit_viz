import streamlit as st
import pandas as pd
import plotly.express as px
from utils import update_permit_type, update_county

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"  # 'collapsed' or 'expanded'
)

# set color map
county_color_map = {
    "Atlanta": "#8A2BE2",
    "Cherokee": "#FF4500",
    "Clayton": "#9370DB",
    "Cobb": "#00BFFF",
    "DeKalb": "#FFD700",
    "Douglas": "#008000",
    "Fayette": "#00FFFF",
    "Forsyth": "#FF8C00",
    "Fulton": "#FF6F61",
    "Fulton less Atlanta": "#FF69B4",
    "Gwinnett": "#32CD32",
    "Henry": "#FF1493",
    "Rockdale": "#87CEEB",
}

county_title_map = {
    "Atlanta": "City of Atlanta",
    "Cherokee": "Cherokee County",
    "Clayton": "Clayton County",
    "Cobb": "Cobb County",
    "DeKalb": "DeKalb County",
    "Douglas": "Douglas County",
    "Fayette": "Fayette County",
    "Forsyth": "Forsyth County",
    "Fulton": "Fulton County",
    "Fulton less Atlanta": "Fulton (less Atlanta)",
    "Gwinnett": "Gwinnett County",
    "Henry": "Henry County",
    "Rockdale": "Rockdale County",
}


# Function to apply the text color to selected multiselect options
def colorize_multiselect_options(selected_counties: list[str]) -> None:
    rules = ""
    for i, county in enumerate(selected_counties):
        # Default to black if county not in map
        color = county_color_map.get(county, "#000000")
        rules += f""".stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({i + 1}){{color: {color};}}"""

    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)


# Initialize session state for the widgets, if not already set
if 'permit_type' not in st.session_state:
    st.session_state['permit_type'] = "All"
if 'county' not in st.session_state:
    st.session_state['county'] = ["Fulton"]

# Use session state variables to populate query parameters not just on widget change
st.query_params["permit_type"] = st.session_state['permit_type']
st.query_params["geo"] = ",".join(st.session_state['county'])


# set font color that will be applied to all text on the page
font_color = "#d9d9d9"

# dashboard title variables
title_font_size = 24
title_margin_top = 0
title_margin_bottom = 15
title_font_weight = 700
title_font_color = font_color

# set title
st.markdown(
    f"""
    <div style='margin-top: {title_margin_top}px; margin-bottom: {title_margin_bottom}px; text-align: center;'>
        <span style='font-size: {title_font_size}px; font-weight: {title_font_weight}; color: {title_font_color}'>Filter data by</span>
    </div>
    """,
    unsafe_allow_html=True
)

column_spacer = 0.1
col1, col2, col3, col4, col5 = st.columns(
    [3, column_spacer, 3, column_spacer, 3])

# permit type select
with col1:
    permit_type = st.radio(
        label="Permit type:",
        options=("Single-family", "Multi-family", "All"),
        index=("Single-family", "Multi-family",
               "All").index(st.session_state['permit_type']),
        key="permit_type_input",
        on_change=update_permit_type,
        horizontal=False,
    )

# jurisdiction select
with col3:
    juris_select = st.multiselect(
        label="Jurisdiction:",
        options=list(county_color_map.keys()),
        default=st.session_state['county'],
        max_selections=5,
        placeholder="Choose up to 5",
        key="county_input",
        on_change=update_county
    )
    colorize_multiselect_options(st.session_state['county'])


# year select
with col5:
    slider = st.slider(
        label="Issued since:",
        min_value=1980,
        max_value=2023,
        value=1990,
        key="starting_year_input",
    )

st.query_params["year"] = slider


# cache function to read in CSV data for Explore page
@st.cache_data
def read_drilldown_data():
    drilldown_df = pd.read_csv('Data/annual_county.csv')
    return drilldown_df


# read in data
df = read_drilldown_data()


# apply filters
df_chart = df[df['county_name'].isin(st.session_state['county'])]
df_chart = df_chart[df_chart['Year'] >= slider]
df_chart = df_chart[df_chart['Series'] == permit_type]


# set chart title based on multiselect
if (len(st.session_state['county']) == 1):
    chart_title = f"{permit_type} permits issued for {county_title_map[st.session_state['county'][0]]} County since {slider}"
else:
    chart_title = f"{permit_type} permits issued for selected jurisdictions since {slider}"

# create fig object
fig = px.line(
    df_chart,
    x='Year',
    y='Permits',
    title=chart_title,
    color='county_name',
    labels={
        'county_name': 'County'
    },
    height=500
)

# update fig layout
fig.update_layout(
    hovermode='x',
    margin=dict(
        t=60,
    ),
    legend=dict(
        orientation='h',
        title_text="",
        yanchor="bottom",
        y=0.97,
        xanchor="left",
        bgcolor="rgba(41,41,41,0)"
    ),
    title={
        'font': {
            'color': font_color,
            'size': 18
        }
    },
    xaxis=dict(
        title='',
        tickfont=dict(
            size=16,
            color=font_color
        ),
        gridcolor='#FFFFFF',
    ),
    yaxis=dict(
        title='',
        tickfont=dict(
            size=16,
            color=font_color
        ),
        tickformat=','
    ),
)

fig.update_traces(
    hovertemplate='<b>%{y}</b>',
    mode='lines',
    line=dict(
        width=3,
        dash='solid'
    ),
    hoverlabel=dict(
        font_color='#171717'
    )
)

# dynamically set the hoverlabel background color to match line color
for trace in fig.data:
    county_name = trace.name
    trace_color = county_color_map.get(county_name, "#000000")
    trace.line.color = trace_color
    trace.hoverlabel.bgcolor = trace_color

fig.update_xaxes(
    showline=True,
    linewidth=1,
    linecolor=font_color,
    showgrid=False,
)
fig.update_yaxes(
    showline=True,
    linewidth=1,
    linecolor=font_color,
    showgrid=False,
    zeroline=False
)

# split the data view into 2 columns
col1, col2 = st.columns([4, 1])
config = {'displayModeBar': False}
col1.plotly_chart(
    fig,
    config=config,
    theme='streamlit',
    use_container_width=True
)


# KPI font variables
heading_margin_top = 0
heading_margin_bottom = 0
heading_font_size = 14
heading_font_weight = 200
heading_font_color = font_color

value_font_size = 22
value_margin_top = 40
value_margin_bottom = 15
value_margin_left = 10
value_font_weight = 700
value_font_color = font_color


col2.write("")

# Create a list of counties and their total permits
county_totals = [(county, df_chart[df_chart['county_name'] == county]['Permits'].sum())
                 for county in df_chart['county_name'].unique()]

# Sort the list by permit_total in descending order
county_totals_sorted = sorted(county_totals, key=lambda x: x[1], reverse=True)

# create KPI boxes
with col2:
    for county, permit_total in county_totals_sorted:
        st.markdown(
            f"""
            <div style='text-align: center; border:2px solid {county_color_map[county]}; padding: 6px; border-radius: 7px;'>
                <span style='margin-top: {heading_margin_top}px; margin-bottom: {heading_margin_bottom}px; font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color}'>{county_title_map[county]} Total:</span><br/>
                <span style='font-size: {value_font_size}px; font-weight: {value_font_weight}; color: {value_font_color}'>
                {permit_total:,.0f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")

# download dataframe as CSV
df_download = df_chart.to_csv(index='False').encode('utf-8')
st.download_button(
    label=":material/download:",
    data=df_download,
    file_name='jurisdiction_compare.csv',
    help='Download filtered data to CSV',
)

# the custom CSS lives here:
hide_default_format = """
        <style>
            .stRadio [data-testid=stWidgetLabel] p {
                font-size: 18px;
            }
            .stRadio [data-testid=stWidgetLabel]{
                justify-content: center;
                text-decoration: underline;
                margin-bottom: 10px;
            }
            .stRadio [role=radiogroup]{
                align-items: center;
                background-color: #171717;
                border-radius: 7px;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            div[data-baseweb="select"] > div {
                width: 100%;
                background-color: #171717;
            }
            .stMultiSelect [data-testid=stWidgetLabel] p {
                font-size: 18px;
            }
            .stMultiSelect [data-testid=stWidgetLabel]{
                justify-content: center;
                text-decoration: underline;
                margin-bottom: 10px;
            }
            .stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]{
                background-color: #292929;
            }
            .stMultiSelect [data-baseweb="select"] span {
                max-width: 280px;
            }
            .stSlider [data-testid=stWidgetLabel] p {
                font-size: 18px;
            }
            .stSlider [data-testid=stWidgetLabel]{
                justify-content: center;
                text-decoration: underline;
                margin-bottom: 10px;
            }
            [data-testid="stAppViewBlockContainer"] {
                padding-top: 40px;
                padding-left: 30px;
                padding-right: 30px;
            }
            [data-testid="stDownloadButton"] {
                position: absolute;
                bottom: 10px;
            }

        </style>
       """

# .main {
#     overflow: hidden
# }

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)