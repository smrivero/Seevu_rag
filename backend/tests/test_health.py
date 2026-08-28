import os

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_status_code_200() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_needs_no_environment() -> None:
    saved = dict(os.environ)
    try:
        os.environ.clear()
        client = TestClient(create_app())
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    finally:
        os.environ.clear()
        os.environ.update(saved)


def test_openapi_declares_status_as_a_literal() -> None:
    document = create_app().openapi()
    status_schema = document["components"]["schemas"]["HealthStatus"]["properties"][
        "status"
    ]
    assert status_schema.get("const") == "ok"
