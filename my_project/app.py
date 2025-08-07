# app.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import plotly.express as px
import requests

from db.database import initialize_db, insert_food_item, get_all_food_items

# --- FUNZIONI DI LOGICA ---

def calculate_statistics(df):
    """Calcola e restituisce le statistiche chiave dal DataFrame."""
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

def highlight_status(val):
    """Funzione per colorare le celle della colonna 'Status' nel DataFrame."""
    if val == "❌ Expired":
        return 'background-color: #ffcccc' # Rosso chiaro
    elif val == "⚠️ Expiring Soon":
        return 'background-color: #fff2cc' # Arancione chiaro
    elif val == "✅ OK":
        return 'background-color: #ccffcc' # Verde chiaro
    return '' # Restituisce una stringa vuota per le altre celle

# ----------------------------------------------------------------------------------

# Inizializza il database
initialize_db()

st.set_page_config(page_title="Food Waste Manager", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f8f8f8; font-family: 'Arial';}
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5em 1em;
    }
    .stDownloadButton > button {
        background-color: #2196F3;
        color: white;
        border-radius: 6px;
        padding: 0.5em 1em;
    }
    .stMetricValue {
        font-size: 26px;
        color: #333;
        font-weight: 600;
    }
    .stDataFrame th {
        background-color: #CED4E0;
    }
    </style>
""", unsafe_allow_html=True)


st.title("🥦 Food Waste Manager")

# ---------- Form nella sidebar per aggiungere un articolo ----------
with st.sidebar.form("add_food"):
    st.header("➕ Aggiungi un nuovo articolo")

    name = st.text_input("Nome Prodotto")
    category = st.selectbox("Categoria", ["Latticini", "Verdure", "Carne", "Frutta", "Bevande", "Altro"])
    purchase_date = st.date_input("Data di Acquisto", datetime.today())
    expiration_date = st.date_input("Data di Scadenza")
    quantity = st.number_input("Quantità", min_value=0.0, step=0.1)
    unit = st.text_input("Unità (es. kg, confezione, bottiglia)")

    submitted = st.form_submit_button("Aggiungi Articolo")

    if submitted and name:
        insert_food_item(name, category, purchase_date, expiration_date, quantity, unit)
        st.success(f"'{name}' è stato aggiunto al tuo frigo! Aggiorna la pagina per vederlo.")

# ---------- Visualizzazione degli articoli ----------
st.subheader("📋 Lista Cibo")

items = get_all_food_items()

if items:
    df = pd.DataFrame(items, columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"])
    
    # 1. Calcolo della colonna Status
    df["Status"] = df["Expiration Date"].apply(check_status)

    # 2. Avvisi visivi per gli articoli in scadenza
    expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]
    expired = df[df["Status"] == "❌ Expired"]

    if not expiring_soon.empty:
        st.warning("⚠️ I seguenti articoli stanno per scadere:")
        st.table(expiring_soon[["Name", "Expiration Date", "Quantity", "Unit"]])

    if not expired.empty:
        st.error("❌ I seguenti articoli sono scaduti:")
        st.table(expired[["Name", "Expiration Date", "Quantity", "Unit"]])

    # ---------- Tabella dei dati ----------
    styled_df = df.style.applymap(highlight_status, subset=["Status"])
    st.dataframe(styled_df)

    # ---------- Suggerimenti per i pasti ----------
    st.subheader("🍽️ Ispirazione per i pasti")

    if st.button("Cosa posso cucinare oggi?"):
        ingredients = expiring_soon["Name"].tolist()

        if ingredients:
            spoonacular_key = "f05378d894eb4eb8b187551e2a492c49"
            st.info("Ricerca di ricette per: " + ", ".join(ingredients))
            query_ingredients = ",".join(ingredients)

            url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={query_ingredients}&number=1&ranking=1&apiKey={spoonacular_key}"

            with st.spinner("Sto cercando una ricetta..."):
                try:
                    response = requests.get(url)
                    recipes = response.json()

                    if isinstance(recipes, list) and recipes:
                        recipe = recipes[0]
                        title = recipe["title"]
                        image = recipe.get("image", "")
                        recipe_id = recipe["id"]

                        st.markdown(f"### 👨‍🍳 {title}")
                        if image:
                            st.image(image, width=400)

                        instructions_url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={spoonacular_key}"
                        instructions_response = requests.get(instructions_url).json()

                        if instructions_response and isinstance(instructions_response, list) and instructions_response[0].get("steps"):
                            steps = instructions_response[0]["steps"]
                            st.markdown("**Passaggi:**")
                            for step in steps:
                                st.markdown(f"**{step['number']}.** {step['step']}")
                        else:
                            st.info("Nessuna istruzione dettagliata disponibile.")
                    else:
                        st.warning("Nessuna ricetta trovata con questi ingredienti.")
                except Exception as e:
                    st.error(f"Errore durante la ricerca della ricetta: {e}")
        else:
            st.success("Nessun articolo in scadenza — niente di urgente da cucinare!")

    # ---------- Grafico a torta ----------
    st.subheader("🥧 Panoramica dello stato")
    status_counts = df["Status"].value_counts()
    st.write(status_counts)

    # Mappatura personalizzata tra stati e colori
    status_colors = {
        "❌ Expired": "#ffcccc",
        "⚠️ Expiring Soon": "#fff2cc",
        "✅ OK": "#ccffcc"
    }

    # Assicurati che l'ordine dei nomi corrisponda all'ordine dei colori
    ordered_names = status_counts.index.tolist()
    ordered_colors = [status_colors[name] for name in ordered_names]

    fig = px.pie(
        names=ordered_names,
        values=status_counts.values,
        title="Distribuzione dello stato del cibo",
        color_discrete_sequence=ordered_colors
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------- Statistiche sullo spreco ----------
    st.subheader("📊 Statistiche sullo spreco")

    total_items, expired_items, ok_items = calculate_statistics(df)
    
    st.metric("Articoli Totali", total_items)
    st.metric("Articoli Scaduti", expired_items)
    st.metric("Consumati (o OK)", ok_items)

    if expired_items > 0:
        avg_price_per_item = 2.5  # Valore segnaposto
        lost_value = expired_items * avg_price_per_item
        st.write(f"💸 Perdita economica stimata: **€{lost_value:.2f}**")

else:
    st.info("Nessun articolo ancora. Usa la barra laterale per aggiungerne alcuni!")