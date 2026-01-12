import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load your hidden API Key
load_dotenv()
API_KEY = os.getenv("WEBACY_API_KEY")

st.set_page_config(page_title="SafeLaunch Guard", page_icon="🛡️")

# --- UI Header ---
st.title("🛡️ SafeLaunch Guard")
st.subheader("Webacy-Powered Token Security Audit")

# --- API Key Validation ---
if not API_KEY:
    st.error("⚠️ Webacy API Key missing! Please add it to your .env file.")
    st.stop()

# --- Input Section ---
target_address = st.text_input("Paste Token Contract Address:", placeholder="0x...")
chain = st.selectbox("Select Chain:", ["base", "solana", "eth", "polygon"])

if st.button("Run Security Audit"):
    if not target_address:
        st.error("Please enter an address first!")
    else:
        with st.spinner("Accessing Webacy Risk Engine..."):
            # Using the Trading Lite endpoint as requested
            url = f"https://api.webacy.com/trading/lite/{target_address}?chain={chain}"
            headers = {
                "accept": "application/json", 
                "X-API-KEY": API_KEY
            }
            
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Audit Complete!")
                    
                    # --- Report Card Summary ---
                    st.markdown("### 📊 Token Report Card")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # Extraction with safety defaults
                    snipers = data.get('SniperPercentageHolding', 0)
                    top10 = data.get('Top10Holders', 0)
                    dev = data.get('DevHoldingPercentage', 0)
                    
                    col1.metric("Sniper Holding", f"{snipers}%")
                    col2.metric("Top 10 Holders", f"{top10}%")
                    col3.metric("Dev Holding", f"{dev}%")
                    
                    st.markdown("---")
                    
                    # --- Risk Analysis Logic ---
                    # Calculate a simple Safety Score (100 - risk factors)
                    risk_score = (snipers * 0.5) + (top10 * 0.3) + (dev * 0.2)
                    safety_score = max(0, 100 - int(risk_score))
                    
                    if safety_score > 75:
                        st.success(f"✅ Overall Safety Score: {safety_score}/100 (Low Risk)")
                    elif safety_score > 40:
                        st.warning(f"⚠️ Overall Safety Score: {safety_score}/100 (Moderate Risk)")
                    else:
                        st.error(f"🚨 Overall Safety Score: {safety_score}/100 (HIGH RISK)")

                    # Specific Flag Logic
                    if snipers > 30:
                        st.error("🚩 CRITICAL: High Sniper concentration detected. Potential for instant dump.")
                    
                    if top10 > 70:
                        st.warning("⚠️ WARNING: Centralized Supply. Top 10 wallets control majority of tokens.")
                        
                elif response.status_code == 401:
                    st.error("❌ Invalid API Key. Please verify your Webacy credentials.")
                elif response.status_code == 404:
                    st.error("❌ Token not found. Ensure the address and chain are correct.")
                else:
                    st.error(f"Webacy API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.markdown("---")
st.caption("Built for the DD.xyz Grant Program | Powered by Webacy Risk Engine")
