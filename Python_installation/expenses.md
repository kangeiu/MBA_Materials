# Appendix 1. expenses.py

Personal Expense Tracker dashboard. Copy everything inside the code block below and save it as `expenses.py` in the project folder.

Run it with:

```
streamlit run expenses.py
```

```python
import streamlit as st
import calendar
import csv
import io
import random
from datetime import date

st.set_page_config(page_title="Expense Tracker", layout="wide")

CATEGORIES = ["Rent", "Food", "Transport", "Shopping", "Entertainment", "Bills", "Health"]


# ---------- Sample data: 6 months of personal expenses ----------
@st.cache_data
def load_data():
    rnd = random.Random(7)
    # category: (min times per month, max times, min amount, max amount)
    plan = {
        "Food": (25, 35, 40_000, 250_000),
        "Transport": (15, 25, 20_000, 150_000),
        "Shopping": (3, 6, 150_000, 1_500_000),
        "Entertainment": (2, 5, 100_000, 600_000),
        "Bills": (2, 3, 300_000, 900_000),
        "Health": (0, 2, 100_000, 800_000),
    }
    methods = ["Cash", "Card", "E-wallet"]
    rows = []
    for month in range(3, 9):                       # March to August 2026
        last_day = calendar.monthrange(2026, month)[1]
        rows.append({"date": date(2026, month, 1), "category": "Rent",
                     "amount": 6_000_000, "method": "Bank transfer"})
        for category, (lo, hi, a_min, a_max) in plan.items():
            for _ in range(rnd.randint(lo, hi)):
                rows.append({
                    "date": date(2026, month, rnd.randint(1, last_day)),
                    "category": category,
                    "amount": int(rnd.uniform(a_min, a_max) // 1000 * 1000),
                    "method": rnd.choice(methods),
                })
    rows.sort(key=lambda r: r["date"])
    return rows


def vnd(x):
    return f"{x:,.0f} VND"


def month_key(row):
    return row["date"].strftime("%Y-%m")


def total_of(rows):
    return sum(r["amount"] for r in rows)


def sum_by(rows, field):
    totals = {}
    for r in rows:
        totals[r[field]] = totals.get(r[field], 0) + r["amount"]
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


data = load_data()
all_months = sorted({month_key(r) for r in data})

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    month = st.selectbox("Month", all_months, index=len(all_months) - 1)
    budget = st.number_input("Monthly budget (VND)", min_value=1_000_000,
                             max_value=50_000_000, value=20_000_000, step=500_000)
    method = st.radio("Payment method", ["All", "Cash", "Card", "E-wallet", "Bank transfer"])
    st.caption("Sample data, not real expenses.")

chosen = data if method == "All" else [r for r in data if r["method"] == method]
this_month = [r for r in chosen if month_key(r) == month]

st.title("Personal Expense Tracker")
st.caption(f"Month: {month}  ·  Payment method: {method}")

if not this_month:
    st.info("No expenses match this month and payment method.")
    st.stop()

# ---------- Key numbers ----------
total = total_of(this_month)
by_category = sum_by(this_month, "category")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total spent", vnd(total))
c2.metric("Budget left", vnd(budget - total))
c3.metric("Transactions", f"{len(this_month)}")
c4.metric("Biggest category", next(iter(by_category)))

# ---------- Budget bar ----------
used = total / budget
st.progress(min(used, 1.0), text=f"{used:.0%} of budget used")
if used > 1:
    st.error(f"Over budget by {vnd(total - budget)}")
elif used > 0.8:
    st.warning("More than 80% of the budget is used.")
else:
    st.success("Spending is within budget.")

st.divider()

# ---------- Charts ----------
left, right = st.columns(2)

with left:
    st.subheader("Spending by category")
    st.bar_chart({"Category": list(by_category), "Amount": list(by_category.values())},
                 x="Category", y="Amount", horizontal=True, height=300)

with right:
    st.subheader("Running total vs budget")
    year, month_number = int(month[:4]), int(month[5:])
    last_day = calendar.monthrange(year, month_number)[1]
    per_day = {}
    for r in this_month:
        per_day[r["date"].day] = per_day.get(r["date"].day, 0) + r["amount"]
    running, spent = [], 0
    for day in range(1, last_day + 1):
        spent += per_day.get(day, 0)
        running.append(spent)
    st.line_chart(
        {"Day": [date(year, month_number, d) for d in range(1, last_day + 1)],
         "Spent": running,
         "Budget": [budget] * last_day},
        x="Day", y=["Spent", "Budget"], height=300,
    )

st.subheader("Last 6 months by category")
monthly = {"Month": all_months}
for category in CATEGORIES:
    monthly[category] = [
        total_of([r for r in chosen if month_key(r) == m and r["category"] == category])
        for m in all_months
    ]
st.bar_chart(monthly, x="Month", y=CATEGORIES, height=320)

# ---------- What-if saving ----------
st.subheader("What if I spend less?")
cut = st.slider("Cut Food, Shopping and Entertainment by (%)", 0, 50, 20, step=5)
flexible = total_of([r for r in this_month
                     if r["category"] in ("Food", "Shopping", "Entertainment")])
saving = flexible * cut / 100
st.write(f"You would save about **{vnd(saving)}** this month, "
         f"or **{vnd(saving * 12)}** in a year.")

# ---------- Details ----------
columns = {
    "date": st.column_config.DateColumn("Date", format="DD MMM"),
    "category": "Category",
    "amount": st.column_config.NumberColumn("Amount (VND)", format="%d"),
    "method": "Method",
}

with st.expander("Top 10 biggest expenses"):
    biggest = sorted(this_month, key=lambda r: r["amount"], reverse=True)[:10]
    st.dataframe(biggest, hide_index=True, column_config=columns)

with st.expander("All transactions this month"):
    st.dataframe(this_month, hide_index=True, height=350, column_config=columns)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["date", "category", "amount", "method"])
    writer.writeheader()
    writer.writerows(this_month)
    st.download_button("Download CSV", buffer.getvalue().encode("utf-8-sig"),
                       file_name="expenses.csv", mime="text/csv")
```
