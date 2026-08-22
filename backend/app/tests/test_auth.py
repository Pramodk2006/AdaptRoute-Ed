"""
Auth endpoint tests.
"""
def test_register_success(client):
    """New user registration returns 201 with user data."""
    payload = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_weak_password(client):
    """Password without uppercase or digit is rejected with 422."""
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weakpassword",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_invalid_email(client):
    """Invalid email format is rejected with 422."""
    payload = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_duplicate_email(client, test_user):
    """Registering with an already existing email returns 409 Conflict."""
    payload = {
        "email": test_user.email,
        "username": "differentusername",
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client, test_user):
    """Valid credentials return 200 with access and refresh tokens."""
    payload = {
        "email": test_user.email,
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Wrong password returns 401 Unauthorized."""
    payload = {
        "email": test_user.email,
        "password": "WrongPassword123",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
