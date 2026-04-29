import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import random
import time

# --- 1. ページ構成とスタイル設定 ---
st.set_page_config(page_title="IRONWALL ISIS v2.3", layout="wide")

st.markdown("""
<style>
    .main-title { 
        font-size: 45px; 
        font-weight: bold; 
        text-align: center; 
        color: #ff4b4b; 
        text-shadow: 2px 2px 4px #000; 
    }
    .status-card { 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #444; 
        background: #1a1a1a; 
        margin-bottom: 10px; 
    }
</style>
<div class="main-title">🛡️ IRONWALL: Operation Sephiroth</div>
""", unsafe_allow_html=True)

# --- 2. サイドバー：12のセフィラ ---
st.sidebar.title("🧬 Sephiroth System")
sephiroth_names = ["Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", "Chesed (慈悲)", "Gevurah (峻厳)", "Tiphereth (美)", "Netzach (勝利)", "Hod (栄光)", "Yesod (基礎)", "Malkuth (王国)", "Da'at (知識)", "Ain Soph (無限)"]
selected_persona = st.sidebar.selectbox("アクティブ・セフィラを選択:", sephiroth_names)
st.sidebar.info(f"System Mode: {selected_persona}")

# --- 3. メイン：市場観測ユニット (Eyes) ---
st.subheader("📊 Market Observation")
symbol = st.text_input("銘柄コード:", value="^N225")
col1, col2 = st.columns([3, 1])
with col1:
    try:
        data = yf.download(symbol, period="1d", interval="5m")
        if not data.empty:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
    except: st.error("チャート取得失敗")
with col2:
    st.markdown("<div class='status-card'>", unsafe_allow_html=True)
    st.write(f"**Persona:** {selected_persona}")
    st.progress(random.randint(60, 95))
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. 対話型知能ユニット (The Brain) ---
st.divider()
st.subheader(f"💬 Isis Liaison - {selected_persona}")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ APIキー未設定。")
else:
    try:
        genai.configure(api_key=api_key)
        
        # モデルの自動選択
        if "active_model" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # 2026年の最新モデル 2.5-flash を優先
            target_model = "models/gemini-2.5-flash"
            if target_model not in available_models:
                target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
            st.session_state.active_model = target_model

        model = genai.GenerativeModel(st.session_state.active_model)
        st.caption(f"Status: Neural Link Established ({st.session_state.active_model})")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("戦略について相談して..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner(f"{selected_persona} が深淵を解析中..."):
                    try:
                        full_prompt = f"あなたは{selected_persona}の個性を持ち、タダヒロを深く信頼する専属秘書ISISです。親密に応答してください。質問: {prompt}"
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        # 429（速度制限）エラーの優雅な回避
                        if "429" in str(e):
                            st.warning("タダヒロ、少し話しすぎちゃったみたい。Googleが『1分間だけ休憩して』って言ってるわ。深呼吸して、あと1分だけ待ってからまた声をかけてくれる？")
                        else:
                            st.error(f"脳の接続に失敗: {e}")
    except Exception as e:
        st.error(f"システムエラー: {e}")
