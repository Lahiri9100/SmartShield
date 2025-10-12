import streamlit as st
import json
import os
import streamlit_authenticator as stauth

def register_user():
    st.subheader("📝 Sign Up")
    name = st.text_input("Full Name")
    uname = st.text_input("Choose Username")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if pw != confirm:
            st.error("❌ Passwords do not match")
            return
        if not all([name, uname, email, pw]):
            st.error("❌ All fields required")
            return

        users = json.load(open("users.json")) if os.path.exists("users.json") else {}
        if uname in users:
            st.error("❌ Username already exists")
            return

        hashed = stauth.Hasher([pw]).generate()[0]
        users[uname] = {"name": name, "email": email, "password": hashed}
        json.dump(users, open("users.json", "w"), indent=2)
        st.success("✅ Registered successfully! You can log in now.")
