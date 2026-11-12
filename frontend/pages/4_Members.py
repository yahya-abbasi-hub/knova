import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import list_workspaces, list_members, invite_member, remove_member

st.set_page_config(page_title="KNOVA — Members", page_icon="👥", layout="wide")

if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Please log in first (see the Login page in the sidebar).")
    st.stop()

token = st.session_state.token
current_user_id = st.session_state.user["id"]

st.title("👥 Workspace Members")

# --- Workspace selector ---
try:
    workspaces = list_workspaces(token)
except Exception as e:
    st.error(f"Could not load workspaces: {e}")
    st.stop()

if not workspaces:
    st.info("No workspaces yet — go to the Documents page to create one first.")
    st.stop()

workspace_names = {w["name"]: w["id"] for w in workspaces}
selected_name = st.selectbox("Workspace", list(workspace_names.keys()))
selected_workspace_id = workspace_names[selected_name]

st.divider()

# --- Invite a new member ---
st.subheader("Invite someone")

with st.form("invite_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        invite_email = st.text_input("Email of the person to invite")
    with col2:
        invite_role = st.selectbox("Role", ["viewer", "member", "admin"])

    submitted = st.form_submit_button("Invite")
    if submitted:
        if not invite_email:
            st.error("Please enter an email.")
        else:
            try:
                invite_member(token, selected_workspace_id, invite_email, invite_role)
                st.success(f"Invited {invite_email} as {invite_role}.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not invite this person: {e}")

st.divider()

# --- Current members list ---
st.subheader("Current members")

try:
    members = list_members(token, selected_workspace_id)
except Exception as e:
    st.error(f"Could not load members: {e}")
    members = []

role_icons = {"owner": "👑", "admin": "🛠️", "member": "✍️", "viewer": "👀"}

for member in members:
    with st.container(border=True):
        col_a, col_b, col_c = st.columns([3, 1, 1])
        with col_a:
            st.markdown(f"**{member['user_email']}**")
        with col_b:
            icon = role_icons.get(member["role"], "")
            st.markdown(f"{icon} {member['role']}")
        with col_c:
            if member["role"] != "owner" and member["user_id"] != current_user_id:
                if st.button("Remove", key=f"remove_{member['id']}"):
                    try:
                        remove_member(token, selected_workspace_id, member["user_id"])
                        st.success("Member removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not remove: {e}")