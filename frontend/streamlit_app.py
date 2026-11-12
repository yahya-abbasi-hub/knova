import streamlit as st

st.set_page_config(
    page_title="KNOVA",
    page_icon="🧠",
    layout="wide",
)

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def is_logged_in() -> bool:
    return st.session_state.token is not None


st.title("🧠 KNOVA")
st.caption("AI Knowledge Intelligence Platform")

if is_logged_in():
    st.success(f"Logged in as {st.session_state.user['email']}")
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
    st.info("Use the sidebar to navigate to Documents or Chat.")
else:
    st.info("👈 Please go to the **Login** page in the sidebar to continue.")