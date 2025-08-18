import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Ensure this import matches your project structure
from my_project.db.database import initialize_db, insert_food_item, get_all_food_items, delete_food_item

# --- LOGIC FUNCTIONS ---

def calculate_statistics(df):
    """Calculate basic statistics from the DataFrame."""
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'] == '✅ OK']) + len(df[df['Status'] == '⚠️ Expiring Soon'])
    return total_items, expired_items, ok_items

def check_status(exp_date_str):
    """Check the status of an item based on its expiration date."""
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

# --- PAGE CONFIGURATION AND STYLE ---
st.set_page_config(page_title="Food Waste Manager", layout="wide")

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
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🥦 Food Waste Manager")

# ---------- SIDEBAR: ADD ITEM ----------
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
            # 🚨 Block insert and notify user
            st.toast("⚠️ Please write down your item before adding!", icon="⚠️")
        else:
            # ✅ Add to database only if name is not empty
            insert_food_item(name, category, purchase_date, expiration_date, quantity, unit)
            st.toast(f"✅ '{name}' has been added to your fridge!", icon="🎉")
            st.rerun()

# ---------- SIDEBAR: MULTI-SELECT FILTERS ----------
with st.sidebar:
    st.header("🔍 Filter Items")
    status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
    selected_status = st.multiselect(
        "Select one or more statuses",
        options=status_options,
        default=[]  # Empty = show all
    )

# ---------- DISPLAY ITEMS ----------
st.subheader("📋 Food List")

items = get_all_food_items()

if not items:
    st.info("No items yet. Use the sidebar to add some!")
else:
    df = pd.DataFrame(
        items,
        columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"]
    ).reset_index(drop=True)

    df["Status"] = df["Expiration Date"].apply(check_status)

    # Filter based on multi-selection
    filtered_df = df.copy()
    if selected_status:
        filtered_df = df[df["Status"].isin(selected_status)]

    # Filtered Table
    if filtered_df.empty:
        st.info("No items match the selected filters.")
    else:
        st.dataframe(
            filtered_df[["Name", "Category", "Expiration Date", "Quantity", "Unit", "Status"]]
            .reset_index(drop=True),
            hide_index=True
        )

    # ---------- DELETE CONFIRMATION FUNCTION ----------
    @st.dialog("Confirm Deletion")
    def confirm_delete(item_id, name):
        st.warning(f"Are you sure you want to delete '{name}'?")
        col_a, col_b = st.columns(2)
        if col_a.button("✅ Yes, delete"):
            delete_food_item(item_id)
            st.success(f"'{name}' has been deleted!")
            st.rerun()
        if col_b.button("❌ Cancel"):
            st.rerun()

    # ---------- FULL ITEM TABLE WITH BUTTONS ----------
    st.subheader("All Items in the Fridge")

    col_header = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
    headers = ["Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit", "Status", "Action"]
    for col, header_text in zip(col_header, headers):
        col.markdown(f"**{header_text}**")

    st.markdown("---")
    
    for index, row in df.iterrows():
        with st.container(border=False):
            col_data = st.columns([2, 2, 2, 2, 1, 1, 2, 1])
            
            col_data[0].write(row['Name'])
            col_data[1].write(row['Category'])
            col_data[2].write(row['Purchase Date'])
            col_data[3].write(row['Expiration Date'])
            col_data[4].write(row['Quantity'])
            col_data[5].write(row['Unit'])
            
            status_class = "ok" if "OK" in row["Status"] else "soon" if "Soon" in row["Status"] else "expired"
            col_data[6].markdown(f"<div class='{status_class}'>{row['Status']}</div>", unsafe_allow_html=True)
            
            if col_data[7].button("🗑️", key=f"del_filtered_{row['ID']}"):
                confirm_delete(row["ID"], row["Name"])
   
    # ---------- PIE CHART + STATISTICS ----------
    st.subheader("📈 General Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥧 Status Overview")
        status_counts = df["Status"].value_counts()
        
        status_colors = {
            "❌ Expired": "#ffcccc",
            "⚠️ Expiring Soon": "#fff2cc",
            "✅ OK": "#ccffcc"
        }

        fig = px.pie(
            names=status_counts.index,
            values=status_counts.values,
            title="Food Status Distribution",
            color=status_counts.index,
            color_discrete_map=status_colors
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
            st.info("No food waste detected! Yey")
