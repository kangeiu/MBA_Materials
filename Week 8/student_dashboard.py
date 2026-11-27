
# Import libraries

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.formula.api as smf
import statsmodels.api as sm
from pathlib import Path


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
# Create Four Tabs
# ==================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Exploratory Data Analysis",
    "Linear Regression (OLS)",
    "Logistic Regression (Logit)",
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
# TAB 2: Linear Regression (OLS)
# ==================================================

with tab2:

    st.header("Linear Regression (OLS)")

    st.write("How is entrance-exam score related to GPA?")

    st.subheader("Model Specification")

    st.latex(r"GPA_i = \beta_0 + \beta_1 ExamTotal_i + \epsilon_i")

    st.write("Dependent variable: GPA (gpa)")
    st.write("Independent variable: Entrance exam total (exam_total)")

    # Prepare the design matrix and estimate the model

    ols_data = df[["exam_total", "gpa"]].dropna().copy()
    x_ols = sm.add_constant(ols_data[["exam_total"]])
    y_ols = ols_data["gpa"]
    gpa_ols = sm.OLS(y_ols, x_ols).fit()

    # Calculation of OLS coefficients

    st.subheader("Calculation of OLS Coefficients")

    st.latex(r"y = X\beta + \epsilon")

    st.write("Mean Squared Error (MSE)")
    st.latex(
        r"MSE(\beta)=\frac{1}{n}\sum_{i=1}^{n}(y_i-x_i\beta)^2"
        r"=\frac{1}{n}(y-X\beta)'(y-X\beta)"
    )

    with st.expander("Derivation of the OLS estimator"):

        st.write("Expand MSE:")
        st.latex(
            r"MSE(\beta)=\frac{1}{n}(y'y-\beta'X'y-y'X\beta+\beta'X'X\beta)"
        )

        st.write("Since the cross-product is a scalar, the two middle terms are equal:")
        st.latex(r"y'X\beta=\beta'X'y")
        st.latex(r"MSE(\beta)=\frac{1}{n}(y'y-2\beta'X'y+\beta'X'X\beta)")

        st.write("Differentiate with respect to the coefficient vector:")
        st.latex(
            r"\frac{\partial MSE(\beta)}{\partial\beta}"
            r"=\frac{1}{n}(-2X'y+2X'X\beta)"
        )

        st.write("Set the derivative to zero (normal equations):")
        st.latex(r"X'X\hat{\beta}=X'y")

    st.write("Solve for the OLS coefficients (assuming full column rank):")
    st.latex(
        r"\hat{\beta}_{OLS}=\arg\min_{\beta}"
        r"\frac{1}{n}\sum_{i=1}^{n}(y_i-x_i\beta)^2"
        r"=(X'X)^{-1}X'y"
    )

    with st.expander("Python implementation and matrix calculation"):

        st.code(
            "import statsmodels.api as sm\n\n"
            'x_ols = sm.add_constant(ols_data[["exam_total"]])\n'
            'y_ols = ols_data["gpa"]\n'
            "gpa_ols = sm.OLS(y_ols, x_ols).fit()\n"
            "gpa_ols.summary()",
            language="python"
        )

        st.write("Design matrix X (first 10 observations):")
        st.dataframe(x_ols.head(10))

        X = x_ols.to_numpy()
        y = y_ols.to_numpy()
        xtx = X.T @ X
        xty = X.T @ y

        col1, col2 = st.columns(2)
        with col1:
            st.latex(r"X'X")
            st.dataframe(pd.DataFrame(xtx, index=x_ols.columns, columns=x_ols.columns).round(4))
        with col2:
            st.latex(r"X'y")
            st.dataframe(pd.DataFrame(xty, index=x_ols.columns, columns=["Value"]).round(4))

        if np.linalg.matrix_rank(X) == X.shape[1]:
            # Solve the normal equations without explicitly inverting X'X.
            beta_matrix = np.linalg.solve(xtx, xty)
            st.write("Coefficients obtained from the normal equations:")
            st.dataframe(pd.DataFrame({
                "Matrix calculation": beta_matrix,
                "Statsmodels OLS": gpa_ols.params
            }, index=x_ols.columns).round(6))
        else:
            st.warning("The design matrix is rank deficient; the inverse formula does not apply.")

    # Regression results and interpretation

    st.subheader("OLS Regression Results")

    confidence_intervals = gpa_ols.conf_int()
    ols_results = pd.DataFrame({
        "Coefficient": gpa_ols.params,
        "Standard Error": gpa_ols.bse,
        "t-statistic": gpa_ols.tvalues,
        "P-value": gpa_ols.pvalues,
        "95% CI Lower": confidence_intervals[0],
        "95% CI Upper": confidence_intervals[1],
        "Significant at 5%": np.where(gpa_ols.pvalues < 0.05, "Yes", "No")
    })

    st.dataframe(ols_results.style.format({
        "Coefficient": "{:.4f}", "Standard Error": "{:.4f}",
        "t-statistic": "{:.4f}", "P-value": "{:.3g}",
        "95% CI Lower": "{:.4f}", "95% CI Upper": "{:.4f}"
    }))

    intercept = gpa_ols.params["const"]
    slope = gpa_ols.params["exam_total"]
    p_value = gpa_ols.pvalues["exam_total"]

    st.subheader("Interpretation of Coefficients")
    st.latex(fr"\widehat{{GPA}}={intercept:.4f}{slope:+.4f}\,ExamTotal")

    direction = "higher" if slope >= 0 else "lower"
    st.write(
        f"A one-point higher entrance exam total is associated with "
        f"a {abs(slope):.4f}-point {direction} fitted GPA."
    )
    st.write(
        f"The slope is {'statistically significant' if p_value < 0.05 else 'not statistically significant'} "
        f"at the 5% level (p-value = {p_value:.3g})."
    )
    st.caption("The intercept is the fitted GPA at an exam score of zero, which is outside the observed score range in this sample.")

    # Scatterplot and fitted regression line

    st.subheader("Entrance Exam Score and GPA: OLS Regression Line")

    ols_data["fitted_gpa"] = gpa_ols.fittedvalues
    ols_data["residual"] = gpa_ols.resid
    fitted_line = ols_data.sort_values("exam_total")

    fig = px.scatter(
        ols_data, x="exam_total", y="gpa",
        labels={"exam_total": "Entrance Exam Total", "gpa": "GPA"},
        opacity=0.65
    )
    fig.add_scatter(
        x=fitted_line["exam_total"], y=fitted_line["fitted_gpa"],
        mode="lines", name="OLS fitted line", line=dict(color="crimson", width=3)
    )
    st.plotly_chart(fig)

    # Model fit

    st.subheader("Model Fit")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Observations", int(gpa_ols.nobs))
    col2.metric("R-squared", f"{gpa_ols.rsquared:.4f}")
    col3.metric("Adjusted R-squared", f"{gpa_ols.rsquared_adj:.4f}")
    col4.metric("RMSE", f"{np.sqrt(np.mean(gpa_ols.resid ** 2)):.4f}")

    st.write(
        f"Entrance exam total explains {gpa_ols.rsquared:.2%} of the "
        "observed variation in GPA in this sample."
    )
    st.caption("RMSE is the in-sample root mean squared prediction error, not an out-of-sample accuracy measure.")

    with st.expander("Full OLS regression summary"):
        st.text(gpa_ols.summary().as_text())

    # Residual diagnostics

    st.subheader("Residual Analysis")
    fig = px.scatter(
        ols_data, x="fitted_gpa", y="residual",
        labels={"fitted_gpa": "Fitted GPA", "residual": "Residual"},
        opacity=0.65
    )
    fig.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig)
    st.caption("Residuals are observed GPA minus fitted GPA. Look for systematic patterns or changes in spread around zero.")

    st.info("OLS estimates an association, not a causal effect. Conventional standard errors are used; inference relies on the relevant OLS assumptions.")


# ==================================================
# Estimate Logistic Regression
# ==================================================

ielts_logit = smf.logit(
    formula="ielts_pass ~ exam_total + gpa + ielts_study_months",
    data=df
).fit(disp=False)


# ==================================================
# TAB 3: Logistic Regression
# ==================================================

with tab3:

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
# TAB 4: Prediction
# ==================================================

with tab4:

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
