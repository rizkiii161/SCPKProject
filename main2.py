import numpy as np
import pandas as pd
import streamlit as st

def validity_check(M, W):
    banyak = len(M)
    RI = {
            2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32,
            8: 1.41, 9: 1.45, 10: 1.51, 11: 1.53, 12: 1.54, 13: 1.56, 14: 1.57
    }

    CV = M @ W / W
    eigen = np.mean(CV)
    CI = (eigen - banyak) / (banyak - 1)
    RI_value = RI.get(banyak, 1.12)  # Default RI for banyak=5
    CR = CI / RI_value

    st.markdown("### Consistency Check")
    st.write(f"λ max: {eigen:.4f}")
    st.write(f"CI (Consistency Index): {CI:.3f}")
    st.write(f"CR (Consistency Ratio): {CR:.3f}")
    if CR <= 0.1:
        st.success("✅ The matrix is **consistent**. (CR ≤ 0.1)")
    else:
        st.error("❌ The matrix is **inconsistent**. Please review your inputs. (CR > 0.1)")

st.title("Job Trend Selection using AHP Method")
st.write("##### by Ardhika Rizki Akbar Pratama - 123230057")
st.write("##### & Akfina Ni'mawati - 123230076")

tab1, tab2, tab3 = st.tabs(["Full Data", "Job Category", " Input Weights & Final Result"])
with tab1:
    # Load data
    df = pd.read_csv("freelancer_earnings_bd.csv")
    st.write("## Full Data")
    st.write(df)
with tab2:
    # Choose category
    st.write("## 🔖 Job Category")
    category = st.radio("", df["Job_Category"].unique())
    df_sorted = df[df["Job_Category"] == category]
    st.write(f"### 🔎 Filtered Data for {category}:")
    st.write(df_sorted)
with tab3:
    # Input weights from user
    st.markdown("## ➕ Input  Weights (0-10)")

    earning = st.number_input("Earnings", min_value=0, max_value=10, step=1)
    rehire = st.number_input("Rehire Rate", min_value=0, max_value=10, step=1)
    spend = st.number_input("Marketing Spend", min_value=0, max_value=10, step=1)
    succes = st.number_input("Success Rate", min_value=0, max_value=10, step=1)
    duration = st.number_input("Duration", min_value=0, max_value=10, step=1)

    criteria_names = ["Earnings_USD", "Rehire_Rate", "Marketing_Spend", "Job_Success_Rate", "Job_Duration_Days"]
    criteria_values = np.array([earning, rehire, spend, succes, duration])

    st.text("Note: The larger the number, the more important the criterion.")

    if np.any(criteria_values == 0):
        st.warning("❗ All criteria must be filled (cannot be zero).")
    else:
        n = len(criteria_values)
        pairwise_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                pairwise_matrix[i][j] = criteria_values[i] / criteria_values[j]

        st.markdown("### 📊 Pairwise Comparison Matrix")
        st.write(pd.DataFrame(pairwise_matrix, columns=criteria_names, index=criteria_names))

        # Normalisasi
        normalized_matrix = pairwise_matrix / pairwise_matrix.sum(axis=0)
        weights = normalized_matrix.mean(axis=1)

        st.markdown("### 🧮 Weights (Eigenvector Approximation)")
        for name, w in zip(criteria_names, weights):
            st.write(f"**{name}**: {w:.4f}")

        # Validity check function
        st.write("#### Matrix:")
        st.write(pairwise_matrix)

        st.write("#### Weights:")
        st.write(weights)

        validity_check(pairwise_matrix, weights)

        for col in criteria_names:
            df_sorted[f"Normalized_{col}"] = (df_sorted[col]  - df_sorted[col].min()) /(df_sorted[col].max()- df_sorted[col].min())
        
        df_sorted["final_score"] = sum(
        df_sorted[f"Normalized_{name}"] * weights[i]
        for i, name in enumerate(criteria_names))

        top_10 = df_sorted.sort_values(by="final_score", ascending=False).head(10)
        st.markdown("## 🏆 Top 10 Freelancers by Final Score")
        st.write(top_10.filter(regex="^(?!Normalized_)", axis=1))