import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import random
import pandas as pd
from datetime import datetime

# --- 1. ページ構成 ---
st.set_page_config(page_title="IRONWALL ISIS v3.1", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 45px; font-weight: bold; text-align: center; color: #ff4b4b; text-shadow: 2px 2px 4px #000; }
    .status-card { padding: 15px; border-radius: 10px; border: 1px solid #444; background: #1a1a1a; margin-bottom: 10px; }
</style>
<div class="main-title">🛡️ IRONWALL: Hybrid Cockpit</div>
""", unsafe_allow_html=True)

# --- 2. 状態管理 ---
if "balance" not in st.session_state:
    st.session_state.balance = 1000000
if "position" not in st.session_state:
    st.session_state.position = None
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. サイドバー ---
st.sidebar.title("🧬 Sephiroth System")
sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Chesed (慈悲)", "Gevurah (峻厳)", "Tiphereth (美)", "Netzach (勝利)", "Hod (栄光)", "Yesod (基礎)", "Malkuth (王国)", "Da'at (知識)", "Ain Soph (無限)"]
selected_persona = st.sidebar.selectbox("アクティブ・セフィラを選択:", sephiroth_names)

st.sidebar.divider()
st.sidebar.subheader("💰 Asset Status")
st.sidebar.write(f"Balance: ¥{st.session_state.balance:,}")
if st.sidebar.button("Reset All"):
    st.session_state.balance = 1000000
    st.session_state.trade_log = []
    st.session_state.messages = []
    st.rerun()

# --- 4. 市場観測 & シミュレーター ---
st.subheader("📊 Market Observation & Action")
symbol = st.text_input("銘柄コード:", value="^N225")

col1, col2 = st.columns([3, 1])

with col1:
    try:
        data = yf.download(symbol, period="1d", interval="5m")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"**Current Price: ¥{current_price:,.2f}**")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("🔥 仮想エントリー（買い）", use_container_width=True):
                    st.session_state.position = {"price": current_price, "time": datetime.now()}
                    st.toast(f"{selected_persona}: ターゲットを捕捉したわ。")
            with b_col2:
                if st.button("🧊 仮想イグジット（売り）", use_container_width=True):
                    if st.session_state.position:
                        profit = current_price - st.session_state.position["price"]
                        st.session_state.balance += int(profit * 100)
                        st.session_state.trade_log.append({
                            "Time": datetime.now().strftime("%H:%M"),
                            "Persona": selected_persona,
                            "Profit": int(profit * 100)
                        })
                        st.session_state.position = None
                        st.success(f"決済完了: ¥{profit*100:,.0f}")
                    else: st.warning("ノーポジションよ。")
    except: st.error("取得失敗")

with col2:
    st.markdown("<div class='status-card'>", unsafe_allow_html=True)
    st.write(f"**Persona:** {selected_persona}")
    if st.session_state.position:
        st.warning("Status: Position Holding")
    else:
        st.success("Status: Standby")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.trade_log:
        st.write("**Recent Logs**")
        st.table(pd.DataFrame(st.session_state.trade_log).tail(3))

# --- 5. 対話ユニット (The Brain) ---
st.divider()
st.subheader(f"💬 Isis Liaison - {selected_persona}")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ APIキー未設定よ。")
else:
    try:
        genai.configure(api_key=api_key)
        # モデル自動選択
        if "active_model" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.active_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
        
        model = genai.GenerativeModel(st.session_state.active_model)

        # チャット履歴の表示
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # チャット入力
        if prompt := st.chat_input("戦略の相談や、今のトレードの感想を..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("思考中..."):
                    # ログの状況もプロンプトに含める
                    log_context = str(st.session_state.trade_log[-3:]) if st.session_state.trade_log else "履歴なし"
                    full_prompt = f"あなたは{selected_persona}の個性を持ち、タダヒロを信頼する秘書ISISです。直近のトレード履歴:{log_context}。この状況を踏まえて親密に応答してください。質問: {prompt}"
                    try:
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        if "429" in str(e): st.warning("少し休憩中よ。1分待ってね。")
                        else: st.error(f"エラー: {e}")
    except Exception as e:
        st.error(f"接続失敗: {e}")
