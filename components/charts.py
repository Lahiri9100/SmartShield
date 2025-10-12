import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def plot_user_activity(df):
    if st.checkbox("📊 Show Anomalies by User"):
        fig, ax = plt.subplots(figsize=(10,5))
        sns.countplot(data=df[df['anomaly_label']=="⚠️ Suspicious"], x='username', ax=ax)
        st.pyplot(fig)

def plot_suspicion_trend(df):
    if st.checkbox("📈 Suspicion Score Trend"):
        df['score'] = df['bytes_sent'] + df['bytes_received']
        fig, ax = plt.subplots()
        ax.plot(df.index, df['score'], color='orange')
        st.pyplot(fig)

def plot_distribution(df):
    if st.checkbox("🥧 Show Normal vs Suspicious"):
        fig, ax = plt.subplots()
        ax.pie(
            [len(df[df['anomaly_label']=="✅ Normal"]),
             len(df[df['anomaly_label']=="⚠️ Suspicious"])],
            labels=['Normal','Suspicious'], autopct='%1.1f%%', colors=['green','red']
        )
        st.pyplot(fig)
