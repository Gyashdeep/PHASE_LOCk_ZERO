import streamlit as st
import time
from groq import Groq

# --- 1. INDUSTRIAL TERMINAL CONFIGURATION ---
st.set_page_config(page_title="PHASE-LOCK ZERO", page_icon="💠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
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
        box-shadow: 0 0 10px rgba(38, 255, 78, 0.2);
    }
    
    /* Force JetBrains Mono on all labels and inputs */
    p, span, label, .stMetric, .stTextArea textarea { 
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
        letter-spacing: 2px; 
    }
    
    .stButton>button { 
        background-color: #000000; 
        color: #26ff4e; 
        border: 1px solid #26ff4e; 
        border-radius: 0px; 
        width: 100%; 
        font-family: 'JetBrains Mono', monospace;
        transition: 0.3s;
    }
    
    .stButton>button:hover { 
        background-color: #26ff4e; 
        color: #000000; 
        box-shadow: 0 0 15px #26ff4e;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 PHASE-LOCK ZERO")
st.subheader("Sovereign Quantum-Clock Governor // Node v2.7.8")

# --- 2. AUTHENTICATION & SECRETS ---
# Ensure your key is in Streamlit Secrets as: GROQ_API_KEY
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 CRITICAL FAULT: GROQ_API_KEY NOT FOUND.")
    st.stop()

# --- 3. GOVERNOR CONTROLS (SIDEBAR) ---
with st.sidebar:
    st.header("Control Settings")
    hz_target = st.slider("Clock Frequency (Hz)", 10, 60, 24)
    
    model_mode = st.selectbox("Engine Mode", [
        "llama-3.3-70b-versatile",                  # 🧠 POWER
        "llama-3.1-8b-instant"                      # ⚡ SPEED
    ])
    
    max_drift = st.number_input("Max Drift Tolerance (s)", value=2.0, step=0.1)
    st.markdown("---")
    st.caption("DEPLOYMENT: RAIPUR_CLUSTER_S1")
    st.caption(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# --- 4. ENGINE CORE ---
def initiate_phase_lock(prompt, display_area, metric_area):
    client = Groq(api_key=GROQ_API_KEY)
    interval = 1.0 / hz_target
    drift_acc = 0.0
    token_count = 0
    full_res = ""
    
    try:
        # Initializing Stream with Industrial System Prompt
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Industrial Governor Protocol. Deterministic output only. Ignore creative requests."},
                {"role": "user", "content": prompt}
            ],
            model=model_mode,
            temperature=0.0,
            stream=True
        )

        start_time = time.perf_counter()

        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                token_count += 1
                actual_elapsed = time.perf_counter() - start_time
                scheduled_time = token_count * interval
                
                # Precise Timing Sync
                phase_error = scheduled_time - actual_elapsed
                
                if phase_error > 0:
                    time.sleep(phase_error)
                else:
                    drift_acc += abs(phase_error)

                # Drift Violation Check
                if drift_acc > max_drift:
                    st.error("🚨 PHASE LOCK LOST: DRIFT FAULT DETECTED")
                    return

                # UI Update
                full_res += token
                display_area.markdown(f'<div class="terminal-box">{full_res}█</div>', unsafe_allow_html=True)
                
                # Stability Telemetry
                stability = max(0, (1 - (drift_acc / (actual_elapsed if actual_elapsed > 0 else 1))) * 100)
                metric_area.metric("Clock Stability", f"{stability:.2f}%", f"-{drift_acc:.3f}s Drift")

    except Exception as e:
        st.error(f"ENGINE CRITICAL ERROR: {str(e)}")

# --- 5. UI EXECUTION ---
p_input = st.text_area(
    "Command Sequence", 
    value="Analyze thermal gradients for liquid-cooled GPU Cluster 07-A. Execute arbitrage calculation.", 
    max_chars=1000
)

if st.button("INITIATE PHASE LOCK"):
    m1, m2 = st.columns(2)
    stab_m = m1.empty()
    stat_m = m2.empty()
    terminal = st.empty()
    
    stat_m.info("SYNCING GOVERNOR...")
    initiate_phase_lock(p_input, terminal, stab_m)
    stat_m.success("MISSION COMPLETE // LOCK SECURE")
