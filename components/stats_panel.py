import streamlit as st

def show_stats(df):
    st.subheader("📊 Stats Overview")
    st.metric("🔍 Total Records", len(df))
    st.metric("⚠️ Anomalies", len(df[df['anomaly_label']=="⚠️ Suspicious"]))
    st.metric("✅ Normal", len(df[df['anomaly_label']=="✅ Normal"]))
