import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests

# Assicurati che questo import corrisponda alla struttura del tuo progetto
from my_project.db.database import initialize_db, insert_food_item, get_all_food_items, delete_food_item

# --- FUNZIONI DI LOGICA ---

def calculate_statistics(df):
    """Calcola le statistiche di base dal DataFrame."""
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'] == '✅ OK']) + len(df[df['Status'] == '⚠️ Expiring Soon'])
    return total_items, expired_items, ok_items

def check_status(exp_date_str):
    """Controlla lo stato di un articolo in base alla data di scadenza."""
    today = datetime.today().date()
    exp = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
    if exp < today:
        return "❌ Expired"
    elif (exp - today).days <= 3:
        return "⚠️ Expiring Soon"
    else:
        return "✅ OK"

# ----------------------------------------------------------------------------------

# Inizializza il database
initialize_db()

# --- CONFIGURAZIONE DELLA PAGINA E STILE ---
st.set_page_config(page_title="Food Waste Manager", layout="wide")

# CSS per personalizzare l'aspetto dell'app
st.markdown("""
    <style>
    .main {background-color: #f8f8f8; font-family: 'Arial';}
    .expired {
        padding: 2px 5px;
        background-color: #ffcccc;
        color: #a60000;
        border-radius: 5px;
        font-weight: bold;
    }
    .soon {
        padding: 2px 5px;
        background-color: #fff2cc;
        color: #ad8600;
        border-radius: 5px;
        font-weight: bold;
    }
    .ok {
        padding: 2px 5px;
        background-color: #ccffcc;
        color: #006300;
        border-radius: 5px;
        font-weight: bold;
    }
    /*
    * NUOVO CODICE AGGIUNTO PER I BORDI DELLA TABELLA
    */
    .row-border {
        border-bottom: 1px solid #ddd;
        padding-top: 5px;
        padding-bottom: 5px;
    }
    .stContainer {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 5px;
        padding: 5px;
    }
    .stContainer.header {
        background-color: #f0f0f0;
        font-weight: bold;
        border: none; /* Rimuovi il bordo per l'intestazione */
    }
    </style>
""", unsafe_allow_html=True)


st.title("🥦 Food Waste Manager")

# ---------- SIDEBAR: AGGIUNTA ARTICOLO ----------
with st.sidebar.form("add_food"):
    st.header("➕ Aggiungi un nuovo articolo")

    name = st.text_input("Nome Prodotto")
    category = st.selectbox("Categoria", ["Latticini", "Verdure", "Carne", "Frutta", "Bevande", "Altro"])
    purchase_date = st.date_input("Data di Acquisto", datetime.today())
    expiration_date = st.date_input("Data di Scadenza")
    quantity = st.number_input("Quantità", min_value=0.0, step=0.1)
    unit = st.text_input("Unit (es. kg, pz, lt)")

    submitted = st.form_submit_button("Aggiungi Articolo")

    if submitted and name:
        insert_food_item(name, category, purchase_date, expiration_date, quantity, unit)
        st.success(f"'{name}' è stato aggiunto al tuo frigo!")
        st.rerun()

# ---------- VISUALIZZAZIONE ARTICOLI ----------
st.subheader("📋 Lista Cibo")

items = get_all_food_items()

if not items:
    st.info("Nessun articolo ancora. Usa la barra laterale per aggiungerne alcuni!")
else:
    df = pd.DataFrame(
        items,
        columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"]
    ).reset_index(drop=True)

    df["Status"] = df["Expiration Date"].apply(check_status)

    expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]
    expired = df[df["Status"] == "❌ Expired"]

    if not expiring_soon.empty:
        st.warning("⚠️ I seguenti articoli stanno per scadere:")
        st.dataframe(
            expiring_soon[["Name", "Expiration Date", "Quantity", "Unit"]].reset_index(drop=True),
            hide_index=True  # Nasconde l'indice numerico
        )

    if not expired.empty:
        st.error("❌ I seguenti articoli sono scaduti:")
        st.dataframe(
            expired[["Name", "Expiration Date", "Quantity", "Unit"]].reset_index(drop=True),
            hide_index=True  # Nasconde l'indice numerico
        )

    # ---------- TABELLA COMPLETA CON PULSANTI (METODO STREAMLIT) ----------
    st.subheader("Tutti gli articoli in frigo")

    # 1. Creiamo un'intestazione per la nostra tabella con una classe CSS
    col_header = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
    headers = ["Nome", "Categoria", "Acquisto", "Scadenza", "Quantità", "Unit", "Stato", "Azione"]
    for col, header_text in zip(col_header, headers):
        col.markdown(f"**{header_text}**")

    st.markdown("---")
    
    # 2. Iteriamo su ogni riga del DataFrame per visualizzare i dati
    for index, row in df.iterrows():
        # Utilizza il parametro 'border=True' per mostrare un bordo per ogni riga
        # Ho rimosso la classe 'stContainer' che ho aggiunto sopra, in modo da poter usare il parametro border
        with st.container(border=True):
            col_data = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
            
            col_data[0].write(row['Name'])
            col_data[1].write(row['Category'])
            col_data[2].write(row['Purchase Date'])
            col_data[3].write(row['Expiration Date'])
            col_data[4].write(row['Quantity'])
            col_data[5].write(row['Unit'])
            
            status_class = "ok" if "OK" in row["Status"] else "soon" if "Soon" in row["Status"] else "expired"
            col_data[6].markdown(f"<div class='{status_class}'>{row['Status']}</div>", unsafe_allow_html=True)
            
            # 3. Creiamo il pulsante di eliminazione con una chiave unica
            if col_data[7].button("🗑️", key=f"delete_{row['ID']}"):
                delete_food_item(row["ID"])
                st.success(f"'{row['Name']}' è stato eliminato!")
                st.rerun()

    # ---------- GRAFICO A TORTA + STATISTICHE AFFIANCATI ----------
    st.subheader("📈 Analisi generale")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥧 Panoramica dello stato")
        status_counts = df["Status"].value_counts()
        
        status_colors = {
            "❌ Expired": "#ffcccc",
            "⚠️ Expiring Soon": "#fff2cc",
            "✅ OK": "#ccffcc"
        }

        fig = px.pie(
            names=status_counts.index,
            values=status_counts.values,
            title="Distribuzione dello stato del cibo",
            color=status_counts.index,
            color_discrete_map=status_colors
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Statistiche sullo spreco")
        total_items, expired_items, ok_items = calculate_statistics(df)
        st.metric("Articoli Totali", total_items)
        st.metric("Articoli Scaduti", expired_items)
        st.metric("Articoli OK / In Scadenza", ok_items)

        if expired_items > 0:
            avg_price_per_item = 2.5  # Valore medio ipotetico per articolo
            lost_value = expired_items * avg_price_per_item
            st.warning(f"💸 Perdita economica stimata: **€{lost_value:.2f}**")
        else:
            st.info("No food items yet. Use the sidebar to add some!")