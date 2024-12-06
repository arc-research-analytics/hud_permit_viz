import streamlit as st
import pandas as pd
import plotly.express as px
from utils import county_color_map, city_list
from pandas.tseries.offsets import DateOffset
from st_screen_stats import ScreenData

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"  # 'collapsed' or 'expanded'
)

# using react component to get screen width
screenD = ScreenData(setTimeout=200)
screen_d = screenD.st_screen_data()
screen_width = screen_d['innerWidth']

# Initialize session state for the widgets, if not already set
if 'geography_3' not in st.session_state:
    st.session_state['geography_3'] = 'Region'
if 'geo_level' not in st.session_state:
    st.session_state['geo_level'] = 'Region'
if 'chart_var' not in st.session_state:
    st.session_state['chart_var'] = 'count'

st.query_params['geo'] = st.session_state['geography_3']
st.query_params['var'] = st.session_state['chart_var']


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

column_spacer = .1
col1, col_spacer, col2, = st.columns(
    [3, column_spacer, 3])

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
    if geo_level == 'Region':
        st.selectbox(
            label='County:',
            options=['Region'],
            placeholder='N/A',
            disabled=True
        )
    elif geo_level == 'County':
        selected_county = st.selectbox(
            label='County:',
            options=list(county_color_map.keys()),
            index=7,
            key="county",
            placeholder="Choose a county",
            on_change=lambda: st.session_state.update({
                'geography_3': st.session_state['county'],
            })
        )
    elif geo_level == 'City':
        selected_city = st.selectbox(
            label='City:',
            options=city_list,
            index=2,
            placeholder="Choose a city",
            key="city",
            on_change=lambda: st.session_state.update({
                'geography_3': st.session_state['city'],
            })
        )

st.write('')


@st.cache_data
def read_master_data():
    master_data = pd.read_csv('Data/monthly_master.csv')
    return master_data


df = read_master_data()
df = df.sort_values(by='Series', ascending=False)
df = df.sort_values(by=['year_month', 'Name'], ascending=True)

# conditionally read in data based on user input
if geo_level == 'City':
    df = df[df['Level'] == 'City/Other']
    if isinstance(selected_city, list):
        selected_city = selected_city[0]
    df = df[df['Name'] == selected_city]
    title = f'Permits Issued in City of {selected_city}, Trailing 18 Months'
    download_file_name = f'{selected_city}_monthly_trends.csv'
elif geo_level == 'Region':
    df = df[df['Name'] == 'Metro']
    title = 'Permits Issued in the 11-County ARC Region, Trailing 18 Months'
    download_file_name = 'Regional_monthly_trends.csv'
elif geo_level == 'County':
    df = df[df['Level'] == 'County']
    if isinstance(selected_county, list):
        selected_county = selected_county[0]
    df = df[df['Name'] == selected_county]
    title = title = f'Permits Issued in {selected_county} County, Trailing 18 Months'
    download_file_name = f'{selected_county}County_monthly_trends.csv'

# color map
color_discrete_map = {
    'Single-Family': '#00BFFF',
    'Multi-Family': '#FF6F61'
}

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

# Get every nth label from the x values
x_labels = df['date'].unique()
tickvals = x_labels[::3]

# desktop / tablet view
if screen_width >= 500:

    # create chart object
    fig = px.area(
        df,
        x='date',
        y='Permits',
        title=title,
        line_group='Series',
        color='Series',
        color_discrete_map=color_discrete_map,
        height=545
    )

    # update fig layout
    fig.update_layout(
        hovermode='x',
        margin=dict(
            t=60,
            r=15
        ),
        legend=dict(
            font_size=14,
            orientation='h',
            title_text="",
            yanchor="bottom",
            y=0.97,
            xanchor="left",
            bgcolor="rgba(41,41,41,0)",
            traceorder="reversed"
        ),
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
            tickangle=0
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

    mf_kpi_title = "Multi-Family Permits:"
    sf_kpi_title = "Single-Family Permits:"

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
                    <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color}; line-height: 0.5;'>{mf_kpi_title}</span><br/><br/>
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
                    <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color};'>{sf_kpi_title}</span><br/><br/>
                    <span style='font-size: {value_font_size}px; font-weight: {value_font_weight}; color: {value_font_color};'>
                    {singleFamily_total:,.0f}</span>
                </div>
                """,
        unsafe_allow_html=True
    )

    # download dataframe as CSV
    df = df.sort_values(by='date', ascending=True)
    df = df[[
        'year_month',
        'Name',
        'Series',
        'Permits'
    ]]

    df_download = df.to_csv(index='False').encode('utf-8')

    st.download_button(
        label=":material/download:",
        data=df_download,
        file_name=download_file_name,
        help='Download filtered data to CSV'
    )

    # the custom CSS lives here:
    hide_default_format_desktop = """
            <style>
                [data-testid="stMainBlockContainer"] {
                    margin-top: -70px;
                    padding-left: 30px;
                    padding-right: 30px;
                }
                .main {
                    overflow: hidden
                }
            </style>
        """

    # inject the CSS
    st.markdown(hide_default_format_desktop, unsafe_allow_html=True)


# mobile view
else:
    df_sf = df[df['Series'] == 'Single-Family']
    df_mf = df[df['Series'] == 'Multi-Family']

    total_mf_permits = df_mf['Permits'].sum()
    total_sf_permits = df_sf['Permits'].sum()

    # get data for most recent month
    max_date = df['year_month'].max()
    max_date_label = df.loc[df['year_month'] == max_date, 'date'].iloc[0]
    max_date_SFpermits = df_sf.loc[df_sf['year_month']
                                   == max_date, 'Permits'].iloc[0]
    max_date_MFpermits = df_mf.loc[df_mf['year_month']
                                   == max_date, 'Permits'].iloc[0]

    # get data for 1 year ago
    min_date = df_sf.sort_values(by='year_month', ascending=False)[
        'year_month'].iloc[12]
    min_date_label = df_sf.loc[df_sf['year_month'] == min_date, 'date'].iloc[0]
    min_date_SFpermits = df_sf.loc[df_sf['year_month']
                                   == min_date, 'Permits'].iloc[0]
    min_date_MFpermits = df_mf.loc[df_mf['year_month']
                                   == min_date, 'Permits'].iloc[0]

    # calculate YoY values for multi-family
    if max_date_MFpermits > 0 and min_date_MFpermits > 0:
        YoYchange_MF = ((max_date_MFpermits-min_date_MFpermits) /
                        min_date_MFpermits)*100
    else:
        YoYchange_MF = "I am a string value!"

    # calculate YoY values for single-family
    if max_date_SFpermits > 0 and min_date_SFpermits > 0:
        YoYchange_SF = ((max_date_SFpermits-min_date_SFpermits) /
                        min_date_SFpermits)*100
    else:
        YoYchange_SF = "I am a string value!"

    st.divider()

    # MF heading
    st.markdown(f'''
        <p style="font-size: 20px; font-weight: 600; text-align: center; color: #FF6F61">
            Multi-Family Permits
        </p>
    ''', unsafe_allow_html=True)

    # 18-month total
    st.markdown(f'''
        <p style="font-size: 16px; font-weight: 100; text-align: center;">
            Trailing 18-Month Total: {total_mf_permits:,.0f}
        </p>
    ''', unsafe_allow_html=True)

    # monthly for most recent date
    st.markdown(f'''
        <p style="font-size: 16px; font-weight: 100; text-align: center;">
            {max_date_label} Total: {max_date_MFpermits:,.0f}
        </p>
    ''', unsafe_allow_html=True)

    if isinstance(YoYchange_MF, float):
        direction = "downward" if YoYchange_MF < 0 else "upward"
        color = "red" if YoYchange_MF < 0 else "green"
        upward_arrow = st.markdown(
            f"12-Month YoY Change: {YoYchange_MF:.1f}% :{color}[:material/arrow_{direction}:]")

    elif isinstance(YoYchange_MF, str):
        st.markdown(f'''
            <p style="font-size: 16px; font-weight: 100; text-align: center;">
                Insufficient data to calculate YoY change.
            </p>
    ''', unsafe_allow_html=True)

    st.divider()

    # SF heading
    st.markdown(f'''
        <p style="font-size: 20px; font-weight: 600; text-align: center; color: #00BFFF">
            Single-Family Permits
        </p>
    ''', unsafe_allow_html=True)

    # 18-month total
    st.markdown(f'''
        <p style="font-size: 16px; font-weight: 100; text-align: center;">
            Trailing 18-Month Total: {total_sf_permits:,.0f}
        </p>
    ''', unsafe_allow_html=True)

    # monthly for most recent date
    st.markdown(f'''
        <p style="font-size: 16px; font-weight: 100; text-align: center;">
            {max_date_label} Total: {max_date_SFpermits:,.0f}
        </p>
    ''', unsafe_allow_html=True)

    if isinstance(YoYchange_SF, float):
        direction = "downward" if YoYchange_SF < 0 else "upward"
        color = "red" if YoYchange_SF < 0 else "green"
        upward_arrow = st.markdown(
            f"12-Month YoY Change: {YoYchange_SF:.1f}% :{color}[:material/arrow_{direction}:]")

    elif isinstance(YoYchange_SF, str):
        st.markdown(f'''
            <p style="font-size: 16px; font-weight: 100; text-align: center;">
                Insufficient data to calculate YoY change.
            </p>
    ''', unsafe_allow_html=True)

    # the custom CSS lives here:
    hide_default_format_mobile = """
            <style>
                [data-testid="stMainBlockContainer"] {
                    margin-top: -30px;
                    padding-left: 30px;
                    padding-right: 30px;
                }
                [data-testid="stMarkdown"] {
                    text-align: center;
                }
            </style>
        """

    # inject the CSS
    st.markdown(hide_default_format_mobile, unsafe_allow_html=True)

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
            [data-baseweb="select"] > div {
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
