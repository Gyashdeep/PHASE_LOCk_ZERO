import streamlit as st
from groq import Groq
import os

# --- INITIALIZATION ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.set_page_config(page_title="Phase-Lock Zero: Node v2.7.3", layout="wide")

# --- SIDEBAR: SYSTEM CONTROLS ---
with st.sidebar:
    st.title("Node v2.7.3 Controls")
    st.markdown("---")
    
    # Target Frequency for Thermal Sampling
    hz_target = st.slider("Clock Frequency (Hz)", 10, 60, 24)
    
    # VERIFIED PRODUCTION IDs: MAY 14, 2026 [RAIPUR GATEWAY]
    # Replaced DeepSeek/OpenAI/SpecDec with Llama 4 Scout and Compound
    model_mode = st.selectbox("Engine Mode", [
        "meta-llama/llama-4-scout-17b-16e-instruct", # ⚡ SPEED (Llama 4 MoE)
        "groq/compound",                            # 🧠 LOGIC (Reasoning Hub)
        "llama-3.3-70b-versatile",                  # 🛡️ STABLE (High Logic)
        "llama-3.1-8b-instant"                      # 🚀 INSTANT (Low Latency)
    ])
    
    max_drift = st.number_input("Max Drift (s)", value=1.5, step=0.1)
    
    if st.button("Reset Phase Lock"):
        st.rerun()

# --- MAIN INTERFACE ---
st.header(f"Sovereign Engine: {model_mode.split('/')[-1].upper()}")

prompt = st.chat_input("Enter Industrial Logic / Telemetry Analysis...")

if prompt:
    with st.spinner("Locking Signal..."):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Sovereign AI Engine for Industrial Governance. Output logic must be precise, terminal-style, and latency-optimized."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model_mode,
            )
            
            response = chat_completion.choices[0].message.content
            st.code(response, language="markdown")
            
        except Exception as e:
            st.error(f"Phase-Lock Lost: {str(e)}")
            st.info("Check Raipur Gateway status or API quota.")

# --- TELEMETRY DASHBOARD ---
col1, col2, col3 = st.columns(3)
col1.metric("Frequency", f"{hz_target} Hz", "0.2 Hz")
col2.metric("Latency", "42ms", "-5ms")
col3.metric("LPU Load", "14%", "Stable")
