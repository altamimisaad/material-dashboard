import streamlit as st
import pandas as pd

st.set_page_config(page_title="Material Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("Material Price list.XLSX")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("📊 Material Price Dashboard")

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")

material_search = st.sidebar.text_input("Search Material Name")
material_id_search = st.sidebar.text_input("Search Material ID")

uom_filter = st.sidebar.multiselect(
    "UOM",
    options=sorted(df["UOM"].dropna().unique())
)

sales_org_filter = st.sidebar.multiselect(
    "Sales Org",
    options=sorted(df["Sales Org."].dropna().unique())
)

price_min, price_max = st.sidebar.slider(
    "Rawabi Price Range",
    float(df["Rawabi Price"].min()),
    float(df["Rawabi Price"].max()),
    (
        float(df["Rawabi Price"].min()),
        float(df["Rawabi Price"].max())
    )
)

# ---------- Apply Filters ----------
filtered = df.copy()

if material_search:
    filtered = filtered[
        filtered["Material Name"].str.contains(material_search, case=False, na=False)
    ]

if material_id_search:
    filtered = filtered[
        filtered["Material"].astype(str).str.contains(material_id_search)
    ]

if uom_filter:
    filtered = filtered[filtered["UOM"].isin(uom_filter)]

if sales_org_filter:
    filtered = filtered[filtered["Sales Org."].isin(sales_org_filter)]

filtered = filtered[
    (filtered["Rawabi Price"] >= price_min) &
    (filtered["Rawabi Price"] <= price_max)
]

# ---------- KPI Cards ----------
col1, col2, col3 = st.columns(3)

col1.metric("Total Materials", len(filtered))
col2.metric("Avg Rawabi Price", round(filtered["Rawabi Price"].mean(), 2))
col3.metric("Avg Market Price", round(filtered["Market Price"].mean(), 2))

# ---------- Table ----------
st.subheader("Materials Table")
st.dataframe(filtered, use_container_width=True)

# ---------- Download Button ----------
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Filtered Data",
    csv,
    "filtered_materials.csv",
    "text/csv"
)
