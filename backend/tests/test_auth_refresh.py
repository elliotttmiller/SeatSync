import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_login_refresh_logout():
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        response = await ac.post("/api/v1/auth/debug", json={"username": "testuser", "password": "testpass"})
        print("DEBUG /debug response:", response.text)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["password"] == "testpass"
        # Continue with login test
        response = await ac.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert "access_token" in data
        cookies = response.cookies
        response = await ac.post("/api/v1/auth/refresh", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        response = await ac.post("/api/v1/auth/logout", cookies=cookies)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out" 