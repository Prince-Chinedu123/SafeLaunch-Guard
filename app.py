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

# --- Input Section ---
target_address = st.text_input("Paste Token Contract Address:", placeholder="0x...")
chain = st.selectbox("Select Chain:", ["eth", "solana", "base", "polygon"])

if st.button("Run Security Audit"):
    if not target_address:
        st.error("Please enter an address first!")
    else:
        with st.spinner("Scanning for Snipers, Bundlers, and Malicious Logic..."):
            # Webacy API Endpoint for Trading/Token Intelligence
            url = f"https://api.webacy.com/trading/lite/{target_address}?chain={chain}"
            headers = {"accept": "application/json", "X-API-KEY": API_KEY}
            
            try:
                # Actual API Call
                response = requests.get(url, headers=headers)
                data = response.json()
                
                if response.status_code == 200:
                    st.success("Audit Complete!")
                    
                    # --- Displaying the "Report Card" ---
                    col1, col2, col3 = st.columns(3)
                    
                    # These keys come directly from Webacy's TradingDD documentation
                    col1.metric("Sniper Holding", f"{data.get('SniperPercentageHolding', 0)}%")
                    col2.metric("Top 10 Holders", f"{data.get('Top10Holders', 0)}%")
                    col3.metric("Dev Holding", f"{data.get('DevHoldingPercentage', 0)}%")
                    
                    if data.get('SniperPercentageOnLaunch', 0) > 30:
                        st.error("⚠️ HIGH RISK: Large percentage of supply taken by snipers at launch.")
                    else:
                        st.info("✅ Sniper activity appears within normal limits.")
                        
                else:
                    st.error(f"Error from Webacy: {data.get('message', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.markdown("---")
st.caption("Built for the DD.xyz Grant Program | Powered by Webacy Risk Engine")