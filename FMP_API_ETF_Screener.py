import streamlit as st 
from openbb_terminal.sdk import openbb
import pandas as pd
import plotly.express as px
import requests
import datetime
from st_aggrid import AgGrid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import altair as alt
from dotenv import load_dotenv
import os
import fmpsdk as fmp

load_dotenv()

# FMP API Key
fmpkey = os.getenv('fmp_api_key')

st.set_page_config(layout="wide")
st.title('ETF Screener')

st.subheader('Search for Symbol')

etf_list = f"https://financialmodelingprep.com/api/v3/etf/list?apikey={os.getenv('fmp_api_key')}"
response = requests.get(etf_list).json()
etfdf = pd.DataFrame(response)

search_by = st.radio("Search by:", ('Symbol', 'Name'))

if search_by == 'Symbol':
    options = etfdf['symbol'].unique()
    selected_etf = st.selectbox('Enter symbol of ETF (ALL CAPS)', options, index=options.tolist().index('SPY'))
    filtered_ticker = etfdf[etfdf['symbol'] == selected_etf]
else:
    options = etfdf['name'].unique()
    selected_etf = st.selectbox('Start typing name of ETF', options, index=options.tolist().index('SPDR S&P 500 ETF Trust'))
    filtered_ticker = etfdf[etfdf['name'] == selected_etf]

if not filtered_ticker.empty:
    st.dataframe(filtered_ticker, use_container_width=True)  
    etf_ticker = filtered_ticker['symbol'].values[0]
    ticker = etf_ticker
else:
    st.warning("No ETFs found for the selected search criteria.")

col1, col2 = st.columns(2)

with col1:
        if ticker:
                st.subheader('Sector Weightings')

        sector = f"https://financialmodelingprep.com/api/v3/etf-sector-weightings/{ticker}?apikey={os.getenv('fmp_api_key')}"
        response = requests.get(sector).json()

        df = pd.DataFrame(response)

        try:
                df['weightPercentage'] = df['weightPercentage'].str.replace('%', '').astype(float)
        except KeyError:
                st.warning('No sector weightings found for this ETF')
        else:
                fig = px.pie(df, values='weightPercentage', names='sector', height=500, width=500)

                st.plotly_chart(fig)

with col2:    
        st.subheader('Country Weightings')

        country = f"https://financialmodelingprep.com/api/v3/etf-country-weightings/{ticker}?apikey={os.getenv('fmp_api_key')}"
        response = requests.get(country).json()
        
        df = pd.DataFrame(response)

        try:
                df['weightPercentage'] = df['weightPercentage'].str.replace('%', '').astype(float)
        except KeyError:
                st.warning('No country weightings found for this ETF')
        else:
                fig = px.pie(df, values='weightPercentage', names='country', height=500, width=500)

                st.plotly_chart(fig)


holdings_date=f"https://financialmodelingprep.com/api/v4/etf-holdings/portfolio-date?symbol={ticker}&apikey={os.getenv('fmp_api_key')}"
response = requests.get(holdings_date).json()
holdings_date = pd.DataFrame(response)

options = holdings_date['date'].unique()

selected_option = st.sidebar.selectbox('Select Holdings Date', options)

# Filter each table and chart based on the selected option
filtered_date = holdings_date[holdings_date['date'] == selected_option]

date_str = filtered_date.iloc[0]['date']
date = pd.to_datetime(date_str).strftime('%Y-%m-%d')

symbol: str = ticker

holdings_url = f"https://financialmodelingprep.com/api/v4/etf-holdings?symbol={symbol}&date={date}&apikey={os.getenv('fmp_api_key')}"
response = requests.get(holdings_url).json()
holdings = pd.DataFrame(response)

# Sort the holdings by pctVal in descending order
sorted_holdings = holdings.sort_values(by='pctVal', ascending=False)

# Select the top 20 holdings
top_50_holdings = sorted_holdings.head(50)

top_50_holdings['pctVal'] = top_50_holdings['pctVal'].astype(float).round(6)

chart = alt.Chart(top_50_holdings).mark_bar().encode(
    x=alt.X('name', sort='-y', axis=alt.Axis(labelAngle=270)),
    y=alt.Y('pctVal'),
    color=alt.Color('name:N', legend=None),
)
            
chart = chart.properties(
        title=('Top 50 Holdings'),
        width=alt.Step(90),
        height=alt.Step(70)

        ).configure_axis(
        labelFontSize=10,
        titleFontSize=14    
        )

st.altair_chart(chart, use_container_width=True)

st.subheader('All Holdings')
st.write(holdings[['date','symbol','name', 'cur_cd', 'title', 'cusip','valUsd', 'pctVal']])  

#Returns
price = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={os.getenv('fmp_api_key')}"
response = requests.get(price).json()
historical = response['historical']
df = pd.DataFrame(historical)


df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
df.sort_index(ascending=True, inplace=True)

daily_returns = df.pct_change()

#One Year:
One_Year = float((df.iloc[-1] - df.iloc[-252]) / df.iloc[-252])
st.write("1 Year Return: {:.2f}%".format(One_Year * 100))

#3 Year
if len(df) >= 758:
    Three_Year = float((df.iloc[-1] - df.iloc[-758]) / df.iloc[-758])
    annualized_return=((1 + Three_Year)**(1/3))-1
    st.write("3 Year Return: {:.2f}%".format(annualized_return * 100))
else:
    st.write()

#5 Year
if len(df) >= 1260:
    Five_Year = float((df.iloc[-1] - df.iloc[-1260]) / df.iloc[-1260])
    annualized_return=((1 + Five_Year)**(1/5))-1
    st.write("5 Year Return: {:.2f}%".format(annualized_return * 100))
else:
    st.write()

#10 Year
if len(df) >= 2520:
    Ten_Year = float((df.iloc[-1] - df.iloc[-2520]) / df.iloc[-2520])
    annualized_return=((1 + Ten_Year)**(1/10))-1
    st.write("10 Year Return: {:.2f}%".format(annualized_return * 100))
else:
    st.write()


#Inception
annualized_return = float(daily_returns.mean() * 252)
st.write("Since Inception Return:" " {:.2f}%".format(annualized_return * 100))

#Mountain Chart
st.subheader('Since Inception')
# Retrieve the historical data

price = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={os.getenv('fmp_api_key')}"
response = requests.get(price).json()
historical = response['historical']
df = pd.DataFrame(historical)

# Add transparency to the area chart
st.line_chart(data=df, x='date', y='close', width=1000, height=0, use_container_width=True)
