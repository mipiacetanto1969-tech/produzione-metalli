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

# Assicuriamoci che la colonna Quantità sia numerica
df['Quantità'] = pd.to_numeric(df['Quantità'], errors='coerce')

# Filtro per Anno
anni_disponibili = sorted(df['Data'].apply(lambda x: x.split('/')[2]).unique())
anni_selezionati = st.multiselect("Seleziona gli Anni da confrontare", anni_disponibili, default=[anni_disponibili[-1]])

if anni_selezionati:
    # Filtriamo il dataframe
    df_filtrato = df[df['Data'].apply(lambda x: x.split('/')[2]).isin(anni_selezionati)]
    
    # Creiamo la tabella raggruppata (Anno, Mese, Fase)
    df_filtrato['Mese'] = df_filtrato['Data'].apply(lambda x: x.split('/')[1])
    tabella = df_filtrato.pivot_table(index=['Anno', 'Mese'], columns='Fase Operativa', values='Quantità', aggfunc='sum').reset_index()
    
    st.subheader(f"Dettaglio Mensile - {', '.join(anni_selezionati)}")
    st.dataframe(tabella)
    
    st.subheader("📊 Grafico")
    st.bar_chart(tabella.set_index('Mese'))
