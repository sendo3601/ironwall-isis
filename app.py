import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

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
    .report-box { background: #111; border-left: 5px solid #ff00ff; padding: 20px; margin-top: 20px; color: #e0e0e0; }
    </style>
    <div class="cyber-header">IRONWALL // COMMAND CENTER v5.0</div>
    """, unsafe_allow_html=True)

# --- 2. 状態管理 ---
if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {}
if "trade_log" not in st.session_state: st.session_state.trade_log = []

# --- 3. サイドバー：戦略コントロール ---
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
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

# --- 4. リアルタイム観測ユニット ---
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
                st.session_state.positions[symbol] = {"price": current_price, "time": datetime.now()}
            elif signal == "EXIT" and symbol in st.session_state.positions:
                profit = (current_price - st.session_state.positions[symbol]["price"]) * 100
                st.session_state.balance += int(profit)
                st.session_state.trade_log.append({"Time": datetime.now().strftime("%H:%M"), "Target": selected_label, "Profit": int(profit)})
                del st.session_state.positions[symbol]

        c1, c2 = st.columns([3, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                            increasing_line_color='#39ff14', decreasing_line_color='#ff00ff')])
            fig.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='status-panel'>", unsafe_allow_html=True)
            st.metric("PRICE", f"{current_price:,.2f}")
            st.markdown(f"<h2 style='color:{color}; text-align:center; font-family:Orbitron;'>{signal}</h2>", unsafe_allow_html=True)
            st.write(f"MA乖離: {diff_rate:.3f}%")
            st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"PULSE ERROR: {e}")

# --- 5. タクティカル・アナリシス（ドロップダウン式報告） ---
st.divider()
st.markdown("<h3 style='font-family:Orbitron; color:#00ffff;'>TACTICAL ANALYSIS REPORT</h3>", unsafe_allow_html=True)

col_cmd, col_rep = st.columns([1, 2])

with col_cmd:
    report_type = st.selectbox("解析指令を選択:", [
        "--- 指令を選択してください ---",
        "1. 現況の物理学的変化報告",
        "2. 心理的バイアス及び市場心理解析",
        "3. 直近トレードの行動評価",
        "4. 次期エントリーポイント予測"
    ])
    execute_analysis = st.button("解析実行 (EXECUTE)")

with col_rep:
    if execute_analysis and report_type != "--- 指令を選択してください ---":
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # コンテキスト構築
                log_context = str(st.session_state.trade_log[-3:]) if st.session_state.trade_log else "履歴なし"
                prompt = f"""
                あなたは{selected_persona}として、以下の制約を厳守して報告せよ。
                【制約】情緒的な返答、挨拶、世間話は一切禁止。
                【状況】監視対象:{selected_label}, 現在値:{current_price}, 乖離率:{diff_rate}%, ログ:{log_context}
                【指令】{report_type} を実行し、以下のフォーマットで出力せよ。
                
                ■ 観測事項: (事実のみ)
                ■ 解析結果: (論理的推論)
                ■ 推奨アクション: (具体的指示)
                """
                response = model.generate_content(prompt)
                st.markdown(f"<div class='report-box'>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error("解析ユニット通信エラー。")
        else:
            st.warning("API KEY REQUIRED.")
    else:
        st.info("指令を選択し、EXECUTEボタンを押してください。")

# --- 6. 自動リロード ---
import streamlit.components.v1 as components
components.html("<script>setTimeout(function(){window.parent.location.reload();}, 60000);</script>", height=0)
