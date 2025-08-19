import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
from my_project.db.database import (
    login_user,
    register_user,
    insert_food_item,
    get_all_food_items,
    delete_food_item,
    initialize_db
)

# ---------------------- INIT ----------------------
initialize_db()

st.set_page_config(page_title="Food Waste Manager", layout="wide")

# ---------------------- SESSION STATE ----------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "items" not in st.session_state:
    st.session_state.items = []

# ---------------------- UTILITY ----------------------
def check_status(exp_date_str):
    today = datetime.today().date()
    exp = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
    if exp < today:
        return "❌ Expired"
    elif (exp - today).days <= 3:
        return "⚠️ Expiring Soon"
    else:
        return "✅ OK"

def calculate_statistics(df):
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'] == '✅ OK']) + len(df[df['Status'] == '⚠️ Expiring Soon'])
    lost_value = expired_items * 2.5
    return total_items, expired_items, ok_items, lost_value

def refresh_items():
    if st.session_state.user_id:
        st.session_state.items = get_all_food_items(st.session_state.user_id)

# ---------------------- LOGIN / REGISTER ----------------------
if st.session_state.user_id is None:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("🔑 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                refresh_items()
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("📝 Register")
        new_username = st.text_input("Username", key="reg_user")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            success = register_user(new_username, new_password)
            if success:
                st.success("User registered! You can now login.")
            else:
                st.error("Username already exists")

# ---------------------- MAIN APP ----------------------
else:
    refresh_items()
    user_id = st.session_state.user_id
    st.title("🥦 Food Waste Manager")
    
    # --- ADD ITEM SIDEBAR ---
    with st.sidebar.form("add_food"):
        st.header("➕ Add a new item")
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
                insert_food_item(user_id, name, category, purchase_date.strftime("%Y-%m-%d"),
                                 expiration_date.strftime("%Y-%m-%d"), quantity, unit)
                st.success(f"'{name}' has been added to your fridge!")
                refresh_items()

    # --- DISPLAY ITEMS ---
    if not st.session_state.items:
        st.info("No items yet. Use the sidebar to add some!")
    else:
        df = pd.DataFrame(st.session_state.items)
        df["Status"] = df["Expiration Date"].apply(check_status)

        # --- FILTER ---
        st.sidebar.header("🔍 Filter Items")
        status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
        selected_status = st.sidebar.multiselect("Select statuses", status_options, default=[])
        filtered_df = df[df["Status"].isin(selected_status)] if selected_status else df

        # --- DISPLAY TABLE ---
        st.subheader("📋 Food List")
        st.dataframe(filtered_df[["Name", "Category", "Expiration Date", "Quantity", "Unit", "Status"]], hide_index=True)

        # --- DELETE ITEMS ---
        st.subheader("🗑️ Delete Items")
        for _, row in filtered_df.iterrows():
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{row['Name']} ({row['Quantity']} {row['Unit']}) - {row['Status']}")
            with col2:
                if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
                    delete_food_item(user_id, row["ID"])
                    refresh_items()
                    st.experimental_rerun()  # solo per aggiornare visivamente, opzionale

        # --- COOK TODAY ---
        st.subheader("🍽️ Meal Inspiration")
        expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]
        if st.button("What Can I Cook Today?"):
            ingredients = ",".join(expiring_soon["Name"].tolist())
            if ingredients:
                spoonacular_key = "f05378d894eb4eb8b187551e2a492c49"
                url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=1&ranking=1&apiKey={spoonacular_key}"
                response = requests.get(url)
                if response.ok and response.json():
                    recipe = response.json()[0]
                    st.markdown(f"**{recipe['title']}**")
                    st.image(recipe['image'])
                else:
                    st.info("No recipes found for these ingredients!")
            else:
                st.info("No expiring items available for cooking!")

        # --- STATISTICS ---
        st.subheader("📊 Stats")
        total, expired, ok, lost_value = calculate_statistics(df)
        st.write(f"Total Items: {total}")
        st.write(f"Expired Items: {expired}")
        st.write(f"OK / Expiring Soon Items: {ok}")
        st.write(f"Estimated lost value: ${lost_value:.2f}")

