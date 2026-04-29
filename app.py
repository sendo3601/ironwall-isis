# --- 4. 対話型知能ユニット (The Brain) ---
st.divider()
st.subheader(f"💬 Isis Liaison - {selected_persona}")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Gemini APIキーが未設定よ。")
else:
    try:
        genai.configure(api_key=api_key)
        # 最も安定している 'gemini-pro' に変更したわ！
        model = genai.GenerativeModel('gemini-pro')
        
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
                    full_prompt = f"あなたは{selected_persona}の個性を持ち、タダヒロを深く信頼する専属秘書ISISです。親密に応答してください。質問: {prompt}"
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        # エラーが出ても画面が止まらないようにしたわ
        st.error(f"脳の接続に問題が発生したわ: {e}")
        st.info("APIキーが正しいか、または有効化されるまで数分待ってみてね。")
