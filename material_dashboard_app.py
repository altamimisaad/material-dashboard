import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Material Intelligence Dashboard", layout="wide")

# -----------------------------
# File Upload
# -----------------------------
st.title("📊 Material Intelligence Dashboard")

uploaded_file = st.file_uploader(
    "Upload Material Price Excel File",
    type=["xlsx"]
)

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    return df

if uploaded_file is None:
    st.info("Upload your Material Price list Excel file to begin.")
    st.stop()

df = load_data(uploaded_file)

# -----------------------------
# Data Prep
# -----------------------------
for col in ["Valid From", "Valid To"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

df["Price Diff"] = df["Market Price"] - df["Rawabi Price"]

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Smart Filters")

search = st.sidebar.text_input(
    "Search Material Name OR ID"
)

uom_filter = st.sidebar.multiselect(
    "UOM",
    sorted(df["UOM"].dropna().unique())
)

sales_org_filter = st.sidebar.multiselect(
    "Sales Org",
    sorted(df["Sales Org."].dropna().unique())
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

# -----------------------------
# Filtering Logic
# -----------------------------
filtered = df.copy()

if search:
    filtered = filtered[
        filtered["Material Name"].str.contains(search, case=False, na=False) |
        filtered["Material"].astype(str).str.contains(search)
    ]

if uom_filter:
    filtered = filtered[filtered["UOM"].isin(uom_filter)]

if sales_org_filter:
    filtered = filtered[filtered["Sales Org."].isin(sales_org_filter)]

filtered = filtered[
    (filtered["Rawabi Price"] >= price_min) &
    (filtered["Rawabi Price"] <= price_max)
]

# -----------------------------
# KPI Section
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Materials", len(filtered))
c2.metric("Avg Rawabi", round(filtered["Rawabi Price"].mean(), 2))
c3.metric("Avg Market", round(filtered["Market Price"].mean(), 2))
c4.metric("Avg Difference", round(filtered["Price Diff"].mean(), 2))

# -----------------------------
# Expiry Warning
# -----------------------------
if "Valid To" in filtered.columns:
    soon_expire = filtered[
        filtered["Valid To"] <= pd.Timestamp.now() + pd.Timedelta(days=30)
    ]

    if len(soon_expire) > 0:
        st.warning(f"⚠️ {len(soon_expire)} materials expiring within 30 days")

# -----------------------------
# Charts
# -----------------------------
st.subheader("📈 Price Distribution")
st.bar_chart(filtered.set_index("Material Name")[["Rawabi Price", "Market Price"]].head(20))

# -----------------------------
# Top Lists
# -----------------------------
colA, colB = st.columns(2)

with colA:
    st.subheader("💰 Most Expensive (Rawabi)")
    st.dataframe(
        filtered.nlargest(10, "Rawabi Price")[
            ["Material", "Material Name", "Rawabi Price"]
        ],
        use_container_width=True
    )

with colB:
    st.subheader("🏷️ Cheapest (Rawabi)")
    st.dataframe(
        filtered.nsmallest(10, "Rawabi Price")[
            ["Material", "Material Name", "Rawabi Price"]
        ],
        use_container_width=True
    )

# -----------------------------
# Main Table
# -----------------------------
st.subheader("📋 Filtered Materials")

st.dataframe(
    filtered,
    use_container_width=True,
    height=500
)

# -----------------------------
# Download
# -----------------------------
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Filtered Data",
    csv,
    "filtered_materials.csv",
    "text/csv"
)
