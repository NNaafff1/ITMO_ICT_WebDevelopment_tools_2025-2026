def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "newuser", "email": "new@example.com",
        "password": "password123", "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "password" not in data
    assert "hashed_password" not in data
    assert "id" in data


def test_register_duplicate_username(client, registered_user):
    response = client.post("/auth/register", json={
        "username": "testuser", "email": "other@example.com",
        "password": "password123", "full_name": "Other"
    })
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_register_duplicate_email(client, registered_user):
    response = client.post("/auth/register", json={
        "username": "otherusername", "email": "test@example.com",
        "password": "password123", "full_name": "Other"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser", "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser", "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_with_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data
