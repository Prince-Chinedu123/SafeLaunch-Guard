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
    return {"count": 11, "history": []}

def save_persistent_data(count, history):
    try:
        with open('audit_log.json', 'w') as f:
            json.dump({"count": count, "history": history}, f)
    except:
        pass

# --- 2. INITIAL SETUP ---
load_dotenv(override=True)
API_KEY = st.secrets.get("WEBACY_API_KEY") or os.getenv("WEBACY_API_KEY", "").strip()

# Initialize session state from persistence
saved_data = get_persistent_data()
if 'audit_count' not in st.session_state:
    st.session_state.audit_count = saved_data.get("count", 11)
if 'audit_history' not in st.session_state:
    st.session_state.audit_history = saved_data.get("history", [])

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️", layout="centered")

# --- 3. SIDEBAR (USAGE & HISTORY) ---
st.sidebar.title("📊 Project Dashboard")
GRANT_LIMIT = 2000
remaining = GRANT_LIMIT - st.session_state.audit_count

# Usage Tracker
if remaining > 500:
    st.sidebar.success(f"Credits: {remaining} (Healthy)")
else:
    st.sidebar.error(f"Credits: {remaining} (Low)")

st.sidebar.progress(min(st.session_state.audit_count / GRANT_LIMIT, 1.0))

# Audit History Table
st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Recent Audits")
if st.session_state.audit_history:
    # Display last 5 scans in a clean table
    for item in st.session_state.audit_history[-5:]:
        st.sidebar.caption(f"🔍 {item['addr'][:10]}... | Score: {item['score']}")
else:
    st.sidebar.write("No history yet.")

st.sidebar.markdown("---")
if st.sidebar.button("Reset Everything", key="reset_all"):
    st.session_state.audit_count = 11
    st.session_state.audit_history = []
    save_persistent_data(11, [])
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
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    # Update History
                    new_entry = {"addr": target_address, "score": safety_score}
                    st.session_state.audit_history.append(new_entry)
                    save_persistent_data(st.session_state.audit_count, st.session_state.audit_history)
                    
                    # Verdicts
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
                    
                    # --- UNIQUE FEATURES ---
                    st.markdown("---")
                    st.subheader("🐋 Whale Watch: Holder Analysis")
                    if rounded_risk > 60:
                        st.error("⚠️ HIGH CONCENTRATION: Supply risk detected.")
                    else:
                        st.success("✅ HEALTHY DISTRIBUTION: Supply is well-dispersed.")

                    if verdict == "LOW RISK":
                        st.subheader("🏆 SafeLaunch Seal of Approval")
                        badge_md = f"![SafeLaunch Verified](https://img.shields.io/badge/SafeLaunch-Verified_Safe-green?style=for-the-badge&logo=shield)"
                        st.markdown(badge_md)
                        st.code(badge_md, language="markdown")

                    # X/TWITTER SHARE
                    tweet_text = f"Just audited {target_address[:10]} on SafeLaunch Guard. Verdict: {verdict}! 🛡️"
                    share_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
                    st.link_button("🐦 Share on X (Twitter)", share_url)

                    # REPORT DOWNLOAD
                    report = f"SafeLaunch Audit\nTarget: {target_address}\nVerdict: {verdict}\nScore: {safety_score}/100"
                    report += "\n\nDISCLAIMER: For informational purposes only. Powered by Webacy."
                    st.download_button("📥 Download Report", data=report, file_name=f"Audit_{target_address[:8]}.txt")
                    
                else:
                    st.error(f"API Error {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
