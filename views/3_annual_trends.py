import streamlit as st
import pandas as pd
import plotly.express as px
from utils import county_color_map, city_list
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
if 'geography_2' not in st.session_state:
    st.session_state['geography_2'] = 'Region'
if 'geo_level_2' not in st.session_state:
    st.session_state['geo_level_2'] = 'Region'

st.query_params['geo'] = st.session_state['geography_2']


# function definitions to set state variables and query parameters on change
def update_geography():
    st.session_state['geo_level_2'] = st.session_state['geography_type_input2']
    if st.session_state['geo_level_2'] == 'Region':
        st.session_state['geography_2'] = 'Region'
    elif st.session_state['geo_level_2'] == 'County':
        st.session_state['geography_2'] = list(county_color_map.keys())[7]
    elif st.session_state['geo_level_2'] == 'City':
        st.session_state['geography_2'] = city_list[2]

    # update only 'geo' query param to reflect selected geography
    st.query_params['geo'] = st.session_state['geography_2']


# set font color that will be applied to all text on the page
font_color = "#d9d9d9"

# dashboard title variables
title_font_size = 24
title_margin_bottom = 15
title_font_weight = 700
title_font_color = font_color

# desktop
if screen_width >= 500:
    title_margin_top = -10

# mobile
else:
    title_margin_top = 20

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
options = ["Region", "County", "City"]

with col1:
    geo_level = st.radio(
        label="Geography level:",
        options=options,
        index=options.index(st.session_state['geo_level_2']),
        key="geography_type_input2",
        on_change=update_geography,
        horizontal=True,
    )

# county select, if applicable
with col3:
    if st.session_state['geo_level_2'] == 'Region':
        st.selectbox(
            label='County:',
            options=['N/A', 'other'],
            placeholder='N/A',
            disabled=True
        )
    elif st.session_state['geo_level_2'] == 'County':
        county_index = list(county_color_map.keys()).index(
            st.session_state['geography_2']
        )
        selected_county = st.selectbox(
            label='County:',
            options=list(county_color_map.keys()),
            index=county_index,
            placeholder="Choose a county",
            key="county2",
            on_change=lambda: st.session_state.update({
                'geography_2': st.session_state['county2'],
            })
        )
    elif st.session_state['geo_level_2'] == 'City':
        city_index = city_list.index(st.session_state['geography_2'])
        selected_city = st.selectbox(
            label='City:',
            options=city_list,
            index=city_index,
            placeholder="Choose a city",
            key="city2",
            on_change=lambda: st.session_state.update({
                'geography_2': st.session_state['city2'],
            })
        )


# starting year select
with col5:
    slider_value = st.slider(
        label="Issued since:",
        min_value=1980,
        max_value=2023,
        value=1985,
        # key="starting_year_input",
    )


st.query_params["year"] = slider_value


# cache function to read in CSV data for Explore page
@st.cache_data
def read_county_data():
    drilldown_df = pd.read_csv('Data/annual_county.csv')

    # don't need the 'All' totals for the annual trends page
    drilldown_df = drilldown_df[drilldown_df['Series'] != 'All']

    # sort the dataframe
    drilldown_df = drilldown_df.sort_values(by='Series', ascending=False)

    return drilldown_df


@st.cache_data
def read_city_data():
    drilldown_df = pd.read_csv('Data/annual_city.csv')

    # sort the dataframe
    drilldown_df = drilldown_df.sort_values(by='Series', ascending=False)

    return drilldown_df


if geo_level == 'Region':
    df = read_county_data()
    df = df[df['county_name'] == 'Metro']
    title = f'Permits Issued in the 11-County ARC Region Since {slider_value}'
    download_file_name = 'Regional_monthly_trends.csv'
elif geo_level == 'County':
    df = read_county_data()
    df = df[df['county_name'] == selected_county]
    title = f'Permits Issued in {selected_county} County Since {slider_value}'
    download_file_name = f'{selected_county}County_annual_trends.csv'
elif geo_level == 'City':
    df = read_city_data()
    df = df[df['City'] == selected_city]
    title = f'Permits Issued in City of {selected_city} Since {slider_value}'
    download_file_name = f'{selected_city}County_annual_trends.csv'

df = df[df['Year'] >= slider_value]

# color map
color_discrete_map = {
    'Single-family': '#00BFFF',
    'Multi-family': '#FF6F61'
}

# chart config, same for desktop and mobile
config = {'displayModeBar': False}

# desktop / tablet view
if screen_width >= 500:

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
            font_size=14,
            orientation='h',
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

    st.write("")

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
        file_name=download_file_name,
        help='Download filtered data to CSV'
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
                    padding-left: 9px;
                    width: 100%;
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

# mobile view
else:

    # # create chart object
    # fig = px.area(
    #     df,
    #     x='Year',
    #     y='Permits',
    #     line_group='Series',
    #     color='Series',
    #     labels={
    #         'county_name': 'County',
    #     },
    #     color_discrete_map=color_discrete_map,
    #     height=300
    # )

    # # update fig layout
    # fig.update_layout(
    #     hovermode='x',
    #     margin=dict(
    #         t=60,
    #         l=0,
    #         r=10
    #     ),
    #     legend=dict(
    #         orientation='h',
    #         entrywidth=100,
    #         title_text="",
    #         yanchor="bottom",
    #         y=0.07,
    #         xanchor="left",
    #         bgcolor="rgba(41,41,41,0)"
    #     ),
    #     legend_traceorder="reversed",
    #     xaxis=dict(
    #         title='',
    #         tickfont=dict(
    #             size=16,
    #             color=font_color
    #         ),
    #         dtick=15,
    #         gridcolor='#FFFFFF',
    #     ),
    #     yaxis=dict(
    #         title='',
    #         tickfont=dict(
    #             size=16,
    #             color=font_color
    #         ),
    #         tickformat=',',
    #     ),
    #     plot_bgcolor='#292929',
    #     paper_bgcolor='#292929'
    # )

    # # configure tooltip
    # fig.update_traces(
    #     hovertemplate='<b>%{y}</b>',
    #     mode='lines',
    #     line=dict(
    #         width=2,
    #         dash='solid'
    #     ),
    #     hoverlabel=dict(
    #         font_color='#171717'
    #     )
    # )

    # for trace in fig.data:
    #     trace.hoverlabel.bgcolor = color_discrete_map[trace.name]

    # fig.update_xaxes(
    #     showline=True,
    #     linewidth=1,
    #     linecolor=font_color,
    #     showgrid=False,
    # )
    # fig.update_yaxes(
    #     showline=True,
    #     linewidth=1,
    #     linecolor=font_color,
    #     showgrid=False,
    #     zeroline=False
    # )

    # st.plotly_chart(
    #     fig,
    #     config=config,
    #     theme='streamlit',
    #     use_container_width=True
    # )

    # For mobile, will only be showing the KPI boxes
    st.divider()

    mf_total = df[df['Series'] == 'Multi-family']['Permits'].sum()
    sf_total = df[df['Series'] == 'Single-family']['Permits'].sum()

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
    top_bottom_padding = 19

    if geo_level == 'City':
        kpi_geo = f'the City of {selected_city}'
    elif geo_level == 'County':
        kpi_geo = f'{selected_county} County'
    else:
        kpi_geo = 'the Metro Region'

    # Multi-Family Permit Historic KPI
    st.markdown(f'''
        <p style="font-size: 20px; font-weight: 900; text-align: center;">
            <span style="color: #FF6F61;">Multi-Family</span> Permits Issued in {kpi_geo} Since {slider_value}:
        </p>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
        <p style='font-size: 22px; font-weight: 900; color: #d9d9d9; text-align: center;'>
            {mf_total:,.0f}
        </p>
        ''', unsafe_allow_html=True)

    st.write('')
    st.write('')

    # Single-Family Permit Historic KPI
    st.markdown(f'''
        <p style="font-size: 20px; font-weight: 900; text-align: center;">
            <span style="color: #00BFFF;">Single-Family</span> Permits Issued in {kpi_geo} Since {slider_value}:
        </p>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
        <p style='font-size: 22px; font-weight: 900; color: #d9d9d9; text-align: center;'>
            {sf_total:,.0f}
        </p>
        ''', unsafe_allow_html=True)

    # # Single-Family Permit KPI box
    # st.markdown(
    #     f"""
    #         <div style='text-align: center; border:{border_thickness}px solid #00BFFF;        padding: 6px; padding-bottom: {top_bottom_padding}px; padding-top: {top_bottom_padding}px; border-radius: 8px; line-height: 110%;'>
    #             <span style='font-size: {heading_font_size}px; font-weight: {heading_font_weight}; color: {title_font_color}; line-height: 25px;'>Single-Family<br/> Permits Issued:</span><br/><br/>
    #             <span style='font-size: {value_font_size}px; font-weight: {value_font_weight}; color: {value_font_color};'>
    #             {sf_total:,.0f}</span>
    #         </div>
    #         """,
    #     unsafe_allow_html=True
    # )

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
                    justify-content: right;
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
                [data-testid="stMainBlockContainer"] {
                    margin-top: -50px;
                    padding-left: 40px;
                    padding-right: 40px;
                }
                [data-testid="stHeader"] {
                    color: #292929;
                }
            </style>
        """

    # inject the CSS
    st.markdown(hide_default_format, unsafe_allow_html=True)
