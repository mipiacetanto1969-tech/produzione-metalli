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
    
    # DEBUG: leggiamo i valori grezzi invece di usare get_all_records
    valori = sh.get_all_values()
    st.write("Cosa vede il sistema nella prima riga:", valori[0]) # Mostra le intestazioni
    
    data = sh.get_all_records()
    return pd.DataFrame(data)

# 3. INTERFACCIA E CARICAMENTO
st.title("Gestione Produzione Metalli")

try:
   @st.cache_data(ttl=1) 
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').worksheet('REGISTRO')
    
    # DEBUG: leggiamo i valori grezzi invece di usare get_all_records
    valori = sh.get_all_values()
    st.write("Cosa vede il sistema nella prima riga:", valori[0]) # Mostra le intestazioni
    
    data = sh.get_all_records()
    return pd.DataFrame(data)
# 4. LOGICA DI CONTROLLO
if df.empty or 'Data' not in df.columns:
    st.warning("Il foglio 'REGISTRO' non è stato letto correttamente. Verifica le intestazioni: 'Data', 'Fase Operativa', 'Quantità'.")
else:
    # Dizionario per i mesi
    mesi_it = {
        'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
        'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
        'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
    }

    # Conversione e pulizia
    df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df['Anno'] = df['Data_DT'].dt.year.astype(str)
    df['Mese'] = df['Data_DT'].dt.month_name().map(mesi_it)
    
    df['Quantità'] = df['Quantità'].astype(str).str.replace(',', '.', regex=False)
    df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')
    
    df['Fase Operativa'] = df['Fase Operativa'].str.strip()
    fasi_reali = ['Metallo Utilizzato KG', 'Verghe KG'] 
    df = df[df['Fase Operativa'].isin(fasi_reali)]

    # Selezione anni
    anni_disponibili = sorted(df['Anno'].unique(), reverse=True)
    anni_selezionati = st.multiselect("Seleziona gli Anni da confrontare", anni_disponibili, default=[anni_disponibili[0]])

    if anni_selezionati:
        df_filtrato = df[df['Anno'].isin(anni_selezionati)]
        tabella = df_filtrato.pivot_table(index=['Mese'], columns='Fase Operativa', values='Quantità', aggfunc='sum').fillna(0)
        
        ordine_mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
        tabella = tabella.reindex([m for m in ordine_mesi if m in tabella.index], fill_value=0)
        
        st.subheader(f"Dettaglio Mensile - {', '.join(anni_selezionati)}")
        st.dataframe(tabella, use_container_width=True)
        st.bar_chart(tabella)
