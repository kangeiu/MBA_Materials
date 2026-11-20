# Python Project Setup with uv — macOS (Terminal)

This is the **macOS (Intel / Apple Silicon)** version of *Python Project Setup with uv – Step-by-Step Guide for Windows & macOS*. It is organized into copy-and-paste **stages** for GitHub readers.

**What you will do:** install `uv` and Python 3.12, create a `code-practice` project and `.venv`, install packages from `requirements.txt`, run two Streamlit dashboards, and learn how to stop/reopen/update the project.

> **How to use:** Complete Stage 1 through Stage 4 in order. Stage 5 covers daily use; Stage 6 is a reference. Copy commands into **Terminal**, not into a Python file. Output examples are **not commands**. The complete app code appears **inside the relevant step**, collapsed by default. Expand the code block, copy it, and preserve Python indentation.

| Stage | What it covers | PDF sections |
| --- | --- | --- |
| [Stage 1](#stage-1) | Install `uv` and Python 3.12 | B1–B2; Steps 1–6 |
| [Stage 2](#stage-2) | Create the project and `.venv` | B3–B4; Steps 7–11 |
| [Stage 3](#stage-3) | `requirements.txt`, install/update libraries | B5; Steps 12–14 |
| [Stage 4](#stage-4) | Create `expenses.py` (code included here) and run it | B6; Steps 15–18 |
| [Stage 5](#stage-5) | Reopen, stop, create `sales.py` (code included here) | B7–B9 |
| [Stage 6](#stage-6) | Quick reference and `pip` vs `uv` | Quick reference |

> **GitHub tip:** The `expenses.py` and `sales.py` blocks are folded by default to keep this guide short. Select **“Click to expand and copy…”** at the exact step where the file is created; GitHub shows a copy button on each Python block when expanded.

<a id="stage-1"></a>
## Stage 1 — Install `uv` and Python 3.12

**Steps 1–4 · Install and check `uv` (once only)**

1. Press **Cmd + Space**, type `terminal`, and press **Enter**.
2. If the prompt begins with `(base)`, run `conda deactivate` first (otherwise skip it).
3. Paste this installer command into **Terminal**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This is the `uv` installer in the PDF; it does not require Python or `pip`. Quit Terminal with **Cmd + Q**, reopen it, then run:

```bash
uv --version
```

Expected output: `uv 0.x.x` (your version may differ). If you see `zsh: command not found: uv`, close Terminal, reopen it, and try the check again. If the issue remains, repeat the installer step.

**Steps 5–6 · Install Python 3.12 and verify (once only)**

```bash
uv python install 3.12
uv python list --only-installed
```

Expected: `Installed Python 3.12.x in ...` and a `cpython-3.12.x-macos-...` entry under `/Users/<your-name>/.local/share/uv/python/...`. `uv` installs Python for you; you do not need the python.org installer or a separate **Install Certificates** step.

<a id="stage-2"></a>
## Stage 2 — Create the project and virtual environment

**Steps 7–11 · Run in the same Terminal session**

Copy and paste this **whole block**; it creates the project directory, enters it, initializes `pyproject.toml`, creates `.venv`, activates it, and checks Python:

```bash
mkdir -p ~/Downloads/code-practice
cd ~/Downloads/code-practice
uv init --bare --python 3.12
uv venv --python 3.12
source .venv/bin/activate
python --version
```

- `uv init --bare --python 3.12` creates `pyproject.toml`.
- `uv venv --python 3.12` creates `.venv`, and activation should show `(code-practice)` in the prompt.
- `python --version` should print `Python 3.12.x`.
- The same instructions work on **Intel** and **Apple Silicon** Macs.

<a id="stage-3"></a>
## Stage 3 — Create `requirements.txt` and install libraries

**Step 12 · Make the dependency list**

The original editor-based method is:

```bash
nano requirements.txt
```

Paste these six lines:

```text
numpy
pandas
matplotlib
seaborn
streamlit
yfinance
```

Save with **Control + O**, press **Enter**, and exit with **Control + X**. Then install the libraries:

```bash
uv pip install -r requirements.txt
```

**Faster copy-paste alternative:** Instead of opening nano, paste this **single block** while inside the project folder. It creates the same file and installs the packages:

```bash
cat > requirements.txt <<'EOF'
numpy
pandas
matplotlib
seaborn
streamlit
yfinance
EOF
uv pip install -r requirements.txt
```

> Choose **either** the nano method **or** the faster alternative, not both. With the PDF's default `uv venv` setup, use `uv pip install`; that environment normally does not contain a `pip` executable.

**Step 13 · Add libraries later (examples, not mandatory setup commands)**

**Option A — manage dependencies through `pyproject.toml`:**

```bash
uv add plotly
uv add scikit-learn scipy
```

`uv add` installs packages and updates project dependency configuration. The two commands are independent examples; run only those you need. Copy the `uv` commands, not explanatory comment lines.

**Option B — install directly into the virtual environment (pip-style):**

```bash
uv pip install plotly scikit-learn
```

> The two options are alternative workflows. For a basic `requirements.txt` project, Option B is the most consistent. If switching to `uv add`, manage the complete dependency set through the project configuration to avoid unexpected synchronization changes.

**Step 14 · Refresh the installed-package list later**

With `.venv` activated:

```bash
uv pip freeze > requirements.txt
```

This **overwrites** `requirements.txt` with installed packages (including transitive dependencies). Use it only when you intend to update the shared list.

<a id="stage-4"></a>
## Stage 4 — Create and run the expense dashboard

**Steps 15–16 · Create `expenses.py`**

```bash
nano expenses.py
```

Expand the section below and copy the **entire Python code block** into nano using **Cmd + V**.

<details>
<summary><strong>📋 Click to expand and copy the complete expenses.py code</strong></summary>

> **Copy all lines** inside the Python block using GitHub's copy button. Do not copy the opening or closing Markdown fences. Keep the indentation unchanged.

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

</details>

**Save the file:** press **Control + O**, then **Enter**, then **Control + X** to exit nano. Keep the indentation exactly as shown.

**Steps 17–18 · Check files and start Streamlit**

```bash
ls
streamlit run expenses.py
```

Expected visible items: `expenses.py`, `pyproject.toml`, `requirements.txt`; `uv.lock` can appear if you used `uv add`. `.venv` is hidden on macOS, so ordinary `ls` does not display it; you can inspect hidden items with `ls -a`.

If Streamlit asks for an email, leave it blank and press **Enter**. The browser normally opens **http://localhost:8501**; open it manually if needed.

<a id="stage-5"></a>
## Stage 5 — Daily use, stop, and switch dashboards

### Reopen the dashboard (PDF section B7)

Each time, open **Terminal**. If you are in a Conda `(base)` environment, run `conda deactivate` first. Then paste these **three commands together**:

```bash
cd ~/Downloads/code-practice
source .venv/bin/activate
streamlit run expenses.py
```

### Stop the dashboard (PDF section B8)

| Goal | Action |
| --- | --- |
| Stop Streamlit | In the Terminal window running it, press **Control + C**. |
| Leave the virtual environment | Type `deactivate`. |
| Stop everything | Press **Cmd + Q** and select **Terminate** if asked. |

**Control + C** stops the dashboard; **Cmd + C** copies text. Closing only the browser tab does not stop Streamlit.

### Run the second dashboard (PDF section B9)

Stop the current app with **Control + C**. While `.venv` is still active, create the new file:

```bash
nano sales.py
```

Expand the section below and copy the **entire Python code block** into `sales.py` using **Cmd + V**.

<details>
<summary><strong>📋 Click to expand and copy the complete sales.py code</strong></summary>

> **Copy all lines** inside the Python block using GitHub's copy button. Do not copy the opening or closing Markdown fences. Keep the indentation unchanged.

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
st.caption(f"{start:%d %b %Y} - {end:%d %b %Y}   ·   {len(channels)} of {len(CHANNELS)} channels")

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

</details>

**Save the file:** press **Control + O**, then **Enter**, then **Control + X** to exit nano. Run:

```bash
streamlit run sales.py
```

There is no need to reactivate the environment or reinstall the libraries while the same session and `.venv` are still active.

<a id="stage-6"></a>
## Stage 6 — Quick reference and environment management

### Command reference (macOS / Terminal)

| Task | Command |
| --- | --- |
| Install `uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Install Python 3.12 | `uv python install 3.12` |
| Enter project | `cd ~/Downloads/code-practice` |
| Initialize project | `uv init --bare --python 3.12` |
| Create `.venv` | `uv venv --python 3.12` |
| Activate | `source .venv/bin/activate` |
| Check Python | `python --version` |
| Edit dependencies | `nano requirements.txt` |
| Install from file | `uv pip install -r requirements.txt` |
| Add a project dependency | `uv add plotly` |
| Install into the environment | `uv pip install plotly scikit-learn` |
| Update installed-package list | `uv pip freeze > requirements.txt` |
| Edit expense app | `nano expenses.py` |
| View files | `ls` (or `ls -a` for hidden files) |
| Run expense app | `streamlit run expenses.py` |
| Run sales app | `streamlit run sales.py` |
| Stop app | **Control + C** |
| Deactivate | `deactivate` |
| Delete `.venv` | `rm -rf .venv` |

**Run without manually activating** (an alternative included in the PDF):

```bash
uv run streamlit run expenses.py
```

For this to work reliably, Streamlit must be a **project-managed dependency** (for example, installed with `uv add streamlit`). If you used *only* `uv pip install -r requirements.txt`, prefer running from the activated environment (Stage 5), because `uv run` may synchronize the project.

**Delete and rebuild the virtual environment** (only if you want to reset it; run inside `code-practice` after stopping Streamlit and deactivating `.venv`):

```bash
rm -rf .venv
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

### `pip` vs `uv` (based on the PDF)

| Task | Standard `pip` workflow | `uv` workflow used here |
| --- | --- | --- |
| Install Python | Download from python.org | `uv python install 3.12` |
| Create environment | `python3 -m venv venv` | `uv init --bare --python 3.12`, then `uv venv --python 3.12` |
| Environment folder | `venv` | `.venv` |
| Typical activated prompt | `(venv)` | `(code-practice)` |
| Install libraries | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Add a library | `pip install plotly` | `uv add plotly` (project mode) or `uv pip install plotly` |
| Export installed packages | `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` |
| Run dashboard after activation | `streamlit run expenses.py` | `streamlit run expenses.py` |
