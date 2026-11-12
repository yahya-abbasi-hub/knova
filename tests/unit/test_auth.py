def test_register_new_user(client, db_session):
    response = client.post("/auth/register", json={
        "email": "pytest_user1@test.com",
        "password": "testpassword123",
        "full_name": "Pytest User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email_fails(client, db_session):
    client.post("/auth/register", json={
        "email": "pytest_dup@test.com",
        "password": "testpassword123",
    })
    response = client.post("/auth/register", json={
        "email": "pytest_dup@test.com",
        "password": "differentpassword456",
    })
    assert response.status_code == 400


def test_login_with_correct_credentials(client, db_session):
    client.post("/auth/register", json={
        "email": "pytest_login@test.com",
        "password": "correctpassword",
    })
    response = client.post("/auth/login", json={
        "email": "pytest_login@test.com",
        "password": "correctpassword",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client, db_session):
    client.post("/auth/register", json={
        "email": "pytest_wrongpw@test.com",
        "password": "correctpassword",
    })
    response = client.post("/auth/login", json={
        "email": "pytest_wrongpw@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 400


def test_me_endpoint_requires_token(client, db_session):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)  # no Authorization header at all


def test_me_endpoint_returns_correct_user(client, db_session):
    register_response = client.post("/auth/register", json={
        "email": "pytest_me@test.com",
        "password": "testpassword123",
        "full_name": "Me Test",
    })
    token = register_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "pytest_me@test.com"