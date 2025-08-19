import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from datetime import datetime
import plotly.express as px
import requests

from my_project.db import database
  # nostro modulo aggiornato (DB per utente)

# --------------- UTILITIES ---------------

def calculate_statistics(df):
    """Calcola statistiche di base dal DataFrame."""
    total_items = len(df)
    expired_items = len(df[df['Status'] == '❌ Expired'])
    ok_items = len(df[df['Status'] == '✅ OK']) + len(df[df['Status'] == '⚠️ Expiring Soon'])
    return total_items, expired_items, ok_items

def check_status(exp_date_str):
    """Determina lo stato di un item rispetto alla data di scadenza."""
    today = datetime.today().date()
    exp = datetime.strptime(str(exp_date_str), "%Y-%m-%d").date()
    if exp < today:
        return "❌ Expired"
    elif (exp - today).days <= 3:
        return "⚠️ Expiring Soon"
    else:
        return "✅ OK"

# --------------- PAGINA / STILI ---------------

st.set_page_config(page_title="Food Waste Manager", layout="wide")

st.markdown("""
<style>
/* -------------------- STATUS BOXES -------------------- */
.ok-box {
    border: 1px solid #2e6c46;
    background-color: rgba(46, 108, 70, 0.2);
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 5px;
    color: var(--text-color);
}
.soon-box {
    border: 1px solid #ad8600;
    background-color: rgba(173, 134, 0, 0.2);
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 5px;
    color: var(--text-color);
}
.expired-box {
    border: 1px solid #a60000;
    background-color: rgba(166, 0, 0, 0.2);
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 5px;
    color: var(--text-color);
}

/* -------------------- STATUS BADGES -------------------- */
.status-badge {
    padding: 2px 6px;
    border-radius: 5px;
    font-weight: bold;
    text-align: center;
    color: white;
}
.status-badge.ok { background-color: #2e6c46; }
.status-badge.soon { background-color: #ad8600; }
.status-badge.expired { background-color: #a60000; }

/* -------------------- STATISTICS BOX -------------------- */
/* light */
.stats-box {
    border: 2px solid #fffce4;
    background-color: #fffce4;
    border-radius: 5px;
    padding: 15px;
    margin-top: 15px;
    color: #000000;
}
/* dark */
html[data-theme="dark"] .stats-box {
    border: 2px solid #faca2b;
    background-color: #faca2b;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

st.title("🥦 Food Waste Manager")

# ---------- DIALOG: SUCCESS ----------
@st.dialog("✅ Item Added")
def success_popup(name):
    st.success(f"'{name}' è stato aggiunto al tuo frigo!")
    if st.button("OK"):
        st.rerun()

# ---------- DIALOG: DELETE ----------
@st.dialog("Confirm Deletion")
def confirm_delete(item_id, name, username):
    st.warning(f"Sei sicuro di voler eliminare '{name}'?")
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Sì, elimina"):
        database.delete_food_item(username, item_id)
        st.success(f"'{name}' eliminato!")
        st.rerun()
    if col_b.button("❌ Annulla"):
        st.rerun()

# --------------- LOGIN ---------------

# Per un progetto vero: sposta queste credenziali su st.secrets o YAML
config = {
    "credentials": {
        "usernames": {
            "mario": {"email": "mario@email.com", "name": "Mario",
                      "password": stauth.Hasher(["1234"]).generate()[0]},
            "anna": {"email": "anna@email.com", "name": "Anna",
                     "password": stauth.Hasher(["abcd"]).generate()[0]},
        }
    },
    "cookie": {"name": "food_cookie", "key": "random_key", "expiry_days": 30},
    "preauthorized": {}
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

name, auth_status, username = authenticator.login("Login", "main")

if not auth_status:
    if auth_status is False:
        st.error("❌ Username o password sbagliati")
    else:
        st.info("🔑 Effettua il login per usare l’app")
    st.stop()

# Logout
with st.sidebar:
    authenticator.logout("Logout", "sidebar")
    st.success(f"👋 Benvenuto {name}")

# --------------- DB PER UTENTE ---------------
database.initialize_db(username)

# --------------- SIDEBAR: AGGIUNTA ITEM ---------------
with st.sidebar.form("add_food"):
    st.header("➕ Aggiungi un nuovo prodotto")
    name_item = st.text_input("Nome prodotto")
    category = st.selectbox("Categoria", ["Dairy", "Vegetables", "Meat", "Fruit", "Drinks", "Fish", "Other"])
    purchase_date = st.date_input("Data acquisto", datetime.today())
    expiration_date = st.date_input("Data scadenza")
    quantity = st.number_input("Quantità", min_value=0.0, step=0.1)
    unit = st.text_input("Unità (es. kg, pcs, lt)")
    submitted = st.form_submit_button("Aggiungi")

    if submitted:
        if not name_item.strip():
            st.toast("⚠️ Inserisci un nome per l’item!", icon="⚠️")
        else:
            # salviamo sempre in ISO (YYYY-MM-DD)
            database.insert_food_item(
                username,
                name_item,
                category,
                purchase_date.strftime("%Y-%m-%d"),
                expiration_date.strftime("%Y-%m-%d"),
                float(quantity),
                unit
            )
            success_popup(name_item)

# --------------- SIDEBAR: FILTRI ---------------
with st.sidebar:
    st.header("🔍 Filtra")
    status_options = ["✅ OK", "⚠️ Expiring Soon", "❌ Expired"]
    selected_status = st.multiselect(
        "Stati",
        options=status_options,
        default=[]
    )

# --------------- LISTA ITEMS ---------------
st.subheader("📋 Food List")

items = database.get_all_food_items(username)

if not items:
    st.info("Nessun prodotto. Usa la sidebar per aggiungerne uno!")
else:
    df = pd.DataFrame(
        items,
        columns=["ID", "Name", "Category", "Purchase Date", "Expiration Date", "Quantity", "Unit"]
    ).reset_index(drop=True)

    # Stato
    df["Status"] = df["Expiration Date"].apply(check_status)

    # Filtri
    filtered_df = df.copy()
    if selected_status:
        filtered_df = df[df["Status"].isin(selected_status)]

    # Tabella filtrata
    if filtered_df.empty:
        st.info("Nessun item corrisponde ai filtri scelti.")
    else:
        st.dataframe(
            filtered_df[["Name", "Category", "Expiration Date", "Quantity", "Unit", "Status"]]
            .reset_index(drop=True),
            hide_index=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------- ELIMINAZIONE ---------------
    st.subheader("🗑️ Elimina elementi")
    st.markdown("<br>", unsafe_allow_html=True)

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
                confirm_delete(row["ID"], row["Name"], username)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------- RICETTE ---------------
    st.subheader("🍽️ Meal Inspiration")
    expiring_soon = df[df["Status"] == "⚠️ Expiring Soon"]

    if st.button("What Can I Cook Today?"):
        ingredients = expiring_soon["Name"].tolist()

        if ingredients:
            # Preferisci usare st.secrets["SPOONACULAR_API_KEY"]
            spoonacular_key = st.secrets.get("SPOONACULAR_API_KEY", None)
            if not spoonacular_key:
                st.error("Imposta SPOONACULAR_API_KEY in st.secrets per usare le ricette.")
            else:
                st.info("Cerco ricette con: " + ", ".join(ingredients))
                query_ingredients = ",".join(ingredients)
                url = (
                    "https://api.spoonacular.com/recipes/findByIngredients"
                    f"?ingredients={query_ingredients}&number=1&ranking=1&apiKey={spoonacular_key}"
                )

                with st.spinner("Finding recipe..."):
                    try:
                        response = requests.get(url, timeout=20)
                        response.raise_for_status()
                        recipes = response.json()

                        if isinstance(recipes, list) and recipes:
                            recipe = recipes[0]
                            title = recipe.get("title", "Recipe")
                            image = recipe.get("image", "")
                            recipe_id = recipe.get("id")

                            st.markdown(f"### 👨‍🍳 {title}")
                            if image:
                                st.image(image, width=400)

                            if recipe_id:
                                instructions_url = (
                                    f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions"
                                    f"?apiKey={spoonacular_key}"
                                )
                                instructions_response = requests.get(instructions_url, timeout=20).json()

                                if (instructions_response and isinstance(instructions_response, list)
                                        and instructions_response[0].get("steps")):
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
            st.success("Nessun item in scadenza: niente di urgente da cucinare!")
    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------- ANALISI / GRAFICO ---------------
    st.subheader("📈 General Analysis")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<br>", unsafe_allow_html=True)
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

    with col_b:
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
            unsafe_allow_html=True
        )

        if expired_items > 0:
            st.warning(f"💸 Estimated Economic Loss: **€{lost_value:.2f}**")
        else:
            st.info("No food waste detected! Yey")
