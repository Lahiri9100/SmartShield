import streamlit as st
import pandas as pd
from detection.history_manager import (
    list_saved_histories, load_history_df, delete_history_item,
    clear_history, save_to_history
)
from detection.model import analyze_dataframe
from auth.register import register_user
from auth.login import authenticate_user
from components.charts import plot_user_activity, plot_suspicion_trend, plot_distribution
from components.stats_panel import show_stats

st.set_page_config(page_title="SmartShield IDS", layout="wide")

auth_status, name = authenticate_user()

if auth_status == "signup":
    register_user()

elif auth_status == "login":
    st.sidebar.markdown(f"👋 Welcome **{name}**")
    st.title("🔐 SmartShield – Intrusion Detection System")

    uploaded = st.file_uploader("📤 Upload CSV File", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        save_to_history(df, uploaded.name)
        st.success(f"✅ '{uploaded.name}' uploaded and saved.")
        df = analyze_dataframe(df)

        st.subheader("📊 Detection Results")
        st.dataframe(df)

        plot_user_activity(df)
        plot_suspicion_trend(df)
        plot_distribution(df)
        show_stats(df)
