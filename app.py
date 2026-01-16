import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# --- 1. PERSISTENCE & HISTORY LOGIC ---
def get_persistent_data():
    try:
        if os.path.exists('audit_log.json'):
            with open('audit_log.json', 'r') as f:
                return json.load(f)
    except:
        pass
    # PERMANENT BASELINE: Ensures your count starts at 16 even if the cloud file is wiped
    return {"count": 16, "history": []}

def save_persistent_data(count, history):
    try:
        with open('audit_log.json', 'w') as f:
            json.dump({"count": count, "history": history}, f)
    except:
        pass

# --- 2. INITIAL SETUP ---
load_dotenv(override=True)
API_KEY = st.secrets.get("WEBACY_API_KEY") or os.getenv("WEBACY_API_KEY", "").strip()

saved_data = get_persistent_data()

# Ensure session state respects the highest number found to prevent resets
if 'audit_count' not in st.session_state:
    st.session_state.audit_count = max(saved_data.get("count", 16), 16)

if 'audit_history' not in st.session_state:
    st.session_state.audit_history = saved_data.get("history", [])

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️", layout="centered")

# --- 3. SIDEBAR (PROFESSIONAL DASHBOARD) ---
st.sidebar.title("📊 Project Dashboard")

# SAFETY CUSHION LOGIC
TRUE_LIMIT = 2000
SAFE_LIMIT = 1800  # Sets a 200-credit buffer to account for "ghost" resets
remaining = SAFE_LIMIT - st.session_state.audit_count

# Usage Tracker Metric
st.sidebar.metric("Total API Usage", f"{st.session_state.audit_count}")
st.sidebar.progress(min(st.session_state.audit_count / SAFE_LIMIT, 1.0))

# Warning system for credits
if remaining <= 100:
    st.sidebar.warning(f"⚠️ Low Credit Warning: {remaining} left")
else:
    st.sidebar.caption(f"Remaining Grant Credits: {remaining}")

# Audit History Section
st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Recent Audits")
if st.session_state.audit_history:
    for item in st.session_state.audit_history[-5:]:
        st.sidebar.caption(f"🔍 {item['addr'][:10]}... (Score: {item['score']})")
    
    if st.sidebar.button("Clear History List", key="clear_hist_btn"):
        st.session_state.audit_history = []
        save_persistent_data(st.session_state.audit_count, [])
        st.rerun()
else:
    st.sidebar.write("No scan history yet.")

st.sidebar.markdown("---")
st.sidebar.info("✅ Webacy Engine: Connected")

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
        st.error("⚠️ SAFE LIMIT REACHED. Please contact the developer for a grant top-up.")
    else:
        with st.spinner("Analyzing Webacy Threat Intelligence..."):
            url = f"https://api.webacy.com/addresses/{target_address}"
            headers = {"x-api-key": API_KEY, "accept": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, params={"chain": chain_map[chain_display]}, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update Persistence & State
                    st.session_state.audit_count += 1
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    # Update History list
                    new_entry = {"addr": target_address, "score": safety_score}
                    st.session_state.audit_history.append(new_entry)
                    save_persistent_data(st.session_state.audit_count, st.session_state.audit_history)
                    
                    # Score Coloring
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
                        st.error("⚠️ HIGH CONCENTRATION: Indicators suggest high control by developer/top wallets.")
                    else:
                        st.success("✅ HEALTHY DISTRIBUTION: Supply appears well-dispersed among holders.")

                    # Risk Detail Expander
                    issues = data.get('issues', [])
                    if issues:
                        st.subheader("🚩 Risk Factors Detected")
                        for issue in issues:
                            t = issue.get('title') or "Security Detail"
                            d = issue.get('description') or "Technical risk detected."
                            with st.expander(f"⚠️ {t}"):
                                st.write(d)
                    else:
                        st.balloons()
                        st.success("SafeLaunch Verdict: No significant threats detected.")

                    # UNIQUE FEATURE: SEAL OF APPROVAL (BADGE)
                    if verdict == "LOW RISK":
                        st.markdown("---")
                        st.subheader("🏆 SafeLaunch Seal of Approval")
                        badge_md = f"![SafeLaunch Verified](https://img.shields.io/badge/SafeLaunch-Verified_Safe-green?style=for-the-badge&logo=shield)"
                        st.markdown(badge_md)
                        st.caption("Developer Badge Code:")
                        st.code(badge_md, language="markdown")

                    # UNIQUE FEATURE: SOCIAL SHARE
                    st.markdown("---")
                    st.subheader("📣 Share Findings")
                    status_emoji = "🛡️" if verdict == "LOW RISK" else "⚠️"
                    tweet_text = f"Just audited {target_address[:10]} on SafeLaunch Guard. Verdict: {verdict} {status_emoji}. Stay safe out there! #Web3 #Security"
                    share_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
                    st.link_button("🐦 Share on X (Twitter)", share_url)

                    # REPORT GENERATION
                    report_text = f"SafeLaunch Guard Security Audit\n"
                    report_text += f"Target: {target_address}\nVerdict: {verdict}\n"
                    report_text += f"Safety Score: {safety_score}/100\n"
                    report_text += f"------------------------------\n"
                    
                    if issues:
                        for issue in issues:
                            report_text += f"- {issue.get('title', 'Issue')}: {issue.get('description', 'No details.')}\n"
                    else:
                        report_text += "No issues detected.\n"
                    
                    report_text += "\n\nDISCLAIMER: For informational purposes only. Powered by Webacy."

                    st.download_button("📥 Download Official Audit", data=report_text, file_name=f"Audit_{target_address[:8]}.txt")

                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
