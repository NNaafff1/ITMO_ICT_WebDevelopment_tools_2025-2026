def test_create_project(client, auth_headers):
    response = client.post("/projects/", json={
        "title": "My Project", "description": "Looking for teammates",
        "required_skills": "Python", "status": "open"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Project"
    assert data["status"] == "open"


def test_create_project_no_auth(client):
    response = client.post("/projects/", json={
        "title": "My Project", "description": "desc"
    })
    assert response.status_code == 401


def test_list_projects(client, test_project):
    response = client.get("/projects/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_projects_status_filter(client, test_project):
    response = client.get("/projects/?status=open")
    assert response.status_code == 200
    for p in response.json():
        assert p["status"] == "open"


def test_get_project_by_id(client, test_project):
    pid = test_project["id"]
    response = client.get(f"/projects/{pid}")
    assert response.status_code == 200
    assert response.json()["id"] == pid


def test_get_project_not_found(client):
    response = client.get("/projects/99999")
    assert response.status_code == 404


def test_update_project_as_owner(client, auth_headers, test_project):
    pid = test_project["id"]
    response = client.put(f"/projects/{pid}", json={"title": "Updated Title"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_project_as_non_owner(client, second_user_headers, test_project):
    pid = test_project["id"]
    response = client.put(f"/projects/{pid}", json={"title": "Hacked"}, headers=second_user_headers)
    assert response.status_code == 403


def test_delete_project_as_owner(client, auth_headers, test_project):
    pid = test_project["id"]
    response = client.delete(f"/projects/{pid}", headers=auth_headers)
    assert response.status_code == 204


def test_get_project_members_empty(client, test_project):
    pid = test_project["id"]
    response = client.get(f"/projects/{pid}/members")
    assert response.status_code == 200
    assert response.json() == []


def test_team_request_flow(client, auth_headers, second_user_headers, test_project):
    pid = test_project["id"]
    response = client.post("/team-requests/", json={
        "project_id": pid, "message": "I want to join!"
    }, headers=second_user_headers)
    assert response.status_code == 201
    request_id = response.json()["id"]
    incoming = client.get("/team-requests/incoming", headers=auth_headers)
    assert incoming.status_code == 200
    accept = client.put(f"/team-requests/{request_id}/accept", headers=auth_headers)
    assert accept.status_code == 200
    assert accept.json()["status"] == "accepted"
    members = client.get(f"/projects/{pid}/members")
    assert len(members.json()) == 1
