import requests
import pandas as pd
import streamlit as st
import plotly.express as px

params = dict(
    grant_type="client_credentials",
    firmName="ndex assigned firm name",
    client_id="username",
    client_secret="password",
    product_type="fullservice",
    date = "2022/12/30",
    currency = "USD",
    portfolioId="portfolio id"
)

authToken = "Ndex API auth token generated using postman"
headers = {
    'Authorization': 'Bearer ' + authToken,
}

url = 'https://m.ndexsystems.com:8443/fengine_api/v1/returnsSummary?'
url += '&'.join([f"{key}={value}" for key, value in params.items()])

response = requests.get(url, headers=headers)

data = response.json()

# Extract the necessary information from the JSON response
title = data['title']
columns = data['columns']
line_items = data['lineItems']

# Create a DataFrame from the line_items data
returns_df = pd.DataFrame(line_items)
returns_df = returns_df.drop(columns=['lineType'])

labels = [column['label'] for column in columns]

ror_values = {}
for item in line_items:
    if item['column 0'] == 'ROR (Time-weighted return)':
        ror_values = {key: value for key, value in item.items()}


column_labels = ['Period', '1 Month', '3 Months', 'Year to Date']
data_row = {'column 0': 'ROR (Time-weighted return)', 'column 1': '-15.1%', 'column 2': '-13.6%', 'column 3': '-42.8%'}

# Extract the column labels from the 'columns' list
column_name = [column['label'] for column in columns]

# Extract only the ROR data from the returns_df DataFrame
ror_df = returns_df[returns_df['column 0'] == 'ROR (Time-weighted return)']

# Rename the DataFrame columns
ror_df.columns = column_name

# Melt the DataFrame to a long format
ror_df_melted = ror_df.melt(id_vars='Period', var_name='Time Period', value_name='Return')
ror_df_melted['Return'] = ror_df_melted['Return'].str.rstrip('%').astype('float') / 100.0


fig = px.bar(ror_df_melted, x='Time Period', y='Return', title='ROR (Time-weighted return)',
             labels={'Return': 'Return (%)'}, text='Return')
fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
st.plotly_chart(fig)


