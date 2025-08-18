import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests
import uuid   # NEW

# Ensure this import matches your project structure
from my_project.db.database import initialize_db, insert_food_item, get_all_food_items, delete_food_item

# --- USER SESSION --- #
if "user_id" not in st.session_state:     # NEW
    st.session_state["user_id"] = str(uuid.uuid4())   # NEW

# --- LOGIC FUNCTIONS --- #
def calculate_statistics(df):
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'] == '✅ OK']) + len(df[df['Status'] == '⚠️ Expiring Soon'])
    return total_items, expired_items, ok_items

def check_status(exp_date_str):
    today = datetime.today().date()
    exp = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
    if exp < today:
        return "❌ Expired"
    elif (exp - today).days <= 3:
        return "⚠️ Expiring Soon"
    else:
        return "✅ OK"

# ----------------------------------------------------------------------------------

# Initialize the database
initialize_db()

# --- PAGE CONFIGURATION AND STYLE --- #
st.set_page_config(page_title="Food Waste Manager", layout="wide")

st.title("🥦 Food Waste Manager")

# ---------- POPUP SUCCESS DIALOG ---------- #
@st.dialog("✅ Item Added")
def success_popup(name):
    st.success(f"'{name}' has been added to your fridge!")
    if st.button("OK"):
        st.rerun()

# ---------- SIDEBAR: ADD ITEM ---------- #
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
            st.toast("⚠️ Please write down your item before adding!", icon="⚠️")
        else:
            insert_food_item(   # NEW add user_id
                st.session_state["user_id"], 
                name, category, purchase_date, expiration_date, quantity, unit
            )
            success_popup(name)

# ---------- FILTERS ---------- #
with st.sidebar:
    st.header("🔍 Filter Items")
    status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
    selected_status = st.multiselect("Select one or more statuses", options=status_options, default=[])

# ---------- DISPLAY ITEMS ---------- #
st.subheader("📋 Food List")

items = get_all_food_items(st.session_state["user_id"])   # NEW pass user_id

if not items:
    st.info("No items yet. Use the sidebar to add some!")
else:
    df = pd.DataFrame(
        items,
        columns=["ID", "user_id", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"]  # NEW user_id
    ).drop(columns=["user_id"]).reset_index(drop=True)  # hide user_id

    df["Status"] = df["Expiration Date"].apply(check_status)

    if selected_status:
        filtered_df = df[df["Status"].isin(selected_status)]
    else:
        filtered_df = df

    if filtered_df.empty:
        st.info("No items match the selected filters.")
    else:
        st.dataframe(
            filtered_df[["Name", "Category", "Expiration Date", "Quantity", "Unit", "Status"]].reset_index(drop=True),
            hide_index=True
        )

    # ---------- DELETE ---------- #
    @st.dialog("Confirm Deletion")
    def confirm_delete(item_id, name):
        st.warning(f"Are you sure you want to delete '{name}'?")
        col_a, col_b = st.columns(2)
        if col_a.button("✅ Yes, delete"):
            delete_food_item(st.session_state["user_id"], item_id)   # NEW user_id
            st.success(f"'{name}' has been deleted!")
            st.rerun()
        if col_b.button("❌ Cancel"):
            st.rerun()

    st.subheader("🗑️ Delete Items in the Fridge")
    col1, col2 = st.columns(2)

    for index, row in filtered_df.iterrows():
        status_class = "ok" if "✅ OK" in row["Status"] else "soon" if "⚠️ Expiring Soon" in row["Status"] else "expired"
        box_class = f"{status_class}-box"
        target_col = col1 if index % 2 == 0 else col2

        with target_col:
            st.markdown(
                f"""
                <div class="{box_class}">
                    <div style="display:flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight:bold;">{row['Name']}</span>
                        <div class="status-badge {status_class}">{row['Status'].split(' ')[1]}</div>
                    </div>
                    <br>
                    <strong>Category:</strong> {row['Category']}<br>
                    <strong>Expiration Date:</strong> {row['Expiration Date']}<br>
                    <strong>Quantity:</strong> {row['Quantity']} {row['Unit']}
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
                confirm_delete(row["ID"], row["Name"])

# ---------- ANALYTICS ---------- #
st.subheader("📈 General Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Status Overview")
    status_counts = df["Status"].value_counts()
    fig = px.pie(
        names=status_counts.index,
        values=status_counts.values,
        title="Food Status Distribution",
        color=status_counts.index,
        color_discrete_map={
            "❌ Expired": "#ffcccc",
            "⚠️ Expiring Soon": "#fff2cc",
            "✅ OK": "#ccffcc"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Waste Statistics")
    total_items, expired_items, ok_items = calculate_statistics(df)
    st.metric("Total Items", total_items)
    st.metric("Expired Items", expired_items)
    st.metric("OK / Expiring Soon Items", ok_items)

    if expired_items > 0:
        avg_price_per_item = 2.5
        lost_value = expired_items * avg_price_per_item
        st.warning(f"💸 Estimated Economic Loss: **€{lost_value:.2f}**")
    else:
        st.info("No food waste detected! 🎉")
