import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt 
import plotly.express as px
import requests

from db.database import initialize_db, insert_food_item, get_all_food_items

# Init DB
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

# ---------- Sidebar Form to Add Food ----------
with st.sidebar.form("add_food"):
    st.header("➕ Add New Food Item")

    name = st.text_input("Product Name")
    category = st.selectbox("Category", ["Dairy", "Vegetables", "Meat", "Fruit", "Beverage", "Other"])
    purchase_date = st.date_input("Purchase Date", datetime.today())
    expiration_date = st.date_input("Expiration Date")
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.text_input("Unit (e.g., kg, pack, bottle)")

    submitted = st.form_submit_button("Add Item")

    if submitted and name:
        insert_food_item(name, category, purchase_date, expiration_date, quantity, unit)
        st.success(f"'{name}' added to your fridge! Refresh to see it below.")

# ---------- View Food Items ----------
st.subheader("📋 Food List")

items = get_all_food_items()

if items:
    df = pd.DataFrame(items, columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"])

    # ✅ 1. Status Column Calculation
    def check_status(exp_date_str):
        today = datetime.today().date()
        exp = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
        if exp < today:
            return "❌ Expired"
        elif (exp - today).days <= 3:
            return "⚠️ Expiring Soon"
        else:
            return "✅ OK"

    df["Status"] = df["Expiration Date"].apply(check_status)

    # ✅ 2. Visual Alerts for Expiring Items
    expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]
    expired = df[df["Status"] == "❌ Expired"]

    if not expiring_soon.empty:
        st.warning("⚠️ The following items are expiring soon:")
        st.table(expiring_soon[["Name", "Expiration Date", "Quantity", "Unit"]])

    if not expired.empty:
        st.error("❌ These items have expired:")
        st.table(expired[["Name", "Expiration Date", "Quantity", "Unit"]])

    # ---------- Data Table ----------
    st.dataframe(df[["Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit", "Status"]])

    # # ✅ 3. "What Can I Cook Today?" Button
st.subheader("🍽️ Meal Inspiration")

if st.button("What Can I Cook Today?"):
    ingredients = expiring_soon["Name"].tolist()

    if ingredients:
        # Directly insert your Spoonacular API key
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
                        st.markdown("**Steps:**")
                        for step in steps:
                            st.markdown(f"**{step['number']}.** {step['step']}")
                    else:
                        st.info("No detailed instructions available.")
                else:
                    st.warning("No recipes found with those ingredients.")
            except Exception as e:
                st.error(f"Error fetching recipe: {e}")
    else:
        st.success("No items are expiring soon — nothing urgent to cook!")


    # ---------- Pie Chart ----------
    st.subheader("🥧 Status Overview")
    status_counts = df["Status"].value_counts()
    st.write(status_counts)

    fig = px.pie(
        names=status_counts.index,
        values=status_counts.values,
        title="Food Status Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig, use_container_width=True)

    # ✅ 4. Waste Statistics
    st.subheader("📊 Waste Statistics")

    total_items = len(df)
    expired_items = len(expired)
    consumed_items = total_items - expired_items  # Simplified logic

    st.metric("Total Items", total_items)
    st.metric("Expired Items", expired_items)
    st.metric("Consumed (or Still OK)", consumed_items)

    if expired_items > 0:
        avg_price_per_item = 2.5  # placeholder for calculation
        lost_value = expired_items * avg_price_per_item
        st.write(f"💸 Estimated economic loss: **€{lost_value:.2f}**")

else:
    st.info("No food items yet. Use the sidebar to add some!")


