import streamlit as st
import pandas as pd
import gspread

st.title("📊 Gestione Produzione Metalli")

def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

df = load_data()

# 1. Pulizia: convertiamo la colonna Data in formato datetime
df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Anno'] = df['Data_DT'].dt.year.astype(str)
df['Mese'] = df['Data_DT'].dt.month_name()

# 2. Assicuriamo che la colonna Quantità sia numerica
df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')

# Filtro per Anno
anni_disponibili = sorted(df['Anno'].unique())
anni_selezionati = st.multiselect("Seleziona gli Anni da confrontare", anni_disponibili, default=[anni_disponibili[-1]])

if anni_selezionati:
    df_filtrato = df[df['Anno'].isin(anni_selezionati)]
    
    # Creiamo la tabella raggruppata
    tabella = df_filtrato.pivot_table(
        index=['Mese'], 
        columns='Fase Operativa', 
        values='Quantità', 
        aggfunc='sum'
    ).fillna(0) # Mettiamo 0 dove non ci sono dati
    
    st.subheader(f"Dettaglio Mensile - {', '.join(anni_selezionati)}")
    st.dataframe(tabella)
    
    st.subheader("📊 Grafico")
    st.bar_chart(tabella)
