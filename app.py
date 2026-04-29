import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- 1. ページ構成 & サイバー・デザイン ---
st.set_page_config(page_title="IRONWALL COMMAND", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #050505; color: #00ffff; font-family: 'Roboto Mono', monospace; }
    .cyber-header {
        font-family: 'Orbitron', sans-serif; color: #ff00ff; text-align: center;
        text-shadow: 0 0 10px #ff00ff; font-size: 35px; padding: 10px; border-bottom: 2px solid #ff00ff; margin-bottom: 20px;
    }
    .status-panel { background: rgba(0, 255, 255, 0.05); border: 1px solid #00ffff; padding: 15px; border-radius: 5px; }
    .report-box { background: #111; border-left: 5px solid #ff00ff; padding: 20px; margin-top: 20px; color: #e0e0e0; white-space: pre-wrap; }
    </style>
    <div class="cyber-header">IRONWALL // STRATEGIC CORE v5.4</div>
    """, unsafe_allow_html=True)

# --- 2. 状態管理 & 自動更新 ---
# セッションを維持したまま60秒(60000ms)ごとにUIを再描画
st_autorefresh(interval=60000, key="datarefresh")

if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {}
if "trade_log" not in st.session_state: st.session_state.trade_log = []
if "current_data" not in st.session_state: 
    st.session_state.current_data = {"price": 0.0, "z_score": 0.0, "symbol": ""}

# --- 3. サイドバー ---
with st.sidebar:
    st.markdown("<h3 style='font-family:Orbitron; color:#ff00ff;'>STRATEGIC CONTROL</h3>", unsafe_allow_html=True)
    sector_options = {
        "日経平均": "^N225", "S&P 500": "^GSPC", "NASDAQ": "^IXIC",
        "世界株": "ACWI", "ドル円": "USDJPY=X", "GOLD": "GC=F", "BTC": "BTC-USD"
    }
    selected_label = st.selectbox("TARGET SECTOR:", list(sector_options.keys()))
    symbol = sector_options[selected_label]
    
    st.divider()
    sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Gevurah (峻厳)"]
    selected_persona = st.selectbox("ACTIVE ENTITY:", sephiroth_names)
    
    st.metric("TOTAL ASSETS", f"¥{st.session_state.balance:,}")
    auto_mode = st.toggle("AUTONOMOUS EXECUTION", value=True)
    
    if st.button("SYSTEM REBOOT"):
        st.session_state.clear()
        st.rerun()

# --- データ取得層（キャッシュによる保護） ---
@st.cache_data(ttl=60)
def fetch_market_data(ticker):
    return yf.download(ticker, period="1d", interval="1m", progress=False)

# --- 4. リアルタイム観測ユニット（使徒別ロジック実装） ---
try:
    data = fetch_market_data(symbol)
    
    if len(data) >= 20: # 20期間以上のデータが存在する場合のみ実行
        latest_row = data.iloc[-1]
        c_price = float(latest_row['Close'])
        
        # ボラティリティ（標準偏差）を用いた動的算出
        m20 = float(data['Close'].rolling(window=20).mean().iloc[-1])
        std20 = float(data['Close'].rolling(window=20).std().iloc[-1])
        
        # ゼロ除算回避のフェイルセーフ
        if std20 == 0 or pd.isna(std20):
            z_score = 0.0
        else:
            z_score = (c_price - m20) / std20
            
        st.session_state.current_data = {"price": c_price, "z_score": z_score, "symbol": selected_label}

        sig = "SCANNING"; col = "#00ffff"; res = ""

        # --- 使徒別：ボラティリティ適応型判断アルゴリズム ---
        if selected_persona == "Kether (王冠)":
            if z_score < -1.0: sig = "ENTRY"; res = "均衡への回帰（重力）"
            elif z_score > 1.0: sig = "EXIT"; res = "過剰流動の収束"
        elif selected_persona == "Chokmah (知恵)":
            if z_score < -0.5: sig = "ENTRY"; res = "微細な波動の増幅"
            elif z_score > 0.5: sig = "EXIT"; res = "エネルギーの散逸"
        elif selected_persona == "Binah (理解)":
            if z_score < -1.5: sig = "ENTRY"; res = "臨界点到達の確認"
            elif z_score > 1.5: sig = "EXIT"; res = "構造的飽和の検知"
        elif selected_persona == "Gevurah (峻厳)":
            if z_score < -2.0: sig = "ENTRY"; res = "厳格な不均衡の是正"
            elif z_score > 2.0: sig = "EXIT"; res = "秩序への強制復帰"

        if auto_mode:
            if sig == "ENTRY" and symbol not in st.session_state.positions:
                st.session_state.positions[symbol] = {"price": c_price, "time": datetime.now()}
            elif sig == "EXIT" and symbol in st.session_state.positions:
                pft = (c_price - st.session_state.positions[symbol]["price"]) * 100
                st.session_state.balance += int(pft)
                st.session_state.trade_log.append({
                    "Time": datetime.now().strftime("%H:%M"), 
                    "Persona": selected_persona, 
                    "Profit": int(pft),
                    "Reason": res
                })
                del st.session_state.positions[symbol]

        c1, c2 = st.columns([3, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                            increasing_line_color='#39ff14', decreasing_line_color='#ff00ff')])
            fig.add_hline(y=m20
