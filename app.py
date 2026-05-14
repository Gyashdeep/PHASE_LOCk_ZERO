import streamlit as st
import asyncio
import time
from groq import AsyncGroq

# --- UI CONFIGURATION (CYBERPUNK INDUSTRIAL) ---
st.set_page_config(page_title="PHASE-LOCK ZERO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .terminal-box {
        background-color: #000000;
        color: #26ff4e;
        font-family: 'JetBrains Mono', monospace;
        padding: 20px;
        border: 1px solid #26ff4e;
        height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
        box-shadow: 0 0 15px rgba(38, 255, 78, 0.2);
    }
    p, span, label, .stMetric { 
        font-family: 'JetBrains Mono', monospace !important; 
        color: #26ff4e !important; 
    }
    .stMetric {
        background-color: #0d0d0d;
        border: 1px solid #26ff4e;
        padding: 10px;
    }
    h1, h2, h3 { 
        color: #26ff4e !important; 
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    .stButton>button {
        background-color: #000000;
        color: #26ff4e;
        border: 1px solid #26ff4e;
        border-radius: 0px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #26ff4e;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor // May 2026 Build")

# --- AUTHENTICATION ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: GROQ_API_KEY MISSING.")
    st.stop()

# --- INDUSTRIAL SIDEBAR ---
with st.sidebar:
    st.header("Engine Control")
    st.markdown("🌐 **NODE:** `USA-EAST-EDGE` status: `GO` ")
    
    hz_target = st.slider("Clock Frequency (Hz)", 10, 60, 30)
    
    # MAY 2026 EXTREME SPEED MODEL STACK
    model_mode = st.selectbox("Engine Model", [
        "openai/gpt-oss-20b",           # 1,000 TPS | ULTRA-FAST REASONING
        "meta-llama/llama-4-scout-17b-16e-instruct", # 750 TPS | AGENTIC ROUTING
        "openai/gpt-oss-120b",          # 500 TPS | MAXIMUM LOGIC DEPTH
        "llama-3.3-70b-versatile"       # 394 TPS | INDUSTRIAL STABILITY
    ])
    
    max_drift = st.number_input("Max Drift Tolerance (s)", value=1.5, step=0.1)
    st.divider()
    st.caption("v2.6.4 // Sovereign Engine Abstraction")

# --- CORE PLL GOVERNOR CLASS ---
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
                temperature=0.2,
                stream=True
            )

            async for chunk in stream:
                if start_time is None:
                    start_time = time.perf_counter()

                token = chunk.choices[0].delta.content
                if token:
                    token_count += 1
                    
                    # --- PLL CLOCK SYNC ---
                    actual = time.perf_counter() - start_time
                    scheduled = token_count * self.interval
                    phase_error = scheduled - actual
                    
                    if phase_error > 0:
                        await asyncio.sleep(phase_error)
                    else:
                        self.drift_acc += abs(phase_error)

                    if self.drift_acc > self.limit:
                        st.error("PHASE LOCK LOST: DRIFT THRESHOLD EXCEEDED")
                        return

                    # --- UI RENDER ---
                    full_response += token
                    display_area.markdown(f'<div class="terminal-box">{full_response}█</div>', unsafe_allow_html=True)
                    
                    # Compute Stability %
                    stability = max(0, (1 - (self.drift_acc / (actual if actual > 0 else 1))) * 100)
                    metric_area.metric("Clock Stability", f"{stability:.2f}%", f"-{self.drift_acc:.3f}s Drift")

        except Exception as e:
            st.error(f"ENGINE FAULT: {str(e)}")

# --- MAIN EXECUTION INTERFACE ---
prompt_input = st.text_area("Control Sequence", "Execute thermal governance logic for GPU Cluster Node-7. Log compute-arbitrage delta.")

if st.button("INITIATE MISSION"):
    m_col1, m_col2 = st.columns(2)
    stability_metric = m_col1.empty()
    status_metric = m_col2.empty()
    
    terminal_container = st.empty()
    status_metric.info("LPU SYNCHRONIZING...")
    
    governor = StreamlitPLL(GROQ_API_KEY, hz_target, model_mode, max_drift)
    
    try:
        asyncio.run(governor.run(prompt_input, terminal_container, stability_metric))
    finally:
        status_metric.success("LOCK SECURE // MISSION COMPLETE")
