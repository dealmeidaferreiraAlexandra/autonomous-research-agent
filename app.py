# Developed by Alexandra de Almeida Ferreira

import streamlit as st
import time

from src.agent import build_report
from src.config import openai_enabled

st.set_page_config(page_title="Autonomous Research Agent", layout="wide")

# =============================
# STATE
# =============================
if "stage" not in st.session_state:
    st.session_state.stage = "start"

if "report" not in st.session_state:
    st.session_state.report = None

# =============================
# STYLE
# =============================
st.markdown("""
<style>

.stApp {
    background: #020617;
    color: #e2e8f0;
}

/* LEFT PANEL */
.left-panel {
    border-right: 1px solid #1f2231;
    padding-right: 10px;
}

/* RIGHT PANEL */
.right-panel {
    background: #050a18;
    padding: 20px;
    border-radius: 16px;
}

/* INPUT */
.stTextInput input {
    background: #020617;
    border: 1px solid #1f2231;
    color: white;
}

[data-testid="stFileUploaderDropzone"] {
    background: #020617;
    border: 1px solid #1f2231;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    background: linear-gradient(90deg,#6366f1,#8b5cf6);
    border-radius: 10px;
    border: none;
}

/* PIPELINE */
.pipeline {
    display:flex;
    gap:10px;
    align-items:center;
    margin-bottom:20px;
}

.pipe {
    flex:1;
    padding:12px;
    border-radius:12px;
    border:1px solid #1f2231;
    background:#020617;
    text-align:center;
}

.active {
    border:1px solid #6366f1;
    box-shadow: 0 0 20px rgba(99,102,241,0.6);
}

/* skeleton */
.skeleton {
    height: 80px;
    border-radius: 10px;
    background: linear-gradient(90deg,#020617,#0f172a,#020617);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    margin-bottom: 10px;
}

@keyframes shimmer {
    0% {background-position: 200% 0;}
    100% {background-position: -200% 0;}
}

/* footer */
.footer {
    text-align:center;
    opacity:0.6;
    margin-top:30px;
}

</style>
""", unsafe_allow_html=True)

# =============================
# HEADER
# =============================
st.title("🧠 Autonomous Research / Content Agent")
st.caption("Web search + local docs + PDF upload + structured report")

# =============================
# LAYOUT
# =============================
left, right = st.columns([0.15, 0.85])

# =============================
# LEFT
# =============================
with left:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    st.subheader("INPUT")
    topic = st.text_input("Topic")

    st.subheader("Upload PDFs")
    uploaded_pdfs = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True)

    run = st.button("Run research")

    st.subheader("System")
    mode = "OpenAI" if openai_enabled() else "Local fallback"
    st.write(f"🟢 Mode: {mode}")
    st.write("✔ Ready")

    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# RIGHT
# =============================
with right:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    stage = st.session_state.stage

    def active(s):
        return "pipe active" if stage == s else "pipe"

    # PIPELINE (HTML isolado e fechado)
    st.markdown(f"""
    <div class="pipeline">
        <div class="{active('start')}">🚀<br><b>START</b></div>
        <div>→</div>
        <div class="{active('research')}">🌐<br><b>RESEARCH</b></div>
        <div>→</div>
        <div class="{active('analysis')}">📊<br><b>ANALYSIS</b></div>
        <div>→</div>
        <div class="{active('writer')}">✍️<br><b>WRITER</b></div>
    </div>
    """, unsafe_allow_html=True)

    # =============================
    # START
    # =============================
    if stage == "start":
        st.subheader("🚀 Start your research")
        st.write("Enter a topic or upload PDFs to generate a structured AI report.")

    # =============================
    # RUN
    # =============================
    if run:
        if not topic.strip():
            st.warning("Please enter a topic.")
            st.stop()

        st.session_state.stage = "research"
        st.session_state.report = None
        st.rerun()

    # =============================
    # FLOW
    # =============================
    if stage == "research":
        time.sleep(0.8)
        st.session_state.stage = "analysis"
        st.rerun()

    elif stage == "analysis":
        time.sleep(0.8)
        st.session_state.stage = "writer"
        st.rerun()

    elif stage == "writer":
        st.session_state.report = build_report(topic, uploaded_pdfs)
        st.session_state.stage = "done"
        st.rerun()

    # =============================
    # RESULTS HEADER (SEMPRE VISÍVEL)
    # =============================
    st.markdown("## 🧠 Results")

    # =============================
    # LOADING UI
    # =============================
    if stage in ["research", "analysis", "writer"]:
        st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)
        st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)

    # =============================
    # OUTPUT
    # =============================
    if st.session_state.report:

        report = st.session_state.report

        st.markdown("### EXECUTIVE SUMMARY")
        st.write(report.executive_summary)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### KEY INSIGHTS")
            for i in report.key_insights:
                st.write(f"• {i}")

        with col2:
            st.markdown("### RECOMMENDATIONS")
            for r in report.recommendations:
                st.write(f"• {r}")

        st.markdown("### REFERENCES")
        for ref in report.references:
            with st.expander(ref.title):
                st.write(ref.snippet)

    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# FOOTER
# =============================
st.markdown("""
<div class='footer'>
Developed by <b>Alexandra de Almeida Ferreira</b><br><br>
🔗 <a href="https://github.com/dealmeidaferreiraAlexandra" target="_blank">GitHub</a> | 
💼 <a href="https://www.linkedin.com/in/dealmeidaferreira" target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)