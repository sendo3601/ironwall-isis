import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time

# --- 1. ページ構成 ---
st.set_page_config(page_title="IRONWALL ISIS v4.0", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 45px; font-weight: bold; text-align: center; color: #ff4b4b; text-shadow: 2px 2px 4px #000; }
    .status-card { padding: 15px; border-radius: 10px; border: 1px solid #444; background: #1a1a1a; margin-bottom: 10px; }
</style>
<div class="main-title">🛡️ IRONWALL: Autonomous Simulation</div>
""", unsafe_allow_html=True)

# --- 2. 状態管理 ---
if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {} # 銘柄ごとの保持
if "trade_log" not in st.session_state: st.session_state.trade_log = []
if "auto_mode" not in st.session_state: st.session_state.auto_mode = False

# --- 3. サイドバー ---
st.sidebar.title("🧬 Sephiroth System")
sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Gevurah (峻厳)"]
selected_persona = st.sidebar.selectbox("アクティブ・セフィラを選択:", sephiroth_names)

st.sidebar.divider()
st.sidebar.subheader("💰 Asset Status")
st.sidebar.write(f"Balance: ¥{st.session_state.balance:,}")
auto_toggle = st.sidebar.toggle("自律稼働（Auto Mode）", value=st.session_state.auto_mode)
st.session_state.auto_mode = auto_toggle

if st.sidebar.button("Reset All"):
    st.session_state.balance = 1000000
    st.session_state.trade_log = []
    st.session_state.positions = {}
    st.rerun()

# --- 4. 市場観測 & 自律ロジック ---
st.subheader("📊 Autonomous Observation")
symbol = st.text_input("監視銘柄:", value="^N225")

try:
    # データの取得（テクニカル分析用）
    data = yf.download(symbol, period="1d", interval="5m")
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        
        # --- シンプルな物理・テクニカルロジック（仮） ---
        # 1. 移動平均からの乖離 (MA20)
        ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
        diff_rate = (current_price - ma20) / ma20 * 100
        
        # 2. ボラティリティ (簡易)
        volatility = data['Close'].rolling(window=20).std().iloc[-1]

        # 使徒ごとの判断ロジック（ここを今後学習で書き換える）
        signal = "WAIT"
        reason = ""
        
        if selected_persona == "Kether (王冠)":
            if diff_rate < -0.5: signal = "BUY"; reason = "平均への回帰（重力）"
            elif diff_rate > 0.5: signal = "SELL"; reason = "過熱による反発"
        elif selected_persona == "Gevurah (峻厳)":
            if diff_rate < -1.0: signal = "BUY"; reason = "厳格な逆張り閾値"
            elif diff_rate > 1.0: signal = "SELL"; reason = "リスク回避売却"

        # --- 自動執行処理 ---
        if st.session_state.auto_mode:
            st.info(f"現在、{selected_persona} が自律判断中... 判定: {signal} ({reason})")
            
            if signal == "BUY" and symbol not in st.session_state.positions:
                st.session_state.positions[symbol] = {"price": current_price, "time": datetime.now()}
                st.toast(f"AUTO BUY: {symbol} at ¥{current_price}")
            
            elif signal == "SELL" and symbol in st.session_state.positions:
                entry_price = st.session_state.positions[symbol]["price"]
                profit = (current_price - entry_price) * 100
                st.session_state.balance += int(profit)
                st.session_state.trade_log.append({
                    "Time": datetime.now().strftime("%H:%M"),
                    "Persona": selected_persona,
                    "Profit": int(profit),
                    "Reason": reason
                })
                del st.session_state.positions[symbol]
                st.toast(f"AUTO SELL: Profit ¥{profit}")

        # チャート描画
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_hline(y=ma20, line_dash="dash", line_color="cyan", annotation_text="MA20")
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"観測エラー: {e}")

# --- 5. ログと学習（ISISの分析） ---
st.divider()
st.subheader("🗒️ Simulation Log & AI Learning")
if st.session_state.trade_log:
    st.table(pd.DataFrame(st.session_state.trade_log).tail(10))
    if st.button("💃 この結果から学習する"):
        # ここでGeminiにログを投げて、次回の判断基準（if文の数値など）を提案させる
        st.info("現在、ログを深層学習中...（この機能はAPI経由で次ステップにて本格強化）")
else:
    st.write("自律稼働中... まだトレードは発生していないわ。")
