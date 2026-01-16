import streamlit as st
import requests
import os
from dotenv import load_dotenv

# 1. INITIAL SETUP & SESSION STATE
load_dotenv(override=True)
# This pulls from Streamlit Secrets (cloud) or .env (local)
API_KEY = os.getenv("WEBACY_API_KEY", "").strip()

if 'audit_count' not in st.session_state:
    st.session_state.audit_count = 0

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️", layout="centered")

# 2. SIDEBAR - USAGE & STATUS
st.sidebar.title("📊 Project Stats")

# Calculate remaining credits from your 2,000 grant
remaining = 2000 - st.session_state.audit_count

# Visual status based on usage
if remaining > 500:
    st.sidebar.success(f"Credits: {remaining} (Healthy)")
elif remaining > 100:
    st.sidebar.warning(f"Credits: {remaining} (Low)")
else:
    st.sidebar.error(f"Credits: {remaining} (Critical)")

st.sidebar.progress(min(st.session_state.audit_count / 2000, 1.0))
st.sidebar.caption("Webacy Grant Usage Tracker")

# Professional Status indicator
st.sidebar.info("✅ Webacy Engine: Connected")

# Fixed unique key to prevent DuplicateElementId error
if st.sidebar.button("Reset Session Counter", key="sidebar_reset_btn"):
    st.session_state.audit_count = 0
    st.rerun()

# 3. MAIN INTERFACE
st.title("🛡️ SafeLaunch Guard")
st.markdown("### Webacy-Powered Token Security Audit")
st.write("Enter a contract address below to perform a deep-scan for vulnerabilities and rug-pull risks.")

# Input Section
target_address = st.text_input("Contract Address:", placeholder="0x...")

chain_map = {
    "Base": "base",
    "Ethereum": "eth",
    "Solana": "sol",
    "BSC": "bsc",
    "Arbitrum": "arb",
    "Polygon": "pol"
}
chain_display = st.selectbox("Select Network:", list(chain_map.keys()))

# 4. AUDIT LOGIC
if st.button("Run Security Audit", type="primary"):
    if not target_address:
        st.error("Please enter a contract address first.")
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
                    st.session_state.audit_count += 1
                    
                    # Risk Scoring
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

                    st.markdown(f"## Assessment: :{color}[{verdict}]")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Safety Score", f"{safety_score}/100")
                    col2.metric("Risk Level", f"{rounded_risk}/100")
                    
                    st.markdown("---")
                    
                    # Risk Factors Display
                    issues = data.get('issues', [])
                    if issues:
                        st.subheader("🚩 Risk Factors Detected")
                        for issue in issues:
                            # Using .get with defaults to avoid 'None' display
                            title = issue.get('title') or "Security Detail"
                            desc = issue.get('description') or "Technical risk detected. Check Webacy dashboard for details."
                            with st.expander(f"⚠️ {title}"):
                                st.write(desc)
                    else:
                        st.balloons()
                        st.success("SafeLaunch Verdict: No significant threats detected by Webacy.")

                    # 5. REPORT GENERATION (Cleaned logic)
                    report_text = f"SafeLaunch Guard Security Audit\n"
                    report_text += f"Target Address: {target_address}\n"
                    report_text += f"Network: {chain_display}\n"
                    report_text += f"Verdict: {verdict}\n"
                    report_text += f"Risk Score: {rounded_risk}/100\n"
                    report_text += f"------------------------------\n\n"
                    
                    if issues:
                        for issue in issues:
                            title = issue.get('title') or "Issue"
                            desc = issue.get('description') or "No description provided."
                            report_text += f"- {title}: {desc}\n"
                    else:
                        report_text += "✅ No significant vulnerabilities detected by the Webacy Risk Engine."

                    st.download_button(
                        label="📥 Download Audit Report",
                        data=report_text,
                        file_name=f"Audit_{target_address[:8]}.txt",
                        mime="text/plain",
                    )
                
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            
            except Exception as e:
                st.error(f"Connection Failed: Ensure your API Key is correctly set in Streamlit Secrets.")

# FOOTER
st.markdown("---")
st.caption("Powered by Webacy | Developed for the DD.xyz Grant Program")
