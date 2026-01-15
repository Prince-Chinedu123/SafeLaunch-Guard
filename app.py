import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load Environment
load_dotenv(override=True)
API_KEY = os.getenv("WEBACY_API_KEY", "").strip()

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️")

st.title("🛡️ SafeLaunch Guard")
st.subheader("Webacy-Powered Token Security Audit")

# Sidebar Status
if API_KEY:
    st.sidebar.success(f"Connection: Active ({API_KEY[:4]}***)")
else:
    st.sidebar.error("Connection: Offline (API Key Missing)")

# --- INPUTS ---
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
                    
                    # 1. DATA PROCESSING
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    # 2. RISK LABELING LOGIC (The "Verdict" System)
                    if rounded_risk <= 23:
                        verdict = "LOW RISK"
                        color = "green"
                    elif rounded_risk <= 50:
                        verdict = "MEDIUM RISK"
                        color = "orange"
                    else:
                        verdict = "HIGH RISK"
                        color = "red"

                    # 3. UI DISPLAY
                    st.markdown(f"### 📊 Security Assessment: :{color}[{verdict}]")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Safety Score", f"{safety_score}/100")
                    col2.metric("Overall Risk Score", f"{rounded_risk}")
                    
                    st.markdown("---")
                    
# FINDINGS DISPLAY (Improved for empty descriptions)
                    issues = data.get('issues', [])
                    if issues:
                        st.subheader("🚩 Risk Factors Detected")
                        for issue in issues:
                            # Use the issue title as the primary header
                            title = issue.get('title', 'Detected Risk Factor')
                            description = issue.get('description', 'Technical risk detected. See Webacy dashboard for deep-dive analysis.')
                            
                            with st.expander(f"⚠️ {title}"):
                                st.write(description)
                    else:
                        st.balloons()
                        st.success("SafeLaunch Verdict: No significant threats detected by Webacy.")
                
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    st.info("Check if the address and network match correctly.")
            
            except Exception as e:
                st.error(f"Connection Failed: {e}")

st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
