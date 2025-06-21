import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import bcrypt
import json
import os

st.set_page_config(page_title="SmartShield", layout="wide")

def register_user():
    st.subheader("📝 Sign Up")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match")
        elif not new_username or not new_password:
            st.error("All fields are required")
        else:
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    users = json.load(f)
            else:
                users = {}
            if new_username in users:
                st.error("Username already exists")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                users[new_username] = hashed_pw
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=2)
                st.success("Registered successfully!")

def login_user():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users = json.load(f)
            if username in users:
                stored_hash = users[username]
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    st.success(f"Welcome, {username}!")
                    return True
            st.error("Invalid credentials")
        else:
            st.error("No users found. Please register first.")
    return False

st.title("🔐 SmartShield – Intrusion Detection System")
st.markdown("""
A cybersecurity + ML project with user authentication, log upload, and anomaly detection.
""")

mode = st.sidebar.radio("Choose Mode", ["Login", "Sign Up"])
if mode == "Sign Up":
    register_user()
    st.stop()
else:
    if not login_user():
        st.stop()

st.subheader("📤 Upload Log File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data", df.head())

    st.subheader("📊 Anomaly Detection")
    with st.spinner("Detecting anomalies using Isolation Forest..."):
        model = IsolationForest(contamination=0.2, random_state=42)
        model.fit(df.select_dtypes(include=np.number))
        df['anomaly'] = model.predict(df.select_dtypes(include=np.number))
        df['label'] = df['anomaly'].map({1: '✅ Normal', -1: '⚠️ Suspicious'})

    st.write("### Detection Results", df[['label']].value_counts().rename("Count"))
    st.write("### Labeled Log Entries", df)

