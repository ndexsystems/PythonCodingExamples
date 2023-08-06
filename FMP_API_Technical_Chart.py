from openbb_terminal.sdk import openbb
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
from dotenv import load_dotenv
import os
load_dotenv()

# FMP API Key
fmpkey = os.getenv('fmp_api_key')

ticker = st.text_input('Symbol')
if not ticker:
    ticker = 'AAPL'

def color_negative_red(val):
    if type(val) != 'str':
        color = 'green' if val >0 else 'red'
        return f'color: {color}'

ma1=10
ma2=30
days_to_plot=120

def get_candlestick_plot(
        df: pd.DataFrame,
        ma1: int,
        ma2: int,
        ticker: str,
        transaction_dates_sales: list = [],
        transaction_dates_purchases: list = []
):
    
    #Create the candlestick chart with two moving avgs + a plot of the volume
    #Parameters

    df : pd.DataFrame
    #The price dataframe
    ma1 : int
    #The length of the first moving average (days)
    ma2 : int
    #The length of the second moving average (days)
    ticker : str
    #The ticker we are plotting (for the title).

    
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.1,
        subplot_titles = (f'{ticker} Stock Price', 'Volume Chart'),
        row_width = [0.3, 0.7],
        row_heights=150
    )
    
    fig.add_trace(
        go.Candlestick(
            x = df['Date'],
            open = df['Open'], 
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            name = 'Candlestick chart'
        ),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
    go.Scatter(x = df['Date'], y = df[f'{ma1}_ma'], mode='lines', name = f'{ma1} SMA'),
    row = 1,
    col = 1,
)

    fig.add_trace(
    go.Scatter(x = df['Date'], y = df[f'{ma2}_ma'], mode='lines', name = f'{ma2} SMA'),
    row = 1,
    col = 1,
)


    for data in transaction_dates_sales:
        fig.add_vline(x=data, line_width=1, line_color="red")

    for data in transaction_dates_purchases:
        fig.add_vline(x=data, line_width=1, line_color="green")
    
    fig.add_trace(
        go.Bar(x = df['Date'], y = df['Volume'], name = 'Volume'),
        row = 2,
        col = 1,
    )
    
    fig['layout']['xaxis2']['title'] = 'Date'
    fig['layout']['yaxis']['title'] = 'Price'
    fig['layout']['yaxis2']['title'] = 'Volume'
    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )

    return fig

if ticker:
        data = openbb.stocks.load(ticker)

        if len(data)>0:
            
            df = data.reset_index()
            df.columns = [x.title() for x in df.columns]

            df[f'{ma1}_ma'] = df['Close'].rolling(ma1).mean()
            df[f'{ma2}_ma'] = df['Close'].rolling(ma2).mean()
            df = df[-days_to_plot:]

            # Display the plotly chart on the dashboard
            st.plotly_chart(
                get_candlestick_plot(df, ma1, ma2, ticker),
                width=0, height=0,
                use_container_width = True,
            )


url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)
st.write(df.style.applymap(color_negative_red, subset=['changesPercentage']))


url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)
st.write(df)

url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?limit=40&apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)
st.write(df)


url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)
st.write(df)
