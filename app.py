import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Portfolio Analysis App", layout="wide")

st.title("📊 Portfolio Management and Risk Analysis App")

# Add a number input for the risk-free rate
risk_free_rate_annual = st.number_input(
    "Annual Risk-Free Rate (e.g., 0.05 for 5%)", 
    min_value=0.0, 
    max_value=1.0, 
    value=0.05, 
    step=0.005,
    format="%.3f"
)
risk_free_rate_daily = risk_free_rate_annual / 252

uploaded_file = st.file_uploader("Upload your CSV file (must contain 'date' and 'ltp'/'close' columns)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.write("### Raw Data Preview")
    st.dataframe(df.head())

    # Standardize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Try to detect Date and LTP columns
    date_col = next((col for col in df.columns if "date" in col), None)
    ltp_col = next((col for col in df.columns if "ltp" in col or "close" in col), None)

    if not date_col or not ltp_col:
        st.error("❌ 'Date' or 'LTP/CLOSE' columns not found. Please check your CSV.")
    else:
        # --- Data Processing Pipeline ---
        try:
            # 1. Convert Date column
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # 2. Convert LTP column to numeric, coercing errors
            df[ltp_col] = pd.to_numeric(df[ltp_col], errors='coerce')
            df = df.dropna(subset=[ltp_col])

            # 3. Sort by date
            df = df.sort_values(by=date_col)
            
            st.success("✅ Data processed successfully!")

            # --- Descriptive Statistics ---
            st.write("### Descriptive Statistics for LTP")
            st.write(df[[ltp_col]].describe())

            # --- Calculate Metrics ---
            df['returns'] = df[ltp_col].pct_change()
            df = df.dropna(subset=['returns']) # Drop first row with NaN return
            
            if df.empty:
                st.warning("Not enough data to calculate returns (need at least 2 data points).")
            else:
                mean_daily_return = df['returns'].mean()
                std_dev_daily = df['returns'].std()
                
                # Annualized Metrics
                annualized_return = mean_daily_return * 252
                annualized_volatility = std_dev_daily * np.sqrt(252)
                
                # Annualized Sharpe Ratio
                if annualized_volatility != 0:
                    annualized_sharpe = (annualized_return - risk_free_rate_annual) / annualized_volatility
                else:
                    annualized_sharpe = np.nan

                st.write("### 📈 Annualized Portfolio Metrics")
                st.write({
                    "Annualized Mean Return": f"{annualized_return:.2%}",
                    "Annualized Volatility (Risk)": f"{annualized_volatility:.2%}",
                    "Annualized Sharpe Ratio": f"{annualized_sharpe:.3f}",
                })

                # --- Visual Analysis ---
                st.write("### 📊 Visual Analysis")
                st.write(f"**{ltp_col.upper()} Over Time**")
                
                # Prep data for Streamlit chart (must have index)
                chart_data = df.set_index(date_col)[[ltp_col]]
                st.line_chart(chart_data)

                # --- Suggestions ---
                st.write("### Suggestions")
                if annualized_sharpe > 1:
                    st.success("👍 Excellent risk-adjusted returns. The portfolio is performing efficiently.")
                elif annualized_sharpe > 0.5:
                    st.info("😐 Moderate performance. The returns are acceptable for the level of risk, but review diversification.")
                elif not np.isnan(annualized_sharpe):
                    st.warning("👎 Low risk-adjusted return. The portfolio's volatility is high relative to its returns. Consider revising asset allocation.")
                else:
                    st.error("Could not calculate Sharpe Ratio (Volatility is zero).")

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")