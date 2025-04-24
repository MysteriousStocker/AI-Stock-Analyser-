
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from ta.trend import MACD
from ta.momentum import RSIIndicator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import datetime
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Stock Analyzer", layout="wide")

def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="max")
    return hist

def fetch_ipo_alerts():
    url = "https://www.moneycontrol.com/ipo/calendar.php"
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        table = soup.find("table")
        return table.text.strip() if table else "No IPO data found."
    except Exception as e:
        return f"Error fetching IPO data: {e}"

def generate_pdf_report(symbol, data, indicators, file_name="stock_report.pdf"):
    c = canvas.Canvas(file_name, pagesize=letter)
    c.drawString(100, 750, f"Stock Report for: {symbol}")
    c.drawString(100, 730, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 710, "Indicators Summary:")
    y = 690
    for k, v in indicators.items():
        c.drawString(100, y, f"{k}: {v}")
        y -= 20
    c.save()

st.title("AI Stock Market Analyzer")

symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)", "AAPL")

if st.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        data = fetch_stock_data(symbol)
        if data.empty:
            st.error("No data found for the symbol.")
        else:
            st.success("Data fetched successfully!")
            
            st.subheader("Price Chart")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close Price"))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Technical Indicators")
            macd = MACD(close=data["Close"]).macd()
            rsi = RSIIndicator(close=data["Close"]).rsi()
            st.line_chart(macd.rename("MACD"))
            st.line_chart(rsi.rename("RSI"))

            latest_macd = macd.iloc[-1]
            latest_rsi = rsi.iloc[-1]
            indicators = {"Latest MACD": round(latest_macd, 2), "Latest RSI": round(latest_rsi, 2)}
            st.write(indicators)

            if st.button("Generate PDF Report"):
                pdf_path = f"{symbol}_report.pdf"
                generate_pdf_report(symbol, data, indicators, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name=pdf_path)
                print(f"Report saved to {pdf_path}")

st.sidebar.title("IPO Alerts")
ipo_info = fetch_ipo_alerts()
st.sidebar.write(ipo_info)
