
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Gold Dashboard",
    layout="wide"
)

st.title("Gold Performance Dashboard")
st.caption("Gold Futures (GC=F)")

# --------------------------------------------------
# 1. Download data
# --------------------------------------------------
current_year = datetime.now().year
years = [current_year - 1, current_year]

@st.cache_data(ttl=3600)
def load_data():

    gold_price = yf.download(
        "GC=F",
        start=f"{current_year - 2}-12-01",
        auto_adjust=True,
        progress=False
    )["Close"]

    if isinstance(gold_price, pd.DataFrame):
        gold_price = gold_price.iloc[:, 0]

    df = gold_price.rename("Price").to_frame().dropna()

    df["Return"] = df["Price"].pct_change()
    df["Year"] = df.index.year
    df["Month"] = df.index.month

    # 21-day rolling annualized volatility
    df["Rolling_Volatility"] = (
        df["Return"].rolling(21).std()
        * np.sqrt(252) * 100
    )

    return df[df["Year"].isin(years)]

df = load_data()

if df.empty:
    st.error("Gold price data is unavailable.")
    st.stop()

# --------------------------------------------------
# 2. Sidebar
# --------------------------------------------------
st.sidebar.header("Settings")

metric = st.sidebar.radio(
    "Select indicator",
    ["Pct Return", "Volatility"]
)

# --------------------------------------------------
# 3. Monthly statistics
# --------------------------------------------------
monthly = (
    df.groupby(["Year", "Month"])
    .agg(
        Return=("Return", lambda x:
                ((1 + x.dropna()).prod() - 1) * 100),

        Volatility=("Return", lambda x:
                    x.std() * np.sqrt(252) * 100),

        Trading_Days=("Return", "count")
    )
    .reset_index()
)

months = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

monthly["MonthName"] = monthly["Month"].map(
    dict(enumerate(months, start=1))
)

# --------------------------------------------------
# 4. Create year tabs
# --------------------------------------------------
tabs = st.tabs([str(year) for year in years])

for tab, year in zip(tabs, years):

    with tab:

        yearly_data = df[df["Year"] == year].copy()

        monthly_data = monthly[
            monthly["Year"] == year
        ].copy()

        if yearly_data.empty:
            st.info("No data available for this year.")
            continue

        annual_return = (
            (1 + yearly_data["Return"].dropna()).prod()
            - 1
        ) * 100

        annual_volatility = (
            yearly_data["Return"].std()
            * np.sqrt(252) * 100
        )

        # ==========================================
        # PERCENTAGE RETURN
        # ==========================================
        if metric == "Pct Return":

            st.header(f"{year} Returns")

            col1, col2, col3 = st.columns(3)

            return_label = (
                "YTD Return"
                if year == current_year
                else "Annual Return"
            )

            col1.metric(
                return_label,
                f"{annual_return:.2f}%"
            )

            col2.metric(
                "Best Monthly Return",
                f"{monthly_data['Return'].max():.2f}%"
            )

            col3.metric(
                "Worst Monthly Return",
                f"{monthly_data['Return'].min():.2f}%"
            )

            # Monthly returns
            fig = px.bar(
                monthly_data,
                x="MonthName",
                y="Return",
                text_auto=".2f",
                title="Monthly Returns (%)",
                category_orders={"MonthName": months},
                labels={
                    "MonthName": "Month",
                    "Return": "Return (%)"
                }
            )

            fig.update_traces(
                marker_color=[
                    "#16A34A" if x >= 0 else "#DC2626"
                    for x in monthly_data["Return"]
                ]
            )

            fig.add_hline(y=0)

            st.plotly_chart(
                fig, use_container_width=True
            )

            # Cumulative returns
            yearly_data["Cumulative_Return"] = (
                (1 + yearly_data["Return"]).cumprod() - 1
            ) * 100

            fig = px.line(
                yearly_data,
                x=yearly_data.index,
                y="Cumulative_Return",
                title="Cumulative Return (%)",
                labels={
                    "x": "Date",
                    "Cumulative_Return": "Return (%)"
                }
            )

            fig.update_traces(line_color="#C9A227")
            fig.add_hline(y=0)

            st.plotly_chart(
                fig, use_container_width=True
            )

            # Daily returns
            yearly_data["Daily_Return_Pct"] = (
                yearly_data["Return"] * 100
            )

            fig = px.bar(
                yearly_data,
                x=yearly_data.index,
                y="Daily_Return_Pct",
                title="Daily Returns (%)",
                labels={
                    "x": "Date",
                    "Daily_Return_Pct": "Return (%)"
                }
            )

            fig.update_traces(
                marker_color=[
                    "#16A34A" if x >= 0 else "#DC2626"
                    for x in yearly_data["Daily_Return_Pct"]
                ]
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            st.dataframe(
                monthly_data[
                    ["MonthName", "Return", "Trading_Days"]
                ].round(2),
                hide_index=True,
                use_container_width=True
            )

        # ==========================================
        # VOLATILITY
        # ==========================================
        else:

            st.header(f"{year} Volatility")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Annualized Volatility",
                f"{annual_volatility:.2f}%"
            )

            col2.metric(
                "Highest Monthly Volatility",
                f"{monthly_data['Volatility'].max():.2f}%"
            )

            col3.metric(
                "Lowest Monthly Volatility",
                f"{monthly_data['Volatility'].min():.2f}%"
            )

            # Monthly volatility
            fig = px.bar(
                monthly_data,
                x="MonthName",
                y="Volatility",
                text_auto=".2f",
                title="Monthly Annualized Volatility (%)",
                category_orders={"MonthName": months},
                labels={
                    "MonthName": "Month",
                    "Volatility": "Volatility (%)"
                }
            )

            fig.update_traces(marker_color="#E69F00")

            fig.add_hline(
                y=annual_volatility,
                line_dash="dash",
                annotation_text="Full-period volatility"
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            # Rolling volatility
            fig = px.line(
                yearly_data,
                x=yearly_data.index,
                y="Rolling_Volatility",
                title="21-Day Rolling Annualized Volatility (%)",
                labels={
                    "x": "Date",
                    "Rolling_Volatility": "Volatility (%)"
                }
            )

            fig.update_traces(line_color="#DC2626")

            st.plotly_chart(
                fig, use_container_width=True
            )

            # Return distribution
            yearly_data["Daily_Return_Pct"] = (
                yearly_data["Return"] * 100
            )

            fig = px.histogram(
                yearly_data,
                x="Daily_Return_Pct",
                nbins=40,
                title="Distribution of Daily Returns",
                labels={
                    "Daily_Return_Pct": "Daily Return (%)"
                }
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            st.dataframe(
                monthly_data[
                    ["MonthName", "Volatility", "Trading_Days"]
                ].round(2),
                hide_index=True,
                use_container_width=True
            )
