from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Group 7 | Store Sales Explorer",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "GROUP_7_raw_data.csv"
DATE_FORMAT = "%d-%m-%Y"


@st.cache_data(show_spinner="Loading the Group 7 dataset…")
def load_data(file_bytes: bytes | None = None) -> pd.DataFrame:
    if file_bytes is None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Dataset not found: {DATA_PATH.name}")
        df = pd.read_csv(DATA_PATH)
    else:
        from io import BytesIO

        df = pd.read_csv(BytesIO(file_bytes))

    required = {
        "date", "store_nbr", "family", "sales", "onpromotion", "city",
        "state", "store_type", "cluster", "oil_price", "month",
        "day_of_week", "day_of_month", "is_payday", "is_weekend",
        "promo_flag", "high_sales",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError("Missing expected columns: " + ", ".join(sorted(missing)))

    df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT, errors="coerce")
    for col in ["sales", "onpromotion", "oil_price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date", "sales"])
    return df


def money(value: float) -> str:
    return f"${value:,.0f}"


st.title("Group 7 Store Sales Explorer")
st.caption(
    "Explore the supplied store and product-family sales data, review the reported "
    "regression findings, and download a filtered extract."
)

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Use another CSV (optional)", type=["csv"])

try:
    data = load_data(uploaded.getvalue() if uploaded else None)
except Exception as exc:
    st.error(f"Could not load the dataset. {exc}")
    st.stop()

with st.sidebar:
    st.caption(f"{len(data):,} rows loaded")
    st.header("Filters")
    min_date = data["date"].min().date()
    max_date = data["date"].max().date()
    selected_dates = st.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    cities = sorted(data["city"].dropna().astype(str).unique())
    city_filter = st.multiselect("City", cities, placeholder="All cities")
    families = sorted(data["family"].dropna().astype(str).unique())
    family_filter = st.multiselect("Product family", families, placeholder="All families")
    stores = sorted(data["store_nbr"].dropna().unique().tolist())
    store_filter = st.multiselect("Store number", stores, placeholder="All stores")

filtered = data.loc[
    data["date"].dt.date.between(start_date, end_date)
].copy()
if city_filter:
    filtered = filtered[filtered["city"].astype(str).isin(city_filter)]
if family_filter:
    filtered = filtered[filtered["family"].astype(str).isin(family_filter)]
if store_filter:
    filtered = filtered[filtered["store_nbr"].isin(store_filter)]

if filtered.empty:
    st.info("No rows match these filters. Widen the date range or clear a filter.")
    st.stop()

total_sales = filtered["sales"].sum()
mean_row_sales = filtered["sales"].mean()
active_days = max(filtered["date"].dt.date.nunique(), 1)
promo_sales_share = (filtered.loc[filtered["promo_flag"].eq(1), "sales"].sum() / total_sales) if total_sales else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Sales in selection", money(total_sales))
k2.metric("Average sales per row", money(mean_row_sales))
k3.metric("Rows", f"{len(filtered):,}")
k4.metric("Sales on promo-flagged rows", f"{promo_sales_share:.1%}")

trend = filtered.groupby("date", as_index=False).agg(sales=("sales", "sum"))
left, right = st.columns([1.7, 1])
with left:
    st.subheader("Sales over time")
    fig = px.line(trend, x="date", y="sales", markers=True, labels={"date": "Date", "sales": "Sales"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), yaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Sales by product family")
    by_family = (
        filtered.groupby("family", as_index=False)["sales"].sum()
        .sort_values("sales", ascending=True)
        .tail(12)
    )
    fig = px.bar(by_family, x="sales", y="family", orientation="h", labels={"sales": "Sales", "family": "Family"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), xaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Sales by store type")
    by_type = filtered.groupby("store_type", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
    fig = px.bar(by_type, x="store_type", y="sales", labels={"store_type": "Store type", "sales": "Sales"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), yaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Sales and promotions")
    promo = filtered.groupby("promo_flag", as_index=False).agg(rows=("sales", "size"), sales=("sales", "sum"))
    promo["promo_flag"] = promo["promo_flag"].map({0: "No promo flag", 1: "Promo flagged"}).fillna("Other")
    fig = px.bar(promo, x="promo_flag", y="sales", labels={"promo_flag": "", "sales": "Sales"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), yaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtered records")
st.dataframe(filtered.head(1000), use_container_width=True, hide_index=True)
st.caption("Showing up to 1,000 rows in the preview. The download contains every filtered row.")
st.download_button(
    "Download filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="group_7_filtered_sales.csv",
    mime="text/csv",
)

st.divider()
st.header("Reported regression findings")
st.markdown(
    "The project materials describe sales as the response and use store, product, "
    "calendar, promotion, and oil-price variables as predictors. The **high_sales** "
    "column is an existing derived label and is not used as a sales predictor here."
)

reported_a, reported_b = st.columns(2)
with reported_a:
    st.subheader("Cross-validation report")
    st.metric("Reported best stepwise model R²", "0.6655")
    st.metric("Reported validation ASE", "617,048.48")
    st.metric("Reported lowest CV PRESS", "1.21942 × 10¹¹")
    st.caption("The report places the best cross-validation result at step 9.")
with reported_b:
    st.subheader("Model comparison summary")
    st.write("The separate model-comparison summary reports:")
    st.write("• Forward selection: highest adjusted R² (0.6680).")
    st.write("• Adaptive LASSO: lowest validation ASE in that comparison (625,409.55).")
    st.write("• Backward elimination: fewest predictors (6).")
    st.caption(
        "These figures come from separate supplied outputs and are not directly "
        "recomputed on the included CSV; the cross-validation report and comparison "
        "summary report different validation ASE values."
    )

with st.expander("Dataset notes"):
    st.write(
        f"The bundled file has {len(data):,} rows and covers "
        f"{data['date'].min():%d %b %Y} to {data['date'].max():%d %b %Y}. "
        "Figures update when sidebar filters change. The supplied CSV is included "
        "in this project folder so the deployed app can load it without a separate upload."
    )
