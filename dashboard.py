import streamlit as st
import pandas as pd
import gspread

st.title("📊 Cruscotto Produzione Metalli")

def load_data():
    # Leggiamo dal TOML usando una stringa singola senza ritorni a capo
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # "Sostituiamo" il simbolo \n con il vero carattere di ritorno a capo
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

try:
    df = load_data()
    st.dataframe(df)
except Exception as e:
    st.error(f"Errore caricamento: {e}")
