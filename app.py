
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(
    page_title="Stock Market Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Market Analysis Dashboard")
st.write("Explore historical stock prices, trading volume, and market trends.")

ticker = st.sidebar.text_input("Enter stock symbol", "AAPL").upper().strip()
period = st.sidebar.selectbox(
    "Select time period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

if st.sidebar.button("Analyze Stock"):
    if not ticker:
        st.error("Please enter a stock symbol.")
    else:
        with st.spinner("Downloading stock data..."):
            try:
                data = yf.download(
                    ticker,
                    period=period,
                    auto_adjust=True,
                    progress=False
                )

                if data.empty:
                    st.error("No data found. Check the stock symbol and try again.")
                else:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)

                    data = data.dropna()

                    st.subheader(f"{ticker} Stock Overview")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Latest Close", f"{data['Close'].iloc[-1]:.2f}")
                    col2.metric("Highest Price", f"{data['High'].max():.2f}")
                    col3.metric("Lowest Price", f"{data['Low'].min():.2f}")

                    data["Daily Return (%)"] = data["Close"].pct_change() * 100
                    data["20-Day Average"] = data["Close"].rolling(20).mean()
                    data["50-Day Average"] = data["Close"].rolling(50).mean()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data["Close"],
                        name="Closing Price"
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data["20-Day Average"],
                        name="20-Day Average"
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data["50-Day Average"],
                        name="50-Day Average"
                    ))

                    fig.update_layout(
                        title=f"{ticker} Closing Price and Moving Averages",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig, width="stretch")

                    st.subheader("Trading Volume")
                    volume_fig = go.Figure(go.Bar(
                        x=data.index, y=data["Volume"]
                    ))
                    volume_fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Volume"
                    )
                    st.plotly_chart(volume_fig, width="stretch")

                    st.subheader("Recent Stock Data")
                    st.dataframe(data.tail(10), width="stretch")

            except Exception as error:
                st.error(f"Unable to retrieve stock data: {error}")

st.caption("Educational analysis only. This dashboard is not financial advice.")
