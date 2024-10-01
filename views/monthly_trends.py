import streamlit as st
import pandas as pd
import plotly.express as px
from utils import county_color_map, city_list
from pandas.tseries.offsets import DateOffset

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"  # 'collapsed' or 'expanded'
)

# Initialize session state for the widgets, if not already set
if 'geography_3' not in st.session_state:
    st.session_state['geography_3'] = 'Region'
if 'geo_level' not in st.session_state:
    st.session_state['geo_level'] = 'Region'

st.query_params['geo'] = st.session_state['geography_3']


# function definitions to set state variables and query parameters on change
def update_geography():
    st.session_state['geo_level'] = st.session_state['geography_type_input3']
    if st.session_state['geo_level'] == 'Region':
        st.session_state['geography_3'] = 'Region'
    elif st.session_state['geo_level'] == 'County':
        st.session_state['geography_3'] = list(county_color_map.keys())[7]
    elif st.session_state['geo_level'] == 'City':
        st.session_state['geography_3'] = city_list[2]

    # update only 'geo' query param to reflect selected geography
    st.query_params["geo"] = st.session_state['geography_3']


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

column_spacer = 0.001
col1, col_spacer, col2 = st.columns([3, column_spacer, 3])

# permit type select
options = ["Region", "County", "City"]

# First input: geography level
with col1:
    geo_level = st.radio(
        label="Geography level:",
        options=options,
        index=options.index(st.session_state['geo_level']),
        key="geography_type_input3",
        on_change=update_geography,
        horizontal=True,
    )

# county/city select, if applicable
with col2:
    if st.session_state['geo_level'] == 'Region':
        st.selectbox(
            label='County:',
            options=['Region'],
            placeholder='N/A',
            disabled=True
        )
    elif st.session_state['geo_level'] == 'County':
        county_index = list(county_color_map.keys()).index(
            st.session_state['geography_3']
        )
        selected_county = st.selectbox(
            label='County:',
            options=list(county_color_map.keys()),
            index=county_index,
            key="county",
            placeholder="Choose a county",
            on_change=lambda: st.session_state.update({
                'geography_3': st.session_state['county'],
            })
        )
    elif st.session_state['geo_level'] == 'City':
        city_index = city_list.index(st.session_state['geography_3'])
        selected_city = st.selectbox(
            label='City:',
            options=city_list,
            index=city_index,
            placeholder="Choose a city",
            key="city",
            on_change=lambda: st.session_state.update({
                'geography_3': st.session_state['city'],
            })
        )

st.write('')


# cache function to read in CSV data for Explore page
@st.cache_data
def read_county_data():
    monthly_county = pd.read_csv('Data/monthly_county.csv')
    monthly_county = monthly_county.sort_values(
        by=['Series', 'date'], ascending=False)
    return monthly_county


def read_city_data():
    monthly_city = pd.read_csv('Data/monthly_city.csv')
    monthly_city = monthly_city.sort_values(
        by=['Series', 'date'], ascending=False)
    return monthly_city


# conditionally read in data based on user input
if st.session_state['geo_level'] == 'City':
    df = read_city_data()
    df = df[df['city'] == selected_city]
    title = f'Permits Issued in City of {selected_city}, Trailing 18 Months'
elif st.session_state['geo_level'] == 'Region':
    df = read_county_data()
    df = df[df['county_name'] == 'Metro']
    title = 'Permits Issued in the 11-County ARC Region, Trailing 18 Months'
elif st.session_state['geo_level'] == 'County':
    df = read_county_data()
    st.write(selected_county)
    df = df[df['county_name'] == selected_county]
    title = f'Permits Issued in {selected_county} County, Trailing 18 Months'

# color map
color_discrete_map = {
    'Single-Family': '#00BFFF',
    'Multi-Family': '#FF6F61'
}

# make sure data is sorted chronologically
df = df.sort_values(by='date', ascending=True)

# create chart object
fig = px.area(
    df,
    x='month_year',
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

# Get every 3rd label from the 'month_year' column
x_labels = df['month_year'].unique()
tickvals = x_labels[::3]  # Show every 3rd label

# update fig layout
fig.update_layout(
    hovermode='x',
    margin=dict(
        t=60,
        r=0
    ),
    legend=dict(
        font_size=16,
        orientation='h',
        entrywidth=120,
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
        tickmode='array',
        tickvals=tickvals,
        tickfont=dict(
            size=16,
            color=font_color
        ),
        gridcolor='#FFFFFF',
        tickangle=90
    ),
    yaxis=dict(
        title='',
        tickfont=dict(
            size=16,
            color=font_color
        ),
        tickformat=','
    ),
    plot_bgcolor='#292929',
    paper_bgcolor='#292929'
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

col1, col2 = st.columns([5, 1])

config = {'displayModeBar': False}
col1.plotly_chart(
    fig,
    config=config,
    theme='streamlit',
    use_container_width=True
)

# KPI section
singleFamily_total = df[df['Series'] ==
                        'Single-Family']['Permits'].sum()
multiFamily_total = df[df['Series'] ==
                       'Multi-Family']['Permits'].sum()

# KPI font variables
heading_font_size = 16
heading_font_weight = 200
heading_font_color = font_color

value_font_size = 22
value_margin_top = 40
value_margin_bottom = 15
value_margin_left = 10
value_font_weight = 700
value_font_color = font_color

border_thickness = 3
top_bottom_padding = 28

col2.write("")
col2.write("")
col2.write("")
col2.write("")
col2.write("")
col2.write("")
col2.write("")

col2.markdown(
    f"""
            <div style='text-align: center; border:{border_thickness}px solid #FF6F61; padding: 6px; padding-bottom: {top_bottom_padding}px; padding-top: {top_bottom_padding}px; border-radius: 8px; line-height: 110%;'>
                <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color}; line-height: 0.5;'>Multi-Family Permits:</span><br/><br/>
                <span style='font-size: {value_font_size}px; font-weight: {value_font_weight}; color: {value_font_color}; margin-top: 0;'>
                {multiFamily_total:,.0f}</span>
            </div>
            """,
    unsafe_allow_html=True
)

col2.write("")
col2.write("")
col2.write("")

col2.markdown(
    f"""
            <div style='text-align: center; border:{border_thickness}px solid #00BFFF; padding: 6px; padding-bottom: {top_bottom_padding}px; padding-top: {top_bottom_padding}px; border-radius: 8px; line-height: 110%;'>
                <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color};'>Single-Family Permits:</span><br/><br/>
                <span style='font-size: {value_font_size}px; font-weight: {value_font_weight}; color: {value_font_color};'>
                {singleFamily_total:,.0f}</span>
            </div>
            """,
    unsafe_allow_html=True
)

# download dataframe as CSV
df = df.sort_values(by='date', ascending=True)
df_download = df.to_csv(index='False').encode('utf-8')

st.download_button(
    label=":material/download:",
    data=df_download,
    file_name='permit_types_monthly.csv',
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
                justify-content: center;
                background-color: #171717;
                border-radius: 7px;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            div[data-baseweb="select"] > div {
                width: 100%;
                background-color: #171717;
                justify-content: center;
                text-align: center;
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
            [data-testid="stAppViewBlockContainer"] {
                margin-top: -50px;
                padding-left: 30px;
                padding-right: 30px;
            }
            [data-testid="stHeader"] {
                color: #292929;
            }
            [data-testid="stDownloadButton"] {
                position: absolute;
                bottom: 10px;
            }
            .main {
                overflow: hidden
            }
        </style>
       """

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)
