import streamlit as st
import pandas as pd
import gspread

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Gestione Produzione Metalli", layout="wide")

# 2. DEFINIZIONE FUNZIONE (Tutto deve essere allineato sotto il def)
@st.cache_data(ttl=1)
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').worksheet('REGISTRO')
    data = sh.get_all_records()
    return pd.DataFrame(data)

# 3. CARICAMENTO DATI
st.title("Gestione Produzione Metalli")

try:
    df = load_data()
    # Debug rapido: se vuoi vedere cosa legge, decommenta la riga sotto:
    # st.write(df.columns) 
except Exception as e:
    st.error(f"Errore caricamento: {e}")
    df = pd.DataFrame()

# 4. LOGICA E PULIZIA
# Controlliamo che le colonne esistano. 
# Se vedi ancora l'errore, guarda se tra le colonne caricate (se hai usato st.write) 
# ci sono spazi tipo "Data " invece di "Data"
if not df.empty:
    # Pulizia nomi colonne: rimuove spazi vuoti accidentali
    df.columns = df.columns.str.strip()
    
    if 'Data' not in df.columns:
        st.error(f"Colonne trovate nel foglio: {df.columns.tolist()}. Assicurati che 'Data' sia tra queste.")
    else:
        # Conversione e logica successiva
        df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df['Anno'] = df['Data_DT'].dt.year.astype(str)
        df['Mese'] = df['Data_DT'].dt.month_name().map({
            'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
            'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
            'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
        })
        
        df['Quantità'] = pd.to_numeric(df['Quantità'].astype(str).str.replace(',', '.'), errors='coerce')
        df['Fase Operativa'] = df['Fase Operativa'].str.strip()
        
        # Filtro fasi
        fasi_reali = ['Metallo Utilizzato KG', 'Verghe KG']
        df = df[df['Fase Operativa'].isin(fasi_reali)]

        # Visualizzazione
        anni_disponibili = sorted(df['Anno'].unique(), reverse=True)
        anni_selezionati = st.multiselect("Seleziona Anni", anni_disponibili, default=[anni_disponibili[0]])

        if anni_selezionati:
            tabella = df[df['Anno'].isin(anni_selezionati)].pivot_table(
                index='Mese', columns='Fase Operativa', values='Quantità', aggfunc='sum'
            ).fillna(0)
            
            st.dataframe(tabella, use_container_width=True)
            st.bar_chart(tabella)
else:
    st.warning("Il foglio sembra vuoto.")
