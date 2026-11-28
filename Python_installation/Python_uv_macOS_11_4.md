# Python Project Setup with uv — macOS 11.4 Big Sur (Terminal)

This is the **macOS 11.4 Big Sur (Intel / Apple Silicon)** compatibility edition of *Python Project Setup with uv – Step-by-Step Guide for Windows & macOS*. It is organized into copy-and-paste **stages** for GitHub readers.

**What you will do:** install `uv` and Python 3.12, create a `code-practice` project and `.venv`, install compatibility-pinned packages from `requirements.txt`, run two Streamlit dashboards, and learn how to stop/reopen/update the project.

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
## Stage 1 — Check macOS, uv and Python 3.12

> **Compatibility note:** Current uv officially supports macOS 13+. On macOS 11.4, keep your existing working uv; do not upgrade it just for this exercise. If uv itself cannot run, use the Python + pip fallback below. This guide is for local classroom practice with older packages, not a production deployment.

**Steps 1–4 · Check your Mac and uv (once only)**

1. Press **Cmd + Space**, type `terminal`, and press **Enter**.
2. If the prompt begins with `(base)`, run `conda deactivate` first.
3. Run these checks:

```bash
sw_vers -productVersion
uname -m
uv --version
```

Expected: `11.4`, `x86_64` (Intel or Rosetta) or `arm64` (native Apple Silicon), and a uv version. If uv already works, continue; do not reinstall it.

4. If uv is not found, check whether it is already installed but missing from PATH:

```bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
uv --version
```

If uv is absent or cannot run on this OS, use the fallback rather than installing an unsupported latest uv version.

**Steps 5–6 · Install or verify Python 3.12 (once only)**

For working uv:

```bash
uv python list --only-installed
```

If Python 3.12 is missing, run:

```bash
uv python install 3.12
```

Then verify the interpreter itself can run:

```bash
uv python find 3.12
"$(uv python find 3.12)" --version
```

Expected: `Python 3.12.x`. If the managed interpreter cannot run or cannot be installed, use the fallback.

**Fallback — Python 3.12 without a working uv**

Download the **macOS 64-bit universal2 installer** from [Python 3.12.10](https://www.python.org/downloads/release/python-31210/) (the installer supports macOS 10.13 and later). This is an older installer for compatibility, not the latest security patch. Install it, and if necessary run **Install Certificates.command** in the Python 3.12 Applications folder. Reopen Terminal and verify:

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 --version
```

If this succeeds, follow the fallback in Stage 2 and use `python -m pip` in Stage 3. If uv works but its managed Python fails, the same installed Python may also be used by uv via `uv venv --python /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12`.

<a id="stage-2"></a>
## Stage 2 — Create or repair the project and virtual environment

**Steps 7–11 · Run in the same Terminal session**

If a dashboard is currently running, stop it with **Control + C**. If a virtual environment is active, run `deactivate` first. Enter the project directory:

```bash
mkdir -p ~/Downloads/code-practice
cd ~/Downloads/code-practice
pwd
ls -la
```

If your real folder has another name, use that path instead. `.venv` is a hidden directory; `drwxr-xr-x` is normal and does not indicate whether the interpreter is functional.

For a new uv project, initialize the metadata only if it is missing:

```bash
if [ ! -f pyproject.toml ]; then
    uv init --bare --python 3.12
fi
```

**If `.venv` already exists**, check it before creating a new one:

```bash
.venv/bin/python --version
```

If it prints Python 3.12.x, keep it and skip the creation command. If it reports a missing interpreter, rename the broken environment first (only if it exists):

```bash
mv .venv ".venv-backup-$(date +%Y%m%d-%H%M%S)"
```

This preserves the previous environment for inspection and does not touch `expenses.py`, `sales.py` or other project files. A copied virtual environment is not portable between machines.

**Create `.venv` only if it is absent — choose one method.**

Working uv:

```bash
uv venv --python 3.12
```

If uv works but you installed Python from python.org instead:

```bash
uv venv --python /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12
```

Fallback without uv:

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 -m venv .venv
```

For all methods, activate and verify:

```bash
source .venv/bin/activate
which python
python --version
python -c "import sys, platform; print(sys.executable); print(platform.machine())"
```

- The prompt may display `(.venv)` or `(code-practice)`.
- The Python path should end in `code-practice/.venv/bin/python`.
- The Python version must be 3.12.x. Stop here if it is missing or cannot run.
- No `sudo` or `chmod -R 777` is needed. If macOS explicitly blocks Downloads access, allow Terminal (or VS Code if used) under **System Preferences → Security & Privacy → Privacy → Files and Folders → Downloads Folder**.

<a id="stage-3"></a>
## Stage 3 — Create compatibility-pinned requirements and install libraries

**Step 12 · Create `requirements.txt`**

For macOS 11.4 and Python 3.12, use this compatibility-oriented set rather than requesting the newest releases. PyArrow 17.0.0 provides CPython 3.12 wheels for macOS 10.15+ Intel and macOS 11.0+ ARM64. NumPy 1.26.4 and pandas 2.2.3 are pinned to avoid newer major-version incompatibilities. Altair is pinned for chart compatibility with Streamlit 1.45.1.

The original `yfinance` library is now optional: neither dashboard imports it, and it brings additional dependencies that may not have compatible wheels on Big Sur.

**Option A — editor method:**

```bash
nano requirements.txt
```

Replace the old contents with these seven lines:

```text
numpy==1.26.4
pandas==2.2.3
matplotlib==3.9.3
seaborn==0.13.2
streamlit==1.45.1
pyarrow==17.0.0
altair==5.5.0
```

Save with **Control + O**, press **Enter**, and exit with **Control + X**.

**Option B — faster copy-paste method:**

```bash
cat > requirements.txt <<'EOF'
numpy==1.26.4
pandas==2.2.3
matplotlib==3.9.3
seaborn==0.13.2
streamlit==1.45.1
pyarrow==17.0.0
altair==5.5.0
EOF
```

Choose either A or B. Option B overwrites the old requirements file; back it up first if it contains other packages you want to preserve (`cp requirements.txt requirements-backup.txt` if the file exists).

**Install (working uv):**

```bash
uv pip install --python .venv/bin/python --only-binary=:all: -r requirements.txt
```

**Install (pip fallback only):**

```bash
python -m pip install --only-binary=:all: -r requirements.txt
```

`--only-binary=:all:` tells the installer to use prebuilt wheels instead of building packages from source. If it reports no compatible wheel or an unsatisfiable requirement, do not remove this option just to force a build. Check the OS, Python version, architecture and exact package named in the error.

**Verify before proceeding:**

```bash
python -c "import numpy, pandas, matplotlib, seaborn, pyarrow, altair, streamlit; print('Streamlit:', streamlit.__version__); print('PyArrow:', pyarrow.__version__); print('Imports OK')"
```

Expected: `Streamlit: 1.45.1`, `PyArrow: 17.0.0`, `Imports OK`. If the process crashes, shows `Illegal instruction`, `dyld`, or an import error, stop and investigate the Terminal output.

```bash
uv pip check --python .venv/bin/python
```

For the pip fallback, use `python -m pip check` instead.

**Test the built-in dashboard before creating your own:**

```bash
python -m streamlit hello --server.address 127.0.0.1 --server.port 8501
```

Open the URL printed by Terminal (normally `http://127.0.0.1:8501`). Keep Terminal running. If the sample dashboard loads, press **Control + C** and continue to Stage 4. If the port is occupied, use `8502`.

**Step 13 · Add optional libraries later**

Use the same requirements as constraints so that adding packages does not silently upgrade the pinned dashboard dependencies:

```bash
uv pip install --python .venv/bin/python --only-binary=:all: -c requirements.txt "plotly==5.24.1" "scikit-learn==1.5.2" "scipy==1.14.1"
```

If you specifically need yfinance, install it separately after the dashboards work:

```bash
uv pip install --python .venv/bin/python --only-binary=:all: -c requirements.txt yfinance
```

These are optional examples, not mandatory setup commands. If yfinance or any optional package has no compatible wheel, skip that package; it is not required for either dashboard. Live Yahoo Finance access is not guaranteed by package installation. For the pip fallback, replace `uv pip install --python .venv/bin/python` with `python -m pip install`.

Do not use `uv add` or ordinary `uv run` with this requirements-based setup; they may synchronize the project and change or remove the installed packages.

**Step 14 · Export the installed packages later**

```bash
uv pip freeze --python .venv/bin/python > requirements-installed.txt
```

For the pip fallback:

```bash
python -m pip freeze > requirements-installed.txt
```

This keeps the compatibility-pinned `requirements.txt` intact and saves a separate snapshot of installed packages, including transitive dependencies.

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
ls -la
python -m streamlit run expenses.py --server.address 127.0.0.1 --server.port 8501
```

Expected visible items: `expenses.py`, `requirements.txt`, `.venv`; `pyproject.toml` is present if you initialized a uv project. `.venv` is hidden on macOS, so use `ls -la` to see it.

If Streamlit asks for an email, leave it blank and press **Enter**. Open **http://127.0.0.1:8501** manually if the browser does not open. Leave Terminal running; see Stage 6 if the browser reports a lost connection.

<a id="stage-5"></a>
## Stage 5 — Daily use, stop, and switch dashboards

### Reopen the dashboard (PDF section B7)

Each time, open **Terminal**. If you are in a Conda `(base)` environment, run `conda deactivate` first. Then run these **three commands** in order:

```bash
cd ~/Downloads/code-practice
source .venv/bin/activate
python -m streamlit run expenses.py --server.address 127.0.0.1 --server.port 8501
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
    if not picked:
        st.info("Select a date range to continue.")
        st.stop()
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
python -m streamlit run sales.py --server.address 127.0.0.1 --server.port 8501
```

There is no need to reactivate the environment or reinstall the libraries while the same session and `.venv` are still active.

<a id="stage-6"></a>
## Stage 6 — Quick reference, troubleshooting and environment management

### Command reference (macOS 11.4 / Terminal)

| Task | Command |
| --- | --- |
| Check macOS | `sw_vers -productVersion` |
| Check architecture | `uname -m` |
| Check uv | `uv --version` |
| Install Python 3.12 (working uv only) | `uv python install 3.12` |
| Enter project | `cd ~/Downloads/code-practice` |
| Initialize new project | `uv init --bare --python 3.12` |
| Create missing `.venv` | `uv venv --python 3.12` |
| Activate | `source .venv/bin/activate` |
| Check Python | `which python` and `python --version` |
| Edit dependencies | `nano requirements.txt` |
| Install from file | `uv pip install --python .venv/bin/python --only-binary=:all: -r requirements.txt` |
| Add optional libraries | `uv pip install --only-binary=:all: -c requirements.txt plotly` (with `.venv` active) |
| Export installed-package list | `uv pip freeze > requirements-installed.txt` (with `.venv` active) |
| Edit expense app | `nano expenses.py` |
| View all files | `ls -la` |
| Run expense app | `python -m streamlit run expenses.py` |
| Run sales app | `python -m streamlit run sales.py` |
| Stop app | **Control + C** |
| Deactivate | `deactivate` |

**Run without activating** (from the project directory):

```bash
.venv/bin/python -m streamlit run expenses.py --server.address 127.0.0.1 --server.port 8501
```

This uses the intended interpreter directly and avoids `uv run` synchronizing an otherwise empty `pyproject.toml`.

### Troubleshooting on Big Sur

| Error | What to do |
| --- | --- |
| `streamlit not found` or `permission denied: streamlit` | Activate `.venv`, check installation with `python -m streamlit --version`, and use `python -m streamlit run ...` instead of the standalone command. |
| `Python interpreter not found at ...` | Stop the dashboard, deactivate, and recreate the broken environment using Stage 2. |
| `Failed to build pyarrow==26.0.1` | Use the pinned `requirements.txt` in Stage 3 and `--only-binary=:all:`. |
| No matching binary wheel | Check macOS, Python version and CPU architecture; report the exact failing package. |
| `Is Streamlit still running?` | Check the Terminal first: the browser cannot reach the server. This is not proof that PyArrow is at fault. |

**If the browser reports a lost connection:**

1. Inspect the Terminal that launched the server. If the shell prompt has returned or there is a crash/traceback, note the complete error.
2. Stop the running server with **Control + C**, then start the built-in demo on a fresh port:

```bash
python -m streamlit hello --server.address 127.0.0.1 --server.port 8502
```

3. Keep Terminal open and browse to `http://127.0.0.1:8502`. Try a private window or another compatible browser, and refresh with **Cmd + Shift + R**. If the demo works, stop it and run your app on that port:

```bash
python -m streamlit run expenses.py --server.address 127.0.0.1 --server.port 8502
```

4. If the demo also fails while Terminal still shows a running server, inspect the browser connection (proxy, VPN, browser compatibility or WebSocket errors). In a **second Terminal window**, check the server's HTTP health endpoint:

```bash
curl -i http://127.0.0.1:8502/_stcore/health
```

An HTTP 200 response with `ok` indicates the HTTP server is reachable; it does not prove the WebSocket or dashboard code works. A connection failure means the server is not reachable on that port.

5. If Terminal suggests a file-watcher problem, stop the server and try disabling the watcher for this local exercise:

```bash
python -m streamlit run expenses.py --server.address 127.0.0.1 --server.port 8502 --server.fileWatcherType none
```

With this option you may need to restart manually after editing Python code. Do not disable CORS or XSRF protections as a first-line fix.

If none of these work, record the following output and the full error from the server Terminal:

```bash
sw_vers
uname -m
which python
python --version
python -c "import streamlit, pyarrow; print(streamlit.__version__, pyarrow.__version__)"
```

### Rebuild only if the environment is broken

Stop Streamlit and deactivate if active. Enter the project directory, rename the existing `.venv` as in Stage 2, recreate it with the correct Python 3.12 interpreter, activate, then reinstall the pinned requirements from Stage 3. Do not delete your entire project folder.

### `pip` vs `uv` (compatibility edition)

| Task | Standard `pip` fallback | Working `uv` workflow |
| --- | --- | --- |
| Install Python | python.org 3.12 universal2 installer | `uv python install 3.12` |
| Create environment | `python3.12 -m venv .venv` | `uv venv --python 3.12` |
| Environment folder | `.venv` | `.venv` |
| Activate | `source .venv/bin/activate` | `source .venv/bin/activate` |
| Install libraries | `python -m pip install --only-binary=:all: -r requirements.txt` | `uv pip install --only-binary=:all: -r requirements.txt` |
| Export packages | `python -m pip freeze > requirements-installed.txt` | `uv pip freeze > requirements-installed.txt` |
| Run dashboard | `python -m streamlit run expenses.py` | `python -m streamlit run expenses.py` |

### Compatibility references and limitations

- [uv platform support](https://docs.astral.sh/uv/reference/platforms/): current official macOS support starts at 13; Big Sur is outside the support guarantee.
- [Python 3.12.10 installer](https://www.python.org/downloads/release/python-31210/): macOS 10.13+ universal2 installer.
- [PyArrow 17.0.0 release files](https://pypi.org/project/pyarrow/17.0.0/#files): CPython 3.12 wheels for macOS 10.15+ x86-64 and 11.0+ ARM64.
- [NumPy 1.26.4](https://pypi.org/project/numpy/1.26.4/#files), [pandas 2.2.3](https://pypi.org/project/pandas/2.2.3/#files), [Matplotlib 3.9.3](https://pypi.org/project/matplotlib/3.9.3/#files): compatible wheel tags for both architectures.
- [Streamlit 1.45.1](https://pypi.org/project/streamlit/1.45.1/) and [Streamlit 1.38 chart API](https://docs.streamlit.io/1.38.0/develop/api-reference/charts/st.bar_chart): older Streamlit release and chart API used by the sample apps.

The selected versions are a compatibility-oriented starting point, not a fully locked dependency graph or a security recommendation. Wheel availability has been checked for key packages; actual installation and browser execution on macOS 11.4 have not been tested here. Prefer an updated OS for security and ongoing support, and keep this setup local.
