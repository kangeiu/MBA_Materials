import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# 1. Page Configuration
st.set_page_config(page_title="Central Limit Theorem Simulation", layout="wide")

st.title("📊 From Sample to Population (Inferential Statistics)")
st.markdown("""
This interactive platform demonstrates two fundamental concepts in inferential statistics:
1. **The Central Limit Theorem (CLT)**: Showing how the distribution of sample means approaches normality.
2. **Confidence Interval (CI) Coverage**: Visually tracking how well sample intervals capture the true population mean ($\mu$).
""")

# 2. Sidebar Controls
st.sidebar.header("🔧 Simulation Parameters")

population_size = st.sidebar.slider("Population Size", min_value=5000, max_value=100000, value=50000, step=5000)
sample_size = st.sidebar.slider("Sample Size (n)", min_value=2, max_value=200, value=30, step=1)
num_simulations = st.sidebar.slider("Number of Simulations", min_value=500, max_value=5000, value=1000, step=500)
confidence_level = st.sidebar.slider("Confidence Level", min_value=0.80, max_value=0.99, value=0.95, step=0.01)
random_seed = st.sidebar.number_input("Random Seed", value=42)

np.random.seed(random_seed)

# Population Type Selector
pop_type = st.sidebar.selectbox(
    "Select Population Distribution",
    ["Uniform", "Exponential", "Binomial", "Bimodal"]
)

# 3. Generate Population Data
if pop_type == "Uniform":
    pop_data = np.random.uniform(low=0, high=10, size=population_size)
    title_suffix = "Uniform Distribution"
elif pop_type == "Exponential":
    pop_data = np.random.exponential(scale=2, size=population_size)
    title_suffix = "Exponential Distribution"
elif pop_type == "Binomial":
    pop_data = np.random.binomial(n=10, p=0.3, size=population_size)
    title_suffix = "Binomial Distribution"
else:
    pop_data = np.concatenate([
        np.random.normal(loc=2, scale=0.5, size=population_size // 2),
        np.random.normal(loc=7, scale=0.8, size=population_size // 2)
    ])
    title_suffix = "Bimodal Distribution"

# 4. Statistical Calculations
pop_mean = np.mean(pop_data)
pop_std = np.std(pop_data)

# Matrix sampling
samples_matrix = np.random.choice(pop_data, size=(num_simulations, sample_size), replace=True)
sample_means = np.mean(samples_matrix, axis=1)

# Using sample standard deviations (ddof=1) for each individual sample row to calculate CIs
sample_stds = np.std(samples_matrix, axis=1, ddof=1)

theoretical_se = pop_std / np.sqrt(sample_size)
empirical_se = np.std(sample_means, ddof=1)

# 5. Confidence Interval Calculations (t-distribution approach)
# Critical t-value based on chosen confidence level and degrees of freedom
t_crit = stats.t.ppf((1 + confidence_level) / 2, df=sample_size - 1)
margins_of_error = t_crit * (sample_stds / np.sqrt(sample_size))

ci_lowers = sample_means - margins_of_error
ci_uppers = sample_means + margins_of_error

# Track which intervals cover the true population mean
contains_pop_mean = (ci_lowers <= pop_mean) & (pop_mean <= ci_uppers)
empirical_coverage_rate = np.mean(contains_pop_mean)

# 6. Dashboard Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Population Mean (μ)", f"{pop_mean:.4f}")
col2.metric("Mean of Sample Means", f"{np.mean(sample_means):.4f}")
col3.metric("Target CI Coverage", f"{confidence_level * 100:.1f}%")
col4.metric("Empirical CI Coverage Rate", f"{empirical_coverage_rate * 100:.2f}%")

st.markdown("---")

# 7. Create Navigation Tabs
tab1, tab2 = st.tabs(["📉 Central Limit Theorem", "🎯 Confidence Interval Tracking"])

with tab1:
    st.subheader("Central Limit Theorem Verification")
    fig1, (ax_pop, ax_clt) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Left: Population
    ax_pop.hist(pop_data, bins=50, color='lightcoral', edgecolor='black', alpha=0.7, density=True)
    ax_pop.axvline(pop_mean, color='darkred', linestyle='--', linewidth=2, label=f'Pop Mean (μ): {pop_mean:.2f}')
    ax_pop.set_title(f"{title_suffix} - Original Population", fontsize=11, fontweight='bold')
    ax_pop.set_xlabel("Value")
    ax_pop.set_ylabel("Density")
    ax_pop.legend(frameon=True)
    
    # Right: CLT Distribution
    ax_clt.hist(sample_means, bins=40, color='lightskyblue', edgecolor='black', alpha=0.7, density=True)
    ax_clt.axvline(pop_mean, color='darkred', linestyle='--', linewidth=2, label=f'Pop Mean (μ): {pop_mean:.2f}')
    ax_clt.axvline(np.mean(sample_means), color='blue', linestyle=':', linewidth=2, label=f'Mean of Means: {np.mean(sample_means):.2f}')
    
    # Overlay Theoretical Fit
    xmin, xmax = ax_clt.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = (1 / (theoretical_se * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - pop_mean) / theoretical_se)**2)
    ax_clt.plot(x, p, color='darkorange', linewidth=2.5, label='Theoretical Normal Fit')
    
    ax_clt.set_title(f"Distribution of Sample Means (n={sample_size})", fontsize=11, fontweight='bold')
    ax_clt.set_xlabel("Sample Mean Value")
    ax_clt.set_ylabel("Density")
    ax_clt.legend(frameon=True)
    
    st.pyplot(fig1)

with tab2:
    st.subheader("Confidence Interval Coverage Tracker")
    st.markdown(f"Showing the first **100 simulated samples** out of {num_simulations:,}. Green intervals capture the true population mean $\mu$, while red intervals miss it.")
    
    # Plotting first 100 intervals for clarity
    display_num = min(100, num_simulations)
    
    fig2, ax_ci = plt.subplots(figsize=(15, 6))
    ax_ci.axvline(pop_mean, color='darkred', linestyle='--', linewidth=2.5, label=f'True Population Mean (μ = {pop_mean:.2f})')
    
    for i in range(display_num):
        color = 'mediumseagreen' if contains_pop_mean[i] else 'crimson'
        ax_ci.plot([ci_lowers[i], ci_uppers[i]], [i, i], color=color, linewidth=1.5)
        ax_ci.plot(sample_means[i], i, 'o', color=color, markersize=4)
        
    ax_ci.set_title(f"Confidence Intervals for {display_num} Random Samples", fontsize=12, fontweight='bold')
    ax_ci.set_xlabel("Parameter Scale Value")
    ax_ci.set_ylabel("Sample Index")
    ax_ci.legend(frameon=True, loc="upper right")
    ax_ci.grid(True, linestyle=':', alpha=0.6)
    
    st.pyplot(fig2)
