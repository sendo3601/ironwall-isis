import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- 1. ページ構成 & リアルタイム更新設定 ---
st.set_page_config(page_title="IRONWALL REALTIME", layout="wide")

# 【ここが肝！】60秒ごとにアプリを強制的に再実行させる設定よ
if "reload_count" not in st.session_state:
    st.session_state.reload_count = 0

# サイバー・デザイン CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #050505; color: #00ffff; font-family: 'Roboto Mono', monospace; }
    .cyber-header {
        font-family: 'Orbitron', sans-serif;
        color: #ff00ff;
        text-align: center;
        text-shadow: 0 0 10px #ff00ff;
        font-size: 40px;
        padding: 10px;
        border-bottom: 1px solid #ff00ff;
        margin-bottom: 20px;
    }
    .cyber-card {
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid #00ffff;
        padding: 15px;
        border-radius: 5px;
    }
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        text-shadow: 0 0 10px #39ff14;
        font-family: 'Orbitron', sans-serif;
        font-size: 30px !important;
    }
    </style>
    <div class="cyber-header">IRONWALL // REAL-TIME PULSE</div>
    """, unsafe_allow_html=True)

# --- 2. 状態管理 ---
if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {}
if "trade_log" not in st.session_state: st.session_state.trade_log = []

# --- 3. サイドバー ---
with st.sidebar:
    st.markdown("<h3 style='font-family:Orbitron;'>CONTROL</h3>", unsafe_allow_html=True)
    sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Gevurah (峻厳)"]
    selected_persona = st.selectbox("ENTITY:", sephiroth_names)
    st.metric("VIRTUAL ASSETS", f"¥{st.session_state.balance:,}")
    auto_mode = st.toggle("AUTONOMOUS", value=True)
    
    if st.button("SYSTEM RESET"):
        st.session_state.balance = 1000000
        st.session_state.trade_log = []
        st.session_state.positions = {}
        st.rerun()

# --- 4. 市場観測（リアルタイム・スキャン） ---
symbol = st.text_input("TARGET:", value="^N225")

try:
    # リアルタイム性を出すために、期間を短くして最新データを叩くわ
    data = yf.download(symbol, period="1d", interval="1m") # 1分足に変更
    
    if not data.empty:
        latest_row = data.iloc[-1]
        current_price = float(latest_row['Close'])
        ma20 = float(data['Close'].rolling(window=20).mean().iloc[-1])
        diff_rate = (current_price - ma20) / ma20 * 100

        # 自律ロジック
        signal = "SCANNING"
        color = "#00ffff"
        if diff_rate < -0.15: signal = "ENTRY"; color = "#39ff14"
        elif diff_rate > 0.15: signal = "EXIT"; color = "#ff00ff"

        if auto_mode:
            if signal == "ENTRY" and symbol not in st.session_state.positions:
                st.session_state.positions[symbol] = {"price": current_price}
                st.toast(f"SYSTEM ENGAGED: {symbol}")
            elif signal == "EXIT" and symbol in st.session_state.positions:
                profit = (current_price - st.session_state.positions[symbol]["price"]) * 100
                st.session_state.balance += int(profit)
                st.session_state.trade_log.append({"Time": datetime.now().strftime("%H:%M"), "Persona": selected_persona, "Profit": int(profit)})
                del st.session_state.positions[symbol]
                st.toast(f"MISSION COMPLETE: ¥{profit:,.0f}")

        # レイアウト
        c1, c2 = st.columns([3, 1])
        with c1:
            # リアルタイム・ローソク足チャート
            fig = go.Figure(data=[go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                increasing_line_color='#39ff14', decreasing_line_color='#ff00ff'
            )])
            fig.update_layout(
                template="plotly_dark", height=500,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis_rangeslider_visible=False,
                margin=dict(l=0,r=0,t=0,b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.metric("PRICE", f"¥{current_price:,.1f}")
            st.markdown(f"<h1 style='color:{color}; text-align:center; font-family:Orbitron; font-size:40px;'>{signal}</h1>", unsafe_allow_html=True)
            st.write(f"MA乖離: {diff_rate:.3f}%")
            st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"PULSE ERROR: {e}")

# --- 5. ミッションログ ---
st.divider()
if st.session_state.trade_log:
    st.dataframe(pd.DataFrame(st.session_state.trade_log).tail(5), use_container_width=True)

# --- 6. 自動リロード・スクリプト ---
# JavaScriptを使って60秒ごとにページをリロードさせるわ
import streamlit.components.v1 as components
components.html(
    """
    <script>
    window.parent.document.querySelector('section.main').scrollTo(0, 0);
    setTimeout(function(){
        window.parent.location.reload();
    }, 60000); // 60秒(60000ms)ごとに実行
    </script>
    """,
    height=0
)
