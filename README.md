# 🛡️ SafeLaunch Guard
**Real-time Security Audits for the Base and Solana Ecosystems**

SafeLaunch Guard is a proactive security dashboard designed to protect retail traders from malicious smart contracts and rug-pulls. Built during the DD.xyz Grant Program, this tool leverages the **Webacy Risk Engine** to provide instant, actionable safety data.

## 🚀 Key Features
* **Multi-Chain Support:** Real-time audits for ETH, Base, and Solana tokens.
* **Webacy Integration:** Deep integration with Webacy's API for contract risk scoring and sniper cluster detection.
* **Trader Insights:** Clear "Report Card" style breakdowns of liquidity, top holders, and minting functions.

## 🛠️ Technical Stack
* **Frontend:** Streamlit
* **Backend:** Python 3.x
* **Security Layer:** Webacy Risk Engine API

## 🏗️ Setup
1. Clone the repository.
2. Install dependencies: `pip install streamlit requests python-dotenv`.
3. Configure your `.env` file with your `WEBACY_API_KEY`.
4. Run the app: `streamlit run app.py`.