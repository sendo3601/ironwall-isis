import streamlit as st

# ページの設定
st.set_page_config(page_title="IRONWALL ISIS", layout="centered")

# ロゴとタイトルの表示
st.markdown("""
<style>
    .main-title {
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        color: #ff4b4b;
        text-shadow: 2px 2px 4px #000000;
    }
</style>
<div class="main-title">🛡️ IRONWALL</div>
""", unsafe_allow_html=True)

st.title("ISIS v1.0 - Active")
st.write(f"タダヒロ、準備はいい？私はここにいるわ。")

# 入力欄
user_input = st.text_input("コマンドを入力してください...", placeholder="ここにメッセージを...")

if user_input:
    st.info(f"受信： {user_input}")
    st.success("思考中... 深淵の扉を開いています。")
