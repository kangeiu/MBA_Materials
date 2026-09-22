import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Titanic EDA", layout="wide")

st.title("🚢 Titanic Dataset Exploratory Data Analysis")

@st.cache_data
def load_data():
    return sns.load_dataset("titanic")

df = load_data()

st.sidebar.header("Filter Data")

pclasses = sorted(df['pclass'].dropna().unique())
selected_pclass = st.sidebar.multiselect("Passenger Class (Pclass)", pclasses, default=pclasses)

sexes = df['sex'].dropna().unique()
selected_sex = st.sidebar.multiselect("Sex", sexes, default=list(sexes))

ports = df['embark_town'].dropna().unique()
selected_ports = st.sidebar.multiselect("Embark Town", ports, default=list(ports))

filtered_df = df[
    (df['pclass'].isin(selected_pclass)) &
    (df['sex'].isin(selected_sex)) &
    (df['embark_town'].isin(selected_ports))
].copy()

bins = [0, 12, 18, 35, 60, 100]
labels = ['Child (0-12)', 'Teen (13-18)', 'Young Adult (19-35)', 'Adult (36-60)', 'Senior (60+)']
filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=bins, labels=labels)
filtered_df['family_size'] = filtered_df['sibsp'] + filtered_df['parch'] + 1

# --- MAIN DASHBOARD ---

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Passengers", len(filtered_df))
col2.metric("Survivors", int(filtered_df['survived'].sum()))
col3.metric("Overall Survival Rate", f"{(filtered_df['survived'].mean() * 100):.1f}%")
col4.metric("Average Fare", f"${filtered_df['fare'].mean():.2f}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dataset Overview", 
    "📈 Visual Distributions", 
    "🔗 Feature Correlations", 
    "🎯 Detailed Survival Analysis",
    "👶 Age Deep-Dive"
])

with tab1:
    st.subheader("Data Preview")
    st.dataframe(filtered_df, width="stretch")
    
    st.subheader("Summary Statistics")
    st.write(filtered_df.describe())

with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Survival Rate by Class & Gender")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=filtered_df, x="pclass", y="survived", hue="sex", errorbar=None, palette="Set2", ax=ax)
        ax.set_ylabel("Survival Rate")
        st.pyplot(fig)
        
    with col_b:
        st.subheader("Age Distribution by Survival")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.kdeplot(data=filtered_df, x="age", hue="survived", common_norm=False, palette="Set1", fill=True, ax=ax)
        ax.set_xlabel("Age")
        st.pyplot(fig)

with tab3:
    st.subheader("Numeric Correlation Heatmap")
    numeric_df = filtered_df.select_dtypes(include=['float64', 'int64'])
    
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

with tab4:
    st.subheader("Survival Rates Across Demographics")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        st.markdown("**1. Survival Rate by Sex**")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        sns.barplot(data=filtered_df, x="sex", y="survived", errorbar=None, palette="viridis", ax=ax)
        ax.set_ylabel("Survival Rate")
        ax.set_ylim(0, 1)
        st.pyplot(fig)
        st.info("💡 **Insight:** Females achieved a significantly higher survival rate (~74%) compared to males (~19%), reflecting the strict 'women and children first' evacuation protocol.")

        st.markdown("**2. Survival Rate by Embarkation Town**")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        sns.barplot(data=filtered_df, x="embark_town", y="survived", hue="sex", errorbar=None, palette="Blues_d", ax=ax)
        ax.set_ylabel("Survival Rate")
        ax.set_ylim(0, 1)
        st.pyplot(fig)
        st.info("💡 **Insight:** Cherbourg passengers had higher survival rates largely due to socioeconomic class distribution—a higher proportion of 1st-class passengers boarded at Cherbourg.")

    with col_y:
        st.markdown("**3. Survival Rate by Age Group**")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        sns.barplot(data=filtered_df, x="age_group", y="survived", errorbar=None, palette="magma", ax=ax)
        ax.set_ylabel("Survival Rate")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=15)
        ax.set_ylim(0, 1)
        st.pyplot(fig)
        st.info("💡 **Insight:** Children (0–12) had the highest priority and survival outcome (~58%), whereas seniors (60+) faced the lowest odds (~22%).")

        st.markdown("**4. Survival Rate by Age Group and Class**")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        sns.barplot(data=filtered_df, x="age_group", y="survived", hue="pclass", errorbar=None, palette="crest", ax=ax)
        ax.set_ylabel("Survival Rate")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=15)
        ax.set_ylim(0, 1)
        st.pyplot(fig)
        st.info("💡 **Insight:** Socioeconomic status modified age prioritization: 1st-class passengers across almost all age groups maintained high survival rates compared to 3rd-class peers.")

with tab5:
    st.subheader("In-Depth Age Analysis")

    valid_age_df = filtered_df.dropna(subset=['age'])
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Mean Age", f"{valid_age_df['age'].mean():.1f} yrs")
    m2.metric("Median Age", f"{valid_age_df['age'].median():.1f} yrs")
    m3.metric("Youngest", f"{valid_age_df['age'].min():.2f} yrs")
    m4.metric("Oldest", f"{int(valid_age_df['age'].max())} yrs")
    m5.metric("Missing Age Count", f"{filtered_df['age'].isna().sum()}")

    st.divider()

    col_age1, col_age2 = st.columns(2)

    with col_age1:
        st.markdown("**1. Age Distribution by Class & Survival (Violin Plot)**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.violinplot(
            data=valid_age_df, 
            x="pclass", 
            y="age", 
            hue="survived", 
            split=True, 
            inner="quart", 
            palette="Set1", 
            ax=ax
        )
        ax.set_xlabel("Passenger Class")
        ax.set_ylabel("Age")
        st.pyplot(fig)
        st.info("💡 **Insight:** 1st Class passengers were systematically older than 2nd and 3rd Class passengers. The child bump is mostly prominent in 2nd and 3rd class.")

        st.markdown("**2. Fare vs. Age Scatter Analysis**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(
            data=valid_age_df, 
            x="age", 
            y="fare", 
            hue="survived", 
            style="sex",
            alpha=0.7, 
            palette="coolwarm", 
            ax=ax
        )
        ax.set_ylabel("Fare ($)")
        ax.set_xlabel("Age")
        st.pyplot(fig)
        st.info("💡 **Insight:** Outlier fares (> $200) belong primarily to adults aged 30–60 who survived, whereas low-fare passengers are spread across all age brackets.")

    with col_age2:
        st.markdown("**3. Family Size vs. Age**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(
            data=valid_age_df, 
            x="family_size", 
            y="age", 
            palette="muted", 
            ax=ax
        )
        ax.set_xlabel("Family Size (Siblings/Spouse + Parents/Children)")
        ax.set_ylabel("Age")
        st.pyplot(fig)
        st.info("💡 **Insight:** Passengers travelling with large families (Family Size ≥ 5) tend to skew significantly younger, representing children travelling with parents.")

        st.markdown("**4. Survival Probability Curve across Continuous Age**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.regplot(
            data=valid_age_df, 
            x="age", 
            y="survived", 
            logistic=True, 
            scatter_kws={'alpha':0.15}, 
            line_kws={'color':'red'}, 
            ax=ax
        )
        ax.set_ylabel("Survival Probability")
        ax.set_xlabel("Age")
        st.pyplot(fig)
        st.info("💡 **Insight:** Logistic regression fit demonstrates an overall downward trend in survival probability as age increases.")
        
