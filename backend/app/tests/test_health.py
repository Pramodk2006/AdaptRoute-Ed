"""
Health check and system availability tests.
"""
def test_health_check(client):
    """GET /health returns 200 with healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
