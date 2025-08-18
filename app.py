import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests

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
    .ok-box {
        border: 1px solid #006300;
        background-color: #ccffcc;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 5px;
    }
    .soon-box {
        border: 1px solid #ad8600;
        background-color: #fff2cc;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 5px;
    }
    .expired-box {
        border: 1px solid #a60000;
        background-color: #ffcccc;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 5px;
    }
    .status-badge {
        padding: 2px 5px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        color: white;
    }
    .status-badge.ok {
        background-color: #006300;
    }
    .status-badge.soon {
        background-color: #ad8600;
    }
    .status-badge.expired {
        background-color: #a60000;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🥦 Food Waste Manager")

# ---------- POPUP SUCCESS DIALOG ----------
@st.dialog("✅ Item Added")
def success_popup(name):
    st.success(f"'{name}' has been added to your fridge!")
    if st.button("OK"):
        st.rerun()

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
            st.toast("⚠️ Please write down your item before adding!", icon="⚠️")
        else:
            insert_food_item(name, category, purchase_date, expiration_date, quantity, unit)
            success_popup(name)  # 🔥 Popup in center


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

    # --- DELETE ITEMS CONTAINERS (UPDATED SECTION) ---
    st.subheader("🗑️ Delete Items in the Fridge")

    items_to_display = filtered_df.iterrows()
    
    col1, col2 = st.columns(2)

    for index, row in items_to_display:
        status_class = "ok" if "✅ OK" in row["Status"] else "soon" if "⚠️ Expiring Soon" in row["Status"] else "expired"
        box_class = f"{status_class}-box"

        if index % 2 == 0:
            with col1:
                # Use a single markdown block for all item info
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
                
                # Button is outside the colored box
                if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
                    confirm_delete(row["ID"], row["Name"])

        else:
            with col2:
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
            
    # ---------- "What Can I Cook Today?" BUTTON ----------
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