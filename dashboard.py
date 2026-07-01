import streamlit as st
import pandas as pd
import gspread

st.title("📊 Cruscotto Produzione Metalli")

def load_data():
    # Legge le credenziali dai "Secrets" di Streamlit
    creds_dict = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds_dict)
    
    # IMPORTANTE: Il nome qui deve essere IDENTICO al nome del file su Google Drive
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    data = sh.get_all_records()
    return pd.DataFrame(data)

df = load_data()
st.dataframe(df)
