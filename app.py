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
    check_user_credentials,
    add_user
)

# ------------------- LOGIC FUNCTIONS -------------------
def calculate_statistics(df):
    total_items = len(df)
    expired_items = len(df[df["Status"] == "❌ Expired"])
    ok_items = len(df[df["Status"].isin(["✅ OK", "⚠️ Expiring Soon"])])
    if "price_per_unit" in df.columns:
        lost_value = (df[df["Status"] == "❌ Expired"]["quantity"] * df[df["Status"] == "❌ Expired"]["price_per_unit"]).sum()
    else:
        lost_value = expired_items * 2.5  # fallback
    return total_items, expired_items, ok_items, lost_value


def check_status(exp_date_str):
    today = datetime.today().date()
    exp = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
    if exp < today:
        return "❌ Expired"
    elif (exp - today).days <= 3:
        return "⚠️ Expiring Soon"
    else:
        return "✅ OK"

# ------------------- INITIALIZE DB -------------------
initialize_db()

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Wasted", layout="wide")

# ------------------- SESSION MANAGEMENT -------------------
if "user" not in st.session_state:
    st.session_state.user = None

# ------------------- LOGIN / SIGNUP -------------------
if not st.session_state.user:
    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://i.pinimg.com/1200x/e0/28/8d/e0288dc89489bea01db65c12a176e8a8.jpg");
            background-size: cover;
            background-position: center;
        }
        div[data-testid="stVerticalBlock"]:has(#login-marker) {
            background-color: rgba(255, 255, 255, 0.92);
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.30);
            max-width: 520px;
            margin: 60px auto;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<span id="login-marker"></span>', unsafe_allow_html=True)
        st.title("🔑 Welcome!")
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        # ---- LOGIN TAB ----
        with tab_login:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if check_user_credentials(username.strip(), password.strip()):
                    st.session_state.user = username.strip()
                    st.success(f"Welcome {st.session_state.user}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        # ---- SIGNUP TAB ----
        with tab_signup:
            new_username = st.text_input("Choose a username", key="signup_user")
            new_password = st.text_input("Choose a password", type="password", key="signup_pass")
            if st.button("Create Account"):
                if new_username.strip() and new_password.strip():
                    add_user(new_username.strip(), new_password.strip())
                    st.success("✅ Account created! Now you can login.")
                else:
                    st.error("⚠️ Please enter both username and password")

    st.stop()

# ------------------- GLOBAL CSS -------------------
st.markdown("""
<style>
[data-testid="stAppViewBlockContainer"], [data-testid="block-container"] {
    padding: 0 !important;
    max-width: 100% !important;
}
html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden; }

.full-bleed {
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    width: 100vw;
}

#banner img {
    width: 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 0 !important;
}

.st-emotion-cache-1ldf560 > div:first-child,
[data-testid="stSidebar"] > div:first-child {
    background-color: #f6e3c3;
}

.ok-box, .soon-box, .expired-box {
    border: 1px solid;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 5px;
}
.ok-box { border-color: #2e6c46; background-color: rgba(46,108,70,0.2); }
.soon-box { border-color: #ad8600; background-color: rgba(173,134,0,0.2); }
.expired-box { border-color: #a60000; background-color: rgba(166,0,0,0.2); }

.status-badge { padding: 2px 6px; border-radius: 5px; font-weight: bold; text-align: center; color: #fff; }
.status-badge.ok { background-color: #2e6c46; }
.status-badge.soon { background-color: #ad8600; }
.status-badge.expired { background-color: #a60000; }

.stats-box {
    border: 2px solid #fffce4;
    background-color: #fffce4;
    border-radius: 5px;
    padding: 15px;
    margin-top: 15px;
}
html[data-theme="dark"] .stats-box {
    border: 2px solid #faca2b;
    background-color: #faca2b;
}
</style>
""", unsafe_allow_html=True)

# ------------------- BANNER -------------------
st.markdown("""
<div id="banner" class="full-bleed">
    <img src="https://i.pinimg.com/1200x/e0/28/8d/e0288dc89489bea01db65c12a176e8a8.jpg" alt="Food banner"/>
</div>
""", unsafe_allow_html=True)

# ------------------- HEADER & LOGOUT -------------------
c1, c2 = st.columns([7,1])
with c1:
    st.markdown(f"<h1 style='text-align:center;'>{st.session_state.user}'s fridge</h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", key="logout"):
        st.session_state.user = None
        st.rerun()

# ------------------- SUCCESS POPUP -------------------
@st.dialog("✅ Item Added")
def success_popup(name):
    st.success(f"'{name}' has been added to your fridge!")
    if st.button("OK"):
        st.rerun()

# ------------------- SIDEBAR: ADD ITEM -------------------
with st.sidebar.form("add_food"):
    st.header("➕ Add a new item")
    name = st.text_input("Product Name")
    category = st.selectbox("Category", ["Dairy", "Vegetables", "Meat", "Fruit", "Drinks", "Fish", "Other"])
    purchase_date = st.date_input("Purchase Date", datetime.today())
    expiration_date = st.date_input("Expiration Date")
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.text_input("Unit (e.g., kg, pcs, lt)")
    price_per_unit = st.number_input("Price per Unit (€)", min_value=0.0, step=0.01)  # NEW

    if st.form_submit_button("Add Item"):
        if not name.strip():
            st.toast("⚠️ Please enter a product name!", icon="⚠️")
        elif quantity <= 0:
            st.toast("⚠️ Quantity must be greater than 0!", icon="⚠️")
        elif price_per_unit <= 0:
            st.toast("⚠️ Price per unit must be greater than 0!", icon="⚠️")
        else:
            insert_food_item(st.session_state.user, name, category, purchase_date, expiration_date, quantity, unit, price_per_unit)
            success_popup(name)

# ------------------- SIDEBAR: FILTERS -------------------
with st.sidebar:
    st.header("🔍 Filter Items")
    status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
    selected_status = st.multiselect("Select one or more statuses", options=status_options, default=[])

# ------------------- DISPLAY FOOD ITEMS -------------------
st.subheader("📋 Food List")
items = get_all_food_items(st.session_state.user)

if not items:
    st.info("No items yet. Use the sidebar to add some!")
    df = pd.DataFrame(columns=["ID","User","Name","Category","Purchase Date",
                               "Expiration Date","Quantity","Unit","Price per Unit","Status"])
else:
    # Include price_per_unit column from DB
    df = pd.DataFrame(
        items,
        columns=["ID","User","Name","Category","Purchase Date","Expiration Date",
                 "Quantity","Unit","Price per Unit"]
    )
    # Add status column
    df["Status"] = df["Expiration Date"].apply(check_status)

# Filter by selected status
filtered_df = df.copy()
if selected_status:
    filtered_df = filtered_df[filtered_df["Status"].isin(selected_status)]

if not filtered_df.empty:
    st.dataframe(
        filtered_df[["Name","Category","Purchase Date","Expiration Date","Quantity","Unit","Price per Unit","Status"]],
        hide_index=True
    )

# Filter items expiring soon (for recipes)
expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]


    # ------------------- DELETE CONFIRMATION -------------------
@st.dialog("Confirm Deletion")
def confirm_delete(item_id, name):
    st.warning(f"Are you sure you want to delete '{name}'?")
    c1, c2 = st.columns(2)
    if c1.button("✅ Yes, delete"):
        delete_food_item(item_id, st.session_state.user)
        st.success(f"'{name}' has been deleted!")
        st.rerun()
    if c2.button("❌ Cancel"):
        st.rerun()

    # ------------------- DELETE ITEMS -------------------
st.subheader("🗑️ Delete Items in the Fridge")
col1, col2 = st.columns(2)
for idx, row in filtered_df.iterrows():
    status_class = "ok" if "✅ OK" in row["Status"] else "soon" if "⚠️ Expiring Soon" in row["Status"] else "expired"
    box_class = f"{status_class}-box"
    target_col = col1 if idx % 2 == 0 else col2
    with target_col:
        st.markdown(f"""
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
        """, unsafe_allow_html=True)
        if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
            confirm_delete(row["ID"], row["Name"])

# ------------------- MEAL INSPIRATION -------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("🍽️ Meal Inspiration")
expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]

if st.button("What Can I Cook Today?"):
    ingredients = expiring_soon["Name"].tolist()
    if ingredients:
        st.info("Searching recipes for: " + ", ".join(ingredients))
        spoonacular_key = "f05378d894eb4eb8b187551e2a492c49"
        query_ingredients = ",".join(ingredients)
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={query_ingredients}&number=1&ranking=1&apiKey={spoonacular_key}"

        with st.spinner("Finding recipe..."):
            try:
                response = requests.get(url)
                recipes = response.json()
                if recipes:
                    recipe = recipes[0]
                    st.markdown(f"### 👨‍🍳 {recipe['title']}")
                    if recipe.get("image"):
                        st.image(recipe["image"], width=400)

                    steps_url = f"https://api.spoonacular.com/recipes/{recipe['id']}/analyzedInstructions?apiKey={spoonacular_key}"
                    steps_resp = requests.get(steps_url).json()
                    if steps_resp and steps_resp[0].get("steps"):
                        st.markdown("*Steps:*")
                        for step in steps_resp[0]["steps"]:
                            st.markdown(f"*{step['number']}.* {step['step']}")
                    else:
                        st.info("No detailed instructions available.")
                else:
                    st.warning("No recipes found with those ingredients.")
            except Exception as e:
                st.error(f"Error fetching recipe: {e}")
    else:
        st.success("No items are expiring soon — nothing urgent to cook!")

# ------------------- ANALYSIS -------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("📈 General Analysis")
c1, c2 = st.columns(2)

with c1:
    st.subheader("🥧 Status Overview")
    status_counts = df["Status"].value_counts()
    status_colors = {"❌ Expired":"#ffcccc","⚠️ Expiring Soon":"#fff2cc","✅ OK":"#ccffcc"}
    fig = px.pie(
        names=status_counts.index,
        values=status_counts.values,
        title="Food Status Distribution",
        color=status_counts.index,
        color_discrete_map=status_colors
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    total_items, expired_items, ok_items, lost_value = calculate_statistics(df)
    st.markdown(f"""
    <div class="stats-box">
        <h3 style="margin-top:0;">📊 Waste Statistics</h3>
        <strong>Total Items:</strong> {total_items}<br>
        <strong>Expired Items:</strong> {expired_items}<br>
        <strong>OK / Expiring Soon Items:</strong> {ok_items}<br>
    </div>
    """, unsafe_allow_html=True)
    if expired_items > 0:
        st.warning(f"💸 Estimated Economic Loss: *€{lost_value:.2f}*")
    else:
        st.info("No food waste detected! 🎉")
