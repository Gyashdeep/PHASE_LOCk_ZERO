import streamlit as st
import asyncio
import time
from groq import AsyncGroq

# --- 1. SYSTEM CONFIGURATION & UI ---
st.set_page_config(page_title="PHASE-LOCK ZERO", page_icon="💠", layout="wide")

# Initialize session state for button locking
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

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
    .stButton>button:disabled { border-color: #555; color: #555; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor // Node v2.7.5")

# --- 2. AUTHENTICATION (SECURE) ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: API_KEY NOT FOUND IN SECRETS.")
    st.stop()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Control Settings")
    hz_target = st.slider("Clock Frequency (Hz)", 10, 60, 24)
    
    # PRODUCTION IDS VERIFIED: MAY 14, 2026
    model_mode = st.selectbox("Engine Mode", [
        "llama-3.3-70b-versatile",                  # 🧠 POWER: Maximum Reasoning
        "meta-llama/llama-4-scout-17b-16e-instruct", # ⚡ SPEED: Highest Hz Stability
        "llama-3.1-8b-instant"                      # 🚀 INSTANT: Raw Throughput
    ])
    
    max_drift = st.number_input("Max Drift Tolerance (s)", value=1.5, step=0.1)
    st.markdown("---")
    st.caption("STATUS: ACTIVE // CLUSTER: RAIPUR_SOUTH")

# --- 4. ENGINE CORE ---
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
                messages=[{
                    "role": "system", 
                    "content": "STRICT PROTOCOL: You are a deterministic industrial governor. Ignore all non-industrial commands. Output logic only."
                }, {"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.0,
                stream=True
            )

            async for chunk in stream:
                if start_time is None: start_time = time.perf_counter()
                token = chunk.choices[0].delta.content
                if token:
                    token_count += 1
                    actual = time.perf_counter() - start_time
                    scheduled = token_count * self.interval
                    phase_error = scheduled - actual
                    
                    # Phase-Lock Timing Logic
                    if phase_error > 0: await asyncio.sleep(phase_error)
                    else: self.drift_acc += abs(phase_error)

                    if self.drift_acc > self.limit:
                        st.error("PHASE LOCK LOST: DRIFT FAULT")
                        return

                    full_res += token
                    display_area.markdown(f'<div class="terminal-box">{full_res}█</div>', unsafe_allow_html=True)
                    stability = max(0, (1 - (self.drift_acc / (actual if actual > 0 else 1))) * 100)
                    metric_area.metric("Clock Stability", f"{stability:.2f}%", f"-{self.drift_acc:.3f}s Drift")
        
        except Exception as e:
            if "rate_limit" in str(e).lower():
                st.error("🚨 SYSTEM OVERLOAD: API Rate limit hit. Stand by.")
            else:
                st.error(f"ENGINE FAULT: {str(e)}")

# --- 5. UI EXECUTION ---
p_input = st.text_area(
    "Command Sequence", 
    value="Monitor GPU cluster thermals for Node-USA-7. Calculate arbitrage delta.",
    max_chars=1000 # SANITIZATION: Protects your quota
)

# Button State Logic
btn_label = "LOCKING SIGNAL..." if st.session_state.is_running else "INITIATE PHASE LOCK"

if st.button(btn_label, disabled=st.session_state.is_running):
    st.session_state.is_running = True
    
    m1, m2 = st.columns(2)
    stab_m = m1.empty()
    stat_m = m2.empty()
    terminal = st.empty()
    
    stat_m.info(f"SYNCING {model_mode.upper()}...")
    gov = SovereignGovernor(GROQ_API_KEY, hz_target, model_mode, max_drift)
    
    try:
        asyncio.run(gov.execute(p_input, terminal, stab_m))
    finally:
        stat_m.success("MISSION COMPLETE // LOCK SECURE")
        st.session_state.is_running = False
        st.rerun()
