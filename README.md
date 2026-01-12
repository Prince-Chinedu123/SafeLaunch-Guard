🛡️ SafeLaunch Guard
Real-time Security Audits for the Base and Solana Ecosystems.

SafeLaunch Guard is a proactive security dashboard designed to protect retail traders from malicious smart contracts and rug-pulls. Built during the DD.xyz Grant Program, this tool leverages the Webacy Risk Engine to provide instant, actionable safety data for new token launches.

🚀 Features
Contract Risk Analysis: Fetches real-time data from the Webacy Trading Lite API to identify vulnerabilities.

Safety Scorecard: Automatically calculates a "Safety Score" (0-100) based on sniper activity and holder concentration.

Sniper Detection: Flags tokens where a high percentage of supply was snatched by bots at launch.

Concentration Alerts: Identifies if the Top 10 holders or Developers control a dangerous amount of the total supply.

Multi-Chain Support: Native support for Base, Solana, Ethereum, and Polygon.

🛠️ Tech Stack
Language: Python 3.9+

Framework: Streamlit (UI)

API: Webacy Risk Engine (Trading Intelligence)

Environment: Managed via .env for secure API key handling.

📦 Installation & Setup

1. Clone the repository:
Bash
git clone https://github.com/Prince-Chinedu123/SafeLaunch-Guard.git
cd safelaunch-guard

2. Install dependencies:
Bash
pip install streamlit requests python-dotenv

3. Configure Environment Variables: Create a .env file in the root directory and add your Webacy API Key:

Code snippet

WEBACY_API_KEY=your_api_key_here

4. Run the Application:
Bash
streamlit run app.py

## 📺 Project Demos

### 🚀 Phase 2: Live Integration & Code Walkthrough (Current)
* **Watch here:** [Link to your new "Plan B" Video]
* **What's new:** API integration, custom Safety Score logic, and a deep dive into the `app.py` architecture.

---

### 🎨 Phase 1: Initial Design & UI Concept
* **Watch here: https://drive.google.com/file/d/1sIXn6O4ZkBXnZguGlROt-tzX4P-4gaRq/view?usp=drive_link
* **Goal:** Early-stage mockup showing the user interface and vision for SafeLaunch Guard.


Built by Prince Chinedu for the Webacy / DD.xyz Ecosystem.


