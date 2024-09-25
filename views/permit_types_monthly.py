import streamlit as st
import pandas as pd
import plotly.express as px
from utils import county_color_map
from pandas.tseries.offsets import DateOffset

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"  # 'collapsed' or 'expanded'
)


# function definitions to set state variables and query parameters on change
def update_geography():
    st.session_state['geography_3'] = st.session_state['geography_type_input3']
    st.query_params["geo"] = st.session_state['geography_3']


def update_county():
    st.session_state['county3'] = st.session_state['county_input3']
    st.query_params["county"] = st.session_state['county3']


# Initialize session state for the widgets, if not already set
if 'geography_3' not in st.session_state:
    st.session_state['geography_3'] = 'Region'
if 'county3' not in st.session_state:
    st.session_state['county3'] = 'Cobb'

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

column_spacer = 0.001
col1, col2, col3 = st.columns([3, column_spacer, 3])

# permit type select
options = ["Region", "Single county"]

# geography select
with col1:
    st.radio(
        label="Geography level:",
        options=options,
        index=options.index(
            st.session_state['geography_3']),
        key="geography_type_input3",
        on_change=update_geography,
        horizontal=False,
    )

# county select, if applicable
with col3:
    if st.session_state['geography_3'] == 'Region':
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
                st.session_state['county3']),
            placeholder="Choose a county",
            key="county_input3",
            on_change=update_county,
            disabled=False
        )

st.write('')

st.query_params["geo"] = st.session_state['geography_3']


# cache function to read in CSV data for Explore page
@st.cache_data
def read_data():
    monthly_data = pd.read_csv('Data/monthly_file.csv')

    # don't need small-mf, large-mf or total permits
    monthly_data = monthly_data[(monthly_data['Series'] == 'All Single-Family Permits')
                                | (monthly_data['Series'] == 'All Multi-Family Permits')]

    # Dictionary for replacements
    replacements = {
        "All Single-Family Permits": "Single-Family",
        "All Multi-Family Permits": "Multi-Family",
    }

    # Replace substrings using the dictionary
    monthly_data["Series"] = monthly_data["Series"].replace(replacements)

    # cast date column to datetime object
    monthly_data['date'] = pd.to_datetime(monthly_data['date'])

    # Find the most recent date in the dataset
    most_recent_date = monthly_data['date'].max()

    # Subtract 18 months from the most recent date
    eighteen_months_ago = most_recent_date - DateOffset(months=18)

    # Filter the DataFrame for the most recent 18 months
    monthly_filtered = monthly_data[monthly_data['date']
                                    >= eighteen_months_ago]

    # sort the dataframe
    monthly_filtered = monthly_filtered.sort_values(
        by='Series', ascending=False)

    return monthly_filtered


# read in, filter data
df = read_data()

if st.session_state['geography_3'] == 'Region':
    df = df[df['county_name'] == 'Metro']
    title = f'Permits Issued in the 11-County ARC Region, Trailing 18 Months'
    st.query_params["county"] = 'Null'
else:
    df = df[df['county_name'] == st.session_state['county3']]
    title = f'Permits Issued in {st.session_state["county3"]} County, Trailing 18 Months'
    st.query_params["county"] = st.session_state['county3']


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
col2.write("")
col2.write("")
col2.write("")
col2.write("")
col2.write("")
col2.write("")

col2.markdown(
    f"""
            <div style='text-align: center; border:2px solid #FF6F61; padding: 6px; padding-bottom: 10px; border-radius: 7px; line-height: 110%;'>
                <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color}; line-height: 0.5;'>Multi-Family Permits, Trailing 18 Months:</span><br/><br/>
                <span style='font-size: {value_font_size}px; font-weight: {value_font_weight}; color: {value_font_color}; margin-top: 0;'>
                {multiFamily_total:,.0f}</span>
            </div>
            """,
    unsafe_allow_html=True
)

col2.write("")
col2.write("")

col2.markdown(
    f"""
            <div style='text-align: center; border:2px solid #00BFFF; padding: 6px; padding-bottom: 10px; border-radius: 7px; line-height: 110%;'>
                <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color}'>Single-Family Permits, Trailing 18 Months:</span><br/><br/>
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
