import streamlit as st
import pandas as pd
import gspread

# 4. Interfaccia Streamlit
st.title("Gestione Produzione Metalli")

# Carichiamo i dati all'interno del controllo
try:
    df = load_data()
except Exception as e:
    st.error(f"Errore nel caricamento dati: {e}")
    df = pd.DataFrame() # Creiamo un dataframe vuoto per evitare il crash

# Ora facciamo il controllo su df
if df.empty or 'Anno' not in df.columns:
    st.warning("Il foglio è vuoto o mancano le intestazioni corrette (Data, Fase Operativa, Quantità).")
else:
    # ... (tutto il resto del tuo codice che avevamo scritto)
    anni_disponibili = sorted(df['Anno'].unique(), reverse=True)
    
    # Gestione sicura: se ci sono anni, usa il primo, altrimenti lascia vuoto
    default_anni = [anni_disponibili[0]] if anni_disponibili else []
    
    anni_selezionati = st.multiselect("Seleziona gli Anni da confrontare", anni_disponibili, default=default_anni)

    if anni_selezionati:
        df_filtrato = df[df['Anno'].isin(anni_selezionati)]
        
        # Creazione tabella pivot
        tabella = df_filtrato.pivot_table(
            index=['Mese'], 
            columns='Fase Operativa', 
            values='Quantità', 
            aggfunc='sum'
        ).fillna(0)
        
        # Riordino dei mesi
        ordine_mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 
                       'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
        # Manteniamo solo i mesi presenti nei dati per evitare errori
        ordine_mesi = [m for m in ordine_mesi if m in tabella.index]
        tabella = tabella.reindex(ordine_mesi, fill_value=0)
        
        st.subheader(f"Dettaglio Mensile - {', '.join(anni_selezionati)}")
        st.dataframe(tabella, use_container_width=True)
        
        st.subheader("📊 Grafico")
        st.bar_chart(tabella)
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
