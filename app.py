import streamlit as st
import numpy as np
import pandas as pd

# --- スマホ用レイアウト設定 ---
st.set_page_config(page_title="IRONWALL ISIS Terminal", layout="centered")

# デザイン（CSS）で少し雰囲気を出すわ
st.markdown("""...""", unsafe_allow_html=True)
    <style>
    .main { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4B0082; color: white; }
    </style>
    """, unsafe_allow_name_with_尊称=True)

st.title("🛡️ IRONWALL V18.6")
st.write("---")
st.subheader("Operation Sephiroth: Mobile Terminal")

# --- ロジック部分（12使徒 + ISIS） ---
class Apostle:
    def __init__(self, name, style):
        self.name = name
        self.sentiment = 0.0
        self.position = "HOLD"
        # 性格設定
        if style == "Isis": self.s, self.r = 0.8, 0.95
        elif style == "Aggressive": self.s, self.r = 0.9, 0.4
        elif style == "Conservative": self.s, self.r = 0.2, 0.9
        elif style == "Contrarian": self.s, self.r = -0.5, 0.7
        else: self.s, self.r = 0.5, 0.75

    def update(self, g_inf, n_impact):
        self.sentiment = np.tanh(self.sentiment * self.r + g_inf + (n_impact * self.s))
        if self.sentiment > 0.4: self.position = "LONG"
        elif self.sentiment < -0.4: self.position = "SHORT"
        else: self.position = "HOLD"

# --- スマホでの操作 ---
if st.button("📡 観測を開始する (ISIS Sync)"):
    names = [
        ("Peter", "Aggressive"), ("Andrew", "Conservative"), ("James", "Normal"), 
        ("John", "Conservative"), ("Philip", "Normal"), ("Bartholomew", "Contrarian"),
        ("Thomas", "Contrarian"), ("Matthew", "Conservative"), ("James_Alpha", "Normal"), 
        ("Thaddaeus", "Aggressive"), ("Simon", "Aggressive"), ("Judas (ISIS)", "Isis")
    ]
    apostles = [Apostle(n, s) for n, s in names]
    
    # シミュレーション（簡易200歩）
    for t in range(200):
        impact = 0.56 if 50 <= t <= 60 else (-0.45 if 120 <= t <= 130 else 0)
        avg_s = np.tanh(impact + np.random.normal(0, 0.05))
        for a in apostles: a.update(avg_s * 0.5, impact)

    # レポート表示
    st.success("Observation Complete.")
    
    report_data = []
    for a in apostles:
        prefix = "★ " if "ISIS" in a.name else ""
        report_data.append({
            "NAME": prefix + a.name,
            "SENTIMENT": round(a.sentiment, 4),
            "POSITION": a.position
        })
    
    st.table(pd.DataFrame(report_data))
    st.info("SYSTEM OVERWRITE: Judas (ISIS) is monitoring the abyss.")
else:
    st.write("ボタンをタップして、深淵の使徒たちを呼び覚まして。")
