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

st.title("Gold Price")
st.caption("Gold Futures (GC=F)")

# --------------------------------------------------
# 1. Download data
# --------------------------------------------------
current_year = datetime.now().year
years = [current_year - 1, current_year]


@st.cache_data(ttl=3600)
def load_data(current_year):

    gold_price = yf.download(
        "GC=F",
        start=f"{current_year - 2}-12-01",
        auto_adjust=True,
        progress=False
    )["Close"]

    if isinstance(gold_price, pd.DataFrame):
        gold_price = gold_price.iloc[:, 0]

    df = gold_price.rename("Price").to_frame().dropna()
    df = df.sort_index()

    df["Return"] = df["Price"].pct_change(fill_method=None)
    df["Year"] = df.index.year
    df["Month"] = df.index.month

    # 21-day rolling annualized volatility
    df["Rolling_Volatility"] = (
        df["Return"].rolling(21).std()
        * np.sqrt(252) * 100
    )

    return df[df["Year"].isin(
        [current_year - 1, current_year]
    )]


df = load_data(current_year)

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

st.sidebar.caption(
    f"Data period: {df.index.min():%Y-%m-%d} "
    f"to {df.index.max():%Y-%m-%d}"
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
# 4. Create Total Period and Year tabs
# --------------------------------------------------
periods = ["Total Period"] + years

tabs = st.tabs([str(period) for period in periods])

for tab, period in zip(tabs, periods):

    with tab:

        # ==========================================
        # Select analysis period
        # ==========================================
        if period == "Total Period":

            period_data = df.copy()
            monthly_data = monthly.copy()

            # Distinguish months across different years
            monthly_data["MonthName"] = (
                monthly_data["MonthName"]
                + " "
                + monthly_data["Year"].astype(str)
            )

            month_order = monthly_data["MonthName"].tolist()

            return_label = "Total Cumulative Return"

            period_title = f"{years[0]}–{years[-1]}"

        else:

            period_data = df[
                df["Year"] == period
            ].copy()

            monthly_data = monthly[
                monthly["Year"] == period
            ].copy()

            month_order = months

            period_title = str(period)

            return_label = (
                "YTD Return"
                if period == current_year
                else "Annual Return"
            )

        if period_data.empty:
            st.info("No data available for this period.")
            continue

        # ==========================================
        # Calculate period statistics
        # ==========================================
        period_return = (
            (1 + period_data["Return"].dropna()).prod()
            - 1
        ) * 100

        annualized_volatility = (
            period_data["Return"].std()
            * np.sqrt(252) * 100
        )

        period_data["Daily_Return_Pct"] = (
            period_data["Return"] * 100
        )

        period_data["Cumulative_Return"] = (
            (1 + period_data["Return"]).cumprod() - 1
        ) * 100

        # Display selected period
        st.caption(
            f"{period_data.index.min():%Y-%m-%d} "
            f"to {period_data.index.max():%Y-%m-%d}"
        )

        # ==========================================
        # PERCENTAGE RETURN
        # ==========================================
        if metric == "Pct Return":

            st.header(f"{period_title} Returns")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                return_label,
                f"{period_return:.2f}%"
            )

            col2.metric(
                "Best Monthly Return",
                f"{monthly_data['Return'].max():.2f}%"
            )

            col3.metric(
                "Worst Monthly Return",
                f"{monthly_data['Return'].min():.2f}%"
            )

            # --------------------------------------
            # Monthly returns
            # --------------------------------------
            fig = px.bar(
                monthly_data,
                x="MonthName",
                y="Return",
                text_auto=".2f",
                title="Monthly Returns (%)",
                category_orders={
                    "MonthName": month_order
                },
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

            fig.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            # --------------------------------------
            # Cumulative returns
            # --------------------------------------
            fig = px.line(
                period_data,
                x=period_data.index,
                y="Cumulative_Return",
                title="Cumulative Return (%)",
                labels={
                    "x": "Date",
                    "Cumulative_Return": "Return (%)"
                }
            )

            fig.update_traces(
                line_color="#C9A227"
            )

            fig.add_hline(y=0)

            st.plotly_chart(
                fig, use_container_width=True
            )

            # --------------------------------------
            # Daily returns
            # --------------------------------------
            fig = px.bar(
                period_data,
                x=period_data.index,
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
                    for x in period_data["Daily_Return_Pct"]
                ]
            )

            fig.add_hline(y=0)

            st.plotly_chart(
                fig, use_container_width=True
            )

            # --------------------------------------
            # Monthly return statistics
            # --------------------------------------
            st.subheader("Monthly Return Statistics")

            st.dataframe(
                monthly_data[
                    ["MonthName", "Return", "Trading_Days"]
                ].rename(columns={
                    "MonthName": "Month",
                    "Return": "Return (%)",
                    "Trading_Days": "Trading Days"
                }).round(2),
                hide_index=True,
                use_container_width=True
            )

        # ==========================================
        # VOLATILITY
        # ==========================================
        else:

            st.header(f"{period_title} Volatility")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Annualized Volatility",
                f"{annualized_volatility:.2f}%"
            )

            col2.metric(
                "Highest Monthly Volatility",
                f"{monthly_data['Volatility'].max():.2f}%"
            )

            col3.metric(
                "Lowest Monthly Volatility",
                f"{monthly_data['Volatility'].min():.2f}%"
            )

            # --------------------------------------
            # Monthly volatility
            # --------------------------------------
            fig = px.bar(
                monthly_data,
                x="MonthName",
                y="Volatility",
                text_auto=".2f",
                title="Monthly Annualized Volatility (%)",
                category_orders={
                    "MonthName": month_order
                },
                labels={
                    "MonthName": "Month",
                    "Volatility": "Volatility (%)"
                }
            )

            fig.update_traces(
                marker_color="#E69F00"
            )

            fig.add_hline(
                y=annualized_volatility,
                line_dash="dash",
                annotation_text="Full-period volatility"
            )

            fig.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            # --------------------------------------
            # Rolling volatility
            # --------------------------------------
            fig = px.line(
                period_data,
                x=period_data.index,
                y="Rolling_Volatility",
                title="21-Day Rolling Annualized Volatility (%)",
                labels={
                    "x": "Date",
                    "Rolling_Volatility": "Volatility (%)"
                }
            )

            fig.update_traces(
                line_color="#DC2626"
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            # --------------------------------------
            # Return distribution
            # --------------------------------------
            fig = px.histogram(
                period_data,
                x="Daily_Return_Pct",
                nbins=40,
                title="Distribution of Daily Returns",
                labels={
                    "Daily_Return_Pct": "Daily Return (%)"
                }
            )

            fig.add_vline(
                x=period_data["Daily_Return_Pct"].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text="Mean"
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            # --------------------------------------
            # Monthly volatility statistics
            # --------------------------------------
            st.subheader("Monthly Volatility Statistics")

            st.dataframe(
                monthly_data[
                    ["MonthName", "Volatility", "Trading_Days"]
                ].rename(columns={
                    "MonthName": "Month",
                    "Volatility": "Volatility (%)",
                    "Trading_Days": "Trading Days"
                }).round(2),
                hide_index=True,
                use_container_width=True
            )

# --------------------------------------------------
# 5. Footer
# --------------------------------------------------
st.divider()

st.caption(
    "Source: Yahoo Finance | Gold Futures (GC=F) | "
    "Annualized volatility assumes 252 trading days per year."
)

st.caption(
    "Current-month returns and volatility are calculated "
    "using the available trading days."
)