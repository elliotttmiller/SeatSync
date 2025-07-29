import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_login_logout():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        # Replace with valid credentials
        login_data = {"username": "testuser", "password": "testpass"}
        response = await ac.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        # Logout
        response = await ac.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_predict_price():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        payload = {
            "game_id": "YOUR_GAME_ID",
            "section": "A",
            "row": "5",
            "seat": "12",
            "date": "2024-08-01"
        }
        response = await ac.post("/api/v1/predict-price", json=payload)
        print("Predict response:", response.text)
        assert response.status_code == 200
        data = response.json()
        assert "price" in data
        assert isinstance(data["price"], (int, float))

@pytest.mark.asyncio
async def test_chat():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        payload = {"message": "Hello, AI!"}
        response = await ac.post("/api/v1/chat", json=payload)
        print("Chat response:", response.text)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data 