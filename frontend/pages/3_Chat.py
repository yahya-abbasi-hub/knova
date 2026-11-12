import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import list_workspaces, ask_question

st.set_page_config(page_title="KNOVA — Chat", page_icon="💬", layout="wide")

if "token" not in st.session_state or st.session_state.token is None:
    st.warning("Please log in first (see the Login page in the sidebar).")
    st.stop()

token = st.session_state.token

st.title("💬 AI Chat")

# --- Workspace selector ---
try:
    workspaces = list_workspaces(token)
except Exception as e:
    st.error(f"Could not load workspaces: {e}")
    st.stop()

if not workspaces:
    st.info("No workspaces yet — go to the Documents page to create one and upload files first.")
    st.stop()

workspace_names = {w["name"]: w["id"] for w in workspaces}
selected_name = st.selectbox("Workspace", list(workspace_names.keys()))
selected_workspace_id = workspace_names[selected_name]

st.divider()

# --- Chat history (per workspace, stored in session_state) ---
history_key = f"chat_history_{selected_workspace_id}"
if history_key not in st.session_state:
    st.session_state[history_key] = []

# Display past messages
for entry in st.session_state[history_key]:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        if not entry["grounded"]:
            st.caption("⚠️ Answered without strong supporting evidence from your documents.")
        if entry["sources"]:
            with st.expander(f"📎 {len(entry['sources'])} source(s)"):
                for src in entry["sources"]:
                    st.markdown(f"**{src['document_name']}** — chunk {src['chunk_index']}")
                    st.caption(src["snippet"])

# --- New question input ---
question = st.chat_input("Ask a question about your documents...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = ask_question(token, selected_workspace_id, question)
                st.write(result["answer"])

                if not result["grounded"]:
                    st.caption("⚠️ Answered without strong supporting evidence from your documents.")

                if result["sources"]:
                    with st.expander(f"📎 {len(result['sources'])} source(s)"):
                        for src in result["sources"]:
                            st.markdown(f"**{src['document_name']}** — chunk {src['chunk_index']}")
                            st.caption(src["snippet"])

                st.session_state[history_key].append({
                    "question": question,
                    "answer": result["answer"],
                    "sources": result["sources"],
                    "grounded": result["grounded"],
                })
            except Exception as e:
                st.error(f"Something went wrong: {e}")