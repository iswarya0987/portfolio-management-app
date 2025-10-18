
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

uploaded_file = st.file_uploader("Upload your CSV file (must contain 'Date' and 'close' columns)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.write("### Raw Data Preview")
    st.dataframe(df.head())

    # --- Specific Column Names for your File ---
    # We will use the exact column names from your CSV
    date_col = "Date"
    ltp_col = "close"

    # Check if these columns exist
    if date_col not in df.columns or ltp_col not in df.columns:
        st.error(f"❌ '{date_col}' or '{ltp_col}' columns not found. Please check your CSV.")
    else:
        # --- Data Processing Pipeline ---
        try:
            # 1. Convert Date column, specifying the exact format
            df[date_col] = pd.to_datetime(df[date_col], format='%d-%b-%Y', errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # 2. Clean and Convert LTP column
            # FIRST: Remove commas from the 'close' column
            df[ltp_col] = df[ltp_col].astype(str).str.replace(',', '', regex=False)
            # SECOND: Convert to numeric
            df[ltp_col] = pd.to_numeric(df[ltp_col], errors='coerce')
            df = df.dropna(subset=[ltp_col])

            # 3. Sort by date (oldest to newest for calculations)
            df = df.sort_values(by=date_col, ascending=True)
            
            st.success("✅ Data processed successfully!")

            # --- Descriptive Statistics ---
            st.write("### Descriptive Statistics for Close Price")
            st.write(df[[ltp_col]].describe())

            # --- Calculate Metrics ---
            # Ensure we have at least two rows to calculate pct_change
            if len(df) < 2:
                st.warning("Not enough data to calculate returns (need at least 2 data points).")
            else:
                df['returns'] = df[ltp_col].pct_change()
                df = df.dropna(subset=['returns']) # Drop first row with NaN return
            
                if df.empty:
                    st.warning("Could not calculate returns from the data.")
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
                    st.write(f"**{ltp_col.capitalize()} Price Over Time**")
                    
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