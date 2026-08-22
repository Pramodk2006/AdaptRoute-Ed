"""
Dashboard endpoints unit tests.
"""
def test_dashboard_empty(client, auth_headers):
    """GET /api/v1/dashboard for new user returns empty/zero stats."""
    response = client.get("/api/v1/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["completed_topics"] == 0
    assert data["total_topics"] == 0
    assert data["completion_percentage"] == 0.0
    assert data["total_quiz_attempts"] == 0
    assert data["roadmap_status"] is None
