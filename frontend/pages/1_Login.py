import streamlit as st
import sys
import os
from api_client import login, register, get_me, forgot_password, reset_password
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import login, register, get_me

st.set_page_config(page_title="KNOVA — Login", page_icon="🧠")

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

st.title("🧠 KNOVA")

if st.session_state.token:
    st.success(f"Already logged in as {st.session_state.user['email']}")
    st.stop()

tab_login, tab_register, tab_forgot = st.tabs(["Login", "Register", "Forgot Password"])

with tab_login:
    st.subheader("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if not login_email or not login_password:
            st.error("Please enter both email and password.")
        else:
            try:
                result = login(login_email, login_password)
                token = result["access_token"]
                user = get_me(token)

                st.session_state.token = token
                st.session_state.user = user
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

with tab_register:
    st.subheader("Create an account")
    reg_name = st.text_input("Full name", key="reg_name")
    reg_email = st.text_input("Email", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_password")

    if st.button("Register", key="register_button"):
        if not reg_email or not reg_password:
            st.error("Please enter at least an email and password.")
        else:
            try:
                result = register(reg_email, reg_password, reg_name)
                token = result["access_token"]
                user = get_me(token)

                st.session_state.token = token
                st.session_state.user = user
                st.success("Account created and logged in!")
                st.rerun()
            #except Exception as e:
             #   st.error(f"Registration failed: {e}")
            except Exception as e:
                st.error(f"Registration failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.error(f"Details: {e.response.text}")
with tab_forgot:
    st.subheader("Reset your password")

    st.caption("Step 1: Enter your email to request a reset.")
    forgot_email = st.text_input("Email", key="forgot_email")

    if st.button("Request Reset", key="forgot_button"):
        if not forgot_email:
            st.error("Please enter your email.")
        else:
            try:
                result = forgot_password(forgot_email)
                st.success(result["message"])
                if result.get("reset_token"):
                    st.info(f"**Development mode** — your reset token is:\n\n`{result['reset_token']}`")
                    st.session_state["last_reset_token"] = result["reset_token"]
            except Exception as e:
                st.error(f"Request failed: {e}")

    st.divider()

    st.caption("Step 2: Enter your reset token and new password.")
    reset_token_input = st.text_input(
        "Reset token",
        value=st.session_state.get("last_reset_token", ""),
        key="reset_token_input",
    )
    new_password_input = st.text_input("New password", type="password", key="new_password_input")

    if st.button("Reset Password", key="reset_password_button"):
        if not reset_token_input or not new_password_input:
            st.error("Please fill in both fields.")
        else:
            try:
                reset_password(reset_token_input, new_password_input)
                st.success("Password reset successfully! Go to the Login tab to log in.")
            except Exception as e:
                st.error(f"Reset failed: {e}")