from openbb_terminal.sdk import openbb
import streamlit as st
import datetime
import pandas as pd
from st_aggrid import AgGrid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import altair as alt
from fmp_python.fmp import FMP
from dotenv import load_dotenv
import os
load_dotenv()

# FMP API Key
fmpkey = os.getenv('fmp_api_key')

st.subheader('Biggest Gainers')
gainers= f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={os.getenv('fmp_api_key')}"
response = requests.get(gainers).json()
df = pd.DataFrame(response)

chart = alt.Chart(df).mark_bar().encode(
        x= alt.X('name', sort='y', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('changesPercentage'),
        color = alt.Color('name:N', legend = None),
        
        )

chart = chart.properties(
        title=('Gainers'),
        width=alt.Step(90),
        height=alt.Step(20)

    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14    
    )

st.altair_chart(chart, use_container_width=True)

st.subheader('Biggest Losers')
losers= f"https://financialmodelingprep.com/api/v3/stock_market/losers?apikey={os.getenv('fmp_api_key')}"
response = requests.get(losers).json()
df = pd.DataFrame(response)

chart = alt.Chart(df).mark_bar().encode(
        x= alt.X('name', sort='y', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('changesPercentage'),
        color = alt.Color('name:N', legend = None),
        
        )

chart = chart.properties(
        title=('Losers'),
        width=alt.Step(90),
        height=alt.Step(20)

    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14    
    )

st.altair_chart(chart, use_container_width=True)
