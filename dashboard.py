import streamlit as st
import pandas as pd
import gspread

st.title("📊 Cruscotto Produzione Metalli")

def load_data():
    # Carichiamo i dati dai secrets
    secrets = st.secrets["gcp_service_account"]
    creds_dict = dict(secrets)
    
    # Questa riga è il passaggio fondamentale per correggere l'errore InvalidData
    # Trasforma la stringa letterale "\n" salvata nel TOML in un vero ritorno a capo
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

# Gestione errore visibile
try:
    df = load_data()
    st.dataframe(df)
except Exception as e:
    st.error(f"Errore tecnico durante il caricamento: {e}")
