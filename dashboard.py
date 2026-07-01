import streamlit as st
import pandas as pd
import gspread

st.title("📊 Cruscotto Produzione Metalli")

def load_data():
    secrets = st.secrets["gcp_service_account"]
    creds_dict = dict(secrets)
    
    # Questa riga è il segreto per risolvere l'errore InvalidData
    # Trasforma le stringhe "\n" in veri caratteri di "a capo"
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

df = load_data()
st.dataframe(df)
