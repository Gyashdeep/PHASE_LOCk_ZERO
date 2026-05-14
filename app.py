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
        box-shadow: 0 0 10px #26ff4e44;
    }
    p, span, label, .stMetric { 
        font-family: 'JetBrains Mono', monospace !important; 
        color: #26ff4e !important; 
    }
    .stMetric { background-color: #0d0d0d; border: 1px solid #26ff4e; padding: 10px; }
    h1, h2, h3 { color: #26ff4e !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button {
        background-color: #000000; color: #26ff4e;
        border: 1px solid #26ff4e; border-radius: 0px; width: 100%;
    }
    .stButton>button:hover { background-color: #26ff4e; color: #000000; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor // Industrial Node")

# --- AUTHENTICATION ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: API_KEY NOT FOUND.")
    st.stop()

# --- SIDEBAR: MAY 2026 VERIFIED STACK ---
with st.sidebar:
    st.header("Control Settings")
    hz_target = st.slider("Clock Frequency (Hz)", 10, 60, 24)
    
    # Updated IDs with verified May 2026 availability
    model_mode = st.selectbox("Engine Model", [
        "meta-llama/llama-4-scout-17b-16e-instruct", # ⚡ ACTIVE: 750 TPS
        "openai/gpt-oss-120b",                       # 🧠 REASONING: 500 TPS
        "openai/gpt-oss-20b",                        # 🚀 SPEED: 1,000 TPS
        "llama-3.3-70b-versatile"                    # ✅ STABLE: 394 TPS
    ])
    
    max_drift = st.number_input("Max Drift (s)", value=1.5, step=0.1)
    st.caption("Deployment: USA-East-Edge-Control")

# --- ENGINE LOGIC ---
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
            # TRY PRIMARY ENGINE
            stream = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.0,
                stream=True
            )
        except Exception:
            # AUTO-HOTSWAP TO LLAMA 4 SCOUT IF PRIMARY FAILS
            st.warning("PRIMARY FAULT. HOT-SWAPPING TO Llama-4-Scout...")
            stream = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
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
                
                if phase_error > 0: await asyncio.sleep(phase_error)
                else: self.drift_acc += abs(phase_error)

                if self.drift_acc > self.limit:
                    st.error("PHASE LOCK LOST: EMERGENCY SHUTDOWN")
                    return

                full_res += token
                display_area.markdown(f'<div class="terminal-box">{full_res}█</div>', unsafe_allow_html=True)
                stability = max(0, (1 - (self.drift_acc / (actual if actual > 0 else 1))) * 100)
                metric_area.metric("Clock Stability", f"{stability:.2f}%", f"-{self.drift_acc:.3f}s Drift")

# --- UI EXECUTION ---
p_input = st.text_area("Command Sequence", "Monitor GPU cluster thermals. Predict compute-arbitrage for Node-USA-7.")

if st.button("INITIATE PHASE LOCK"):
    m1, m2 = st.columns(2)
    stab_m = m1.empty()
    stat_m = m2.empty()
    terminal = st.empty()
    
    stat_m.info("SYNCING LPU...")
    gov = SovereignGovernor(GROQ_API_KEY, hz_target, model_mode, max_drift)
    
    try:
        asyncio.run(gov.execute(p_input, terminal, stab_m))
    finally:
        stat_m.success("MISSION COMPLETE")
