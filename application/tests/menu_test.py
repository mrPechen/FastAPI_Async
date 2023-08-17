from typing import Any

import pytest
from httpx import AsyncClient

from application.main import app

client = AsyncClient(app=app, base_url='http://127.0.0.1:8000')
pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def init_cache(request: Any) -> Any:
    request.config.cache.get('menu', None)


@pytest.mark.order(1)
async def test_create_menu(request: Any) -> Any:
    body = {
        'title': 'title',
        'description': 'description'
    }
    response = await client.post(url='/api/v1/menus', json=body)
    json_response = response.json()
    print(response.request)
    print(response)
    print(json_response)
    assert response.status_code == 201
    if response.status_code == 201:
        data = json_response
        request.config.cache.set('menu', data)
    assert response.json()['title'] == body['title']
    assert response.json()['description'] == body['description']


@pytest.mark.order(2)
async def test_get_menus() -> Any:
    response = await client.get(url='/api/v1/menus')
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


@pytest.mark.order(3)
async def test_get_menu(request: Any, test_count: bool = False, submenu_count: Any = None,
                        dish_count: Any = None) -> Any:
    if test_count is False:
        cache = request.config.cache.get('menu', None)
        menu_id = cache['id']
        response = await client.get(url=f'/api/v1/menus/{menu_id}')
        title = cache['title']
        description = cache['description']
        print(response.request)
        print(response)
        print(response.json())
        if response.status_code == 200:
            assert response.status_code == 200
            assert response.json()['id'] == menu_id
            assert response.json()['title'] == title
            assert response.json()['description'] == description
        if response.status_code == 404:
            assert response.status_code == 404
            assert response.json() == {'detail': 'menu not found'}
    if test_count is True:
        cache = request.config.cache.get('menu', None)
        menu_id = cache['id']
        response = await client.get(url=f'/api/v1/menus/{menu_id}')
        print(response.request)
        print(response)
        print(response.json())
        assert response.status_code == 200
        assert response.json()['id'] == menu_id
        assert response.json()['submenus_count'] == submenu_count
        assert response.json()['dishes_count'] == dish_count


@pytest.mark.order(4)
async def test_update_menu(request: Any) -> Any:
    body = {
        'title': 'updated title',
        'description': 'updated description'
    }
    cache = request.config.cache.get('menu', None)
    menu_id = cache['id']
    response = await client.patch(url=f'/api/v1/menus/{menu_id}', json=body)
    print(response.request)
    print(response)
    print(response.json())
    assert response.status_code == 200
    if response.status_code == 200:
        cache['title'] = body['title']
        cache['description'] = body['description']
        request.config.cache.set('menu', cache)
    assert response.json()['title'] == body['title']
    assert response.json()['description'] == body['description']
    await test_get_menu(request)


@pytest.mark.order(5)
async def test_delete_menu(request: Any) -> Any:
    cache = request.config.cache.get('menu', None)
    menu_id = cache['id']
    response = await client.delete(url=f'/api/v1/menus/{menu_id}')
    print(response.request)
    print(response)
    assert response.status_code == 200


@pytest.mark.order(6)
async def test_deleted_menu(request: Any) -> Any:
    await test_get_menus()
    await test_get_menu(request)
