import requests

API_BASE_URL = "http://127.0.0.1:8000"


def register(email: str, password: str, full_name: str = None) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    response.raise_for_status()
    return response.json()


def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    return response.json()


def get_me(token: str) -> dict:
    response = requests.get(
        f"{API_BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return response.json()


def list_workspaces(token: str) -> list:
    response = requests.get(
        f"{API_BASE_URL}/workspaces/",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return response.json()


def create_workspace(token: str, name: str, description: str = None) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/workspaces/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "description": description},
    )
    response.raise_for_status()
    return response.json()


def list_documents(token: str, workspace_id: str) -> list:
    response = requests.get(
        f"{API_BASE_URL}/workspaces/{workspace_id}/documents/",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return response.json()


def upload_document(token: str, workspace_id: str, file) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/workspaces/{workspace_id}/documents/",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (file.name, file.getvalue())},
    )
    response.raise_for_status()
    return response.json()


def ask_question(token: str, workspace_id: str, question: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/workspaces/{workspace_id}/chat/ask",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": question},
    )
    response.raise_for_status()
    return response.json()
def list_members(token: str, workspace_id: str) -> list:
    response = requests.get(
        f"{API_BASE_URL}/workspaces/{workspace_id}/members/",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return response.json()


def invite_member(token: str, workspace_id: str, user_email: str, role: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/workspaces/{workspace_id}/members/",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_email": user_email, "role": role},
    )
    response.raise_for_status()
    return response.json()


def remove_member(token: str, workspace_id: str, user_id: str) -> None:
    response = requests.delete(
        f"{API_BASE_URL}/workspaces/{workspace_id}/members/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()

def delete_document(token: str, workspace_id: str, document_id: str) -> None:
    response = requests.delete(
        f"{API_BASE_URL}/workspaces/{workspace_id}/documents/{document_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()


def delete_workspace(token: str, workspace_id: str) -> None:
    response = requests.delete(
        f"{API_BASE_URL}/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
def forgot_password(email: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/auth/forgot-password",
        json={"email": email},
    )
    response.raise_for_status()
    return response.json()


def reset_password(reset_token: str, new_password: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/auth/reset-password",
        json={"reset_token": reset_token, "new_password": new_password},
    )
    response.raise_for_status()
    return response.json()