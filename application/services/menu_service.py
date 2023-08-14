from typing import Any

from fastapi import BackgroundTasks, Depends

from application.cache.cache import RedisRepository
from application.db_app import schemas
from application.repositories.menu_repository import MenuRepository


class MenuService:
    def __init__(self, menu_repository: MenuRepository = Depends()):
        self.menu_repository = menu_repository
        self.redis = RedisRepository()
        self.cache_name = 'menu_cache'
        self.background_task = BackgroundTasks()

    async def set_cache(self, value: Any, menu_id: int | None = None, if_list: bool = False) -> Any:
        name = self.cache_name
        if if_list is True:
            return await self.redis.set_cache(name=f'{name}', value=value, if_list=True)
        if menu_id:
            return await self.redis.set_cache(name=f'{name}_{menu_id}', value=value)
        return await self.redis.set_cache(name=name, value=value)

    async def get_cache(self, menu_id: int | None = None) -> Any:
        name = self.cache_name
        if menu_id:
            return await self.redis.get_cache(name=f'{name}_{menu_id}')
        return await self.redis.get_cache(name=name)

    async def delete_cache(self, menu_id: int | None = None) -> Any:
        name = self.cache_name
        if menu_id:
            return await self.redis.delete_cache(name=f'{name}_{menu_id}')
        await self.redis.delete_cache(name='submenu_cache')
        await self.redis.delete_cache(name='dish_cache')
        return await self.redis.delete_cache(name=f'{name}')

    async def update_menu_cache(self, menu_id: int | None = None) -> Any:
        if menu_id:
            menu = await self.menu_repository.get_menu(menu_id=menu_id)
            return await self.set_cache(value=menu, menu_id=menu_id)
        menus = await self.menu_repository.get_menus()
        return await self.set_cache(value=menus, if_list=True)

    async def get_menus(self) -> Any:
        menus = await self.menu_repository.get_menus()
        get_cache = await self.get_cache()
        if get_cache:
            print("cache")
            return get_cache
        self.background_task.add_task(await self.set_cache(value=menus, if_list=True))
        return menus

    async def get_menu(self, menu_id: int) -> Any:
        menu = await self.menu_repository.get_menu(menu_id=menu_id)
        get_cache = await self.get_cache(menu_id=menu_id)
        if get_cache:
            return get_cache
        self.background_task.add_task(await self.set_cache(value=menu, menu_id=menu_id))
        return menu

    async def delete_menu(self, menu_id: int) -> Any:
        delete = await self.menu_repository.delete_menu(menu_id=menu_id)
        self.background_task.add_task(await self.delete_cache())
        self.background_task.add_task(await self.delete_cache(menu_id=menu_id))
        return delete

    async def update_menu(self, menu_schemas: schemas.MenuUpdate, menu_id: int) -> Any:
        update = await self.menu_repository.update_menu(menu_schemas=menu_schemas, menu_id=menu_id)
        self.background_task.add_task(await self.update_menu_cache())
        self.background_task.add_task(await self.update_menu_cache(menu_id=menu_id))
        return update

    async def create_menu(self, menu_schemas: schemas.MenuCreate) -> Any:
        create = await self.menu_repository.create_menu(menu_schemas=menu_schemas)
        self.background_task.add_task(await self.update_menu_cache())
        return create
