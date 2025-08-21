import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests

from db.database import initialize_db, insert_food_item, get_all_food_items

# ----------------------- INIT -----------------------------------------------
initialize_db()
st.set_page_config(page_title="Food Waste Manager", layout="wide")

# --- Style overrides (buttons, etc.)
st.markdown("""
<style>
.stButton > button {
    background-color:#4CAF50; color:white; border:none; border-radius:6px; padding:0.5em 1em;
}
.logout > button {
    background-color:#e94e4e; color:white; border:none; border-radius:6px; padding:0.4em 0.8em;
}
</style>
""", unsafe_allow_html=True)

# ----------------------- LOGIN ----------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🥦 Food Waste Manager — Login")
    username = st.text_input("Enter your username:")
    if st.button("Login"):
        if username.strip():
            st.session_state.user = username.strip()
            st.success(f"Welcome {st.session_state.user}!")
            st.rerun()
        else:
            st.error("Please enter a username.")
    st.stop()

# ----------------------- LOGOUT BUTTON --------------------------------------
col1, col2 = st.columns([7,1])
with col2:
    if st.button("Logout", key="logout"):
        st.session_state.user = None
        st.rerun()

# ---------------------- MAIN APP -------------------------------------------
user = st.session_state.user
st.title(f"🥦 Food Waste Manager — {user}'s fridge")

# ------ SIDEBAR ADD FORM ----------------------------------------------------
with st.sidebar.form("add_food"):
    st.header("➕ Add New Food Item")
    name = st.text_input("Product Name")
    category = st.selectbox("Category", ["Dairy", "Vegetables", "Meat", "Fruit", "Beverage", "Other"])
    purchase_date = st.date_input("Purchase Date", datetime.today())
    expiration_date = st.date_input("Expiration Date")
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.text_input("Unit (e.g. kg, pack)")
    submitted = st.form_submit_button("Add Item")
    if submitted and name:
        insert_food_item(user, name, category, purchase_date, expiration_date, quantity, unit)
        st.success(f"'{name}' added.")
        st.rerun()

# --------- VIEW ITEMS --------------------------------------------------------
st.subheader("📋 Food List")
items = get_all_food_items(user)

if items:
    df = pd.DataFrame(items, columns=["ID","User","Name","Category","Purchase Date","Expiration Date","Quantity","Unit"])

    def status(exp_date):
        today = datetime.today().date()
        if not isinstance(exp_date,str): return "Unknown"
        try: d = datetime.strptime(exp_date,"%Y-%m-%d").date()
        except: return "Unknown"
        if d < today: return "❌ Expired"
        if (d - today).days <= 3: return "⚠️ Expiring Soon"
        return "✅ OK"

    df["Status"] = df["Expiration Date"].apply(status)
    expiring = df[df["Status"]=="⚠️ Expiring Soon"]
    expired = df[df["Status"]=="❌ Expired"]

    if not expiring.empty:
        st.warning("⚠️ Expiring Soon:")
        st.table(expiring[["Name","Expiration Date","Quantity","Unit"]])
    if not expired.empty:
        st.error("❌ Already Expired:")
        st.table(expired[["Name","Expiration Date","Quantity","Unit"]])

    st.dataframe(df[["Name","Category","Purchase Date","Expiration Date","Quantity","Unit","Status"]])

    # ---------- MEAL SUGGEST --------------------------------------------------
    st.subheader("🍽️ Meal Inspiration")
    if st.button("What can I cook?"):
        ingred = expiring["Name"].tolist()
        if ingred:
            key = "f05378d894eb4eb8b187551e2a492c49"
            q = ",".join(ingred)
            url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={q}&number=1&ranking=1&apiKey={key}"
            try:
                r=requests.get(url).json()
                if isinstance(r,list) and r:
                    rec=r[0]
                    st.markdown(f"### 👨‍🍳 {rec['title']}")
                    if rec.get("image"): st.image(rec["image"])
                    steps=requests.get(f"https://api.spoonacular.com/recipes/{rec['id']}/analyzedInstructions?apiKey={key}").json()
                    if steps and steps[0].get("steps"):
                        for s in steps[0]["steps"]:
                            st.markdown(f"**{s['number']}.** {s['step']}")
                    else:
                        st.info("No steps available.")
                else:
                    st.warning("No recipe found.")
            except Exception as e:
                st.error(str(e))
        else:
            st.success("Nothing urgent to cook!")

    # ---------- STATS ---------------------------------------------------------
    st.subheader("🥧 Status Overview")
    fig = px.pie(names=df["Status"].value_counts().index,
                 values=df["Status"].value_counts().values)
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("📊 Waste Statistics")
    total=len(df); exp=len(expired); ok=total-exp
    st.metric("Total Items",total)
    st.metric("Expired",exp)
    st.metric("Consumed/OK",ok)
    if exp>0:
        loss = exp*2.5
        st.write(f"💸 Estimated loss: **€{loss:.2f}**")

else:
    st.info("Add your first food item from the sidebar.")
