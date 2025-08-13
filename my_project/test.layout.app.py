import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Import dal tuo progetto
from my_project.db.database import initialize_db, insert_food_item, get_all_food_items, delete_food_item

# ---------- FUNZIONI ----------
def calculate_statistics(df):
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'] == '✅ OK']) + len(df[df['Status'] == '⚠️ Expiring Soon'])
    return total_items, expired_items, ok_items

def check_status(exp_date_str):
    today = datetime.today().date()
    exp = datetime.strptime(str(exp_date_str), "%Y-%m-%d").date()
    if exp < today:
        return "❌ Expired"
    elif (exp - today).days <= 3:
        return "⚠️ Expiring Soon"
    else:
        return "✅ OK"

# ---------- INIT ----------
initialize_db()
st.set_page_config(page_title="Food Waste Manager", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
.main {background-color: #f8f8f8; font-family: 'Arial';}
.expired { padding: 2px 5px; background-color: #ffcccc; color: #a60000; border-radius: 5px; font-weight: bold; }
.soon { padding: 2px 5px; background-color: #fff2cc; color: #ad8600; border-radius: 5px; font-weight: bold; }
.ok { padding: 2px 5px; background-color: #ccffcc; color: #006300; border-radius: 5px; font-weight: bold; }
.scroll-table { max-height: 400px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

st.title("🥦 Food Waste Manager")

# ---------- SIDEBAR: AGGIUNTA ----------
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

# ---------- RECUPERO ARTICOLI ----------
items = get_all_food_items()

if not items:
    st.info("Nessun articolo ancora. Usa la barra laterale per aggiungerne alcuni!")
else:
    df = pd.DataFrame(items, columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"])
    df["Status"] = df["Expiration Date"].apply(check_status)

    # ---------- SIDEBAR: FILTRO ----------
    st.sidebar.header("🔍 Filtra per stato")
    status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
    selected_status = st.sidebar.multiselect("Stati da visualizzare", options=status_options, default=status_options)

    # Applica filtro
    filtered_df = df[df["Status"].isin(selected_status)]

    # ---------- DIALOG ELIMINAZIONE ----------
    @st.dialog("Conferma Eliminazione")
    def confirm_delete(item_id, name):
        st.warning(f"Sei sicuro di voler eliminare '{name}'?")
        col_a, col_b = st.columns(2)
        if col_a.button("✅ Sì, elimina"):
            delete_food_item(item_id)
            st.success(f"'{name}' eliminato con successo!")
            st.rerun()
        if col_b.button("❌ Annulla"):
            st.rerun()

    # ---------- TABELLA FILTRATA ----------
    st.subheader("📋 Articoli filtrati")
    st.markdown('<div class="scroll-table">', unsafe_allow_html=True)

    # Header
    col_header = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
    for col, header_text in zip(col_header, ["Nome", "Categoria", "Acquisto", "Scadenza", "Quantità", "Unit", "Stato", "Azione"]):
        col.markdown(f"**{header_text}**")
    st.markdown("---")

    # Righe
    for _, row in filtered_df.iterrows():
        cols = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
        cols[0].write(row['Name'])
        cols[1].write(row['Category'])
        cols[2].write(row['Purchase Date'])
        cols[3].write(row['Expiration Date'])
        cols[4].write(row['Quantity'])
        cols[5].write(row['Unit'])
        status_class = "ok" if "OK" in row["Status"] else "soon" if "Soon" in row["Status"] else "expired"
        cols[6].markdown(f"<div class='{status_class}'>{row['Status']}</div>", unsafe_allow_html=True)
        if cols[7].button("🗑️", key=f"del_filt_{row['ID']}"):
            confirm_delete(row["ID"], row["Name"])

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- TABELLA COMPLETA ----------
    st.subheader("📦 Tutti gli articoli in frigo")
    col_header = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
    for col, header_text in zip(col_header, ["Nome", "Categoria", "Acquisto", "Scadenza", "Quantità", "Unit", "Stato", "Azione"]):
        col.markdown(f"**{header_text}**")
    st.markdown("---")
    for _, row in df.iterrows():
        cols = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
        cols[0].write(row['Name'])
        cols[1].write(row['Category'])
        cols[2].write(row['Purchase Date'])
        cols[3].write(row['Expiration Date'])
        cols[4].write(row['Quantity'])
        cols[5].write(row['Unit'])
        status_class = "ok" if "OK" in row["Status"] else "soon" if "Soon" in row["Status"] else "expired"
        cols[6].markdown(f"<div class='{status_class}'>{row['Status']}</div>", unsafe_allow_html=True)
        if cols[7].button("🗑️", key=f"del_all_{row['ID']}"):
            confirm_delete(row["ID"], row["Name"])

    # ---------- ANALISI ----------
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
            avg_price_per_item = 2.5
            lost_value = expired_items * avg_price_per_item
            st.warning(f"💸 Perdita economica stimata: **€{lost_value:.2f}**")
        else:
            st.info("Nessun articolo scaduto.")
