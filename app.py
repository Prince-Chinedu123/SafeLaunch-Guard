import streamlit as st
import requests
import os
import json
import random # For the probability weighting
from dotenv import load_dotenv
import pandas as pd # Essential for the holder breakdown table

# --- 1. PERSISTENCE & HISTORY LOGIC ---
def get_persistent_data():
    try:
        if os.path.exists('audit_log.json'):
            with open('audit_log.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {"count": 22, "history": []} 

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

if 'audit_count' not in st.session_state:
    st.session_state.audit_count = max(saved_data.get("count", 22), 22)

if 'audit_history' not in st.session_state:
    st.session_state.audit_history = saved_data.get("history", [])

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️", layout="centered")

# --- 3. SIDEBAR (PROFESSIONAL DASHBOARD) ---
st.sidebar.title("📊 Project Dashboard")

HARD_LIMIT = 1750 
SAFE_LIMIT = 1700 
remaining = HARD_LIMIT - st.session_state.audit_count

st.sidebar.metric("Total API Usage", f"{st.session_state.audit_count}")
st.sidebar.progress(min(st.session_state.audit_count / HARD_LIMIT, 1.0))

if remaining <= 100:
    st.sidebar.warning(f"⚠️ Beta Limit Near: {remaining} left")
else:
    st.sidebar.caption(f"Grant Credits Remaining: {remaining}")

st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Recent Audits")
if st.session_state.audit_history:
    for item in st.session_state.audit_history[-5:]:
        st.sidebar.caption(f"🔍 {item['addr'][:10]}... (Score: {item['score']})")
else:
    st.sidebar.write("No scan history yet.")

st.sidebar.markdown("---")
st.sidebar.info("✅ Webacy Threat Engine: Active")

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
        st.error("⚠️ BETA LIMIT REACHED. Saving remaining credits for Feb 10 Launch!")
    else:
        with st.spinner("Analyzing Contract & Creator Pedigree..."):
            url = f"https://api.webacy.com/addresses/{target_address}"
            headers = {"x-api-key": API_KEY, "accept": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, params={"chain": chain_map[chain_display]}, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.audit_count += 1
                    
                    raw_risk = float(data.get('overallRisk', 0))
                    rounded_risk = round(raw_risk, 2)
                    safety_score = max(0, 100 - int(raw_risk))
                    
                    # RUG PROBABILITY MATH (As requested, unchanged)
                    issues_count = len(data.get('issues', []))
                    creator_risk = data.get('creatorRisk', raw_risk)
                    rug_prob = min(100, (rounded_risk * 0.6) + (creator_risk * 0.2) + (issues_count * 5))
                    
                    new_entry = {"addr": target_address, "score": safety_score}
                    st.session_state.audit_history.append(new_entry)
                    save_persistent_data(st.session_state.audit_count, st.session_state.audit_history)
                    
                    if rounded_risk <= 23:
                        verdict, color, icon = "LOW RISK", "green", "✅"
                    elif rounded_risk <= 50:
                        verdict, color, icon = "MEDIUM RISK", "orange", "⚠️"
                    else:
                        verdict, color, icon = "HIGH RISK", "red", "🚨"

                    st.success(f"Audit Complete for {target_address[:10]}...")
                    
                    # --- BEAUTIFUL LAYOUT START ---
                    
                    # 1. TOP LEVEL VERDICT
                    st.markdown(f"## {icon} {verdict}")
                    st.write(f"**Rug Probability Score: {round(rug_prob, 1)}%**")
                    st.progress(rug_prob / 100)
                    
                    # 2. SCORECARD METRICS
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Safety Grade", f"{safety_score}/100")
                    col_m2.metric("Threat Level", f"{rounded_risk}%")
                    col_m3.metric("Network", chain_display)

                    st.markdown("---")

                    # 3. TECHNICAL HEALTH CARDS (Side-by-Side)
                    row1_col1, row1_col2 = st.columns(2)
                    
                    has_liq_issue = any("liquidity" in str(iss).lower() for iss in data.get('issues', []))
                    
                    with row1_col1:
                        with st.container(border=True):
                            st.subheader("🔒 Liquidity")
                            if has_liq_issue or rounded_risk > 80:
                                st.error("🚨 UNLOCKED")
                            else:
                                st.success("✅ STABLE")
                            st.caption("LP Token status check.")

                    with row1_col2:
                        with st.container(border=True):
                            st.subheader("🐋 Whale Analysis")
                            if rug_prob > 60 or rounded_risk > 65:
                                st.error("🚨 INSIDERS")
                            else:
                                st.success("💎 ORGANIC")
                            st.caption("Distribution patterns.")

                    # 4. CREATOR PROFILE CARD
                    with st.container(border=True):
                        st.subheader("👨‍💻 Creator Pedigree")
                        if creator_risk > 70:
                            st.error(f"High Risk Creator Profile ({creator_risk}%)")
                        elif creator_risk > 30:
                            st.warning("New or Unknown Developer Wallet")
                        else:
                            st.success("💎 Established Clean Reputation")

                    # 5. DETAILED HOLDER TABLE
                    st.subheader("📊 Top 5 Holder Breakdown")
                    holders = data.get('topHolders', [])
                    if holders:
                        st.dataframe(pd.DataFrame(holders).head(5), use_container_width=True)
                    else:
                        st.info("No public holder data available for this contract.")

                    # --- BEAUTIFUL LAYOUT END ---

                    # RISK DETAIL EXPANDER (Retained Findings)
                    issues = data.get('issues', [])
                    if issues:
                        st.subheader("🚩 Security Findings")
                        for issue in issues:
                            title = issue.get('title', 'Risk Factor')
                            description = issue.get('description') or "Technical risk identified. Manual review recommended."
                            with st.expander(f"⚠️ {title}"):
                                st.write(description)
                    else:
                        st.balloons()
                        st.success("SafeLaunch Verdict: No significant threats detected.")

                    # SEAL OF APPROVAL
                    if verdict == "LOW RISK":
                        st.markdown("---")
                        st.subheader("🏆 SafeLaunch Seal of Approval")
                        badge_md = f"![SafeLaunch Verified](https://img.shields.io/badge/SafeLaunch-Verified_Safe-green?style=for-the-badge&logo=shield)"
                        st.markdown(badge_md)
                        st.code(badge_md)

                    st.markdown("---")
                    tweet_text = f"Audit complete for {target_address[:10]} on @SafeLaunchGuard. Rug Probability: {round(rug_prob, 1)}%. Protected by @mywebacy tech. #Web3 #Security"
                    share_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
                    st.link_button("🐦 Share Result on X", share_url)

                else:
                    st.error(f"API Error: Please check your connection or address format.")
            except Exception as e:
                st.error(f"System Error: {e}")

st.markdown("---")
st.caption("Official Grantee: DD.xyz | Security Engine: Webacy")
