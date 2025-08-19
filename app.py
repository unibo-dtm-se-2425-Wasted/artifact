import streamlit as st
from my_project.db.database import initialize_db, register_user, login_user, insert_food_item, get_all_food_items, delete_food_item

# --------------------- INIT DB ---------------------
initialize_db()

# --------------------- SESSION STATE ---------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "items" not in st.session_state:
    st.session_state.items = []

# --------------------- FUNZIONI ---------------------
def refresh_items():
    user_id = st.session_state.get("user_id")
    if user_id:
        st.session_state.items = get_all_food_items(user_id)
    else:
        st.session_state.items = []

def handle_login(username, password):
    user_id = login_user(username, password)
    if user_id:
        st.session_state.user_id = user_id
        refresh_items()
        st.success(f"Login avvenuto! Benvenuto {username}.")
    else:
        st.error("Username o password errati.")

def handle_register(username, password):
    if register_user(username, password):
        st.success("Registrazione avvenuta! Ora puoi fare login.")
    else:
        st.error("Username già esistente.")

def handle_add_item(name, category, purchase_date, expiration_date, quantity, unit):
    insert_food_item(st.session_state.user_id, name, category, purchase_date, expiration_date, quantity, unit)
    refresh_items()
    st.success(f"{name} aggiunto!")

# --------------------- INTERFACCIA ---------------------
st.title("Food Inventory App")

if st.session_state.user_id is None:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            handle_login(username, password)
    with col2:
        if st.button("Register"):
            handle_register(username, password)
else:
    st.subheader("I tuoi alimenti")
    refresh_items()
    
    for item in st.session_state.items:
        st.write(f"{item['Name']} - {item['Quantity']} {item['Unit']} (scade: {item['Expiration Date']})")

    st.subheader("Aggiungi nuovo alimento")
    name = st.text_input("Nome")
    category = st.text_input("Categoria")
    purchase_date = st.date_input("Data acquisto")
    expiration_date = st.date_input("Data scadenza")
    quantity = st.number_input("Quantità", min_value=0.0)
    unit = st.text_input("Unità")
    if st.button("Aggiungi"):
        handle_add_item(name, category, purchase_date, expiration_date, quantity, unit)
