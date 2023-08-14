from typing import Any

import pytest
from httpx import AsyncClient

from application.main import app

client = AsyncClient(app=app, base_url='http://127.0.0.1:8000')
pytestmark = pytest.mark.asyncio


@pytest.mark.order(23)
async def test_get_all_data() -> Any:
    response = await client.get(url='api/v1/all')
    response_json = response.json()
    print(response.request)
    print(response)
    print(response_json)
    if response:
        assert response.status_code == 200
        assert response.json() != [{}]
    if not response:
        assert response.status_code == 200
        assert response.json() == []
