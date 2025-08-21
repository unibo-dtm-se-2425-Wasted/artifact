import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests

from my_project.db.database import (
    initialize_db,
    insert_food_item,
    get_all_food_items,
    delete_food_item,
    get_unique_users,
)

# --- LOGIC FUNCTIONS ---
def calculate_statistics(df):
    total_items = len(df)
    expired_items = len(df[df["Status"] == "❌ Expired"])
    ok_items = len(df[df["Status"] == "✅ OK"]) + len(df[df["Status"] == "⚠️ Expiring Soon"])
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

# Initialize DB
initialize_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wasted", layout="wide")

# --- LOGIN HANDLING ---
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("Welcome to Wasted!")
    username = st.text_input("Enter your username:")
    if st.button("Login"):
        if username.strip():
            st.session_state.user = username.strip()
            st.success(f"Welcome {st.session_state.user}!")
            st.rerun()
        else:
            st.error("Please enter a username.")
    st.stop()

# --- GLOBAL CSS ---
st.markdown(
    """
<style>

/* ================================================================================
STILI GENERALI E LAYOUT
================================================================================
*/

/* Rimuovi padding dal main container */
[data-testid="stAppViewBlockContainer"] {
    padding: 0 !important;
}
[data-testid="block-container"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Previeni scrollbar orizzontale */
html, body, [data-testid="stAppViewContainer"] {
    overflow-x: hidden;
}

/* Utility full-bleed */
.full-bleed {
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    width: 100vw;
}

/* Banner */
#banner img {
    width: 100%;
    height: 300px;      /* 👈 altezza fissa */
    object-fit: cover;  /* 👈 crop senza deformare */
    border-radius: 0 !important;
    margin: 0;
}


/* -------------------- SIDEBAR -------------------- */
.st-emotion-cache-1ldf560 > div:first-child {
    background-color: #f6e3c3;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #f6e3c3;
}


/* ================================================================================
STILI DEI COMPONENTI PERSONALIZZATI
================================================================================
*/

/* Contenitori per gli stati degli alimenti (ok, in scadenza, scaduto) */
.ok-box, .soon-box, .expired-box {
    border: 1px solid;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 5px;
    color: inherit;
}
.ok-box { border-color: #2e6c46; background-color: rgba(46,108,70,0.2); }
.soon-box { border-color: #ad8600; background-color: rgba(173,134,0,0.2); }
.expired-box { border-color: #a60000; background-color: rgba(166,0,0,0.2); }

/* Etichette colorate per lo stato */
.status-badge {
    padding: 2px 6px;
    border-radius: 5px;
    font-weight: bold;
    text-align: center;
    color: #fff;
}
.status-badge.ok { background-color: #2e6c46; }
.status-badge.soon { background-color: #ad8600; }
.status-badge.expired { background-color: #a60000; }

/* Box delle statistiche */
.stats-box {
    border: 2px solid #fffce4;
    background-color: #fffce4;
    border-radius: 5px;
    padding: 15px;
    margin-top: 15px;
    color: #000;
}
/* Stile del box statistiche per il tema scuro */
html[data-theme="dark"] .stats-box {
    border: 2px solid #faca2b;
    background-color: #faca2b;
    color: #000;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- BANNER (TOP OF MAIN, TRUE FULL-WIDTH) ---
st.markdown(
    """
    <div id="banner" class="full-bleed">
        <img src="https://i.pinimg.com/736x/c6/49/90/c64990fc753fdcfbf18fe193690fd5e9.jpg"
             alt="Food banner"
             style="width:100%; height:300px; object-fit:cover;"/>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- LOGOUT BUTTON ROW (below banner) ---
c1, c2 = st.columns([7, 1])
with c1:
    user = st.session_state.user
    st.markdown(f"<h1 style='text-align: center;'>{user}'s fridge</h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", key="logout", type="primary"):
        st.session_state.user = None
        st.rerun()

# ---------- POPUP SUCCESS DIALOG ----------
@st.dialog("✅ Item Added")
def success_popup(name):
    st.success(f"'{name}' has been added to your fridge!")
    if st.button("OK"):
        st.rerun()

# ---------- SIDEBAR: ADD ITEM ----------
st.markdown("<br><br>", unsafe_allow_html=True)
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
            insert_food_item(user, name, category, purchase_date, expiration_date, quantity, unit)
            success_popup(name)

# ---------- SIDEBAR: FILTERS ----------
with st.sidebar:
    st.header("🔍 Filter Items")
    status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
    selected_status = st.multiselect(
        "Select one or more statuses",
        options=status_options,
        default=[],
        key="status_filter",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("👤 Filter User")
    user_options = get_unique_users()
    selected_users = st.multiselect(
        "Select one or more users",
        options=user_options,
        default=user_options,
        key="user_filter",
    )

# ---------- DISPLAY ITEMS ----------
st.subheader("📋 Food List")
items = get_all_food_items(user)

if not items:
    st.info("No items yet. Use the sidebar to add some!")
else:
    df = pd.DataFrame(
        items,
        columns=["ID", "User", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"],
    ).reset_index(drop=True)

    df["Status"] = df["Expiration Date"].apply(check_status)

    # Filtering
    filtered_df = df.copy()
    if selected_users:
        filtered_df = filtered_df[filtered_df["User"].isin(selected_users)]
    if selected_status:
        filtered_df = filtered_df[filtered_df["Status"].isin(selected_status)]

    if filtered_df.empty:
        st.info("No items match the selected filters.")
    else:
        st.dataframe(
            filtered_df[["Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit", "Status", "User"]]
            .reset_index(drop=True),
            hide_index=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------- DELETE CONFIRMATION ----------
    @st.dialog("Confirm Deletion")
    def confirm_delete(item_id, name):
        st.warning(f"Are you sure you want to delete '{name}'?")
        ca, cb = st.columns(2)
        if ca.button("✅ Yes, delete"):
            delete_food_item(item_id, user)
            st.success(f"'{name}' has been deleted!")
            st.rerun()
        if cb.button("❌ Cancel"):
            st.rerun()

    # --- DELETE ITEMS UI ---
    st.subheader("🗑️ Delete Items in the Fridge")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for idx, row in filtered_df.iterrows():
        status_class = "ok" if "✅ OK" in row["Status"] else "soon" if "⚠️ Expiring Soon" in row["Status"] else "expired"
        box_class = f"{status_class}-box"

        target_col = col1 if idx % 2 == 0 else col2
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
                unsafe_allow_html=True,
            )
            if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
                confirm_delete(row["ID"], row["Name"])

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------- MEAL INSPIRATION ----------
    st.subheader("🍽️ Meal Inspiration")
    expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]

    if st.button("What Can I Cook Today?"):
        ingredients = expiring_soon["Name"].tolist()

        if ingredients:
            spoonacular_key = "f05378d894eb4eb8b187551e2a492c49"
            st.info("Searching recipes for: " + ", ".join(ingredients))
            query_ingredients = ",".join(ingredients)
            url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={query_ingredients}&number=1&ranking=1&apiKey={spoonacular_key}"

            with st.spinner("Finding recipe..."):
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
                            st.markdown("*Steps:*")
                            for step in steps:
                                st.markdown(f"*{step['number']}.* {step['step']}")
                        else:
                            st.info("No detailed instructions available.")
                    else:
                        st.warning("No recipes found with those ingredients.")
                except Exception as e:
                    st.error(f"Error fetching recipe: {e}")
        else:
            st.success("No items are expiring soon — nothing urgent to cook!")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------- ANALYSIS ----------
    st.subheader("📈 General Analysis")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🥧 Status Overview")
        status_counts = df["Status"].value_counts()
        status_colors = {
            "❌ Expired": "#ffcccc",
            "⚠️ Expiring Soon": "#fff2cc",
            "✅ OK": "#ccffcc",
        }
        fig = px.pie(
            names=status_counts.index,
            values=status_counts.values,
            title="Food Status Distribution",
            color=status_counts.index,
            color_discrete_map=status_colors,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        total_items, expired_items, ok_items = calculate_statistics(df)
        lost_value = expired_items * 2.5 if expired_items > 0 else 0
        st.markdown(
            f"""
            <div class="stats-box">
                <h3 style="margin-top:0;">📊 Waste Statistics</h3>
                <br>
                <strong>Total Items:</strong> {total_items}<br>
                <strong>Expired Items:</strong> {expired_items}<br>
                <strong>OK / Expiring Soon Items:</strong> {ok_items}
                <br>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if expired_items > 0:
            st.warning(f"💸 Estimated Economic Loss: *€{lost_value:.2f}*")
        else:
            st.info("No food waste detected! Yey 🎉")
