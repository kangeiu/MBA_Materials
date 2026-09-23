# Appendix 2. sales.py

Online Store Sales dashboard. Copy everything inside the code block below and save it as `sales.py` in the project folder.

Run it with:

```
streamlit run sales.py
```

```python
import streamlit as st
import csv
import io
import math
import random
from datetime import date, timedelta

st.set_page_config(page_title="Online Store Sales", layout="wide")

CHANNELS = ["Website", "Shopee", "Lazada", "TikTok Shop", "Facebook"]
PRODUCTS = {
    "T-shirt": 180_000,
    "Hoodie": 450_000,
    "Sneakers": 890_000,
    "Backpack": 520_000,
    "Cap": 150_000,
    "Socks": 60_000,
}


# ---------- Sample data: 6 months of online orders ----------
@st.cache_data
def load_data():
    rnd = random.Random(11)
    first, last = date(2026, 3, 1), date(2026, 8, 31)
    span = (last - first).days + 1

    # How popular each channel is, and how fast it is growing
    weight = {"Website": 1.0, "Shopee": 1.7, "Lazada": 0.9,
              "TikTok Shop": 1.4, "Facebook": 0.6}
    growth = {"Website": 1.10, "Shopee": 1.35, "Lazada": 0.95,
              "TikTok Shop": 1.90, "Facebook": 1.05}

    rows = []
    for i in range(span):
        day = first + timedelta(days=i)
        season = 1.0 + 0.25 * math.sin(i / 30)            # slow ups and downs
        weekend = 1.30 if day.weekday() >= 5 else 1.0
        for channel in CHANNELS:
            ramp = 1 + (growth[channel] - 1) * (i / span)
            mean = 8 * weight[channel] * ramp * season * weekend
            n_orders = max(0, round(rnd.gauss(mean, mean ** 0.5)))
            for _ in range(n_orders):
                product = rnd.choice(list(PRODUCTS))
                units = rnd.randint(1, 3)
                rows.append({
                    "order_id": f"ORD-{10_000 + len(rows)}",
                    "date": day,
                    "channel": channel,
                    "product": product,
                    "units": units,
                    "revenue": units * PRODUCTS[product],
                })
    return rows


def vnd(x):
    return f"{x / 1_000_000:,.1f}M VND"


def total_of(rows, field="revenue"):
    return sum(r[field] for r in rows)


def sum_by(rows, field, value="revenue"):
    totals = {}
    for r in rows:
        totals[r[field]] = totals.get(r[field], 0) + r[value]
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


data = load_data()
first_day = data[0]["date"]
last_day = data[-1]["date"]

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Filters")
    picked = st.date_input("Date range", value=(first_day, last_day),
                           min_value=first_day, max_value=last_day)
    channels = st.multiselect("Sales channel", CHANNELS, default=CHANNELS)
    compare = st.toggle("Compare with previous period", value=True)
    st.divider()
    st.caption("Sample data, not real sales.")

# date_input gives one date while you are still picking, two when you are done
if isinstance(picked, (list, tuple)):
    start, end = picked[0], picked[-1]
else:
    start = end = picked

view = [r for r in data if start <= r["date"] <= end and r["channel"] in channels]

st.title("Online Store Sales")
st.caption(f"{start:%d %b %Y} - {end:%d %b %Y}  ·  {len(channels)} of {len(CHANNELS)} channels")

if not view:
    st.info("No orders match these filters. Pick at least one channel.")
    st.stop()

# ---------- Key numbers ----------
n_days = (end - start).days + 1
prev_start = start - timedelta(days=n_days)
prev_end = start - timedelta(days=1)
before = [r for r in data if prev_start <= r["date"] <= prev_end and r["channel"] in channels]


def delta(now, then):
    # No arrow when the toggle is off, or when there is nothing to compare with
    if not compare or then == 0:
        return None
    return f"{(now - then) / then * 100:+.1f}%"


revenue_now = total_of(view)
units_now = total_of(view, "units")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", vnd(revenue_now), delta(revenue_now, total_of(before)))
c2.metric("Orders", f"{len(view):,}", delta(len(view), len(before)))
c3.metric("Units sold", f"{units_now:,}", delta(units_now, total_of(before, "units")))
c4.metric("Average order value", f"{revenue_now / len(view):,.0f} VND")

if compare:
    st.caption("Arrows compare with the period of the same length just before this one.")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Trend", "Channels and products", "Orders"])

days = [start + timedelta(days=i) for i in range(n_days)]

with tab1:
    st.subheader("Revenue per day")
    per_day = sum_by(view, "date")
    st.area_chart({"Day": days, "Revenue": [per_day.get(d, 0) for d in days]},
                  x="Day", y="Revenue", height=320)

    st.subheader("Revenue per day, split by channel")
    split = {"Day": days}
    for channel in channels:
        totals = sum_by([r for r in view if r["channel"] == channel], "date")
        split[channel] = [totals.get(d, 0) for d in days]
    st.line_chart(split, x="Day", y=channels, height=320)

with tab2:
    left, right = st.columns(2)

    with left:
        st.subheader("Revenue by channel")
        by_channel = sum_by(view, "channel")
        st.bar_chart({"Channel": list(by_channel), "Revenue": list(by_channel.values())},
                     x="Channel", y="Revenue", horizontal=True, height=300)

    with right:
        st.subheader("Revenue by product")
        by_product = sum_by(view, "product")
        st.bar_chart({"Product": list(by_product), "Revenue": list(by_product.values())},
                     x="Product", y="Revenue", horizontal=True, height=300)

    st.subheader("Product table")
    # One small line chart inside each row: weekly revenue for that product
    weeks = sorted({r["date"] - timedelta(days=r["date"].weekday()) for r in view})
    table = []
    for product, revenue in by_product.items():
        lines = [r for r in view if r["product"] == product]
        weekly = sum_by(lines, "date")
        trend = []
        for week_start in weeks:
            week_days = [week_start + timedelta(days=i) for i in range(7)]
            trend.append(sum(weekly.get(d, 0) for d in week_days))
        table.append({
            "product": product,
            "units": total_of(lines, "units"),
            "revenue": revenue,
            "orders": len(lines),
            "share": revenue / total_of(view) * 100,
            "trend": trend,
        })

    st.dataframe(
        table,
        hide_index=True,
        column_config={
            "product": "Product",
            "units": st.column_config.NumberColumn("Units", format="%d"),
            "revenue": st.column_config.NumberColumn("Revenue (VND)", format="%d"),
            "orders": st.column_config.NumberColumn("Orders", format="%d"),
            "share": st.column_config.ProgressColumn(
                "Share of revenue", min_value=0,
                max_value=max(row["share"] for row in table), format="%.1f%%"),
            "trend": st.column_config.LineChartColumn("Weekly trend", y_min=0),
        },
    )

with tab3:
    st.subheader("Order lines")
    st.write(f"Showing {len(view):,} rows.")

    newest_first = sorted(view, key=lambda r: r["date"], reverse=True)
    st.dataframe(
        newest_first,
        hide_index=True,
        height=400,
        column_config={
            "order_id": "Order",
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "channel": "Channel",
            "product": "Product",
            "units": st.column_config.NumberColumn("Units"),
            "revenue": st.column_config.NumberColumn("Revenue (VND)", format="%d"),
        },
    )

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(view[0]))
    writer.writeheader()
    writer.writerows(newest_first)
    st.download_button("Download CSV", buffer.getvalue().encode("utf-8-sig"),
                       file_name="online_store_sales.csv", mime="text/csv")
```
