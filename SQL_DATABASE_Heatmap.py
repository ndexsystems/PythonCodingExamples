import pandas as pd
import numpy as np
import plotly.express as px
import sqlalchemy as sa
from sqlalchemy import create_engine
import pyodbc
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

conn = pyodbc.connect(
    'Data Source Name=MssqlDataSource;'
    'Driver={SQL Server};'
    'Server= server address;'
    'Database= database name;'
    'Trusted_connection=yes;'
)

st.set_page_config(page_title="Position Heat Map",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

symbol = []
poschange = []
classification = []
description = []
currentValue = []

# query data from SQL database
query = 'SELECT *FROM databaseName.dbo.tableName'
data = pd.read_sql(query, conn)
df = pd.DataFrame(data)
df.rename(columns={'class': 'classification'}, inplace=True)

positions = df[df['currentValue'] > 100000]

positions['poschange'] = np.where(
    positions['eomPrice'] == 0, np.nan, (positions['currentPrice'] - positions['eomPrice']) / positions['eomPrice']
)

df = positions[['symbol', 'description', 'classification', 'poschange', 'currentValue']]
df.columns = ['symbol', 'security', 'classification', 'change', 'total_allocation']


color_bin = [-1,-0.01,-0.001, 0, 0.001, 0.01, 1]
df['colors'] = pd.cut(df['change'], bins=color_bin, labels=['9b0303','c8591e','3D689E','bcc080','5ea814','196219'])
df

fig = px.treemap(df, path=[px.Constant("all"), 'classification','symbol'], values = 'total_allocation', color='colors',
                 color_discrete_map ={'(?)':'262931','9b0303':'9b0303','c8591e':'c8591e','3D689E':'3D689E','bcc080':'bcc080','5ea814':'5ea814','196219':'196219'},

                hover_data = {'change':':.2p'}
                
                )
fig.show()