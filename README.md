🔐 SmartShield – AI-Powered Intrusion Detection System

SmartShield is a cloud-based Streamlit app that uses machine learning to detect suspicious activity from uploaded network logs. Designed for educational institutions and offices, it analyzes network behavior, flags anomalies, and offers detailed visualization and reporting.

---

🚀 Features

* 📤 Upload network log CSV files
* 🤖 AI-powered anomaly detection (Isolation Forest)
* 📊 Graphs for suspicious behavior:

  * Line chart of suspicion scores
  * Pie chart of anomaly distribution
  * Bar chart of suspicious activity by user
* 📡 Real-time style log simulation
* 📈 Stats panel with total vs anomalous logs
* 📥 Downloadable anomaly report (CSV)
* 🔐 Admin login for secure access
* 🧪 Fake log generator for demos
* ⚙️ Optional CLI-based model script (`smartshield_model.py`) for testing/validation

---

📁 File Structure

```
smartshield/
├── smartshield.py            # Main Streamlit application
├── requirements.txt             # Project dependencies
├── README.md                    # Project overview (this file)
```

---

🧪 Generate Demo Logs

Use the following command to generate fake but realistic logs:

```bash
python generate_fake_logs.py
```

This will create a file called `demo_network_logs.csv` with normal and suspicious patterns.

---

🖥️ Run the App Locally

```bash
pip install -r requirements.txt
streamlit run smartshield_app.py
```

---

🌐 Online Deployment

The app is fully compatible with Streamlit Cloud. Just upload the files to your GitHub repo and deploy via [streamlit.io](https://streamlit.io).

---

📊 Sample Use Case

SmartShield helps IT administrators at colleges/offices:

* Identify abnormal login times
* Detect unusual data transfers
* Flag potential brute-force or data exfiltration events
* Visually monitor activity patterns with graphs

---

👨‍💻 Authors

* N. Lahiri
* Built for Hackathon 2025

---

📜 License

This project is intended for educational and demonstration use only. For production-level deployment, integration with real-time network capture tools and security protocols is required.
