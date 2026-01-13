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
            # Ensure chain is lowercase (crucial for API compatibility)
            selected_chain = chain.lower() 
            url = f"https://api.webacy.com/trading/lite/{target_address}?chain={selected_chain}"
            
            # --- THE FIX: Added User-Agent and accepted format ---
            headers = {
                "accept": "application/json", 
                "X-API-KEY": API_KEY,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            
            try:
                # Added a 15-second timeout to handle the delay you saw
                response = requests.get(url, headers=headers, timeout=15)
                
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
                    risk_score = (snipers * 0.5) + (top10 * 0.3) + (dev * 0.2)
                    safety_score = max(0, 100 - int(risk_score))
                    
                    if safety_score > 75:
                        st.success(f"✅ Overall Safety Score: {safety_score}/100 (Low Risk)")
                    elif safety_score > 40:
                        st.warning(f"⚠️ Overall Safety Score: {safety_score}/100 (Moderate Risk)")
                    else:
                        st.error(f"🚨 Overall Safety Score: {safety_score}/100 (HIGH RISK)")
                        
                elif response.status_code == 403:
                    st.error("🛡️ Webacy Firewall: Request Forbidden. This often happens if the API key isn't fully active yet or the IP is flagged. Try again in 15 minutes.")
                elif response.status_code == 401:
                    st.error("❌ Invalid API Key. Please verify the key in your .env file has no spaces.")
                else:
                    st.error(f"Webacy API Error {response.status_code}: {response.text}")
            
            except requests.exceptions.Timeout:
                st.error("⏳ Request Timed Out. The Webacy server is taking too long to respond.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.markdown("---")
st.caption("Built for the DD.xyz Grant Program | Powered by Webacy Risk Engine")
