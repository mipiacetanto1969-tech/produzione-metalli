import streamlit as st
import pandas as pd
import gspread

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Gestione Produzione Metalli", layout="wide")

# 2. DEFINIZIONE FUNZIONE
@st.cache_data(ttl=1)
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').worksheet('REGISTRO')
    data = sh.get_all_records()
    return pd.DataFrame(data)

# 3. INTERFACCIA E CARICAMENTO
st.title("Gestione Produzione Metalli")

try:
    df = load_data()
except Exception as e:
    st.error(f"Errore caricamento: {e}")
    df = pd.DataFrame()

if df.empty:
    st.warning("Il foglio 'REGISTRO' sembra vuoto o non raggiungibile.")
else:
    # PULIZIA COLONNE
    df.columns = df.columns.str.strip()
    
    if 'Data' not in df.columns:
        st.error("Errore: colonna 'Data' non trovata nel foglio.")
    else:
        # CONVERSIONE DATA
        df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Anno'] = df['Data_DT'].dt.year.astype(str)
        df['Mese'] = df['Data_DT'].dt.month_name().map({
            'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
            'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
            'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
        })
        
        # PULIZIA QUANTITÀ (FIX PER IL 500)
        df['Quantità'] = df['Quantità'].astype(str).str.replace(',', '.', regex=False)
        df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')
        
        # PULIZIA FASI (RIMUOVE RIGHE VUOTE)
        df['Fase Operativa'] = df['Fase Operativa'].str.strip()
        df = df[df['Fase Operativa'] != ""]
        df = df.dropna(subset=['Quantità', 'Fase Operativa'])

       # VISUALIZZAZIONE
        anni_disponibili = sorted(df['Anno'].dropna().unique(), reverse=True)
        if anni_disponibili:
            anni_selezionati = st.multiselect("Seleziona Anni", anni_disponibili, default=[anni_disponibili[0]])
            
            if anni_selezionati:
                df_filtrato = df[df['Anno'].isin(anni_selezionati)]
                
                # Questa pivot mette le Fasi sulle righe e gli Anni sulle colonne
                tabella = df_filtrato.pivot_table(
                    index='Fase Operativa', 
                    columns='Anno', 
                    values='Quantità', 
                    aggfunc='sum'
                ).fillna(0)
                
                st.subheader(f"Totali per Fase - Anni: {', '.join(anni_selezionati)}")
                st.dataframe(tabella, use_container_width=True)
                
                # Il grafico ora mostrerà le barre raggruppate per anno
                st.bar_chart(tabella)
