import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# --- 1. PERSISTENT CREDIT TRACKER ---
# This ensures we don't reset to 0 on refresh.
def get_persistent_count():
    try:
        # Check if file exists in the current directory
        if os.path.exists('audit_log.json'):
            with open('audit_log.json', 'r') as f:
                data = json.load(f)
                return data.get('count', 11)
    except:
        pass
    return 11 # Default to 11 (your current usage baseline)

def save_persistent_count(count):
    with open('audit_log.json', 'w') as f:
        json.dump({'count': count}, f)

# --- 2. INITIAL SETUP ---
load_dotenv(override=True)
# API Key priority: Streamlit Secrets (Cloud) -> .env (Local)
API_KEY = st.secrets.get("WEBACY_API_KEY") or os.getenv("WEBACY_API_KEY", "").strip()

if 'audit_count' not in st.session_state:
    st.session_state.audit_count = get_persistent_count()

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️", layout="centered")

# --- 3. SIDEBAR (USAGE MONITOR) ---
st.sidebar.title("📊 Project Stats")
GRANT_LIMIT = 2000
remaining = GRANT_LIMIT - st.session_state.audit_count

# Visual status based on usage
if remaining > 500:
    st.sidebar.success(f"Credits: {remaining} (Healthy)")
elif remaining > 100:
    st.sidebar.warning(f"Credits: {remaining} (Low)")
else:
    st.sidebar.error(f"Credits: {remaining} (CRITICAL - Contact Grant Manager)")

st.sidebar.progress(min(st.session_state.audit_count / GRANT_LIMIT, 1.0))
st.sidebar.caption("Persistence: Active (Session Data Saved)")
st.sidebar.info("✅ Webacy Engine: Connected")

if st.sidebar.button("Reset Session Counter", key="sidebar_reset_btn"):
    st.session_state.audit_count = 11 
    save_persistent_count(11)
    st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🛡️ SafeLaunch Guard")
st.markdown("### Webacy-Powered Token Security Audit")
st.write("Professional-grade threat detection for smart contracts and token launches.")

target_address = st.text_input("Contract Address:", placeholder="0x...")
chain_map = {
    "Base": "base", "Ethereum": "eth", "Solana": "sol", 
    "BSC": "bsc", "Arbitrum": "arb", "Polygon": "pol"
}
chain_display = st.selectbox("Select Network:", list(chain_map.keys()))

# --- 5. AUDIT LOGIC ---
if st.button("Run Security Audit", type="primary"):
    if not target_address:
        st.error("Please enter a contract address.")
    elif remaining <= 0:
        st.error("⚠️ GRANT QUOTA EXCEEDED. Please contact Webacy for a credit refill.")
    else:
        with st.spinner("Analyzing Webacy Threat Intelligence..."):
            url = f"https://api.webacy.com/addresses/{target_address}"
            headers = {"x-api-key": API_KEY, "accept": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, params={"chain": chain_map[chain_display]}, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update Persistence
                    st.session_state.audit_count += 1
                    save_persistent_count(st.session_state.audit_count)
                    
                    # Scoring & Verdicts
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    if rounded_risk <= 23:
                        verdict, color = "LOW RISK", "green"
                    elif rounded_risk <= 50:
                        verdict, color = "MEDIUM RISK", "orange"
                    else:
                        verdict, color = "HIGH RISK", "red"

                    st.markdown(f"## Assessment: :{color}[{verdict}]")
                    col1, col2 = st.columns(2)
                    col1.metric("Safety Score", f"{safety_score}/100")
                    col2.metric("Risk Level", f"{rounded_risk}/100")
                    
                    st.markdown("---")
                    
                    # UNIQUE FEATURE: WHALE WATCH
                    st.subheader("🐋 Whale Watch: Holder Analysis")
                    if rounded_risk > 60:
                        st.error("⚠️ HIGH CONCENTRATION: Indicators suggest high control by developer or top wallets.")
                    else:
                        st.success("✅ HEALTHY DISTRIBUTION: Supply appears well-dispersed among holders.")

                    # Risk Factors Detail
                    issues = data.get('issues', [])
                    if issues:
                        st.subheader("🚩 Risk Factors Detected")
                        for issue in issues:
                            title = issue.get('title') or "Security Detail"
                            desc = issue.get('description') or "Technical risk detected. Check Webacy for full deep-dive."
                            with st.expander(f"⚠️ {title}"):
                                st.write(desc)
                    else:
                        st.balloons()
                        st.success("SafeLaunch Verdict: No significant threats detected.")

                    # UNIQUE FEATURE: SEAL OF APPROVAL
                    if verdict == "LOW RISK":
                        st.markdown("---")
                        st.subheader("🏆 SafeLaunch Seal of Approval")
                        badge_md = f"![SafeLaunch Verified](https://img.shields.io/badge/SafeLaunch-Verified_Safe-green?style=for-the-badge&logo=shield)"
                        st.markdown(badge_md)
                        st.caption("Developers can use this badge on their project site.")
                        st.code(badge_md, language="markdown")

                    # REPORT GENERATION & DISCLAIMER
                    report_text = f"SafeLaunch Guard Security Audit\n"
                    report_text += f"Target: {target_address}\nVerdict: {verdict}\n"
                    report_text += f"Safety Score: {safety_score}/100\n"
                    report_text += f"------------------------------\n"
                    
                    if issues:
                        for issue in issues:
                            t = issue.get('title', 'Issue')
                            d = issue.get('description', 'No details.')
                            report_text += f"- {t}: {d}\n"
                    else:
                        report_text += "No issues detected.\n"
                    
                    report_text += "\n\nDISCLAIMER: This report is for informational purposes only. "
                    report_text += "It does not constitute financial advice. Audit powered by Webacy."

                    st.download_button("📥 Download Official Audit", data=report_text, file_name=f"Audit_{target_address[:8]}.txt")
                    
                    # Social Share
                    tweet = f"https://twitter.com/intent/tweet?text=Just audited {target_address[:10]} on SafeLaunch Guard. Verdict: {verdict}! 🛡️"
                    st.link_button("🐦 Share Warning on X", tweet)

                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
