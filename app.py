import streamlit as st
import asyncio
import time
from groq import AsyncGroq

# --- UI CONFIGURATION ---
st.set_page_config(page_title="PHASE-LOCK ZERO", page_icon="⚡", layout="wide")

# Custom CSS for the Cyberpunk Terminal Aesthetic
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .terminal-box {
        background-color: #000000;
        color: #26ff4e;
        font-family: 'JetBrains Mono', monospace;
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #26ff4e;
        height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
        box-shadow: 0 0 15px #26ff4e33;
    }
    p, span, label, .stMetric { 
        font-family: 'JetBrains Mono', monospace !important; 
        color: #26ff4e !important; 
    }
    .stMetric {
        background-color: #0e1117;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #26ff4e;
    }
    h1, h2, h3 { color: #26ff4e !important; text-shadow: 0 0 10px #26ff4e; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor | DeepSeek-V4")

# --- AUTHENTICATION GATE ---
# Pulling key automatically from .streamlit/secrets.toml
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: GROQ_API_KEY NOT FOUND IN SECRETS.")
    st.stop()

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("Industrial Settings")
    st.markdown("🌐 **STATUS:** `AUTHENTICATED`")
    hz_target = st.slider("Clock Frequency (Hz)", 5, 30, 15)
    model_mode = st.selectbox("Engine Mode", ["deepseek-v4-flash", "deepseek-v4-pro"])
    max_drift = st.number_input("Max Drift Threshold (s)", value=0.6)

# --- THE GOVERNOR ENGINE ---
class StreamlitPLL:
    def __init__(self, key, hz, model, drift_limit):
        self.client = AsyncGroq(api_key=key)
        self.interval = 1.0 / hz
        self.model = model
        self.limit = drift_limit
        self.drift_acc = 0.0

    async def run(self, prompt, display_area, metric_area):
        start_time = time.perf_counter()
        token_count = 0
        full_response = ""
        
        try:
            stream = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.0,
                stream=True,
                extra_body={"thinking": False}
            )

            async for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    token_count += 1
                    
                    # --- PLL CLOCK LOGIC ---
                    actual = time.perf_counter() - start_time
                    scheduled = token_count * self.interval
                    phase_error = scheduled - actual
                    
                    if phase_error > 0:
                        await asyncio.sleep(phase_error)
                    else:
                        self.drift_acc += abs(phase_error)

                    # --- SAFETY GATE ---
                    if self.drift_acc > self.limit:
                        st.error("PHASE LOCK LOST: EMERGENCY SHUTDOWN")
                        return

                    # --- UI UPDATE ---
                    full_response += token
                    display_area.markdown(f'<div class="terminal-box">{full_response}█</div>', unsafe_allow_html=True)
                    
                    # Update Metrics in real-time
                    stability = (1 - (self.drift_acc / (actual if actual > 0 else 1))) * 100
                    metric_area.metric("Clock Stability", f"{stability:.2f}%", f"-{self.drift_acc:.3f}s Drift")

        except Exception as e:
            st.error(f"System Fault: {e}")

# --- MAIN INTERFACE ---
prompt_input = st.text_area("Industrial Instruction", "Generate 50 thermal fan speed float values (0.0 - 1.0) for the Raipur GPU Cluster.")

if st.button("INITIATE PHASE LOCK"):
    # Create UI containers
    m_col1, m_col2 = st.columns(2)
    stability_metric = m_col1.empty()
    status_metric = m_col2.empty()
    
    terminal_container = st.empty()
    
    status_metric.info("LOCK ACTIVE")
    
    # Initialize Governor using the secret key
    governor = StreamlitPLL(GROQ_API_KEY, hz_target, model_mode, max_drift)
    
    # Execution
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(governor.run(prompt_input, terminal_container, stability_metric))
    finally:
        loop.close()
    
    status_metric.success("MISSION COMPLETE")
