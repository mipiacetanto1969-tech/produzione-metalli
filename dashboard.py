import streamlit as st
import pandas as pd
import gspread

# Configurazione per leggere da Google Sheets
def load_data():
    gc = gspread.service_account(filename='credenziali.json')
    sh = gc.open('Gestione_Produzione_Metalli').sheet1 # Assicurati che il nome sia identico al tuo file!
    data = sh.get_all_records()
    return pd.DataFrame(data)

st.title("📊 Cruscotto Produzione Metalli")
df = load_data()

st.write("Ecco i tuoi dati inseriti:")
st.dataframe(df)

# Esempio grafico veloce
st.bar_chart(df.groupby('Fase Operativa')['Quantità'].sum())