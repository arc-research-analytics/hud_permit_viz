import streamlit as st
import pandas as pd
import plotly.express as px
from st_screen_stats import ScreenData

# set page configurations
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)


# using react component to get screen width
screenD = ScreenData(setTimeout=200)
screen_d = screenD.st_screen_data()
screen_width = screen_d['innerWidth']


# cache function to read in CSV data for Overview page
@ st.cache_data
def read_overview_data():
    overview_df = pd.read_csv('Data/metro_total_annual.csv')
    return overview_df


# read in CSV
df = read_overview_data()
permits_avg = df['Permits'].mean()
# permits_total = df['Permits'].sum()

# set font color that will be applied to all text on the page
font_color = "#d9d9d9"


# desktop / tablet view
if screen_width >= 500:

    # dashboard title variables
    title_font_size = 32
    title_margin_top = 40
    title_margin_bottom = 5
    title_margin_left = 10
    title_font_weight = 700
    title_font_color = font_color

    # set title
    st.markdown(
        f"""
        <div style='margin-top: {title_margin_top}px; margin-bottom: {title_margin_bottom}px; margin-left: {title_margin_left}px'>
            <span style='font-size: {title_font_size}px; font-weight: {title_font_weight}; color: {title_font_color}'>Welcome to the Atlanta Building Permit Explorer!</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # dashboard paragraph variables
    paragraph_font_size = 18
    paragraph_margin_top = 0
    paragraph_margin_bottom = 20
    paragraph_margin_left = 10
    paragraph_font_weight = 100
    paragraph_font_color = font_color

    # set paragraph text
    st.markdown(
        f"""
        <div style='margin-top: {paragraph_margin_top}px; margin-bottom: {paragraph_margin_bottom}px; margin-left: {paragraph_margin_left}px;'>
            <span style='font-size: {paragraph_font_size}px; font-weight: {paragraph_font_weight}; color: {paragraph_font_color}'>Like many cities across the nation, Atlanta lacks affordable housing. One primary means to address this shortage is by building more housing units! To provide greater transparency in the crucial permitting process, we have built a tracker for residential building permits issued across the 11-county metro Atlanta region. Explore trend data using the side panel navigation.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # create fig object
    fig = px.line(
        df,
        x='Year',
        y='Permits',
        title='Annual Building Permits Issued in 11-County Metro Region (All Types)',
        height=500
    )

    # update fig layout
    fig.update_layout(
        hovermode='x unified',
        hoverlabel=dict(
            font_size=16,  # this changes the font size of the tooltip
            bgcolor='#292929',
            font_color=font_color
        ),
        title={
            'font': {
                'color': font_color,
                'weight': 'normal'
            }
        },
        xaxis=dict(
            title='',
            tickfont=dict(
                size=16,
                color=font_color
            ),
            gridcolor='#FFFFFF'
        ),
        yaxis=dict(
            title='',
            tickfont=dict(
                size=16,
                color=font_color
            )
        ),
        plot_bgcolor='#292929',
        paper_bgcolor='#292929'
    )

    # customize line trace
    line_color = '#FF6F61'
    fig.update_traces(
        hovertemplate='%{y:,.0f}',
        mode='lines',
        line=dict(
            color=line_color,
            width=4,
            dash='solid'
        )
    )

    # Add a horizontal line at the average value of 'Permits'
    annotation_color = '#00BFFF'
    fig.add_shape(
        type='line',
        x0=df['Year'].min(),
        x1=df['Year'].max(),
        # Position of the line on the y-axis (average 'Permits')
        y0=permits_avg,
        y1=permits_avg,  # Same y0 and y1 to create a horizontal line
        line=dict(
            color=annotation_color,
            width=2,
            dash='dash'
        )
    )

    # Add label annotation for the horizontal average line
    fig.add_annotation(
        x='2017.5',  # Position the text near the end of the line (latest year)
        y=permits_avg,  # Position the text just above the horizontal line
        text="Average since 1980",  # Text to display
        showarrow=False,  # No arrow needed
        yshift=10,  # Shift text upwards by 10 pixels to avoid overlapping with the line
        font=dict(
            color=annotation_color,
            size=16,
            weight='bold'
        )
    )

    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=font_color
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=font_color,
        showgrid=False
    )

    config = {'displayModeBar': False}
    st.plotly_chart(
        fig,
        config=config,
        theme='streamlit',
        use_container_width=True
    )

    # the custom CSS for desktop lives here:
    hide_default_format = """
        <style>
            [data-testid="stAppViewBlockContainer"] {
                margin-top: -100px;
                padding-left: 40px;
                padding-right: 50px;
            }
            .main {
                overflow: hidden;
            }
        </style>
       """

    # inject the CSS
    st.markdown(hide_default_format, unsafe_allow_html=True)

# mobile view
else:
    st.markdown(
        '<div style="text-align: center; margin-top: 0px; margin-bottom: -40px;"><p>Welcome to the Atlanta Building Permit Explorer!</p></div>', unsafe_allow_html=True)

    # create fig object
    fig = px.line(
        df,
        x='Year',
        y='Permits',
        title='Building Permits <br>Issued in 11-County<br> Region (All Types)',
        height=300
    )

    # update fig object
    fig.update_layout(
        title={
            'text': 'Building Permits Issued in 11-<br>County Region (All Types)',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 13}
        },
        xaxis_title=None,
        yaxis={
            'dtick': 20000
        },
        yaxis_title=None
    )

    # customize line trace
    line_color = '#FF6F61'
    fig.update_traces(
        hovertemplate='%{y:,.0f}',
        mode='lines',
        line=dict(
            color=line_color,
            width=2,
            dash='solid'
        )
    )

    # Add a horizontal line at the average value of 'Permits'
    annotation_color = '#00BFFF'
    fig.add_shape(
        type='line',
        x0=df['Year'].min(),
        x1=df['Year'].max(),
        # Position of the line on the y-axis (average 'Permits')
        y0=permits_avg,
        y1=permits_avg,  # Same y0 and y1 to create a horizontal line
        line=dict(
            color=annotation_color,
            width=1,
            dash='dash'
        )
    )

    # draw fig object
    config = {'displayModeBar': False}
    st.plotly_chart(
        fig,
        config=config,
        theme='streamlit',
        use_container_width=True
    )

    st.markdown(
        f'<div style="text-align: left; margin-top: -65px;"><p style="color:{annotation_color}; font-size: 14px;"><b>Blue line</b> = historic average of permits issued since 1980.</p></div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align: left; margin-top: -20px;"><p>Explore trends in single- and multi-family building permits issued in Atlanta-area jurisdictions by using expandable side-panel navigation menu.</p></div>', unsafe_allow_html=True)

    # closing remarks
    st.markdown(
        '<div style="text-align: left; margin-top: 5px;"><p><b>Note:</b> This app is not optimized for mobile screens. For the best user experience, please use on a desktop or tablet!</p></div>', unsafe_allow_html=True)

    # the custom CSS for mobile lives here:
    hide_default_format = """
        <style>
            [data-testid="stAppViewBlockContainer"] {
                margin-top: -50px;
                padding-left: 40px;
                padding-right: 50px;
                height: 100%;
            }
            [data-testid="stDownloadButton"] {
                position: absolute;
                left: 1050px;
                top: -695px;
            }
        </style>
       """

    # inject the CSS
    st.markdown(hide_default_format, unsafe_allow_html=True)
