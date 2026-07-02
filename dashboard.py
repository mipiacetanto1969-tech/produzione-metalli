import streamlit as st
import pandas as pd
import gspread

# Configurazione della pagina
st.set_page_config(page_title="Gestione Produzione Metalli", layout="wide")

# Cache per caricamento dati
@st.cache_data(ttl=1) 
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open('Gestione_Produzione_Metalli').sheet1
    
    # Invece di get_all_records, leggiamo tutto e forziamo la prima riga come header
    data = sh.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    
    return df

# Dizionario per tradurre i mesi
mesi_it = {
    'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
    'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
    'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
}

# Caricamento e pulizia dati
df = load_data()

# 1. Conversione Data
df['Data_DT'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Anno'] = df['Data_DT'].dt.year.astype(str)
df['Mese'] = df['Data_DT'].dt.month_name().map(mesi_it)

# 2. Pulizia Quantità (Gestione virgola decimale)
df['Quantità'] = df['Quantità'].astype(str).str.replace(',', '.', regex=False)
df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')

# 3. Pulizia Fasi Operative e Filtro (Rimuove righe indesiderate)
df['Fase Operativa'] = df['Fase Operativa'].str.strip()
# Inserisci qui SOTTO tutti i nomi esatti delle tue fasi operative presenti nel foglio
fasi_reali = ['Metallo Utilizzato KG', 'Verghe KG'] 
df = df[df['Fase Operativa'].isin(fasi_reali)]

# 4. Interfaccia Streamlit
st.title("Gestione Produzione Metalli")

anni_disponibili = sorted(df['Anno'].unique(), reverse=True)
anni_selezionati = st.multiselect("Seleziona gli Anni da confrontare", anni_disponibili, default=[anni_disponibili[0]])

if anni_selezionati:
    df_filtrato = df[df['Anno'].isin(anni_selezionati)]
    
    # Creazione tabella pivot
    tabella = df_filtrato.pivot_table(
        index=['Mese'], 
        columns='Fase Operativa', 
        values='Quantità', 
        aggfunc='sum'
    ).fillna(0)
    
    # Riordino dei mesi cronologicamente (non alfabetico)
    ordine_mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 
                   'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
    tabella = tabella.reindex(ordine_mesi, fill_value=0)
    
    st.subheader(f"Dettaglio Mensile - {', '.join(anni_selezionati)}")
    st.dataframe(tabella, use_container_width=True)
    
    st.subheader("📊 Grafico")
    st.bar_chart(tabella)
