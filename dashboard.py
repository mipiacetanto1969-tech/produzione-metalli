import streamlit as st
import pandas as pd
import gspread

st.title("📊 Cruscotto Produzione Metalli")

def load_data():
    # Leggiamo i dati dai Secrets di Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Questo passaggio corregge gli a capo che causano l'errore
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # Usiamo il dizionario invece di un file
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

# Proviamo a caricare
try:
    df = load_data()
    st.dataframe(df)
except Exception as e:
    st.error(f"Errore: {e}")
