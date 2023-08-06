from openbb_terminal.sdk import openbb
import streamlit as st
import datetime
import pandas as pd
import altair as alt
from st_aggrid import AgGrid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
import os
from dotenv import load_dotenv
load_dotenv()

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
formatted_date = yesterday.strftime('%Y-%m-%d')

# FMP API Key
fmpkey = os.getenv('fmp_api_key')

# Get data
url = f"https://financialmodelingprep.com/api/v3/quotes/index?apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)

# Create a sidebar selectbox for choosing the name of the index
index_name = st.sidebar.selectbox("Select Index Name", df["name"].unique())

# Filter dataframe to only include the selected index
df_filtered = df[df["name"] == index_name]

# Define columns to use for the bar chart and their labels
columns = ["price", "yearHigh", "yearLow", "priceAvg50", "priceAvg200"]
labels = ["Price", "Year High", "Year Low", "50-day Moving Average", "200-day Moving Average"]

# Convert data to long format
df_long = pd.melt(df_filtered, id_vars=["symbol", "name"], value_vars=columns, var_name="metric", value_name="value")
df_long['value'] = df_long['value'].astype(float).round(2)

col1, col2, col3 = st.columns([5,1,5])

with col1:
    chart = alt.Chart(df_long).mark_bar().encode(
        alt.X("metric:N", axis=alt.Axis(title="Metric", labelAngle=0)),
        alt.Y("value:Q", axis=alt.Axis(title="Value")),
        alt.Color("metric:N", scale=alt.Scale(scheme="set2"), legend=None),
        
    ).properties(
        width=600,
        height=400,
        title=f"{index_name} Index Values"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    # Display chart
    st.altair_chart(chart, use_container_width=True)


with col3:
    st.write(df_long.style.set_properties(**{'text-align': 'center'}))  

col1, col2 = st.columns(2)

with col2: 
    url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?date={formatted_date}&exchange=NYSE&apikey={os.getenv('fmp_api_key')}"
    response = requests.get(url).json()
    df = pd.DataFrame(response)

    df['pe'] = df['pe'].astype(float).round(2)

    chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('sector', sort='y',axis=alt.Axis(labelAngle=270)),
            y=alt.Y('pe'),
            color = alt.Color('sector:N', legend = None),
            )    

    chart = chart.properties(
            title=('Sector PE Ratio'),
            width=alt.Step(90),
            height=alt.Step(70)

        ).configure_axis(
            labelFontSize=10,
            titleFontSize=14    
        )

    st.altair_chart(chart, use_container_width=True)

with col1:
    url = f"https://financialmodelingprep.com/api/v3/sector-performance?apikey={os.getenv('fmp_api_key')}"
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    
    to_float = lambda x: round(float(x.strip('%')) / 100.0, 4)
    df['% Change'] = df['changesPercentage'].apply(to_float)

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('sector', sort='y', axis=alt.Axis(labelAngle=270)),
        y=alt.Y('% Change', axis=alt.Axis(format='%')),
    color=alt.condition(
        alt.datum.Return > 0,
        alt.value('green'),
        alt.value('red'),
    )
    ).properties(
        title='Sector Performance'
    )
    
    st.altair_chart(chart, use_container_width=True)

url = f"https://financialmodelingprep.com/api/v4/industry_price_earning_ratio?date={formatted_date}&exchange=NYSE&apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)
df['pe'] = df['pe'].astype(float).round(2)

chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('industry', sort='y',axis=alt.Axis(labelAngle=270)),
        y=alt.Y('pe'),
        color = alt.Color('industry:N', legend = None),
          )    

chart = chart.properties(
        title=('Industry PE Ratio'),
        width=alt.Step(90),
        height=alt.Step(70)

    ).configure_axis(
        labelFontSize=10,
        titleFontSize=14    
    )

st.altair_chart(chart, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('SP500')
    st.subheader('S&P 500')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

with col2:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('DJIA')
    st.subheader('Dow Jones')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('NASDAQCOM')
    st.subheader('Nasdaq')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

with col2:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('DGS10')
    st.subheader('10 Year Treasury')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('BAMLCC0A0CMTRIV')
    st.subheader('Corporate Bond Total Market')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

with col2:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('GFDEGDQ188S')
    st.subheader('Debt to GDP')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('FDHBFRBN')
    st.subheader('Debt Held By Fed Banks')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

with col2:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('FYGDP')
    st.subheader('GDP')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('FYOINT')
    st.subheader('Fed Interest Payments')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)

with col2:
    from fredapi import Fred
    fred = Fred(api_key=os.getenv('fred_api'))
    data = fred.get_series('CPIAUCSL')
    st.subheader('CPI All Urban Consumers')
    st.line_chart(data=data,  x=None, y=None, width=0, height=0, use_container_width=True)