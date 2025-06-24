import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
import streamlit_authenticator as stauth
import json
import os
from datetime import datetime
from yaml.loader import SafeLoader
from cryptography.fernet import Fernet

# --- CONFIG ---
st.set_page_config(page_title="SmartShield IDS", layout="wide")

# --- ENCRYPTION ---
KEY_FILE = "secret.key"
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())
with open(KEY_FILE, "rb") as f:
    key = f.read()
fernet = Fernet(key)

# --- HISTORY ---
HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def save_to_history(df, original_filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = f"{original_filename}__{timestamp}"
    csv_path = os.path.join(HISTORY_DIR, f"{file_id}.csv")
    json_path = os.path.join(HISTORY_DIR, f"{file_id}.json")

    csv_data = df.to_csv(index=False).encode()
    with open(csv_path, "wb") as f:
        f.write(fernet.encrypt(csv_data))

    metadata = {
        "display_name": original_filename,
        "file_id": file_id,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "record_count": len(df)
    }
    json_data = json.dumps(metadata, indent=2).encode()
    with open(json_path, "wb") as f:
        f.write(fernet.encrypt(json_data))

def list_saved_histories():
    items = []
    for file in os.listdir(HISTORY_DIR):
        if file.endswith(".json"):
            with open(os.path.join(HISTORY_DIR, file), "rb") as f:
                decrypted = fernet.decrypt(f.read()).decode()
                metadata = json.loads(decrypted)
                items.append((metadata["file_id"], metadata["display_name"], metadata))
    return sorted(items, key=lambda x: x[2]["uploaded_at"], reverse=True)

def load_history_df(file_id):
    with open(os.path.join(HISTORY_DIR, f"{file_id}.csv"), "rb") as f:
        decrypted = fernet.decrypt(f.read()).decode()
    from io import StringIO
    return pd.read_csv(StringIO(decrypted))

def delete_history_item(file_id):
    os.remove(os.path.join(HISTORY_DIR, f"{file_id}.csv"))
    os.remove(os.path.join(HISTORY_DIR, f"{file_id}.json"))

def clear_history():
    for file in os.listdir(HISTORY_DIR):
        os.remove(os.path.join(HISTORY_DIR, file))

# --- USER AUTH & SIGNUP ---
def register_user():
    st.subheader("📝 Sign Up")
    new_name = st.text_input("Full Name")
    new_username = st.text_input("Choose a Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if new_password != confirm:
            st.error("❌ Passwords do not match")
        elif not all([new_name, new_username, new_email, new_password]):
            st.error("❌ All fields are required")
        else:
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    users = json.load(f)
            else:
                users = {}
            if new_username in users:
                st.error("❌ Username already exists")
            else:
                hashed_pw = stauth.Hasher([new_password]).generate()[0]
                users[new_username] = {
                    "email": new_email,
                    "name": new_name,
                    "password": hashed_pw
                }
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=2)
                st.success("✅ Registration successful. You can now log in.")

if "signup_mode" not in st.session_state:
    st.session_state.signup_mode = False
if st.sidebar.button("🔄 Toggle Sign Up / Login"):
    st.session_state.signup_mode = not st.session_state.signup_mode
if st.session_state.signup_mode:
    register_user()
    st.stop()

# --- LOGIN SETUP ---
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

dynamic_credentials = {"usernames": {}}
for uname, info in user_data.items():
    dynamic_credentials["usernames"][uname] = {
        "email": info["email"],
        "name": info["name"],
        "password": info["password"]
    }

config = {
    "credentials": dynamic_credentials,
    "cookie": {"name": "smartshield_cookie", "key": "somekey", "expiry_days": 30}
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

name, authentication_status, username = authenticator.login("Login", "main")

# --- MAIN APP ---
if authentication_status:
    st.sidebar.markdown(f"👋 Welcome **{name}**")
    authenticator.logout("Logout", "sidebar")
    st.title("🔐 SmartShield – Intrusion Detection System")

    # --- SIDEBAR HISTORY + BENCHMARK SELECT ---
    history = list_saved_histories()
    selected_log = None
    selected_logs = []

    st.sidebar.markdown("### 🕓 History (Select to Compare)")
    for file_id, display_name, meta in history:
        checkbox_key = f"check_{file_id}"
        if st.sidebar.checkbox(display_name, key=checkbox_key):
            selected_logs.append(file_id)
        if st.sidebar.button(f"🗑️ Delete {display_name}", key=file_id + "_del"):
            delete_history_item(file_id)
            st.experimental_rerun()

    if history and st.sidebar.button("🧹 Clear All History"):
        clear_history()
        st.rerun()

    # 🧪 Compare Logs
    if selected_logs and st.sidebar.button("📊 Compare Selected Logs"):
        st.session_state["benchmark_mode"] = selected_logs

    # 🧪 BENCHMARK MODE
    if "benchmark_mode" in st.session_state:
        selected_ids = st.session_state["benchmark_mode"]
        st.subheader("📊 Benchmark Mode – Log Comparison")

        summary_rows = []
        for file_id in selected_ids:
            df_bench = load_history_df(file_id)
            model = IsolationForest(contamination=0.2, random_state=42)
            model.fit(df_bench.select_dtypes(include=np.number))
            df_bench["anomaly"] = model.predict(df_bench.select_dtypes(include=np.number))
            anomalies = len(df_bench[df_bench["anomaly"] == -1])
            total = len(df_bench)
            top_users = df_bench[df_bench["anomaly"] == -1]["username"].value_counts().head(1)
            summary_rows.append({
                "File": file_id.split("__")[0],
                "Total Logs": total,
                "Anomalies": anomalies,
                "Top Suspicious User": top_users.index[0] if not top_users.empty else "N/A"
            })

        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df)

        st.subheader("📉 Anomalies per File")
        fig, ax = plt.subplots()
        ax.bar(summary_df["File"], summary_df["Anomalies"], color='red')
        ax.set_ylabel("Anomaly Count")
        ax.set_xlabel("File")
        ax.set_title("Detected Anomalies per Log File")
        plt.xticks(rotation=30)
        st.pyplot(fig)

        if st.button("🔁 Exit Benchmark Mode"):
            del st.session_state["benchmark_mode"]
            st.experimental_rerun()
        st.stop()

    # UPLOAD or SELECT SINGLE FILE
    # Initialize df
    df = None
    
    # UPLOAD or SELECT SINGLE FILE
    uploaded_file = st.file_uploader("📤 Upload CSV File", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        save_to_history(df, uploaded_file.name)
        st.success(f"✅ '{uploaded_file.name}' uploaded and saved.")
    elif df is None and not uploaded_file:
        for file_id, _, _ in history:
            selected_log = file_id
            break

    if selected_log:
        df = load_history_df(selected_log)
        st.info(f"📁 Loaded: {selected_log.split('__')[0]}")
    else:
        df = None

    # MAIN ANALYSIS VIEW
    if df is not None:
        st.subheader("📄 Uploaded Data")
        st.dataframe(df)

        with st.spinner("Analyzing with AI..."):
            model = IsolationForest(contamination=0.2, random_state=42)
            model.fit(df.select_dtypes(include=np.number))
            df['anomaly'] = model.predict(df.select_dtypes(include=np.number))
            df['anomaly_label'] = df['anomaly'].map({1: "✅ Normal", -1: "⚠️ Suspicious"})

        st.subheader("📊 Detection Results")
        st.dataframe(df)

        st.subheader("⚠️ Suspicious Entries")
        st.dataframe(df[df['anomaly_label'] == "⚠️ Suspicious"])

        if st.checkbox("📈 Suspicion Score Over Time"):
            df['suspicion_score'] = df['bytes_sent'] + df['bytes_received']
            df['log_index'] = df.index
            fig1, ax1 = plt.subplots()
            ax1.plot(df['log_index'], df['suspicion_score'], color='orange')
            ax1.set_title("Suspicion Score Trend")
            st.pyplot(fig1)

        if st.checkbox("📊 Show Anomalies by User"):
            fig2, ax2 = plt.subplots(figsize=(12, 5))
            sns.countplot(data=df[df['anomaly_label'] == "⚠️ Suspicious"], x='username', ax=ax2)
            ax2.set_title("Suspicious Activity by User")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

        if st.checkbox("🥧 Show Normal vs Suspicious Distribution"):
            fig3, ax3 = plt.subplots()
            labels = ['Normal', 'Suspicious']
            sizes = [
                len(df[df['anomaly_label'] == "✅ Normal"]),
                len(df[df['anomaly_label'] == "⚠️ Suspicious"])
            ]
            ax3.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['green', 'red'])
            st.pyplot(fig3)

        st.subheader("📡 Live Detection Simulation")
        for i in range(min(20, len(df))):
            log = df.iloc[i]
            st.write(f"👤 {log.get('username', 'Unknown')} | 🕒 {log['login_time']} | {log['anomaly_label']}")
            time.sleep(0.1)

        st.subheader("📥 Download Anomaly Report")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "anomaly_report.csv", "text/csv")

        st.subheader("📊 Stats Overview")
        st.metric("🔍 Total Records", len(df))
        st.metric("⚠️ Anomalies", len(df[df['anomaly_label'] == "⚠️ Suspicious"]))
        st.metric("✅ Normal", len(df[df['anomaly_label'] == "✅ Normal"]))

elif authentication_status is False:
    st.error("❌ Incorrect username or password")
elif authentication_status is None:
    st.warning("Please enter your credentials.") 
