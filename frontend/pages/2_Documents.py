import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import (
    list_workspaces,
    create_workspace,
    list_documents,
    upload_document,
    list_members,
    delete_document,
)

st.set_page_config(page_title="KNOVA — Documents", page_icon="📄", layout="wide")

if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Please log in first (see the Login page in the sidebar).")
    st.stop()

token = st.session_state.token

st.title("📄 Documents")

# --- Workspace selection / creation ---
st.subheader("Workspace")

try:
    workspaces = list_workspaces(token)
except Exception as e:
    st.error(f"Could not load workspaces: {e}")
    st.stop()

workspace_names = {w["name"]: w["id"] for w in workspaces}

col1, col2 = st.columns([3, 1])

selected_workspace_id = None
my_role = "viewer"

with col1:
    if workspace_names:
        selected_name = st.selectbox("Select a workspace", list(workspace_names.keys()))
        selected_workspace_id = workspace_names[selected_name]

        try:
            members = list_members(token, selected_workspace_id)
            my_membership = next(
                (m for m in members if m["user_id"] == st.session_state.user["id"]), None
            )
            my_role = my_membership["role"] if my_membership else "viewer"
        except Exception:
            my_role = "viewer"
    else:
        st.info("No workspaces yet — create one to get started.")

with col2:
    with st.popover("+ New workspace"):
        new_ws_name = st.text_input("Name", key="new_ws_name")
        new_ws_desc = st.text_input("Description (optional)", key="new_ws_desc")
        if st.button("Create", key="create_ws_button"):
            if not new_ws_name:
                st.error("Name is required.")
            else:
                try:
                    create_workspace(token, new_ws_name, new_ws_desc or None)
                    st.success("Workspace created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create workspace: {e}")

st.divider()

can_upload = my_role in ("owner", "admin", "member")
can_delete = my_role in ("owner", "admin")

# --- Document upload + list (only if a workspace is selected) ---
if selected_workspace_id:
    st.subheader(f"Documents in '{selected_name}'")

    if can_upload:
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "txt", "docx", "csv", "xlsx", "pptx", "png", "jpg", "jpeg"],
        )

        if uploaded_file is not None:
            if st.button("Upload"):
                try:
                    with st.spinner("Uploading..."):
                        result = upload_document(token, selected_workspace_id, uploaded_file)
                    st.success(f"Uploaded '{result['filename']}' — processing in background.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")
    else:
        st.info("You have view-only access in this workspace — uploading is not available to your role.")

    st.divider()

    try:
        documents = list_documents(token, selected_workspace_id)
    except Exception as e:
        st.error(f"Could not load documents: {e}")
        documents = []

    if not documents:
        st.info("No documents uploaded yet in this workspace.")
    else:
        for doc in documents:
            status = doc["status"]
            status_icon = {
                "uploaded": "⏳",
                "processing": "⚙️",
                "ready": "✅",
                "failed": "❌",
            }.get(status, "❓")

            with st.container(border=True):
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                with col_a:
                    st.markdown(f"**{doc['filename']}**")
                    if doc.get("page_count"):
                        st.caption(f"{doc['page_count']} page(s)")
                with col_b:
                    st.markdown(f"{status_icon} {status}")
                with col_c:
                    size_kb = (doc.get("file_size_bytes") or 0) / 1024
                    st.caption(f"{size_kb:.1f} KB")
                with col_d:
                    if can_delete:
                        if st.button("🗑️ Delete", key=f"del_{doc['id']}"):
                            try:
                                delete_document(token, selected_workspace_id, doc["id"])
                                st.success("Document deleted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")

                if status == "failed" and doc.get("error_message"):
                    st.error(doc["error_message"])