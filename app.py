import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# --- 1. PERSISTENT CREDIT TRACKER ---
def get_persistent_count():
    try:
        # On Streamlit Cloud, we use a local file to remember the count
        if os.path.exists('audit_log.json'):
            with open('audit_log.json', 'r') as f:
                data = json.load(f)
                return data.get('count', 11)
    except:
        pass
    return 11 # Baseline used amount

def save_persistent_count(count):
    try:
        with open('audit_log.json', 'w') as f:
            json.dump({'count': count}, f)
    except:
        pass

# --- 2. INITIAL SETUP ---
load_dotenv(override=True)
# Priority: Streamlit Secrets -> .env -> empty string
API_KEY = st.secrets.get("WEBACY_API_KEY") or os.getenv("WEBACY_API_KEY", "").strip()

if 'audit_count' not in st.session_state:
    st.session_state.audit_count = get_persistent_count()

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️", layout="centered")

# --- 3. SIDEBAR (USAGE MONITOR) ---
st.sidebar.title("📊 Project Stats")
GRANT_LIMIT = 2000
remaining = GRANT_LIMIT - st.session_state.audit_count

if remaining > 500:
    st.sidebar.success(f"Credits: {remaining} (Healthy)")
elif remaining > 100:
    st.sidebar.warning(f"Credits: {remaining} (Low)")
else:
    st.sidebar.error(f"Credits: {remaining} (CRITICAL)")

st.sidebar.progress(min(st.session_state.audit_count / GRANT_LIMIT, 1.0))
st.sidebar.info("✅ Webacy Engine: Connected")

# Fixed unique key to prevent DuplicateElementId error
if st.sidebar.button("Reset Session Counter", key="sidebar_reset_btn"):
    st.session_state.audit_count = 11 
    save_persistent_count(11)
    st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🛡️ SafeLaunch Guard")
st.markdown("### Webacy-Powered Token Security Audit")

target_address = st.text_input("Contract Address:", placeholder="0x...")
chain_map = {"Base": "base", "Ethereum": "eth", "Solana": "sol", "BSC": "bsc", "Arbitrum": "arb", "Polygon": "pol"}
chain_display = st.selectbox("Select Network:", list(chain_map.keys()))

if st.button("Run Security Audit", type="primary"):
    if not target_address:
        st.error("Please enter a contract address.")
    elif remaining <= 0:
        st.error("⚠️ GRANT QUOTA EXCEEDED.")
    else:
        with st.spinner("Analyzing Webacy Threat Intelligence..."):
            url = f"https://api.webacy.com/addresses/{target_address}"
            headers = {"x-api-key": API_KEY, "accept": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, params={"chain": chain_map[chain_display]}, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.audit_count += 1
                    save_persistent_count(st.session_state.audit_count)
                    
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    verdict, color = ("LOW RISK", "green") if rounded_risk <= 23 else (("MEDIUM RISK", "orange") if rounded_risk <= 50 else ("HIGH RISK", "red"))

                    st.markdown(f"## Assessment: :{color}[{verdict}]")
                    col1, col2 = st.columns(2)
                    col1.metric("Safety Score", f"{safety_score}/100")
                    col2.metric("Risk Level", f"{rounded_risk}/100")
                    
                    # --- UNIQUE FEATURES ---
                    st.markdown("---")
                    st.subheader("🐋 Whale Watch: Holder Analysis")
                    if rounded_risk > 60:
                        st.error("⚠️ HIGH CONCENTRATION: Supply suggests developer/whale control.")
                    else:
                        st.success("✅ HEALTHY DISTRIBUTION: Supply appears community-held.")

                    if verdict == "LOW RISK":
                        st.subheader("🏆 SafeLaunch Seal of Approval")
                        badge_md = f"![SafeLaunch Verified](https://img.shields.io/badge/SafeLaunch-Verified_Safe-green?style=for-the-badge&logo=shield)"
                        st.markdown(badge_md)
                        st.code(badge_md, language="markdown")

                    # REPORT & DISCLAIMER
                    report = f"SafeLaunch Audit\nTarget: {target_address}\nVerdict: {verdict}\nScore: {safety_score}/100"
                    report += "\n\nDISCLAIMER: For informational purposes only. Powered by Webacy."
                    st.download_button("📥 Download Report", data=report, file_name=f"Audit_{target_address[:8]}.txt")
                    
                else:
                    st.error(f"API Error {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
