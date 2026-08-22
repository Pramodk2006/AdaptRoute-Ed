"""
Learner Profile endpoint unit tests.
"""
def test_get_profile_not_found(client, auth_headers):
    """GET /api/v1/profile without existing profile returns 404."""
    response = client.get("/api/v1/profile", headers=auth_headers)
    assert response.status_code == 404
    assert "Profile not found" in response.json()["detail"]


def test_create_profile_success(client, auth_headers):
    """POST /api/v1/profile creates profile and returns 201."""
    payload = {
        "full_name": "Jane Learner",
        "skill_level": "beginner",
        "learning_goal": "Learn Python for Web Development and Data Analysis",
        "preferred_pace": "fast",
        "daily_study_time": 90,
    }
    response = client.post("/api/v1/profile", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Jane Learner"
    assert data["skill_level"] == "beginner"
    assert data["daily_study_time"] == 90


def test_create_profile_duplicate_conflict(client, auth_headers, test_profile):
    """POST /api/v1/profile when profile exists returns 409 Conflict."""
    payload = {
        "full_name": "Duplicate Student",
        "skill_level": "advanced",
        "learning_goal": "Another goal",
        "preferred_pace": "slow",
        "daily_study_time": 30,
    }
    response = client.post("/api/v1/profile", json=payload, headers=auth_headers)
    assert response.status_code == 409


def test_update_profile_success(client, auth_headers, test_profile):
    """PUT /api/v1/profile updates specified fields."""
    payload = {
        "full_name": "Updated Name",
        "daily_study_time": 120,
    }
    response = client.put("/api/v1/profile", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["daily_study_time"] == 120
    assert data["skill_level"] == "intermediate"  # unchanged field preserved


def test_profile_unauthorized_access(client):
    """GET /api/v1/profile without auth token returns 401 Unauthorized."""
    response = client.get("/api/v1/profile")
    assert response.status_code == 401
