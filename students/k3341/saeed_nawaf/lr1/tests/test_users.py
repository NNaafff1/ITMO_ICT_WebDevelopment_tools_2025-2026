def test_list_users(client, registered_user):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_list_users_skill_filter(client, registered_user):
    response = client.get("/users/?skill=Python")
    assert response.status_code == 200
    users = response.json()
    assert any("Python" in (u["skills"] or "") for u in users)


def test_get_user_by_id(client, registered_user):
    user_id = registered_user["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_update_own_profile(client, auth_headers, registered_user):
    user_id = registered_user["id"]
    response = client.put(f"/users/{user_id}", json={"bio": "Updated bio"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["bio"] == "Updated bio"


def test_update_other_profile_forbidden(client, auth_headers, second_user_headers):
    me = client.get("/auth/me", headers=second_user_headers).json()
    second_id = me["id"]
    response = client.put(f"/users/{second_id}", json={"bio": "Hacked"}, headers=auth_headers)
    assert response.status_code == 403


def test_delete_own_account(client, auth_headers, registered_user):
    user_id = registered_user["id"]
    response = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_other_account_forbidden(client, auth_headers, second_user_headers):
    me = client.get("/auth/me", headers=second_user_headers).json()
    second_id = me["id"]
    response = client.delete(f"/users/{second_id}", headers=auth_headers)
    assert response.status_code == 403
