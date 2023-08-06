import streamlit as st 
from openbb_terminal.sdk import openbb
from dotenv import load_dotenv


def configure():
    load_dotenv()

sidebar = st.sidebar

def main():
     configure()

     st.set_page_config(layout="wide")
     st.title('Leveraging Ndex Systems Data Utilities Services')
    
     st.subheader('Python based coding examples for customizable user interfaces and connecting to:')

     st.text('')
     st.text('Data from Ndex Systems API Library')
     st.text('Data from Ndex Systems SFTP Server delivered to Microsoft Azure')
     st.text('Data from Ndex Systems SFTP Server delivered SQL Server Database')
     st.text('Federal Reserve APIs for market and economic data')
     st.text('Financial Modeling Prep APIs for market, indice and additional security data')



main()

