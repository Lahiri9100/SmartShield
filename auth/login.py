import streamlit as st
import json
import streamlit_authenticator as stauth
import os

def authenticate_user():
    if st.sidebar.button("🔄 Toggle Sign Up / Login"):
        st.session_state.signup = not st.session_state.get("signup", False)

    if st.session_state.get("signup", False):
        return "signup", None

    if not os.path.exists("users.json"):
        st.warning("No users found. Please sign up first.")
        return "signup", None

    users = json.load(open("users.json"))
    creds = {"usernames": {}}
    for uname, info in users.items():
        creds["usernames"][uname] = {
            "name": info["name"],
            "email": info["email"],
            "password": info["password"]
        }

    authenticator = stauth.Authenticate(
        creds, "smartshield_cookie", "somekey", 30
    )
    name, status, uname = authenticator.login("Login", "main")

    if status:
        authenticator.logout("Logout", "sidebar")
        return "login", name
    elif status is False:
        st.error("❌ Incorrect credentials")
    else:
        st.warning("Enter credentials")
    return None, None
