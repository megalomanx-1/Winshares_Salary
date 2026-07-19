import os
import pandas as pd
import streamlit as st

# --- 1. Page Configuration & Setup ---
st.set_page_config(
    page_title="2026 NBA Contract Evaluator", page_icon="🏀", layout="wide"
)
st.title("🏀 2026 Consolidated Contract Valuation Engine")
st.markdown(
    "Automatically parsing performance and contract data directly from `2026BBREFStats.xlsx`."
)

# Core valuation constant: $4.32M per individual Win Share
WIN_COST_2026 = 4.32
TARGET_FILE = "2026BBREFStats.xlsx"

# --- 2. Automated File Verification & Load ---
# Check if the file exists in your project directory
if os.path.exists(TARGET_FILE):
    # Load the spreadsheet into memory automatically
    df = pd.read_excel(TARGET_FILE)

    st.write("---")
    st.write("### 🛠️ Map Your Spreadsheet Columns")
    st.markdown(
        "Select which columns from your file match the required data profiles:"
    )

    col1, col2, col3 = st.columns(3)

    # Automatically try to guess the column indexes if they match common naming patterns
    with col1:
        player_col = st.selectbox("Player Name Column", df.columns, index=0)
    with col2:
        ws_col = st.selectbox(
            "Win Shares Column (Production)",
            df.columns,
            index=1 if len(df.columns) > 1 else 0,
        )
    with col3:
        salary_col = st.selectbox(
            "Actual Salary ($M) Column",
            df.columns,
            index=2 if len(df.columns) > 2 else 0,
        )

    # --- 3. Vectorized Valuation Calculations ---
    # Calculate the model's projected fair market valuation based on win shares
    df["Model Valuation ($M)"] = round(df[ws_col] * WIN_COST_2026, 2)
    df["Surplus Value ($M)"] = round(df["Model Valuation ($M)"] - df[salary_col], 2)

    # Sort the table so the highest-surplus contract assets sit on top
    df_sorted = df.sort_values(by="Surplus Value ($M)", ascending=False)

    st.write("---")
    st.write("### 📊 Valuation Assessment Table")

    # Render the interactive database results directly onto the web interface
    st.dataframe(
        df_sorted[
            [
                player_col,
                ws_col,
                salary_col,
                "Model Valuation ($M)",
                "Surplus Value ($M)",
            ]
        ],
        column_config={
            salary_col: st.column_config.NumberColumn(format="$%.2fM"),
            "Model Valuation ($M)": st.column_config.NumberColumn(format="$%.2fM"),
            "Surplus Value ($M)": st.column_config.NumberColumn(format="$%.2fM"),
        },
        use_container_width=True,
        hide_index=True,
    )

else:
    # Diagnostic error warning if you forgot to place or name the file correctly
    st.error(
        f"⚠️ File Not Found: Could not find `{TARGET_FILE}` in your root project folder."
    )
    st.info(
        "💡 To fix this, simply drop your spreadsheet into your project folder and ensure it is named exactly `2026BBREFStats.xlsx`."
    )
