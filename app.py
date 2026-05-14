import streamlit as st
import asyncio
import time
from groq import AsyncGroq

# --- UI CONFIGURATION ---
st.set_page_config(page_title="PHASE-LOCK ZERO", page_icon="⚡", layout="wide")

# Industrial Terminal CSS
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .terminal-box {
        background-color: #000000;
        color: #26ff4e;
        font-family: 'JetBrains Mono', monospace;
        padding: 20px;
        border-radius: 0px;
        border: 1px solid #26ff4e;
        height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    p, span, label, .stMetric { 
        font-family: 'JetBrains Mono', monospace !important; 
        color: #26ff4e !important; 
    }
    .stMetric {
        background-color: #000000;
        border: 1px solid #26ff4e;
        padding: 10px;
    }
    h1, h2, h3 { 
        color: #26ff4e !important; 
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button {
        background-color: #000000;
        color: #26ff4e;
        border: 1px solid #26ff4e;
        border-radius: 0px;
        width: 100%;
    }
    .stButton>button:hover { background-color: #26ff4e; color: #000000; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor")

# --- AUTHENTICATION ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: GROQ_API_KEY NOT FOUND.")
    st.stop()

# --- SIDEBAR: PRODUCTION REGISTRY ---
with st.sidebar:
    st.header("Industrial Settings")
    st.markdown("🌐 **STATUS:** `AUTHENTICATED`")
    hz_target = st.slider("Clock Frequency (Hz)", 5, 60, 20)
    
    # These are the CURRENT production-active IDs on Groq LPU
    model_mode = st.selectbox("Engine Mode", [
        "deepseek-r1",            # Unified Flagship Reasoning
        "llama-3.1-70b-versatile", # High-stability Production
        "llama-3.1-8b-instant"     # Low-latency Flash
    ])
    
    max_drift = st.number_input("Max Drift Threshold (s)", value=2.0)
    st.caption("Deployment Node: Raipur-Central-01")

# --- THE GOVERNOR ENGINE ---
class StreamlitPLL:
    def __init__(self, key, hz, model, drift_limit):
        self.client = AsyncGroq(api_key=key)
        self.interval = 1.0 / hz
        self.model = model
        self.limit = drift_limit
        self.drift_acc = 0.0

    async def run(self, prompt, display_area, metric_area):
        start_time = None
        token_count = 0
        full_response = ""
        
        try:
            stream = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.0,
                stream=True
            )

            async for chunk in stream:
                # Synchronize clock only when the first token arrives
                if start_time is None:
                    start_time = time.perf_counter()

                token = chunk.choices[0].delta.content
                if token:
                    token_count += 1
                    
                    actual = time.perf_counter() - start_time
                    scheduled = token_count * self.interval
                    phase_error = scheduled - actual
                    
                    if phase_error > 0:
                        await asyncio.sleep(phase_error)
                    else:
                        self.drift_acc += abs(phase_error)

                    if self.drift_acc > self.limit:
                        st.error("PHASE LOCK LOST: CRITICAL DRIFT")
                        return

                    full_response += token
                    display_area.markdown(f'<div class="terminal-box">{full_response}█</div>', unsafe_allow_html=True)
                    
                    stability = (1 - (self.drift_acc / (actual if actual > 0 else 1))) * 100
                    metric_area.metric("Clock Stability", f"{max(0, stability):.2f}%", f"-{self.drift_acc:.3f}s Drift")

        except Exception as e:
            st.error(f"LPU System Fault: {e}")

# --- MAIN INTERFACE ---
prompt_input = st.text_area("Instruction", "Generate real-time GPU thermal telemetry for Raipur cluster.")

if st.button("INITIATE PHASE LOCK"):
    m_col1, m_col2 = st.columns(2)
    stability_metric = m_col1.empty()
    status_metric = m_col2.empty()
    
    terminal_container = st.empty()
    status_metric.info("LOCK ACTIVE")
    
    governor = StreamlitPLL(GROQ_API_KEY, hz_target, model_mode, max_drift)
    
    try:
        asyncio.run(governor.run(prompt_input, terminal_container, stability_metric))
    finally:
        status_metric.success("LOCK TERMINATED")
