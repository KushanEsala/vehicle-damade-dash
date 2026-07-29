from fastapi.testclient import TestClient

from backend.main import app


def test_api_requires_login_and_clears_session():
    with TestClient(app) as client:
        assert client.get("/api/dashboard").status_code == 401
        login = client.post(
            "/api/auth/login",
            json={"identifier": "admin", "password": "Admin@123456"},
        )
        assert login.status_code == 200
        assert login.json()["user"]["role"] == "admin"
        assert client.get("/api/users").status_code == 200
        assert client.post("/api/auth/logout").status_code == 204
        assert client.get("/api/dashboard").status_code == 401
