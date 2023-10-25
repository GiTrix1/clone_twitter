import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_add_tweet_with_media():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        tweet_data = {"tweet_data": "Test tweet data", "tweet_media_ids": [1, 2, 3]}
        headers = {"api_key": "test"}
        response = await client.post("/api/tweets", json=tweet_data, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True
        assert "tweet_id" in result


@pytest.mark.asyncio
async def test_add_tweet_without_media():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        tweet_data = {"tweet_data": "Test tweet data", "tweet_media_ids": ''}
        headers = {"api_key": "test"}
        response = await client.post("/api/tweets", json=tweet_data, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True
        assert "tweet_id" in result


@pytest.mark.asyncio
async def test_delete_tweet_by_id():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.delete("/api/tweets/53", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True


@pytest.mark.asyncio
async def test_put_like():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.post("/api/tweets/50/likes", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True


@pytest.mark.asyncio
async def test_delete_like():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.delete("/api/tweets/50/likes", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True


@pytest.mark.asyncio
async def test_subscribe():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.post("/api/users/2/follow", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True


@pytest.mark.asyncio
async def test_unsubscribe():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.delete("/api/users/2/follow", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True


@pytest.mark.asyncio
async def test_get_tweets():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.get("/api/tweets", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True
        assert "tweets" in result


@pytest.mark.asyncio
async def test_get_my_info_profile():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True
        assert "user" in result


@pytest.mark.asyncio
async def test_get_info_another_profile():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        headers = {"api_key": "test"}
        response = await client.get("/api/users/1", headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert result["result"] is True
        assert "user" in result
