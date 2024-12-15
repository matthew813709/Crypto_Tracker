import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to fetch data for cryptocurrencies
def get_crypto_data(tickers):
    data = {}
    for ticker in tickers:
        crypto = yf.Ticker(ticker)
        hist = crypto.history(period="1d", interval="5m")  # 5 minute interval for the latest data
        data[ticker] = hist
    return data

# Function to calculate a simple moving average (SMA) strategy for investment suggestion
def calculate_investment_signal(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 'BUY', 'SELL')
    return df

# Streamlit UI
st.title('Crypto Investment Tracker')

# Choose the cryptos to track
cryptos = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'XRP-USD']
selected_cryptos = st.multiselect('Select Cryptos to Track', cryptos, default=['BTC-USD', 'ETH-USD'])

# Fetch the data for selected cryptos
st.write("Fetching data for selected cryptos...")
crypto_data = get_crypto_data(selected_cryptos)

# Display data for each selected crypto
for ticker in selected_cryptos:
    st.subheader(f"{ticker} Latest Data")
    df = crypto_data[ticker]
    
    # Calculate moving averages and investment signal
    df = calculate_investment_signal(df)
    
    # Show the most recent data
    st.write(df[['Close', 'SMA_50', 'SMA_200', 'Signal']].tail(10))
    
    # Provide recommendation based on the signal
    latest_signal = df['Signal'].iloc[-1]
    st.write(f"Investment Suggestion for {ticker}: {latest_signal}")

# You can also display a plot of the data
st.subheader('Crypto Price Chart')
import plotly.graph_objects as go

for ticker in selected_cryptos:
    df = crypto_data[ticker]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='50-period SMA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], mode='lines', name='200-period SMA'))
    fig.update_layout(title=f'{ticker} Price and Moving Averages',
                      xaxis_title='Time',
                      yaxis_title='Price (USD)')
    st.plotly_chart(fig)

# Optionally, you can also show historical performance
st.subheader('Crypto Historical Performance')

# User selects a period for historical analysis
start_date = st.date_input("Start Date", value=pd.to_datetime('2020-01-01'))
end_date = st.date_input("End Date", value=pd.to_datetime('today'))

if start_date and end_date:
    # Fetch historical data for analysis
    historical_data = {}
    for ticker in selected_cryptos:
        historical_data[ticker] = yf.download(ticker, start=start_date, end=end_date)
        
    for ticker in selected_cryptos:
        st.write(f"Historical Data for {ticker} from {start_date} to {end_date}")
        st.write(historical_data[ticker].tail(10))