import streamlit as st
import pandas as pd
import gspread

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Gestione Produzione Metalli", layout="wide")

@st.cache_data(ttl=1)
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').worksheet('REGISTRO')
    # get_all_records() legge tutto. Se ne legge poche, forse hai dei filtri nel foglio Google?
    data = sh.get_all_records()
    return pd.DataFrame(data)

st.title("Gestione Produzione Metalli")

try:
    df = load_data()
except Exception as e:
    st.error(f"Errore caricamento: {e}")
    df = pd.DataFrame()

if df.empty:
    st.warning("Il foglio è vuoto.")
else:
    # PULIZIA COLONNE
    df.columns = df.columns.str.strip()
    
    if 'Data' not in df.columns:
        st.error(f"Colonne trovate: {df.columns.tolist()}. Assicurati che 'Data' sia corretta.")
    else:
        # CONVERSIONE DATA
        df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Anno'] = df['Data_DT'].dt.year.astype(str)
        df['Mese'] = df['Data_DT'].dt.month_name().map({
            'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
            'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
            'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
        })
        
        # PULIZIA QUANTITÀ - Versione corretta per il formato "5,00"
        # 1. Convertiamo in stringa
        df['Quantità'] = df['Quantità'].astype(str)
        
        # 2. Se c'è la virgola, sostituiamo con il punto decimale
        df['Quantità'] = df['Quantità'].str.replace(',', '.', regex=False)
        
        # 3. Ora forziamo la conversione in numero (pd.to_numeric gestirà il 5.00 come 5.0)
        df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')
        
        # 4. SOLO SE continua a segnare 500, decommenta la riga sotto:
        # df['Quantità'] = df['Quantità'] / 100
        
        # FILTRO FASI
        df['Fase Operativa'] = df['Fase Operativa'].str.strip()
        fasi_reali = ['Metallo Utilizzato KG', 'Verghe KG']
        df = df[df['Fase Operativa'].isin(fasi_reali)]

        # VISUALIZZAZIONE
        anni_disponibili = sorted(df['Anno'].dropna().unique(), reverse=True)
        if anni_disponibili:
            anni_selezionati = st.multiselect("Seleziona Anni", anni_disponibili, default=[anni_disponibili[0]])
            if anni_selezionati:
                tabella = df[df['Anno'].isin(anni_selezionati)].pivot_table(
                    index='Mese', columns='Fase Operativa', values='Quantità', aggfunc='sum'
                ).fillna(0)
                st.dataframe(tabella, use_container_width=True)
                st.bar_chart(tabella)
