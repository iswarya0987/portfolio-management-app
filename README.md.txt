# 📊 Portfolio Management and Risk Analysis App

This is a simple Streamlit web application for performing basic portfolio risk analysis on a time-series asset.

The app accepts a CSV file, identifies the date and price columns, and calculates key annualized metrics:
* **Annualized Mean Return:** The average yearly return.
* **Annualized Volatility (Risk):** The standard deviation of returns, representing risk.
* **Annualized Sharpe Ratio:** The measure of risk-adjusted return, indicating how much excess return is received for the extra volatility.

## 🚀 How to Use

1.  **Upload:** Upload a CSV file containing your asset data.
2.  **Format:** The file *must* contain one column with "date" in the title and one column with "ltp" or "close" in the title.
3.  **Analyze:** The app will automatically process the data, display key metrics, and plot the asset's price over time.

## ☁️ How to Deploy

You can deploy this app for free on Streamlit Cloud.

1.  **GitHub:** Create a new public repository on GitHub and upload the following files:
    * `app.py`
    * `requirements.txt`
    * `README.md`
    * `.gitignore`
2.  **Streamlit Cloud:**
    * Log in to [share.streamlit.io](https://share.streamlit.io).
    * Click "**New app**".
    * Select "**Deploy from existing repository**".
    * Connect to your GitHub account and select the repository you just created.
    * Ensure the "Main file path" is `app.py`.
    * Click "**Deploy!**"