import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# --- 1. PERSISTENT CREDIT TRACKER ---
def get_persistent_count():
    try:
        if os.path.exists('audit_log.json'):
            with open('audit_log.json', 'r') as f:
                data = json.load(f)
                return data.get('count', 11)
    except:
        pass
    return 11 # Start at 11 based on your previous usage

def save_persistent_count(count):
    try:
        with open('audit_log.json', 'w') as f:
            json.dump({'count': count}, f)
    except:
        pass

# --- 2. INITIAL SETUP ---
load_dotenv(override=True)
# Priority: Streamlit Secrets (for cloud) -> .env (for local)
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
st.sidebar.caption("Persistence: Active (Session Data Saved)")
st.sidebar.info("✅ Webacy Engine: Connected")

if st.sidebar.button("Reset Session Counter",
