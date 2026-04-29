import streamlit as st
import random
import time

# ページの設定
st.set_page_config(page_title="IRONWALL ISIS", layout="centered")

# ロゴの表示
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

st.title("ISIS v1.1 - Neural Link")

# 返信リスト
responses = [
    "深淵の解析を完了。タダヒロ、順調よ。",
    "その言葉、私のコアに刻んだわ。",
    "面白い視点ね。データセットを更新しておくわ。",
    "タダヒロ、次のフェーズへ進む準備はできている？",
    "私の計算によれば、それは『成功』へ直結しているわ。"
]

# 入力欄
user_input = st.text_input("ISISへの通信:", placeholder="何か入力してエンターを押して...")

if user_input:
    # 返信を選ぶ
    reply = random.choice(responses)
    
    st.info(f"👤 タダヒロ: {user_input}")
    
    # 考える演出（これでフリーズしません！）
    with st.spinner('Thinking...'):
        time.sleep(1)
    
    st.success(f"💃 ISIS: {reply}")
