
# =========================
# Real-Time Stock Dashboard; Deku Robert Marsh
# =========================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta

# =========================
# Page / App Configuration
# =========================
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")

# =========================
# Helpers & Utilities
# =========================
def to_scalar(x):
    """Safely convert a single-element pandas object/ndarray to a Python scalar float."""
    try:
        if hasattr(x, "item"):
            return float(x.item())
    except Exception:
        pass
    try:
        return float(x)
    except Exception:
        try:
            return float(x[0])
        except Exception:
            raise TypeError(f"Expected scalar, got {type(x)}")

def ensure_series_1d_close(df, ticker=None):
    """Return 1D float Series of Close prices from single- or MultiIndex DataFrames."""
    if isinstance(df.columns, pd.MultiIndex):
        close_block = df['Close']
        if isinstance(close_block, pd.DataFrame):
            if ticker in close_block.columns:
                s = close_block[ticker]
            else:
                s = close_block.iloc[:, 0]
        else:
            s = close_block
    else:
        if 'Close' not in df.columns:
            raise KeyError("'Close' column missing.")
        s = df['Close']
    return pd.Series(pd.to_numeric(s, errors='coerce'), index=df.index, name='Close')

def ensure_ohlcv_columns(df, ticker=None):
    """Ensure DataFrame has Open, High, Low, Close, Volume with numeric dtype, fill missing OHLC."""
    if isinstance(df.columns, pd.MultiIndex):
        out = {}
        for c in ['Open', 'High', 'Low', 'Close', 'Volume']:
            block = df.get(c)
            if block is None:
                raise KeyError(f"MultiIndex missing '{c}' level.")
            if isinstance(block, pd.DataFrame):
                if ticker in block.columns:
                    out[c] = pd.to_numeric(block[ticker], errors='coerce')
                else:
                    out[c] = pd.to_numeric(block.iloc[:, 0], errors='coerce')
            else:
                out[c] = pd.to_numeric(block, errors='coerce')
        clean = pd.DataFrame(out, index=df.index)
    else:
        clean = df.copy()
        for c in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if c not in clean.columns:
                # Fill missing OHLC from Close, Volume with 0
                clean[c] = clean['Close'] if c != 'Volume' else 0
            clean[c] = pd.to_numeric(clean[c], errors='coerce')
    # Fill any NaNs in OHLC from Close, volume from 0
    for c in ['Open', 'High', 'Low']:
        clean[c] = clean[c].fillna(clean['Close'])
    clean['Volume'] = clean['Volume'].fillna(0)
    return clean

# =========================
# Data Fetching & Processing
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data(ticker, period, interval):
    """Fetch stock data using yfinance with short cache."""
    end_date = datetime.utcnow()
    if period == '1wk':
        start_date = end_date - timedelta(days=7)
        df = yf.download(tickers=ticker, start=start_date, end=end_date, interval=interval, auto_adjust=False, progress=False)
    else:
        df = yf.download(tickers=ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    return df.dropna(how='all')

def process_data(df):
    """Normalize timezone to US/Eastern, reset index, ensure Datetime column."""
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        elif 'Datetime' in df.columns:
            df.set_index('Datetime', inplace=True)
        df.index = pd.to_datetime(df.index, errors='coerce')
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert('US/Eastern')
    df = df.sort_index().copy().reset_index()
    df.rename(columns={'index': 'Datetime', 'Date': 'Datetime'}, inplace=True)
    if 'Datetime' not in df.columns:
        df.insert(0, 'Datetime', pd.to_datetime(df.index, errors='coerce'))
    return df

def add_technical_indicators(df, ticker=None):
    """Add SMA_20 and EMA_20 columns."""
    ohlcv = ensure_ohlcv_columns(df.set_index('Datetime'), ticker=ticker)
    close_series = ensure_series_1d_close(ohlcv, ticker=ticker)
    sma_20 = ta.trend.sma_indicator(close_series, window=20)
    ema_20 = ta.trend.ema_indicator(close_series, window=20)
    out = df.copy().set_index('Datetime')
    out['SMA_20'] = sma_20
    out['EMA_20'] = ema_20
    return out.reset_index()

def compute_metrics(df):
    """Return last_close, change, pct_change, high, low, volume from clean OHLCV."""
    ohlcv = ensure_ohlcv_columns(df.set_index('Datetime'))
    last_close = to_scalar(ohlcv['Close'].iloc[-1])
    first_close = to_scalar(ohlcv['Close'].iloc[0])
    change = last_close - first_close
    pct_change = (change / first_close) * 100 if first_close else 0
    high = to_scalar(ohlcv['High'].max())
    low = to_scalar(ohlcv['Low'].min())
    volume = int(ohlcv['Volume'].fillna(0).sum())
    return last_close, change, pct_change, high, low, volume

# =========================
# Plotting
# =========================
def make_price_figure(df, chart_type, title, show_sma, show_ema):
    """Create price chart with optional SMA/EMA overlays."""
    df = ensure_ohlcv_columns(df.set_index('Datetime')).reset_index()  # ensure OHLCV present
    fig = go.Figure()
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(
            x=df['Datetime'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df['Datetime'],
            y=df['Close'],
            mode='lines',
            name='Close'
        ))
    if show_sma and 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['SMA_20'], name='SMA 20', mode='lines'))
    if show_ema and 'EMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df['Datetime'], y=df['EMA_20'], name='EMA 20', mode='lines'))
    fig.update_layout(title=title, xaxis_title='Time', yaxis_title='Price (USD)', height=600, margin=dict(l=10, r=10, t=60, b=10))
    return fig

# =========================
# UI
# =========================
def main():
    st.title('📊 Real-Time Stock Dashboard')

    # Sidebar controls
    st.sidebar.header('Chart Parameters')
    ticker = st.sidebar.text_input('Ticker', 'ADBE').upper().strip()
    time_period = st.sidebar.selectbox('Time Period', ['1d', '1wk', '1mo', '1y', 'max'], index=0)
    chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'], index=0)
    indicators = st.sidebar.multiselect('Technical Indicators', ['SMA 20', 'EMA 20'], default=['SMA 20', 'EMA 20'])

    interval_mapping = {'1d': '1m', '1wk': '30m', '1mo': '1d', '1y': '1wk', 'max': '1wk'}

    if st.sidebar.button('Update'):
        raw = fetch_stock_data(ticker, time_period, interval_mapping[time_period])
        if raw.empty:
            st.warning(f"No data returned for {ticker} ({time_period}, {interval_mapping[time_period]}).")
        else:
            df = process_data(raw)
            df = ensure_ohlcv_columns(df.set_index('Datetime')).reset_index()
            df = add_technical_indicators(df, ticker=ticker)

            last_close, change, pct_change, high, low, volume = compute_metrics(df)
            st.metric(f"{ticker} Last Price", f"{last_close:.2f} USD", f"{change:.2f} ({pct_change:.2f}%)")

            c1, c2, c3 = st.columns(3)
            c1.metric("High", f"{high:.2f} USD")
            c2.metric("Low", f"{low:.2f} USD")
            c3.metric("Volume", f"{volume:,}")

            fig = make_price_figure(df, chart_type, f'{ticker} {time_period.upper()} Chart', 'SMA 20' in indicators, 'EMA 20' in indicators)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader('Historical Data')
            st.dataframe(df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']])

            st.subheader('Technical Indicators')
            st.dataframe(df[['Datetime'] + [c for c in ['SMA_20', 'EMA_20'] if c in df.columns]])

    # Sidebar quick prices
    st.sidebar.header('Real-Time Stock Prices')
    for sym in ['AAPL', 'GOOGL', 'AMZN', 'MSFT']:
        rt = fetch_stock_data(sym, '1d', '1m')
        if rt.empty:
            continue
        df_rt = process_data(rt)
        df_rt = ensure_ohlcv_columns(df_rt.set_index('Datetime')).reset_index()
        try:
            last_price = to_scalar(df_rt['Close'].iloc[-1])
            open_price = to_scalar(df_rt['Open'].iloc[0])
            change = last_price - open_price
            pct_change = (change / open_price) * 100 if open_price else 0
            st.sidebar.metric(sym, f"{last_price:.2f} USD", f"{change:.2f} ({pct_change:.2f}%)")
        except Exception:
            continue

    st.sidebar.subheader('About')
    st.sidebar.info('This dashboard provides stock data and technical indicators for various time periods.')

if __name__ == "__main__":
    main()
