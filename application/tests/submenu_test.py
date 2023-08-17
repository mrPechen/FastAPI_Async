from typing import Any

import pytest
from httpx import AsyncClient

from application.main import app

from . import menu_test

client = AsyncClient(app=app, base_url='http://127.0.0.1:8000')
pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def init_cache(request: Any) -> Any:
    request.config.cache.get('menu', None)
    request.config.cache.get('submenu', None)


@pytest.mark.order(7)
async def test_create_menu(request: Any) -> Any:
    await menu_test.test_create_menu(request)


@pytest.mark.order(8)
async def test_create_submenu(request: Any) -> Any:
    menu_id = request.config.cache.get('menu', None)['id']
    print('!!!!!!!!!!', menu_id)
    body = {
        'title': 'title submenu 15',
        'description': 'description submenu 15'
    }
    response = await client.post(url=f'/api/v1/menus/{menu_id}/submenus', json=body)
    json_response = response.json()
    print(response.request)
    print(response)
    print(json_response)
    assert response.status_code == 201
    if response.status_code == 201:
        data = json_response
        request.config.cache.set('submenu', data)
    assert response.json()['title'] == body['title']
    assert response.json()['description'] == body['description']


@pytest.mark.order(9)
async def test_get_submenus(request: Any) -> Any:
    menu_id = request.config.cache.get('menu', None)['id']
    response = await client.get(url=f'/api/v1/menus/{menu_id}/submenus')
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


@pytest.mark.order(10)
async def test_get_submenu(request: Any, test_count: bool = False, dish_count: Any = None) -> Any:
    if test_count is False:
        menu_id = request.config.cache.get('menu', None)['id']
        cache_submenu = request.config.cache.get('submenu', None)
        print('!!!!!!!!!!', cache_submenu)
        submenu_id = cache_submenu['id']
        submenu_title = cache_submenu['title']
        submenu_description = cache_submenu['description']
        response = await client.get(url=f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
        print(response.request)
        print(response)
        print(response.json())
        if response.status_code == 200:
            assert response.status_code == 200
            assert response.json()['id'] == submenu_id
            assert response.json()['title'] == submenu_title
            assert response.json()['description'] == submenu_description
        if response.status_code == 404:
            assert response.status_code == 404
            assert response.json() == {'detail': 'submenu not found'}
    if test_count is True:
        menu_id = request.config.cache.get('menu', None)['id']
        cache_submenu = request.config.cache.get('submenu', None)
        print('!!!!!!!!!!', cache_submenu)
        submenu_id = cache_submenu['id']
        response = await client.get(url=f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
        print(response.request)
        print(response)
        print(response.json())
        assert response.status_code == 200
        assert response.json()['id'] == submenu_id
        assert response.json()['dishes_count'] == dish_count


@pytest.mark.order(11)
async def test_update_submenu(request: Any) -> Any:
    body = {
        'title': 'updated title submenu',
        'description': 'updated description submenu'
    }
    menu_id = request.config.cache.get('menu', None)['id']
    cache_submenu = request.config.cache.get('submenu', None)
    print('!!!!!!!!!!', cache_submenu)
    submenu_id = cache_submenu['id']
    response = await client.patch(url=f'/api/v1/menus/{menu_id}/submenus/{submenu_id}', json=body)
    print(response.request)
    print(response)
    print(response.json())
    assert response.status_code == 200
    if response.status_code == 200:
        cache_submenu['title'] = body['title']
        cache_submenu['description'] = body['description']
        request.config.cache.set('submenu', cache_submenu)
    assert response.json()['title'] == body['title']
    assert response.json()['description'] == body['description']
    await test_get_submenu(request)


@pytest.mark.order(12)
async def test_delete_submenu(request: Any) -> Any:
    menu_id = request.config.cache.get('menu', None)['id']
    cache_submenu = request.config.cache.get('submenu', None)
    submenu_id = cache_submenu['id']
    response = await client.delete(url=f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    print(response.request)
    print(response)
    assert response.status_code == 200


@pytest.mark.order(13)
async def test_deleted_submenu(request: Any) -> Any:
    await test_get_submenus(request)
    await test_get_submenu(request)


@pytest.mark.order(14)
async def test_delete_menu(request: Any) -> Any:
    await menu_test.test_delete_menu(request)
