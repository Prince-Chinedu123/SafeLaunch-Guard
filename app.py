import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load Environment
load_dotenv(override=True)
API_KEY = os.getenv("WEBACY_API_KEY", "").strip()

# Initialize session state for tracking usage
if 'audit_count' not in st.session_state:
    st.session_state.audit_count = 0

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️")

st.title("🛡️ SafeLaunch Guard")
st.subheader("Webacy-Powered Token Security Audit")

# --- SIDEBAR USAGE MONITOR ---
st.sidebar.title("📊 Project Stats")

# Calculate remaining
remaining = 2000 - st.session_state.audit_count

# Visual Feedback based on remaining credits
if remaining > 500:
    st.sidebar.success(f"Credits: {remaining} (Healthy)")
elif remaining > 100:
    st.sidebar.warning(f"Credits: {remaining} (Low)")
else:
    st.sidebar.error(f"Credits: {remaining} (CRITICAL - Refill Needed)")

# Progress Bar
progress_val = min(st.session_state.audit_count / 2000, 1.0)
st.sidebar.progress(progress_val)
st.sidebar.caption("Webacy Grant Usage Tracker")

# FIXED: Added a unique key to prevent the DuplicateElementId error
if st.sidebar.button("Reset Session Counter", key="sidebar_reset_btn"):
    st.session_state.audit_count = 0
    st.rerun() # Refresh the page to show the reset

# --- MAIN APP LOGIC ---
target_address = st.text_input("Contract Address:", placeholder="0x...")
chain_map = {
    "Base": "base",
    "Ethereum": "eth",
    "Solana": "sol",
    "BSC": "bsc",
    "Arbitrum": "arb",
    "Polygon": "pol"
}
chain_display = st.selectbox("Network:", list(chain_map.keys()))

if st.button("Run Security Audit"):
    if not target_address:
        st.error("Please enter a contract address.")
    else:
        with st.spinner("Analyzing Webacy Threat Intelligence..."):
            selected_chain = chain_map[chain_display]
            url = f"https://api.webacy.com/addresses/{target_address}"
            params = {"chain": selected_chain}
            headers = {"x-api-key": API_KEY, "accept": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Audit Complete")
                    
                    # Track successful audit
                    st.session_state.audit_count += 1
                    
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    if rounded_risk <= 23:
                        verdict = "LOW RISK"
                        color = "green"
                    elif rounded_risk <= 50:
                        verdict = "MEDIUM RISK"
                        color = "orange"
                    else:
                        verdict = "HIGH RISK"
                        color = "red"

                    st.markdown(f"### 📊 Security Assessment: :{color}[{verdict}]")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Safety Score", f"{safety_score}/100")
                    col2.metric("Overall Risk Score", f"{rounded_risk}")
                    
                    st.markdown("---")
                    
                    issues = data.get('issues', [])
                    if issues:
                        st.subheader("🚩 Risk Factors Detected")
                        for issue in issues:
                            title = issue.get('title', 'Security Detail')
                            desc = issue.get('description', 'Technical risk detected. See Webacy dashboard for deep-dive analysis.')
                            with st.expander(f"⚠️ {title}"):
                                st.write(desc)
                    else:
                        st.balloons()
                        st.success("SafeLaunch Verdict: No significant threats detected by Webacy.")
                
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            
            except Exception as e:
                st.error(f"Connection Failed: {e}")

st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
