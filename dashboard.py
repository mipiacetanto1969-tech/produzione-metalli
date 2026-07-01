import streamlit as st
import pandas as pd
import gspread
import json

st.title("📊 Cruscotto Produzione Metalli")

def load_data():
    # Definiamo le credenziali direttamente qui dentro.
    # Copia esattamente il contenuto del tuo file gestioneproduzione-0406af9a1f26.json
    # qui sotto, sostituendo i dati tra le virgolette.
    creds_dict = {
        "type": "service_account",
        "project_id": "gestioneproduzione",
        "private_key_id": "IL_TUO_ID_CHE_TROVI_NEL_JSON",
        "private_key": "-----BEGIN PRIVATE KEY-----\nLA_TUA_CHIAVE_PRIVATA_QUI_CON_GLI_A_CAPO\n-----END PRIVATE KEY-----\n",
        "client_email": "nome-account@gestioneproduzione.iam.gserviceaccount.com",
        "client_id": "IL_TUO_CLIENT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
    }
    
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

try:
    df = load_data()
    st.dataframe(df)
except Exception as e:
    st.error(f"Errore tecnico: {e}")
