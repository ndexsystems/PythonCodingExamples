import os
import pandas as pd
from fredapi import Fred
import streamlit as st
from dotenv import load_dotenv
import numpy as np
import altair as alt
import plotly.graph_objects as go
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv
import requests

load_dotenv()

#Connect to Azure Blob Storage Account
account_name = 'storage account name'
account_key = 'access key'
container_name = 'container name'
connect_str = 'connection string'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)
blob_list = []

# In this case, uploads is the name of the directory in the container and
# blob_i is the name designated for the file containing position data.
for blob_i in container_client.walk_blobs('uploads/', delimiter='/'):
    blob_list.append(blob_i.name)

blob_i = 'filename.csv'
for blob_i in blob_list:

    sas_i = generate_blob_sas(account_name= account_name,
                              container_name= container_name,
                              blob_name=blob_i,
                              account_key=account_key,
                              permission=BlobSasPermissions(read=True),
                              expiry=datetime.utcnow() + timedelta(hours=1)
    )   
sas_url = 'https://' + account_name+'.blob.core.windows.net/' + container_name + '/' + blob_i + '?' +sas_i

monthly=pd.read_csv(sas_url)
monthly['Date'] = pd.to_datetime(monthly['Date']).dt.date

fred = Fred(api_key=os.getenv('fred_api'))

SP = fred.get_series('SP500')
SP500 = (1 + SP.resample('M').ffill().pct_change()).cumprod() - 1

Dow = fred.get_series('DJIA')
Dow_Jones = (1 + Dow.resample('M').ffill().pct_change()).cumprod() - 1

NDaq = fred.get_series('NASDAQCOM')
Nasdaq = (1 + NDaq.resample('M').ffill().pct_change()).cumprod() - 1

TenYr = fred.get_series('DGS10')
Ten_Year = (1 + TenYr.resample('M').ffill().pct_change()).cumprod() - 1

selected_hh = st.sidebar.selectbox('Select a Household:', monthly['HH Name'].unique())
hh_df = monthly[monthly['HH Name'] == selected_hh]

# Create date slider that starts with the first month the household has data
start_date = st.slider('Select start date:', min_value=(hh_df['Date']).min(), max_value=(hh_df['Date']).max(), value=(hh_df['Date']).min())

# Create benchmark selection multi-select menu
benchmark_selection = st.sidebar.multiselect('Select benchmarks to plot:', ['SP500', 'Dow_Jones','Nasdaq', 'Ten_Year'])

# Add returns column to benchmark selection
benchmark_selection.append('Return')

col1, col2 = st.columns([2,1])

with col1:
    # Create line chart showing monthly returns for household and selected benchmark(s)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hh_df['Date'], y=(1 + hh_df['Return'].fillna(0)).cumprod() - 1, name='Household'))
    for benchmark in benchmark_selection:
        if benchmark == 'SP500':
            fig.add_trace(go.Scatter(x=SP500.index, y=SP500, name='S&P 500'))
        elif benchmark == 'Dow_Jones':
            fig.add_trace(go.Scatter(x=Dow_Jones.index, y=Dow_Jones, name='Dow Jones'))
        elif benchmark == 'Nasdaq':
            fig.add_trace(go.Scatter(x=Nasdaq.index, y=Nasdaq, name='Nasdaq'))
        elif benchmark == 'Ten_Year':
            fig.add_trace(go.Scatter(x=Ten_Year.index, y=Ten_Year, name='10 Year Treasury'))

    fig.update_layout(xaxis_range=[start_date, pd.to_datetime(monthly['Date']).max()])
    st.plotly_chart(fig, width= None)

with col2:
    # Calculate the standard deviation of the monthly returns
    monthly_std = np.std(hh_df['Return'])
    #Risk Gauge
    min_val = 0
    max_val = 20
    green_range = (0, 10)
    orange_range = (10, 15)
    red_range = (15, 20)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=(monthly_std*100),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Standard Deviation"},
        gauge={'axis': {'range': [min_val, max_val]},
            'bar': {'color': 'darkblue'},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [{'range': green_range, 'color': 'green'},
                        {'range': orange_range, 'color': 'orange'},
                        {'range': red_range, 'color': 'red'}],
            'threshold': {'line': {'color': 'black', 'width': 3},
                            'value': monthly_std},
                
            }
            
            ))
    fig.update_layout(width=250, height=250)
    st.plotly_chart(fig, use_container_width=True, text_align='center')

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
