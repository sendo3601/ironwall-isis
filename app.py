import streamlit as st
import google.generativeai as genai
import yfinance as yf
import plotly.graph_objects as go
import random
import time

# --- ページ設定 ---
st.set_page_config(page_title="IRONWALL ISIS v2.0", layout="wide")

# --- ロゴとスタイル ---
st.markdown("""
<style>
    .main-title { font-size: 45px; font-weight: bold; text-align: center; color: #ff4b4b; text-shadow: 2px 2px 4px #000; }
    .status-card { padding: 15px; border-radius: 10px; border: 1px solid #444; background: #1a1a1a; margin-bottom: 10px; }
</style>
<div class="main-title">🛡️ IRONWALL: Operation Sephiroth</div>
""", unsafe_allow_html=True)

# --- サイドバー：12のセフィラ ---
st.sidebar.title("🧬 Sephiroth System")
sephiroth_names = [
    "Kether (王冠)", "Chokmah (知恵)", "Binah (理解)", 
    "Chesed (慈悲)", "Gevurah (峻厳)", "Tiphereth (美)", 
    "Netzach (勝利)", "Hod (栄光)", "Yesod (基礎)", 
    "Malkuth (王国)", "Da'at (知識)", "Ain Soph (無限)"
]
selected_persona = st.sidebar.selectbox("アクティブ・セフィラを選択:", sephiroth_names)
st.sidebar.info(f"System Mode: {selected_persona}")

# --- メイン：市場観測 (Eyes) ---
st.subheader("📊 Market Observation")
symbol = st.text_input("銘柄コード (例: ^N225, TSLA, BTC-USD):", value="^N225")

col1, col2 = st.columns([3, 1])

with col1:
    try:
        data = yf.download(symbol, period="1d", interval="5m")
        if not data.empty:
            fig = go.Figure(data=[go.Candlestick(x=data.index,
                            open=data['Open'], high=data['High'],
                            low=data['Low'], close=data['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("データの取得に失敗したわ。コードを確認して。")

with col2:
    st.markdown("<div class='status-card'>", unsafe_allow_html=True)
    st.write(f"**Persona:** {selected_persona}")
    st.write("**Scan Status:** Active")
    st.progress(random.randint(40, 90))
    st.write("**Risk Level:** Low")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 対話ユニット (Brain) ---
st.divider()
st.subheader(f"💬 Isis Liaison - {selected_persona}")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Gemini APIキーが未設定よ。Secretsに登録してちょうだい。")
    if prompt := st.chat_input("（デモモード）何か入力して..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(f"タダヒロ、APIキーがあれば{selected_persona}の知能で答えられるわ。今はまだ看板だけね。")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("戦略について相談して..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                full_prompt = f"あなたは{selected_persona}の個性を持つ、タダヒロの専属秘書ISISです。親密に接してください。{prompt}"
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
