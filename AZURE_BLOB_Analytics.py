from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns
from dotenv import load_dotenv
import os
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
monthly['Date'] = pd.to_datetime(monthly['Date'])

st.header('Household Analysis')

options = monthly['HH Name'].unique()
selected_option = st.sidebar.selectbox('Select a Household', options)

filtered_hh = monthly[monthly['HH Name'] == selected_option]

#RISK STATS
# Calculate the standard deviation of the monthly returns
monthly_std = np.std(filtered_hh['Return'])

col1, col2, col3 = st.columns([3,1,1])

with col1:
    #Line Chart
    chart = alt.Chart(filtered_hh).mark_area(opacity=.70).encode(
            x='Date:T',
            y='Value:Q'
        )

    st.altair_chart(chart, use_container_width=True)

    #Bar Chart

    chart = alt.Chart(filtered_hh).mark_bar().encode(
        x=alt.X('Date', sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Return', axis=alt.Axis(format='%')),
        color=alt.condition(
            alt.datum.Return > 0,
            alt.value('green'),
            alt.value('red')
        )
    )

with col2:

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
    st.plotly_chart(fig)

with col3:
     
    #ANNUALIZED RETURNS

    filtered_hh['Cumulative Return'] = (1 + filtered_hh['Return']).cumprod()
    total_return = filtered_hh['Cumulative Return'].iloc[-1] - 1
    num_years = len(filtered_hh) / 12
    annualized_return = (1 + total_return) ** (1 / num_years) - 1
    st.write("Annualized Return: {:.2%}".format(annualized_return))

    #SHARPE RATIO
    excess_returns = filtered_hh['Return'] - 0

    sharpe_ratio = np.sqrt(12) * (np.mean(excess_returns) / np.std(excess_returns))
    st.write("Sharpe Ratio: {:.2f}".format(sharpe_ratio))
        
    #SORTINO RATIO

    # Define the risk-free rate
    risk_free_rate = 0.01

    # Calculate the average of the negative monthly returns
    negative_returns = filtered_hh[filtered_hh['Return'] < 0]['Return']
    negative_return_avg = negative_returns.mean()

    # Calculate the standard deviation of the negative monthly returns
    negative_return_std = negative_returns.std()

    # Calculate the Sortino ratio
    portfolio_return = filtered_hh['Return'].mean()
    sortino_ratio = (portfolio_return - risk_free_rate) / negative_return_std

    # Print the Sortino ratio
    st.write("Sortino Ratio: {:.2f}".format(sortino_ratio))

    #MAXDRAWDOWN

    # Calculate the cumulative returns
    filtered_hh['Cumulative Return'] = (1 + filtered_hh['Return']).cumprod()

    # Calculate the cumulative maximum of the returns at each point in time
    filtered_hh['Cumulative Max'] = filtered_hh['Cumulative Return'].cummax()

    # Calculate the drawdown by subtracting the cumulative maximum from the cumulative returns
    filtered_hh['Drawdown'] = filtered_hh['Cumulative Return'] - filtered_hh['Cumulative Max']

    # Calculate the maximum drawdown as the minimum value of the drawdown series
    max_drawdown = filtered_hh['Drawdown'].min()

    # Print the maximum drawdown
    st.write("Maximum Drawdown: {:.2%}".format(max_drawdown))

#Monthly Returns
st.subheader('Monthly Returns')
chart = chart.properties(
    title='Monthly Returns',
    width=alt.Step(90),
    height=alt.Step(20)
).configure_axis(
    labelFontSize=12,
    titleFontSize=14    
)

st.altair_chart(chart, use_container_width=True)

#UNDERWATER CHART

# Load monthly returns data into a pandas dataframe
monthlydd = filtered_hh

ddreturns = monthlydd['Return']

# Calculate the cumulative returns
cumulative_returns = (1 + ddreturns).cumprod()
# Calculate the underwater chart data
underwater_chart = (cumulative_returns.cummax() - cumulative_returns) / cumulative_returns.cummax()

st.subheader('Underwater Chart')
st.area_chart(underwater_chart)
