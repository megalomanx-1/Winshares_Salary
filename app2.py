import os
import pandas as pd
import streamlit as st

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="2026 NBA Win Shares Dashboard", page_icon="🏀", layout="wide"
)

st.title("🏀 2026 NBA Win Shares & Valuation Dashboard")
st.markdown(
    "Analyze and compare player productivity (**Win Shares**) and contract values straight from your local database."
)

# Core constants matching your spreadsheet setup
TARGET_FILE = "2026BBREFStats.xlsx"
WIN_COST_2026 = 4.32  # $4.32M per Win Share market baseline

# --- 2. Safe Data Loading & Cleaning Pipeline ---
if os.path.exists(TARGET_FILE):
    # Read Excel, skipping row 0 metadata row if present
    df_raw = pd.read_excel(TARGET_FILE, sheet_name="Hard Numbers")

    # Clean empty/metadata guide rows (like row 0 in BBREF files)
    df = df_raw.dropna(subset=["Player", "WS"]).copy()

    # Clean and fill salary columns to numbers (handling potential string symbols)
    salary_col = "2026-27Salary"
    if salary_col in df.columns:
        df[salary_col] = pd.to_numeric(df[salary_col], errors="coerce").fillna(
            0
        )
        # Convert raw dollars to millions for display uniformity (e.g. 49800000 -> 49.80)
        if df[salary_col].max() > 1000000:
            df["Salary ($M)"] = round(df[salary_col] / 1_000_000, 2)
        else:
            df["Salary ($M)"] = round(df[salary_col], 2)
    else:
        df["Salary ($M)"] = 0.0

    # Execute Baseline Financial Formulas
    df["Model Value ($M)"] = round(df["WS"] * WIN_COST_2026, 2)
    df["Surplus Value ($M)"] = round(
        df["Model Value ($M)"] - df["Salary ($M)"], 2
    )

    # --- 3. UI Navigation Filters ---
    st.write("---")
    view_option = st.radio(
        "Choose Your Analysis Mode:",
        ["Compare by Player", "Compare by Team"],
        horizontal=True,
    )

    # ==================== VIEW A: PLAYER COMPARISON ====================
    if view_option == "Compare by Player":
        st.subheader("👤 Individual Player Metrics & Rankings")

        # Multi-select search filters
        available_teams = sorted(df["Team"].unique().tolist())
        selected_teams = st.multiselect(
            "Filter Table by Team (Leave blank for League-wide):",
            available_teams,
        )

        # Apply search parameters
        df_players = df.copy()
        if selected_teams:
            df_players = df_players[df_players["Team"].isin(selected_teams)]

        # Highlight Top 3 Key KPI Metrics for context
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            top_ws_player = df_players.sort_values(by="WS", ascending=False).iloc[0]
            st.metric(
                "Win Shares Leader",
                f"{top_ws_player['Player']}",
                f"{top_ws_player['WS']} WS",
            )
        with kpi2:
            top_value_player = df_players.sort_values(
                by="Surplus Value ($M)", ascending=False
            ).iloc[0]
            st.metric(
                "Best Value Contract",
                f"{top_value_player['Player']}",
                f"+${top_value_player['Surplus Value ($M)']}M",
            )
        with kpi3:
            avg_ws = round(df_players["WS"].mean(), 2)
            st.metric("Group Average Win Shares", f"{avg_ws} WS")

        # Render Main Player Data Frame Matrix
        df_players_display = df_players.sort_values(by="WS", ascending=False)[
            [
                "Player",
                "Team",
                "Pos",
                "Age",
                "WS",
                "Salary ($M)",
                "Model Value ($M)",
                "Surplus Value ($M)",
            ]
        ]

        st.dataframe(
            df_players_display,
            column_config={
                "Salary ($M)": st.column_config.NumberColumn(format="$%.2fM"),
                "Model Value ($M)": st.column_config.NumberColumn(format="$%.2fM"),
                "Surplus Value ($M)": st.column_config.NumberColumn(format="$%.2fM"),
            },
            use_container_width=True,
            hide_index=True,
        )

    # ==================== VIEW B: TEAM COMPARISON ====================
    else:
        st.subheader("🏢 Team Aggregate Win Shares & Cap Value Efficiency")

        # Aggregate row statistics metrics via Pandas groupbys
        team_summary = (
            df.groupby("Team")
            .agg(
                Total_Win_Shares=("WS", "sum"),
                Roster_Count=("Player", "count"),
                Total_Salary_Spent=("Salary ($M)", "sum"),
                Total_Model_Value=("Model Value ($M)", "sum"),
                Net_Surplus_Value=("Surplus Value ($M)", "sum"),
            )
            .reset_index()
        )

        # Sort based on absolute performance
        team_summary = team_summary.sort_values(
            by="Total_Win_Shares", ascending=False
        )

        # Render Team Data Frame Overview
        st.dataframe(
            team_summary,
            column_config={
                "Total_Win_Shares": st.column_config.NumberColumn(format="%.1f"),
                "Total_Salary_Spent": st.column_config.NumberColumn(format="$%.2fM"),
                "Total_Model_Value": st.column_config.NumberColumn(format="$%.2fM"),
                "Net_Surplus_Value": st.column_config.NumberColumn(format="$%.2fM"),
            },
            use_container_width=True,
            hide_index=True,
        )

        # Quick summary analytics chart
        st.write("### 📊 Visualizing Team Efficiency (Win Shares vs. Salary Paid)")
        st.bar_chart(
            team_summary,
            x="Team",
            y=["Total_Win_Shares", "Net_Surplus_Value"],
            use_container_width=True,
        )

else:
    st.error(
        f"⚠️ System File Error: Could not verify location path for `{TARGET_FILE}`."
    )
    st.info(
        "Make sure your spreadsheet is committed right next to your `app.py` in the root GitHub repository directory layer."
    )
