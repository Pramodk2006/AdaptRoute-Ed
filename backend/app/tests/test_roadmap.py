"""
Roadmap & Content endpoint tests with mocked LLM calls.
"""
from unittest.mock import patch, AsyncMock


def test_get_roadmap_not_found(client, auth_headers):
    """GET /api/v1/roadmap without generating first returns 404."""
    response = client.get("/api/v1/roadmap", headers=auth_headers)
    assert response.status_code == 404


def test_generate_roadmap_without_profile(client, auth_headers):
    """POST /api/v1/roadmap/generate without profile returns 400."""
    response = client.post("/api/v1/roadmap/generate", json={"num_weeks": 8}, headers=auth_headers)
    assert response.status_code == 400


@patch("app.services.adaptive_llm_service.get_provider")
def test_generate_roadmap_success(mock_get_provider, client, auth_headers, test_profile):
    """POST /api/v1/roadmap/generate creates roadmap and topics using mocked LLM."""
    from app.llm.base import LLMResponse
    mock_provider = AsyncMock()
    mock_provider.model_name = "gemma3"
    mock_provider.generate = AsyncMock(return_value=LLMResponse(
        text="""{
            "title": "Python Data Science Roadmap",
            "goal": "Master Python data science",
            "weeks": [
                {
                    "week_number": 1,
                    "topics": [
                        {"title": "Python Basics & Syntax", "description": "Variables, types, control flow", "order_index": 1},
                        {"title": "Data Structures", "description": "Lists, dicts, sets, tuples", "order_index": 2}
                    ]
                }
            ]
        }""",
        model="gemma3",
        prompt_tokens=10,
        completion_tokens=50,
        latency_ms=150,
    ))
    mock_get_provider.return_value = mock_provider

    response = client.post("/api/v1/roadmap/generate", json={"num_weeks": 4}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Python Data Science Roadmap"
    assert len(data["weeks"]) == 1
    assert len(data["weeks"][0]["topics"]) == 2

    # Now GET /roadmap should return 200
    get_res = client.get("/api/v1/roadmap", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Python Data Science Roadmap"
