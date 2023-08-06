import base64
import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.express as px
import os
import locale
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv

load_dotenv()

fmpkey = os.getenv('fmp_api_key')

#Connect to Azure Blob Storage Account
account_name = 'storage account name'
account_key = 'access key'
container_name = 'container name'
connect_str = 'connection string'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)
blob_list = []

# In this case, uploads is the name of the directory in the container and
# blob_pos is the name designated for the file containing position data.
for blob_pos in container_client.walk_blobs('uploads/', delimiter='/'):
    blob_list.append(blob_pos.name)

blob_pos = 'uploads/filename.csv'
if blob_pos in blob_list:
    sas_pos = generate_blob_sas(account_name= account_name,
                              container_name= container_name,
                              blob_name= blob_pos,
                              account_key=account_key,
                              permission=BlobSasPermissions(read=True),
                              expiry=datetime.utcnow() + timedelta(hours=1)
    )
     
    pos_url = 'https://' + account_name +'.blob.core.windows.net/' + container_name + '/' + blob_pos + '?' +sas_pos

    holdings = pd.read_csv(pos_url, dtype={"Account ID": str})
    
# The hhdata.csv file is read from a desktop folder
hhdata = pd.read_csv("C:/Documents/HouseholdData.csv")
print(hhdata)

def color_negative_red(val):
    if type(val) != 'str':
        color = 'green' if val >0 else 'red'
        return f'color: {color}'

st.title('Real Time Data Center')
st.subheader('Real Time by Position')

# Extract the symbols from the holdings.csv file and join them into a comma-separated string
holdings.dropna(subset=['Symbol'], inplace=True)
tickers = ','.join(set(holdings['Symbol'].astype(str)))

url = f"https://financialmodelingprep.com/api/v3/quote/{tickers}?apikey={os.getenv('fmp_api_key')}"
response = requests.get(url).json()
df = pd.DataFrame(response)
df = df.drop(['marketCap', 'exchange', 'volume', 'avgVolume','timestamp', 'sharesOutstanding', 'earningsAnnouncement'], axis=1)

df.set_index('symbol', inplace=True)

symbols = df.index.unique().tolist()

# Loop through each symbol and create a link
for symbol in symbols:
    link = f'<a href="/holdings?symbol={symbol}">{symbol}</a>'
    df.loc[df.index == symbol, 'symbol'] = link

st.dataframe(df.style.applymap(color_negative_red, subset=['changesPercentage']))

st.subheader('Expand for Real Time % Changes')
df[['changesPercentage']] = df[['changesPercentage']].apply(pd.to_numeric)

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('changesPercentage'),
    y=alt.Y('name', sort='x', axis=alt.Axis(labelAngle=0)),
    color=alt.condition(
        alt.datum.changesPercentage > 0,
        alt.value('green'),
        alt.value('red')
    )
)

chart = chart.properties(
    ).configure_axis(
    labelFontSize=12,
    titleFontSize=14    
).configure_view(
    width=900
)

with st.expander('Position % Change'):
    st.altair_chart(chart, use_container_width=False)

st.subheader('Real Time Client Data')

household_name = st.sidebar.selectbox('Select Household Name', hhdata['Household Name'].unique())
account_id = st.sidebar.selectbox('Select Account ID', hhdata[hhdata['Household Name'] == household_name]['Account ID'].unique())

filtered_data = hhdata[(hhdata['Household Name'] == household_name) & (hhdata['Account ID'] == account_id)]

col1, col2, col3 = st.columns(3)

with col1:

    subheader_text = filtered_data['Household Name'].values[0]
    st.markdown(f"<h2 style='font-size: 18px; margin-top: 100px;'>Household Name: {subheader_text}</h2>", unsafe_allow_html=True)
    subheader_text = filtered_data['HH Total Value'].values[0]
    
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    # format the number as currency
    subheader_text = locale.currency(subheader_text, grouping=True)
    #subheader_text("Household Value: " + subheader_text)
    st.markdown(f"<h2 style='font-size: 18px;'>Household Value: {subheader_text}</h2>", unsafe_allow_html=True)

with col2:
    subheader_text = filtered_data['Account name'].values[0]
    st.markdown(f"<h2 style='font-size: 18px; margin-top: 100px;'>Account name: {subheader_text}</h2>", unsafe_allow_html=True)
    subheader_text = filtered_data['Account total value'].values[0]
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    # format the number as currency
    subheader_text = locale.currency(subheader_text, grouping=True)
    st.markdown(f"<h2 style='font-size: 18px;'>Current Value: {subheader_text}</h2>", unsafe_allow_html=True)


with col3:
    class_data = filtered_data.groupby('Classification').agg({'Account total value': 'sum', 'Position Market Value': 'sum'}).rename(columns={'Account total value': 'total', 'Position Market Value': 'market'})
    class_data['percent'] = class_data['market'] / class_data['total'] * 100
    fig = px.pie(class_data, values='percent', names=class_data.index, width=450, height=350)
    st.plotly_chart(fig)


livehhdata = filtered_data.rename(columns={'# of Units': 'Qty', 'Position Market Value': 'Close Value'})[['Symbol', 'Description', 'Qty', 'Close Price', 'Close Value']]

# Add a new column called 'Current Price' with default value of 0
livehhdata = livehhdata.assign(**{'Current Price': 0})
livehhdata = livehhdata.assign(**{'$ Change Price': 0})
livehhdata = livehhdata.assign(**{'% Change Price': 0})
livehhdata = livehhdata.assign(**{'Current Value': 0})
livehhdata = livehhdata.assign(**{'$ Change Value': 0})
livehhdata = livehhdata.assign(**{'% Change Value': 0})

livehhdata['Current Price'] = livehhdata.apply(lambda row: df.loc[row['Symbol'], 'price']
                                               if row['Symbol'] in df.index
                                               else row['Close Price'], axis=1)

livehhdata['Current Value'] = livehhdata.apply(lambda row: row['Current Price'] * row['Qty']
                                               if row['Symbol'] in df.index
                                               else row['Close Value'], axis=1)

livehhdata['$ Change Price'] = livehhdata['Current Price'] - livehhdata['Close Price']
livehhdata['% Change Price'] = (livehhdata['$ Change Price']/livehhdata['Close Price']).apply(lambda x: '{:.2%}'.format(x))
livehhdata['$ Change Value'] = livehhdata['Current Value'] - livehhdata['Close Value']
livehhdata['% Change Value'] = (livehhdata['$ Change Value']/livehhdata['Close Value']).apply(lambda x: '{:.2%}'.format(x))

def color_negative_red(val):
    if isinstance(val, str):
        val = float(val.strip('%'))  # remove the % symbol and convert to float
    if val < 0:
        color = 'red'
    elif val == 0:
        color = 'white'
    else:
        color = 'green'
    return f'color: {color}'

pd.set_option('display.max_rows', None)

pd.set_option('display.max_colwidth', 100)

styled_livehhdata = livehhdata.style.applymap(color_negative_red, subset=['$ Change Price', '% Change Price', '$ Change Value', '% Change Value'])

st.dataframe(styled_livehhdata, use_container_width = True)

# create a new page to filter by symbol
st.sidebar.subheader("Filter by Symbol")
symbol_input = st.sidebar.text_input("Symbol (ALL CAPS)")
filter_button = st.sidebar.button("Client List")

st.markdown("<h1 style='font-size: 18px;'>Click 'Client List' to see Clients Holding A Position</h1>", unsafe_allow_html=True)

# define function to display filtered dataframe
def display_filtered_holdings(df):
    st.dataframe(df)

# store filtered dataframe in a variable
filtered_holdings = None

# if filter button is clicked, filter holdings by symbol
if filter_button:
    if symbol_input:
        filtered_holdings = holdings[holdings['Symbol'] == symbol_input]
    else:
        filtered_holdings = holdings

    # display filtered holdings if they exist
    if not filtered_holdings.empty:
        # add a button to download the filtered holdings as CSV
        csv_button = st.button("Export as CSV")
        if csv_button:
            csv = filtered_holdings.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="filtered_holdings.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
        # display the filtered holdings
        display_filtered_holdings(filtered_holdings)

# get symbol from URL query parameter
params = st.experimental_get_query_params()
symbol = params.get("symbol", None)

# if symbol exists in query parameter, display filtered holdings
if symbol:
    filtered_holdings = holdings[holdings['Symbol'] == symbol]
    display_filtered_holdings(filtered_holdings)
