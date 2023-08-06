import requests
import pandas as pd
import streamlit as st
import plotly.express as px

params = dict(
    grant_type="client_credentials",
    firmName="ndex assigned firm name",
    client_id="user id",
    client_secret="password",
    product_type="fullservice",
    portfolioId="portfolio id"
)

authToken = "Ndex API auth token generated using postman"
headers = {
    'Authorization': 'Bearer ' + authToken,
}

url = 'https://m.ndexsystems.com:8443/fengine_api/v1/assetAllocationBreakdown?'
url += '&'.join([f"{key}={value}" for key, value in params.items()])

response = requests.get(url, headers=headers)

data = response.json()

# Extract asset allocation breakdown groups
asset_allocation = data['assetAllocationBreakdownGroups']

# Convert to DataFrame
allocation_df = pd.DataFrame(asset_allocation)

# Remove the row for "Total Value" as it makes no sense in the pie chart
allocation_df = allocation_df[allocation_df['group'] != 'Total Value']

# Convert marketValue to float for the pie chart
allocation_df['marketValue'] = allocation_df['marketValue'].str.replace(',', '').astype(float)

# Plotting
fig = px.pie(allocation_df, values='marketValue', names='group', title='Asset Allocation Breakdown')
st.plotly_chart(fig)
