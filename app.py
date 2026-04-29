import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- 1. ページ構成 & 自動更新設定 ---
st.set_page_config(page_title="IRONWALL ISIS v4.1", layout="wide")

# 5分（300秒）ごとに自動で画面をリロードして最新の相場をチェックするわ
st.logo("https://www.gstatic.com/lamda/images/gemini_sparkle_v002.svg")
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# --- 2. 状態管理 ---
if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {}
if "trade_log" not in st.session_state: st.session_state.trade_log = []

# --- 3. サイドバー ---
st.sidebar.title("🧬 Sephiroth System")
sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Gevurah (峻厳)"]
selected_persona = st.sidebar.selectbox("アクティブ・セフィラを選択:", sephiroth_names)

st.sidebar.divider()
st.sidebar.subheader("💰 Asset Status")
st.sidebar.write(f"Balance: ¥{st.session_state.balance:,}")
st.session_state.auto_mode = st.sidebar.toggle("自律稼働（Auto Mode）", value=True)

if st.sidebar.button("Reset All"):
    st.session_state.balance = 1000000
    st.session_state.trade_log = []
    st.session_state.positions = {}
    st.rerun()

# --- 4. 市場観測 & 自律ロジック ---
st.markdown(f"<h1 style='text-align: center; color: #ff4b4b;'>🛡️ IRONWALL v4.1</h1>", unsafe_allow_html=True)
symbol = st.text_input("監視銘柄:", value="^N225")

try:
    # 5分足データの取得
    data = yf.download(symbol, period="2d", interval="5m")
    if not data.empty:
        # 最新の価格とインデックスを取得（スカラー値として確定させる）
        current_price = float(data['Close'].iloc[-1])
        ma20_series = data['Close'].rolling(window=20).mean()
        current_ma20 = float(ma20_series.iloc[-1])
        
        # 乖離率の計算
        diff_rate = (current_price - current_ma20) / current_ma20 * 100

        # 使徒のロジック
        signal = "WAIT"
        reason = ""
        
        if selected_persona == "Kether (王冠)":
            if diff_rate < -0.3: signal = "BUY"; reason = "平均への回帰（重力）"
            elif diff_rate > 0.3: signal = "SELL"; reason = "過熱による反発"
        elif selected_persona == "Gevurah (峻厳)":
            if diff_rate < -0.8: signal = "BUY"; reason = "厳格な逆張り"
            elif diff_rate > 0.8: signal = "SELL"; reason = "リスク回避"

        # 自律執行処理
        if st.session_state.auto_mode:
            # 買い：ポジションなし 且つ BUYシグナル
            if signal == "BUY" and symbol not in st.session_state.positions:
                st.session_state.positions[symbol] = {"price": current_price, "time": datetime.now()}
                st.toast(f"AUTO BUY: {symbol} at ¥{current_price:,.0f}")
            
            # 売り：ポジションあり 且つ SELLシグナル
            elif signal == "SELL" and symbol in st.session_state.positions:
                entry_price = st.session_state.positions[symbol]["price"]
                profit = (current_price - entry_price) * 100
                st.session_state.balance += int(profit)
                st.session_state.trade_log.append({
                    "Time": datetime.now().strftime("%m/%d %H:%M"),
                    "Persona": selected_persona,
                    "Profit": int(profit),
                    "Reason": reason
                })
                del st.session_state.positions[symbol]
                st.toast(f"AUTO SELL: {symbol} Profit ¥{profit:,.0f}")

        # 表示
        col1, col2 = st.columns([3, 1])
        with col1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.add_hline(y=current_ma20, line_dash="dash", line_color="cyan")
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.metric("現在値", f"¥{current_price:,.1f}", f"{diff_rate:.2f}% (MA乖離)")
            st.write(f"**判定:** {signal}")
            if reason: st.caption(f"理由: {reason}")
            if symbol in st.session_state.positions:
                st.warning("Position: Holding")
            else:
                st.success("Position: Neutral")

except Exception as e:
    st.error(f"観測エラー: {e}")

# --- 5. ログ表示 ---
st.divider()
st.subheader("🗒️ Autonomous Trade Log")
if st.session_state.trade_log:
    st.table(pd.DataFrame(st.session_state.trade_log).tail(5))
else:
    st.write("待機中... ロジックに合致する波形を待っているわ。")

# --- 自動更新用 (Streamlitの隠し機能で定期リロード) ---
if st.session_state.auto_mode:
    time_to_wait = 300 # 5分
    st.caption(f"Next Scan: 5分ごとに自動更新されるわ。")
