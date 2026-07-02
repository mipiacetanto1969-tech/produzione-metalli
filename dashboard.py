import streamlit as st
import pandas as pd
import gspread

st.title("📊 Gestione Produzione Metalli")

# Dizionario per tradurre i mesi
mesi_it = {
    'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
    'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
    'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
}

def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    return pd.DataFrame(sh.get_all_records())

df = load_data()

# 1. Convertiamo la data
df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Anno'] = df['Data_DT'].dt.year.astype(str)
# Traduciamo il mese
df['Mese'] = df['Data_DT'].dt.month_name().map(mesi_it)

# 2. Correzione Quantità: 
# Se inserisci 5 e vedi 500, dividiamo per 100 (potrebbe essere un formato nel foglio)
df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')
# Scommenta la riga sotto se vuoi dividere per 100 (se il problema persiste)
# df['Quantità'] = df['Quantità'] / 100 

# Filtro per Anno
anni_disponibili = sorted(df['Anno'].unique())
anni_selezionati = st.multiselect("Seleziona gli Anni da confrontare", anni_disponibili, default=[anni_disponibili[-1]])

if anni_selezionati:
    df_filtrato = df[df['Anno'].isin(anni_selezionati)]
    
    tabella = df_filtrato.pivot_table(
        index=['Mese'], 
        columns='Fase Operativa', 
        values='Quantità', 
        aggfunc='sum'
    ).fillna(0)
    
    st.subheader(f"Dettaglio Mensile - {', '.join(anni_selezionati)}")
    st.dataframe(tabella)
    
    st.subheader("📊 Grafico")
    st.bar_chart(tabella)
