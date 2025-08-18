import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- IMPORT DATABASE --- #
from database import initialize_db, insert_food_item, get_all_food_items, delete_food_item

# --- INIZIALIZZAZIONE DB --- #
initialize_db()  # Crea il DB per l'utente se non esiste

# --- HEADER --- #
st.set_page_config(page_title="Smart Fridge", page_icon="🥶")
st.title("🥶 Smart Fridge")

# --- FORM AGGIUNTA PRODOTTO --- #
with st.sidebar.form("add_food"):
    st.header("Add Food Item")
    name = st.text_input("Product Name")
    category = st.selectbox("Category", ["Dairy", "Vegetables", "Meat", "Fruit", "Drinks", "Fish", "Other"])
    purchase_date = st.date_input("Purchase Date", datetime.today())
    expiration_date = st.date_input("Expiration Date")
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.text_input("Unit (e.g., kg, pcs, lt)")

    submitted = st.form_submit_button("Add Item")
    if submitted:
        if not name.strip():
            st.warning("⚠️ Please write down your item before adding!")
        else:
            insert_food_item(name, category, purchase_date, expiration_date, quantity, unit)
            st.success(f"'{name}' has been added to your fridge!")

# --- CARICAMENTO DATI --- #
items = get_all_food_items()
if items:
    df = pd.DataFrame(items, columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"])
    
    # --- TABELLA DATI --- #
    st.subheader("Fridge Inventory")
    st.dataframe(df)

    # --- DELETE BUTTON --- #
    st.subheader("Delete Item")
    item_to_delete = st.selectbox("Select item to delete", df["Name"])
    if st.button("Delete Selected Item"):
        item_id = df[df["Name"] == item_to_delete]["ID"].values[0]
        delete_food_item(item_id)
        st.success(f"'{item_to_delete}' deleted!")
        st.experimental_rerun()

    # --- STATUS COUNTS (esempio per grafico) --- #
    st.subheader("Category Counts")
    category_counts = df["Category"].value_counts()
    st.bar_chart(category_counts)

    # --- PLOTLY CHART --- #
    st.subheader("Quantity by Category")
    fig = px.pie(df, names="Category", values="Quantity", title="Food Quantity Distribution")
    st.plotly_chart(fig)
else:
    st.info("No items in your fridge yet. Add some!")
