import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
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

def refresh_items():
    if st.session_state.user_id:
        st.session_state.items = get_all_food_items(st.session_state.user_id)
        for item in st.session_state.items:
            item["Status"] = check_status(item["Expiration Date"])

def calculate_statistics(df):
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'].isin(['✅ OK', '⚠️ Expiring Soon'])])
    lost_value = expired_items * 2.5
    return total_items, expired_items, ok_items, lost_value

# ---------------------- AUTH ----------------------
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

# ---------------------- APP ----------------------
else:
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
                refresh_items()
                st.success(f"'{name}' has been added to your fridge!")

    # --- REFRESH ITEMS ---
    refresh_items()
    items = st.session_state.items

    if not items:
        st.info("No items yet. Use the sidebar to add some!")
    else:
        df = pd.DataFrame(items)

        # --- FILTER ---
        st.sidebar.header("🔍 Filter Items")
        status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
        selected_status = st.sidebar.multiselect("Select statuses", status_options, default=[])
        filtered_df = df[df["Status"].isin(selected_status)] if selected_status else df

        # --- DISPLAY ---
        st.subheader("📋 Food List")
        st.dataframe(filtered_df[["Name", "Category", "Expiration Date", "Quantity", "Unit", "Status"]], hide_index=True)

        # --- DELETE ITEMS ---
        st.subheader("🗑️ Delete Items")
        to_delete = []
        for _, row in filtered_df.iterrows():
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(f"{row['Name']} ({row['Quantity']} {row['Unit']}) - {row['Status']}")
            with col2:
                if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
                    to_delete.append(row["ID"])
        # delete all selected
        for item_id in to_delete:
            delete_food_item(user_id, item_id)
        if to_delete:
            refresh_items()
            st.success(f"{len(to_delete)} item(s) deleted!")

        # --- STATISTICS ---
        st.subheader("📈 General Analysis")
        col1, col2 = st.columns(2)
        with col1:
            status_counts = df["Status"].value_counts()
            fig = px.pie(
                names=status_counts.index,
                values=status_counts.values,
                color=status_counts.index,
                color_discrete_map={"❌ Expired":"#ffcccc","⚠️ Expiring Soon":"#fff2cc","✅ OK":"#ccffcc"}
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            total_items, expired_items, ok_items, lost_value = calculate_statistics(df)
            st.markdown(f"""
                **Total Items:** {total_items}  
                **Expired Items:** {expired_items}  
                **OK / Expiring Soon Items:** {ok_items}  
            """)
            if expired_items > 0:
                st.warning(f"💸 Estimated Economic Loss: €{lost_value:.2f}")
            else:
                st.info("No food waste detected!")

    # --- LOGOUT ---
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.items = []
        st.success("Logged out successfully!")
