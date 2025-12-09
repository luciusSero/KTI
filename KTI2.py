import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Stock Data Viewer", layout="wide")
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; height: 20vh;">
<h1 style='text-align: center; color: white; margin: 0.;'>📈 Stock Data Viewer Sederhana Menggunakan YFinance</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar layout
st.sidebar.title('🔧 Masukkan kode saham')
ticker_symbol = st.sidebar.text_input('Masukkan Kode Saham').upper()

# Default dates set
default_start = datetime.now() - timedelta(days=100)
default_end = datetime.now()

start_date = st.sidebar.date_input('Tanggal Awal', value=default_start)
end_date = st.sidebar.date_input('Tanggal Akhir', value=default_end)

# Chart type selection
chart_type = st.sidebar.selectbox('Jenis Chart:', ['Candlestick', 'Line Chart', 'Area Chart'])

if st.sidebar.button('📊 Muat Data Stock'):
    try:
        # Fetch data
        with st.spinner(f'Mengambil data untuk {ticker_symbol}...'):
            ticker = yf.Ticker(ticker_symbol)
            stock_data = ticker.history(start=start_date, end=end_date)
            
        if stock_data.empty:
            st.error(f"❌ Tidak ada data untuk nama saham untuk {ticker_symbol}. Pastikan ticker symbol benar.")
        else:
            # Company info
            try:
                info = ticker.info
                company_name = info.get('longName', ticker_symbol)
                st.subheader(f"📊 {company_name} ({ticker_symbol})")
            except:
                st.subheader(f"📊 {ticker_symbol}")
            
            # Metrics
            if len(stock_data) > 0:
                current_price = stock_data['Close'].iloc[-1]
                prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
                daily_change = ((current_price - prev_price) / prev_price) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 Harga Saat Ini", f"${current_price:.2f}")
                
                with col2:
                    st.metric("📈 Perubahan Harian", f"{daily_change:.2f}%", 
                             delta=f"{daily_change:.2f}%")
                
                with col3:
                    high_52w = stock_data['High'].max()
                    st.metric("🔺 Period High", f"${high_52w:.2f}")
                
                with col4:
                    low_52w = stock_data['Low'].min()
                    st.metric("🔻 Period Low", f"${low_52w:.2f}")
            
            # Tabs
            price_tab, chart_tab, analysis_tab, raw_data_tab = st.tabs(['💹 Preview Harga', '📊 Grafik', '🔍 Analisa', '📋 Raw Data'])
            
            with price_tab:
                st.subheader("Data Harga Terbaru")
                # Show last 10 records with formatted columns
                recent_data = stock_data.tail(90).copy()
                for col in ['Open', 'High', 'Low', 'Close']:
                    recent_data[col] = recent_data[col].apply(lambda x: f"${x:.2f}")
                recent_data['Volume'] = recent_data['Volume'].apply(lambda x: f"{x:,}")
                st.dataframe(recent_data, use_container_width=True) 
            with chart_tab:
                st.subheader(f"📊 {chart_type} - {ticker_symbol}")
                
                if chart_type == 'Candlestick':
                    # Candlestick chart
                    fig = go.Figure(data=go.Candlestick(
                        x=stock_data.index,
                        open=stock_data['Open'],
                        high=stock_data['High'],
                        low=stock_data['Low'],
                        close=stock_data['Close'],
                        name=ticker_symbol
                    ))
                    
                    fig.update_layout(
                        title=f'{ticker_symbol} Candlestick Chart',
                        yaxis_title='Harga ($)',
                        xaxis_title='Tanggal',
                        template='plotly_white',
                        height=600
                    )
                    
                elif chart_type == 'Line Chart':
                    fig = px.line(
                        x=stock_data.index, 
                        y=stock_data['Close'], 
                        title=f'{ticker_symbol} Harga Penutup',
                        labels={'x': 'Tanggal', 'y': 'Harga ($)'}
                    )
                    fig.update_layout(height=600, template='plotly_white')
                    
                elif chart_type == 'Area Chart':
                    fig = px.area(
                        x=stock_data.index, 
                        y=stock_data['Close'], 
                        title=f'{ticker_symbol} Price Area Chart',
                        labels={'x': 'Tanggal', 'y': 'Harga ($)'},
                        color_discrete_sequence=["#037b66"]
                    )
                    fig.update_layout(height=600, template='plotly_white')
                
                st.plotly_chart(fig, use_container_width=True)

            with analysis_tab:
                st.subheader("🔍 Analisis Teknis")
                
                # Calculate moving averages
                stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
                stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
                
                # Price with moving averages
                fig_ma = go.Figure()
                
                fig_ma.add_trace(go.Scatter(
                    x=stock_data.index, 
                    y=stock_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='blue')
                ))
                
                fig_ma.add_trace(go.Scatter(
                    x=stock_data.index, 
                    y=stock_data['MA20'],
                    mode='lines',
                    name='MA 20',
                    line=dict(color='orange')
                ))
                
                fig_ma.add_trace(go.Scatter(
                    x=stock_data.index, 
                    y=stock_data['MA50'],
                    mode='lines',
                    name='MA 50',
                    line=dict(color='red')
                ))
                
                fig_ma.update_layout(
                    title=f'{ticker_symbol} Price with Moving Averages',
                    xaxis_title='Date',
                    yaxis_title='Price ($)',
                    template='plotly_white',
                    height=500
                )
                
                st.plotly_chart(fig_ma, use_container_width=True)
                
                # Statistics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Statistik Harga")
                    stats = {
                        'Rata-Rata Harga': f"${stock_data['Close'].mean():.2f}",
                        'Harga Tengah': f"${stock_data['Close'].median():.2f}",
                        'Standard Deviation': f"${stock_data['Close'].std():.2f}",
                        'Range Harga': f"${stock_data['Close'].max() - stock_data['Close'].min():.2f}"
                    }
                    
                    for key, value in stats.items():
                        st.write(f"**{key}:** {value}")
                
                with col2:
                    st.subheader("📊 Statistik Harga")
                    vol_stats = {
                        'Rata-Rata Volume': f"{stock_data['Volume'].mean():,.0f}",
                        'Max Volume': f"{stock_data['Volume'].max():,.0f}",
                        'Min Volume': f"{stock_data['Volume'].min():,.0f}",
                        'Total Volume': f"{stock_data['Volume'].sum():,.0f}"
                    }
                    
                    for key, value in vol_stats.items():
                        st.write(f"**{key}:** {value}")
            
            with raw_data_tab:
                st.subheader("📋 Complete Raw Data")
                st.dataframe(stock_data, use_container_width=True)
                
                # Download button
                csv = stock_data.to_csv()
                st.download_button(
                    label="💾 Download data sebagai file CSV",
                    data=csv,
                    file_name=f'{ticker_symbol}.csv',
                    mime='text/csv'
                )
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Tips: Pastikan ticker symbol benar dan koneksi internet stabil.")
