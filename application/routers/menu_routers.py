from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from application.db_app import schemas
from application.services.all_data_service import AllDataService
from application.services.menu_service import MenuService

router = APIRouter(prefix='/api/v1')


@router.get('/all')
async def get_all(menu: AllDataService = Depends()) -> Any:
    return await menu.get_all_data()


@router.post('/menus', response_model=schemas.Menu, status_code=201)
async def create_menu(schema: schemas.MenuCreate, menu: MenuService = Depends()) -> schemas.Menu:
    return await menu.create_menu(menu_schemas=schema)


@router.get('/menus', response_model=list[schemas.Menu])
async def read_menus(menu: MenuService = Depends()) -> list[schemas.Menu]:
    return await menu.get_menus()


@router.patch('/menus/{target_menu_id}', response_model=schemas.Menu)
async def update_menus(target_menu_id: int, schema: schemas.MenuUpdate,
                       menu: MenuService = Depends()) -> HTTPException | schemas.Menu:
    return await menu.update_menu(menu_schemas=schema, menu_id=target_menu_id)


@router.delete('/menus/{target_menu_id}', response_model=None)
async def delete_menus(target_menu_id: int, menu: MenuService = Depends()) -> HTTPException | dict[str, str | bool]:
    return await menu.delete_menu(menu_id=target_menu_id)


@router.get('/menus/{target_menu_id}', response_model=schemas.Menu)
async def read_menu(target_menu_id: int, menu: MenuService = Depends()) -> HTTPException | schemas.Menu:
    return await menu.get_menu(menu_id=target_menu_id)
