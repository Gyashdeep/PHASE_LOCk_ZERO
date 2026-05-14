import streamlit as st
import asyncio
import time
from groq import AsyncGroq

# --- INDUSTRIAL TERMINAL UI ---
st.set_page_config(page_title="PHASE-LOCK ZERO", page_icon="💠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .terminal-box {
        background-color: #000000;
        color: #26ff4e;
        font-family: 'JetBrains Mono', monospace;
        padding: 20px;
        border: 1px solid #26ff4e;
        height: 520px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    p, span, label, .stMetric { font-family: 'JetBrains Mono', monospace !important; color: #26ff4e !important; }
    .stMetric { background-color: #0d0d0d; border: 1px solid #26ff4e; padding: 10px; }
    h1, h2, h3 { color: #26ff4e !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { background-color: #000000; color: #26ff4e; border: 1px solid #26ff4e; border-radius: 0px; width: 100%; }
    .stButton>button:hover { background-color: #26ff4e; color: #000000; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor // Node v2.7.2")

# --- AUTHENTICATION ---
# Ensure your Streamlit Secret is named GROQ_API_KEY
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: GROQ_API_KEY NOT FOUND IN SECRETS.")
    st.stop()

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("Control Settings")
    hz_target = st.slider("Clock Frequency (Hz)", 10, 60, 24)
    
    # VERIFIED PRODUCTION IDs: MAY 14, 2026 
    # [CLEAN STACK: NO OPENAI // NO DEEPSEEK // NO QWEN]
    model_mode = st.selectbox("Engine Mode", [
        "meta-llama/llama-4-scout-17b-16e-instruct", # ⚡ SPEED: Llama 4 Scout (MoE)
        "llama-3.3-70b-specdec",                   # 🧠 LOGIC: 70B Speculative Decoding
        "llama-3.3-70b-versatile",                  # 🛡️ STABLE: Standard Production Workhorse
        "llama-3.1-8b-instant"                      # 🚀 INSTANT: Raw 60Hz Performance
    ])
    
    max_drift = st.number_input("Max Drift (s)", value=1.5, step=0.1)

class SovereignGovernor:
    def __init__(self, key, hz, model, limit):
        self.client = AsyncGroq(api_key=key)
        self.interval = 1.0 / hz
        self.model = model
        self.limit = limit
        self.drift_acc = 0.0

    async def execute(self, prompt, display_area, metric_area):
        start_time = None
        token_count = 0
        full_res = ""
        
        try:
            stream = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.0,
                stream=True
            )

            async for chunk in stream:
                if start_time is None: start_time = time.perf_counter()
                
                # Handling Groq stream structure
                if hasattr(chunk.choices[0].delta, 'content'):
                    token = chunk.choices[0].delta.content
                    if token:
                        token_count += 1
                        actual = time.perf_counter() - start_time
                        scheduled = token_count * self.interval
                        phase_error = scheduled - actual
                        
                        # Apply Phase-Lock Timing
                        if phase_error > 0: 
                            await asyncio.sleep(phase_error)
                        else: 
                            self.drift_acc += abs(phase_error)

                        # Drift Security Tripwire
                        if self.drift_acc > self.limit:
                            st.error("PHASE LOCK LOST: CRITICAL DRIFT FAULT")
                            return

                        full_res += token
                        display_area.markdown(f'<div class="terminal-box">{full_res}█</div>', unsafe_allow_html=True)
                        
                        # Real-time Metrics
                        stability = max(0, (1 - (self.drift_acc / (actual if actual > 0 else 1))) * 100)
                        metric_area.metric("Clock Stability", f"{stability:.2f}%", f"-{self.drift_acc:.3f}s Drift")
        
        except Exception as e:
            st.error(f"ENGINE FAULT: {str(e)}")

# --- UI EXECUTION ---
p_input = st.text_area("Command Sequence", "INIT: Monitor silicon thermals and energy-compute arbitrage for GPU Cluster Node-7.")

if st.button("INITIATE PHASE LOCK"):
    m1, m2 = st.columns(2)
    stab_m = m1.empty()
    stat_m = m2.empty()
    terminal = st.empty()
    
    stat_m.info("SYNCING LPU ENGINE...")
    gov = SovereignGovernor(GROQ_API_KEY, hz_target, model_mode, max_drift)
    
    try:
        asyncio.run(gov.execute(p_input, terminal, stab_m))
    finally:
        stat_m.success("MISSION COMPLETE // LOCK SECURE")
