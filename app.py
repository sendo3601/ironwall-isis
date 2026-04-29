import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- 1. ページ構成 & リアルタイム更新設定 ---
st.set_page_config(page_title="IRONWALL TACTICAL", layout="wide")

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
        font-size: 35px;
        padding: 10px;
        border-bottom: 1px solid #ff00ff;
    }
    .cyber-card {
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid #00ffff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .chat-container { border-top: 1px solid #ff00ff; padding-top: 20px; margin-top: 30px; }
    </style>
    <div class="cyber-header">IRONWALL // TACTICAL COMMAND</div>
    """, unsafe_allow_html=True)

# --- 2. 状態管理 ---
if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {}
if "trade_log" not in st.session_state: st.session_state.trade_log = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 3. サイドバー：監視対象のドロップダウン ---
with st.sidebar:
    st.markdown("<h3 style='font-family:Orbitron; color:#ff00ff;'>STRATEGIC CONTROL</h3>", unsafe_allow_html=True)
    
    # セクター選択メニュー
    sector_options = {
        "日経平均 (Nikkei 225)": "^N225",
        "米国株 (S&P 500)": "^GSPC",
        "米国株 (NASDAQ)": "^IXIC",
        "世界株 (MSCI ACWI)": "ACWI",
        "FX (ドル円)": "USDJPY=X",
        "FX (ユーロドル)": "EURUSD=X",
        "金 (GOLD)": "GC=F",
        "ビットコイン (BTC)": "BTC-USD"
    }
    selected_label = st.selectbox("TARGET SECTOR:", list(sector_options.keys()))
    symbol = sector_options[selected_label]
    
    st.divider()
    
    # 使徒選択
    sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Gevurah (峻厳)"]
    selected_persona = st.selectbox("ACTIVE ENTITY:", sephiroth_names)
    
    st.metric("ASSETS", f"¥{st.session_state.balance:,}")
    auto_mode = st.toggle("AUTONOMOUS", value=True)
    
    if st.button("RESET ALL SYSTEM"):
        st.session_state.balance = 1000000
        st.session_state.trade_log = []
        st.session_state.chat_history = []
        st.session_state.positions = {}
        st.rerun()

# --- 4. リアルタイム・観測ユニット ---
try:
    data = yf.download(symbol, period="1d", interval="1m")
    if not data.empty:
        latest_row = data.iloc[-1]
        current_price = float(latest_row['Close'])
        ma20 = float(data['Close'].rolling(window=20).mean().iloc[-1])
        diff_rate = (current_price - ma20) / ma20 * 100

        # 自律ロジック
        signal = "SCANNING"; color = "#00ffff"
        if diff_rate < -0.12: signal = "ENTRY"; color = "#39ff14"
        elif diff_rate > 0.12: signal = "EXIT"; color = "#ff00ff"

        if auto_mode:
            if signal == "ENTRY" and symbol not in st.session_state.positions:
                st.session_state.positions[symbol] = {"price": current_price}
            elif signal == "EXIT" and symbol in st.session_state.positions:
                profit = (current_price - st.session_state.positions[symbol]["price"]) * 100
                st.session_state.balance += int(profit)
                st.session_state.trade_log.append({
                    "Time": datetime.now().strftime("%H:%M"),
                    "Target": selected_label,
                    "Profit": int(profit)
                })
                del st.session_state.positions[symbol]

        c1, c2 = st.columns([3, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                            increasing_line_color='#39ff14', decreasing_line_color='#ff00ff')])
            fig.update_layout(template="plotly_dark", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.write(f"TARGET: {selected_label}")
            st.metric("PRICE", f"{current_price:,.2f}")
            st.markdown(f"<h2 style='color:{color}; text-align:center; font-family:Orbitron;'>{signal}</h2>", unsafe_allow_html=True)
            st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')}")
            st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"PULSE ERROR: {e}")

# --- 5. イシスとの軍議 ---
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
st.markdown("<h3 style='font-family:Orbitron; color:#ff00ff;'>ISIS COMMUNICATION</h3>", unsafe_allow_html=True)

# 過去の会話を表示
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

# 新しい入力
if prompt := st.chat_input("指示を入力して、タダヒロ"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Geminiへの問い合わせ
    api_key = st.secrets.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            full_prompt = f"あなたは{selected_persona}の個性を持ち、タダヒロを信頼する秘書ISISです。現在の監視対象は{selected_label}です。親密に応答してください。質問: {prompt}"
            response = model.generate_content(full_prompt)
            res_text = response.text
        except: res_text = "通信が少し不安定ね。でも、あなたの指示は理解しているわ。"
    else:
        res_text = "APIキーが設定されていないみたい。でも私はここにいるわよ。"
    
    st.session_state.chat_history.append({"role": "assistant", "content": res_text})
    with st.chat_message("assistant"):
        st.write(res_text)
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. 自動リロード ---
import streamlit.components.v1 as components
components.html("<script>setTimeout(function(){window.parent.location.reload();}, 60000);</script>", height=0)
