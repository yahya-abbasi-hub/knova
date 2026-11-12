def _get_token(client, email="pytest_ws@test.com"):
    client.post("/auth/register", json={"email": email, "password": "testpass123"})
    response = client.post("/auth/login", json={"email": email, "password": "testpass123"})
    return response.json()["access_token"]


def test_create_workspace(client, db_session):
    token = _get_token(client)
    response = client.post(
        "/workspaces/",
        json={"name": "Test WS", "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test WS"


def test_list_workspaces_only_shows_own(client, db_session):
    token_a = _get_token(client, "pytest_wsA@test.com")
    token_b = _get_token(client, "pytest_wsB@test.com")

    client.post("/workspaces/", json={"name": "WS A"}, headers={"Authorization": f"Bearer {token_a}"})

    response = client.get("/workspaces/", headers={"Authorization": f"Bearer {token_b}"})
    names = [w["name"] for w in response.json()]
    assert "WS A" not in names  # workspace isolation


def test_cannot_access_other_users_workspace(client, db_session):
    token_a = _get_token(client, "pytest_wsC@test.com")
    token_b = _get_token(client, "pytest_wsD@test.com")

    create_resp = client.post("/workspaces/", json={"name": "Private WS"}, headers={"Authorization": f"Bearer {token_a}"})
    workspace_id = create_resp.json()["id"]

    response = client.get(f"/workspaces/{workspace_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 403