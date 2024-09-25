import streamlit as st
import pandas as pd
import plotly.express as px
from utils import county_color_map

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"  # 'collapsed' or 'expanded'
)


# 3 function definitions to set state variables and query parameters on change
def update_geography():
    st.session_state['geography_type2'] = st.session_state['geography_type_input2']
    st.query_params["geo"] = st.session_state['geography_type2']


def update_county():
    st.session_state['county_permitType'] = st.session_state['county_input2']
    st.query_params["county"] = st.session_state['county_permitType']


# def update_starting_year():
#     st.session_state['starting_year_type'] = st.session_state['starting_year_input']
#     st.query_params["year"] = st.session_state['starting_year_type']


# Initialize session state for the widgets, if not already set
if 'geography_type2' not in st.session_state:
    st.session_state['geography_type2'] = 'Region'
if 'county_permitType' not in st.session_state:
    st.session_state['county_permitType'] = 'Cobb'
if 'starting_year_type' not in st.session_state:
    st.session_state['starting_year_type'] = 1985


# set font color that will be applied to all text on the page
font_color = "#d9d9d9"

# dashboard title variables
title_font_size = 32
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
options = ["Region", "Single county"]

with col1:
    st.radio(
        label="Geography level:",
        options=options,
        index=options.index(
            st.session_state['geography_type2']),
        key="geography_type_input2",
        on_change=update_geography,
        horizontal=False,
    )

# county select, if applicable
with col3:
    if st.session_state['geography_type2'] == 'Region':
        st.selectbox(
            label='County:',
            options=['Region', 'other'],
            placeholder='N/A',
            disabled=True
        )
        st.query_params["county"] = 'Null'
    else:
        st.selectbox(
            label='County:',
            options=list(county_color_map.keys()),
            index=list(county_color_map.keys()).index(
                st.session_state['county_permitType']),
            placeholder="Choose a county",
            key="county_input2",
            on_change=update_county,
            disabled=False
        )


# starting year select
with col5:
    slider_value = st.slider(
        label="Issued since:",
        min_value=1980,
        max_value=2023,
        value=1985,
        key="starting_year_input",
        # on_change=update_starting_year
    )

st.query_params["geo"] = st.session_state['geography_type2']

# st.session_state['starting_year_type'] = slider_value
st.query_params["year"] = slider_value


# cache function to read in CSV data for Explore page
@st.cache_data
def read_drilldown_data():
    drilldown_df = pd.read_csv('Data/annual_file_county.csv')

    metro_data_annual = drilldown_df.groupby(['Year', 'Series']).agg(
        {'Permits': 'sum'}).reset_index()

    metro_data_annual['county_name'] = 'Metro'

    # concatenate the metro-wide aggregations with the county data
    annual_final = pd.concat(
        [drilldown_df, metro_data_annual], ignore_index=True)

    # don't need small-mf, large-mf or total permits
    annual_final = annual_final[(annual_final['Series'] == 'All Single-Family Permits')
                                | (annual_final['Series'] == 'All Multi-Family Permits')]

    # Dictionary for replacements
    replacements = {
        "All Single-Family Permits": "Single-Family",
        "All Multi-Family Permits": "Multi-Family",
    }

    # Replace substrings using the dictionary
    annual_final["Series"] = annual_final["Series"].replace(replacements)

    # sort the dataframe
    annual_final = annual_final.sort_values(by='Series', ascending=False)

    return annual_final


# read in, filter data
df = read_drilldown_data()

if st.session_state['geography_type2'] == 'Region':
    df = df[df['county_name'] == 'Metro']
    title = f'Permits Issued in the Atlanta Region since {slider_value}'
    st.query_params["county"] = 'Null'
else:
    df = df[df['county_name'] == st.session_state['county_permitType']]
    title = f'Permits Issued in {st.session_state["county_permitType"]} County since {slider_value}'
    st.query_params["county"] = st.session_state['county_permitType']

df = df[df['Year'] >= slider_value]

# color map
color_discrete_map = {
    'Single-Family': '#00BFFF',
    'Multi-Family': '#FF6F61'
}

# create chart object
fig = px.area(
    df,
    x='Year',
    y='Permits',
    title=title,
    line_group='Series',
    color='Series',
    labels={
        'county_name': 'County',
    },
    color_discrete_map=color_discrete_map,
    height=545
)

# update fig layout
fig.update_layout(
    hovermode='x',
    margin=dict(
        t=60,
    ),
    legend=dict(
        orientation='h',
        entrywidth=100,
        title_text="",
        yanchor="bottom",
        y=0.97,
        xanchor="left",
        bgcolor="rgba(41,41,41,0)"
    ),
    legend_traceorder="reversed",
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

# configure tooltip
fig.update_traces(
    hovertemplate='<b>%{y}</b>',
    mode='lines',
    line=dict(
        width=2,
        dash='solid'
    ),
    hoverlabel=dict(
        font_color='#171717'
    )
)


for trace in fig.data:
    trace.hoverlabel.bgcolor = color_discrete_map[trace.name]

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

st.write("")
config = {'displayModeBar': False}
st.plotly_chart(
    fig,
    config=config,
    theme='streamlit',
    use_container_width=True
)

# download dataframe as CSV
df = df.sort_values(by='Year', ascending=True)
df_download = df.to_csv(index='False').encode('utf-8')
st.download_button(
    label=":material/download:",
    data=df_download,
    file_name='permit_types_annual.csv',
    help='Download the filtered data'
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
            .stSelectbox [data-testid=stWidgetLabel] p {
                font-size: 18px;
            }
            .stSelectbox [data-testid=stWidgetLabel]{
                justify-content: center;
                text-decoration: underline;
                margin-bottom: 10px;
            }
            .stSelectbox div[data-baseweb="select"] span[data-baseweb="tag"]{
                background-color: #292929;
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
                margin-top: -50px;
                padding-left: 30px;
                padding-right: 30px;
            }
            .main {
                overflow: hidden
            }
            [data-testid="stHeader"] {
                color: #292929;
            }
            [data-testid="stDownloadButton"] {
                position: absolute;
                bottom: 10px;
            }
        </style>
       """


# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
