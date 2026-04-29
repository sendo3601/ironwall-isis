import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import random
import pandas as pd
from datetime import datetime

# --- 1. ページ構成 ---
st.set_page_config(page_title="IRONWALL ISIS v3.0", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 45px; font-weight: bold; text-align: center; color: #ff4b4b; text-shadow: 2px 2px 4px #000; }
    .status-card { padding: 15px; border-radius: 10px; border: 1px solid #444; background: #1a1a1a; margin-bottom: 10px; }
    .log-box { font-family: 'Courier New', Courier, monospace; font-size: 12px; }
</style>
<div class="main-title">🛡️ IRONWALL: Simulation Mode</div>
""", unsafe_allow_html=True)

# --- 2. 状態管理（仮想資産・ログ） ---
if "balance" not in st.session_state:
    st.session_state.balance = 1000000  # 初期資金100万円
if "position" not in st.session_state:
    st.session_state.position = None  # 現在のポジション
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []   # トレード履歴

# --- 3. サイドバー：使徒の選択と資産状況 ---
st.sidebar.title("🧬 Sephiroth System")
sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Chesed (慈悲)", "Gevurah (峻厳)", "Tiphereth (美)", "Netzach (勝利)", "Hod (栄光)", "Yesod (基礎)", "Malkuth (王国)", "Da'at (知識)", "Ain Soph (無限)"]
selected_persona = st.sidebar.selectbox("アクティブ・セフィラを選択:", sephiroth_names)

st.sidebar.divider()
st.sidebar.subheader("💰 Virtual Assets")
st.sidebar.write(f"Balance: ¥{st.session_state.balance:,}")
if st.sidebar.button("資産リセット"):
    st.session_state.balance = 1000000
    st.session_state.trade_log = []
    st.rerun()

# --- 4. 市場観測とシミュレーション操作 ---
st.subheader("📊 Market & Simulation")
symbol = st.text_input("銘柄コード:", value="^N225")

col1, col2 = st.columns([3, 1])

with col1:
    try:
        data = yf.download(symbol, period="1d", interval="5m")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # --- シミュレーション・操作ボタン ---
            st.markdown(f"**Current Price: ¥{current_price:,.2f}**")
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔥 仮想エントリー（買い）", use_container_width=True):
                    st.session_state.position = {"price": current_price, "time": datetime.now()}
                    st.toast(f"{selected_persona}: エントリーを確認。深淵へ潜るわよ。")
            with btn_col2:
                if st.button("🧊 仮想イグジット（売り）", use_container_width=True):
                    if st.session_state.position:
                        profit = current_price - st.session_state.position["price"]
                        st.session_state.balance += int(profit * 100) # 100単位取引と仮定
                        log_entry = {
                            "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Persona": selected_persona,
                            "Symbol": symbol,
                            "Profit": int(profit * 100)
                        }
                        st.session_state.trade_log.append(log_entry)
                        st.session_state.position = None
                        st.success(f"決済完了。損益: ¥{profit*100:,.0f}")
                    else:
                        st.warning("ポジションを持っていないわ。")
    except: st.error("チャート取得失敗")

with col2:
    st.markdown("<div class='status-card'>", unsafe_allow_html=True)
    st.write(f"**Operator:** タダヒロ")
    st.write(f"**Persona:** {selected_persona}")
    if st.session_state.position:
        st.warning("Position: Holding")
    else:
        st.success("Position: Neutral")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. 学習ユニット：トレードログと解析 ---
st.divider()
st.subheader("📝 Strategic Simulation Log")
if st.session_state.trade_log:
    df_log = pd.DataFrame(st.session_state.trade_log)
    st.table(df_log)
    
    # 私（ISIS）による解析ボタン
    if st.button("💃 ISISにログを解析（学習）させる"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.info("APIキーを設定すれば、このログに基づいた戦略講評ができるわ。")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            log_str = df_log.to_string()
            prompt = f"以下のトレードログを、{selected_persona}の視点で物理学的に解析し、タダヒロへのアドバイスを生成して。{log_str}"
            try:
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
            except Exception as e:
                st.error(f"解析失敗: {e}")
else:
    st.write("まだログが溜まっていないわ。シミュレーションを開始して。")
