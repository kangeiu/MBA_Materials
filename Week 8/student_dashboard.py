
# Import libraries

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.formula.api as smf


# ==================================================
# Dashboard Configuration
# ==================================================

st.set_page_config(
    page_title="IELTS Student Performance",
    layout="wide"
)

st.title("IELTS Student Performance & Prediction")
st.caption("BUS 520 | Global Markets, Investments & Analytics") # subheader

# col1, col2 = st.columns([1, 8], vertical_alignment="center")

# with col1:
#     st.image("eiulogo.png", width=200)

# with col2:
#     st.title("IELTS Student Performance & Prediction")
#     st.subheader("BUS 520 | Global Markets, Investments & Analytics")

# ==================================================
# Load Data
# ==================================================

df = pd.read_csv("student_sample.csv", index_col=0)

df["outcome"] = np.where(df["ielts_pass"] == 1, "Pass", "Fail")


# ==================================================
# Key Performance Indicators (KPIs)
# ==================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Students",
    len(df)
)

col2.metric(
    "IELTS Pass Rate",
    f"{df['ielts_pass'].mean():.2%}"
)

col3.metric(
    "Average IELTS Score",
    f"{df['ielts_score'].mean():.2f}"
)

col4.metric(
    "Pass Within One Year",
    f"{df['ielts_pass_within_1year'].mean():.2%}"
)


# ==================================================
# Create Three Tabs
# ==================================================

tab1, tab2, tab3 = st.tabs([
    "Exploratory Data Analysis",
    "Logistic Regression",
    "Prediction"
])


# ==================================================
# TAB 1: Exploratory Data Analysis
# ==================================================

with tab1:

    st.header("Exploratory Data Analysis")

    # Select variables

    variables = [
        "exam_total",
        "gpa",
        "ielts_study_months",
        "ielts_score",
        "ielts_pass"
    ]

    # Preview data

    st.subheader("Student Data")

    st.dataframe(df[variables].head(30))


    # Descriptive statistics

    st.subheader("Descriptive Statistics")

    st.dataframe(df[variables].describe().round(3))


    # IELTS outcomes

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("IELTS Pass and Fail")

        fig = px.pie(
            df,
            names="outcome",
            hole=0.3
        )

        st.plotly_chart(fig)

    with col2:

        st.subheader("IELTS Score Distribution")

        fig = px.histogram(
            df,
            x="ielts_score",
            color="outcome",
            nbins=15
        )

        st.plotly_chart(fig)


    # Academic performance and IELTS outcomes

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("GPA by IELTS Outcome")

        fig = px.box(
            df,
            x="outcome",
            y="gpa",
            color="outcome"
        )

        st.plotly_chart(fig)

    with col2:

        st.subheader("Entrance Exam Score by IELTS Outcome")

        fig = px.box(
            df,
            x="outcome",
            y="exam_total",
            color="outcome"
        )

        st.plotly_chart(fig)


    # Scatterplot

    st.subheader("Entrance Exam Score and GPA")

    fig = px.scatter(
        df,
        x="exam_total",
        y="gpa",
        color="outcome"
    )

    st.plotly_chart(fig)


    # # Correlation matrix

    # st.subheader("Correlation Matrix")

    # correlation = df[variables].corr()

    # fig = px.imshow(
    #     correlation,
    #     text_auto=".2f",
    #     color_continuous_scale="RdBu_r",
    #     zmin=-1,
    #     zmax=1
    # )

    # st.plotly_chart(fig)


    # Pass rate by study duration

    st.subheader("IELTS Pass Rate by Study Duration")

    pass_rate = df.groupby("ielts_study_months")[
        "ielts_pass"
    ].mean().reset_index()

    pass_rate["pass_rate"] = pass_rate["ielts_pass"] * 100

    fig = px.bar(
        pass_rate,
        x="ielts_study_months",
        y="pass_rate",
        labels={
            "ielts_study_months": "Study Months",
            "pass_rate": "Pass Rate (%)"
        }
    )

    st.plotly_chart(fig)


# ==================================================
# Estimate Logistic Regression
# ==================================================

ielts_logit = smf.logit(
    formula="ielts_pass ~ exam_total + gpa + ielts_study_months",
    data=df
).fit(disp=False)


# ==================================================
# TAB 2: Logistic Regression
# ==================================================

with tab2:

    st.header("Binary Logistic Regression")

    st.subheader("Model Specification")

    st.latex(
        r"\log\left(\frac{p}{1-p}\right)"
        r"=\beta_0+\beta_1 ExamTotal"
        r"+\beta_2 GPA+\beta_3 StudyMonths"
    )

    st.write("Dependent variable: IELTS pass (1 = Pass, 0 = Fail)")

    st.write(
        "Independent variables: Entrance exam total, GPA, "
        "and IELTS study months."
    )


    # Model summary

    # st.subheader("Logistic Regression Results")

    # st.text(ielts_logit.summary().as_text())


    # Coefficients and odds ratios

    st.subheader("Interpretation of Coefficients")

    results = pd.DataFrame({
        "Coefficient": ielts_logit.params,
        "Odds Ratio": np.exp(ielts_logit.params),
        "Change in Odds (%)":
            (np.exp(ielts_logit.params) - 1) * 100,
        "P-value": ielts_logit.pvalues
    })

    st.dataframe(results.round(4))


    # Statistical significance

    results["Significant at 5%"] = np.where(
        results["P-value"] < 0.05,
        "Yes",
        "No"
    )

    st.dataframe(results.round(4))


    # Visualize percentage change in odds

    st.subheader("Percentage Change in Odds")

    fig = px.bar(
        results.drop("Intercept"),
        x="Change in Odds (%)",
        orientation="h",
        text_auto=".2f"
    )

    st.plotly_chart(fig)


    # Average marginal effects

    st.subheader("Average Marginal Effects")

    marginal_effects = ielts_logit.get_margeff()

    st.text(marginal_effects.summary().as_text())


    # Model fit

    st.subheader("Model Fit")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Observations",
        int(ielts_logit.nobs)
    )

    col2.metric(
        "Pseudo R-squared",
        f"{ielts_logit.prsquared:.4f}"
    )

    col3.metric(
        "LLR p-value",
        f"{ielts_logit.llr_pvalue:.3e}"
    )

    st.caption(
        "Pseudo R-squared is not the proportion of variance explained."
    )


# ==================================================
# TAB 3: Prediction
# ==================================================

with tab3:

    st.header("IELTS Pass Probability Prediction")

    st.write(
        "Enter a student's academic characteristics "
        "to estimate the probability of passing IELTS."
    )


    # Interactive inputs

    col1, col2, col3 = st.columns(3)

    with col1:

        exam_total = st.slider(
            "Entrance Exam Total",
            min_value=0.0,
            max_value=30.0,
            value=27.0,
            step=0.1
        )

    with col2:

        gpa = st.slider(
            "GPA",
            min_value=0.0,
            max_value=4.0,
            value=3.5,
            step=0.1
        )

    with col3:

        study_months = st.slider(
            "IELTS Study Months",
            min_value=0,
            max_value=24,
            value=12
        )


    # Create new observation

    new_student = pd.DataFrame({
        "exam_total": [exam_total],
        "gpa": [gpa],
        "ielts_study_months": [study_months]
    })

    st.subheader("Student Profile")

    st.dataframe(new_student)


    # Predict probability

    probability = ielts_logit.predict(new_student).iloc[0]


    # Display prediction

    col1, col2 = st.columns(2)

    col1.metric(
        "Probability of Passing",
        f"{probability:.2%}"
    )

    col2.metric(
        "Probability of Failing",
        f"{1 - probability:.2%}"
    )

    st.progress(float(probability))

    st.write(
        f"The predicted probability of passing IELTS is "
        f"**{probability:.2%}**."
    )


    # Probability chart

    prediction = pd.DataFrame({
        "Outcome": ["Pass", "Fail"],
        "Probability": [probability, 1 - probability]
    })

    fig = px.pie(
        prediction,
        names="Outcome",
        values="Probability",
        hole=0.4
    )

    st.plotly_chart(fig)


    # Scenario analysis: Study duration

    st.subheader("Scenario Analysis: IELTS Study Duration")

    scenarios = pd.DataFrame({
        "exam_total": exam_total,
        "gpa": gpa,
        "ielts_study_months": np.arange(0, 25)
    })

    scenarios["probability"] = ielts_logit.predict(scenarios)

    fig = px.line(
        scenarios,
        x="ielts_study_months",
        y="probability",
        markers=True,
        labels={
            "ielts_study_months": "Study Months",
            "probability": "Probability of Passing"
        }
    )

    fig.update_yaxes(tickformat=".0%", range=[0, 1])

    st.plotly_chart(fig)

    st.caption(
        "Entrance exam total and GPA are held constant."
    )

    st.info(
        "Predicted probabilities do not establish causal effects. "
        "Predictions outside the observed data range should be "
        "interpreted cautiously."
    )
