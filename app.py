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
    .report-box { background: #111; border-left: 5px solid #ff00ff; padding: 20px; margin-top: 20px; color: #e0e0e0; white-space: pre-wrap; }
    </style>
    <div class="cyber-header">IRONWALL // STRATEGIC CORE v5.3</div>
    """, unsafe_allow_html=True)

# --- 2. 状態管理 ---
if "balance" not in st.session_state: st.session_state.balance = 1000000
if "positions" not in st.session_state: st.session_state.positions = {}
if "trade_log" not in st.session_state: st.session_state.trade_log = []
if "current_data" not in st.session_state: 
    st.session_state.current_data = {"price": 0.0, "diff": 0.0, "symbol": ""}

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
    # 精鋭4使徒を固定
    sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Gevurah (峻厳)"]
    selected_persona = st.selectbox("ACTIVE ENTITY:", sephiroth_names)
    
    st.metric("TOTAL ASSETS", f"¥{st.session_state.balance:,}")
    auto_mode = st.toggle("AUTONOMOUS EXECUTION", value=True)
    
    if st.button("SYSTEM REBOOT"):
        st.session_state.clear()
        st.rerun()

# --- 4. リアルタイム観測ユニット（使徒別ロジック実装） ---
try:
    data = yf.download(symbol, period="1d", interval="1m")
    if not data.empty:
        latest_row = data.iloc[-1]
        c_price = float(latest_row['Close'])
        m20 = float(data['Close'].rolling(window=20).mean().iloc[-1])
        d_rate = (c_price - m20) / m20 * 100
        
        st.session_state.current_data = {"price": c_price, "diff": d_rate, "symbol": selected_label}

        sig = "SCANNING"; col = "#00ffff"; res = ""

        # --- 使徒別：物理学的判断アルゴリズム ---
        if selected_persona == "Kether (王冠)":
            # 王道：中庸を保つ。0.15%の乖離で反応
            if d_rate < -0.15: sig = "ENTRY"; res = "均衡への回帰（重力）"
            elif d_rate > 0.15: sig = "EXIT"; res = "過剰流動の収束"
        elif selected_persona == "Chokmah (知恵)":
            # 知恵（加速）：わずかな変化に敏感。0.08%で早期反応
            if d_rate < -0.08: sig = "ENTRY"; res = "微細な波動の増幅"
            elif d_rate > 0.08: sig = "EXIT"; res = "エネルギーの散逸"
        elif selected_persona == "Binah (理解)":
            # 理解（安定）：確実性を重視。0.25%まで待つ
            if d_rate < -0.25: sig = "ENTRY"; res = "臨界点到達の確認"
            elif d_rate > 0.25: sig = "EXIT"; res = "構造的飽和の検知"
        elif selected_persona == "Gevurah (峻厳)":
            # 峻厳（制裁）：激しい乖離のみを狙い、即座に利益を刈り取る。0.4%で反応
            if d_rate < -0.4: sig = "ENTRY"; res = "厳格な不均衡の是正"
            elif d_rate > 0.4: sig = "EXIT"; res = "秩序への強制復帰"

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
            fig.add_hline(y=m20, line_dash="dash", line_color="cyan")
            fig.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("<div class='status-panel'>", unsafe_allow_html=True)
            st.metric("PRICE", f"{c_price:,.2f}")
            st.markdown(f"<h2 style='color:{col}; text-align:center; font-family:Orbitron;'>{sig}</h2>", unsafe_allow_html=True)
            st.write(f"MA乖離: {d_rate:.3f}%")
            if res: st.caption(f"Reason: {res}")
            st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"PULSE ERROR: {e}")

# --- 5. タクティカル・アナリシス ---
st.divider()
st.markdown("<h3 style='font-family:Orbitron; color:#00ffff;'>TACTICAL ANALYSIS REPORT</h3>", unsafe_allow_html=True)
col_cmd, col_rep = st.columns([1, 2])
with col_cmd:
    report_type = st.selectbox("解析指令を選択:", [
        "--- 指令を選択してください ---",
        "1. 現況の物理学的変化報告",
        "2. 心理偏向と市場力学の相関",
        "3. 個別使徒の行動最適化評価",
        "4. 次期不均衡発生の確率予測"
    ])
    ready = st.session_state.current_data["price"] > 0
    execute_analysis = st.button("解析実行 (EXECUTE)", disabled=not ready)
with col_rep:
    if execute_analysis and report_type != "--- 指令を選択してください ---":
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                cur_p, cur_d, cur_s = st.session_state.current_data.values()
                
                # 安全なモデル取得
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_model_name = "models/gemini-1.5-flash"
                if target_model_name not in available_models: target_model_name = available_models[0]
                model = genai.GenerativeModel(target_model_name)
                
                log_context = str(st.session_state.trade_log[-3:]) if st.session_state.trade_log else "履歴なし"
                prompt = f"""
                あなたは{selected_persona}（使徒）として、タダヒロに報告せよ。
                【制約】情緒的な返答、挨拶、世間話は一切禁止。組織の観測ログとして出力せよ。
                【状況】ターゲット:{cur_s}, 現在値:{cur_p}, 乖離率:{cur_d}%, 直近ログ:{log_context}
                【指令】{report_type} を実行し、以下のフォーマットで出力せよ。
                
                ■ 観測事項: (物理的事実のみ)
                ■ 解析結果: (使徒の個性を反映した論理的推論)
                ■ 推奨アクション: (具体的な次期行動指針)
                """
                with st.spinner("ANALYSING QUANTUM WAVES..."):
                    response = model.generate_content(prompt)
                st.markdown(f"<div class='report-box'>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e: st.error(f"解析ユニットエラー: {str(e)}")
        else: st.warning("API KEY REQUIRED.")
    else: st.info("指令を選択し、EXECUTEを実行せよ。")

# --- 6. 自動リロード ---
import streamlit.components.v1 as components
components.html("<script>setTimeout(function(){window.parent.location.reload();}, 60000);</script>", height=0)
