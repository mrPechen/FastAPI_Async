from typing import Any

from fastapi import Depends
from fastapi.background import BackgroundTasks

from application.cache.cache import RedisRepository
from application.db_app import schemas
from application.repositories.submenu_repository import SubmenuRepository
from application.services.menu_service import MenuService


class SubmenuService:
    def __init__(self, submenu_repository: SubmenuRepository = Depends()):
        self.submenu_repository = submenu_repository
        self.redis = RedisRepository()
        self.cache_name = 'submenu_cache'
        self.menu_service = MenuService(self.submenu_repository.menu_repository)
        self.background_task = BackgroundTasks()

    async def set_cache(self, value: Any, submenu_id: int | None = None, if_list: bool = False) -> Any:
        name = self.cache_name
        if if_list is True:
            return await self.redis.set_cache(name=f'{name}', value=value, if_list=True)
        if submenu_id:
            return await self.redis.set_cache(name=f'{name}_{submenu_id}', value=value)
        return await self.redis.set_cache(name=name, value=value)

    async def get_cache(self, submenu_id: int | None = None) -> Any:
        name = self.cache_name
        if submenu_id:
            return await self.redis.get_cache(name=f'{name}_{submenu_id}')
        return await self.redis.get_cache(name=name)

    async def delete_cache(self, submenu_id: int | None = None) -> Any:
        name = self.cache_name
        if submenu_id:
            await self.redis.delete_cache(name=f'{name}_{submenu_id}')
        await self.redis.delete_cache(name='menu_cache')
        await self.redis.delete_cache(name='dish_cache')
        return await self.redis.delete_cache(name=f'{name}')

    async def update_submenu_cache(self, menu_id: int, submenu_id: int | None = None) -> Any:
        if submenu_id:
            submenu = await self.submenu_repository.get_submenu(menu_id=menu_id, submenu_id=submenu_id)
            return await self.set_cache(value=submenu, submenu_id=submenu_id)
        submenus = await self.submenu_repository.get_submenus(menu_id=menu_id)
        return await self.set_cache(value=submenus, if_list=True)

    async def get_submenus(self, menu_id: int) -> Any:
        submenus = await self.submenu_repository.get_submenus(menu_id=menu_id)
        get_cache = await self.get_cache()
        if get_cache:
            return get_cache
        self.background_task.add_task(await self.set_cache(value=submenus, if_list=True))
        return submenus

    async def get_submenu(self, menu_id: int, submenu_id: int) -> Any:
        submenu = await self.submenu_repository.get_submenu(menu_id=menu_id, submenu_id=submenu_id)
        get_cache = await self.get_cache(submenu_id=submenu_id)
        if get_cache:
            return get_cache
        self.background_task.add_task(await self.set_cache(value=submenu, submenu_id=submenu_id))
        return submenu

    async def delete_submenu(self, menu_id: int, submenu_id: int) -> Any:
        delete = await self.submenu_repository.delete_submenu(menu_id=menu_id, submenu_id=submenu_id)
        self.background_task.add_task(await self.delete_cache())
        self.background_task.add_task(await self.delete_cache(submenu_id=submenu_id))
        self.background_task.add_task(await self.menu_service.delete_cache(menu_id=menu_id))
        return delete

    async def update_submenu(self, submenu_schemas: schemas.SubmenuUpdate, menu_id: int, submenu_id: int) -> Any:
        update = await self.submenu_repository.update_submenu(submenu_schemas=submenu_schemas,
                                                              menu_id=menu_id, submenu_id=submenu_id)
        self.background_task.add_task(await self.update_submenu_cache(menu_id=menu_id))
        self.background_task.add_task(await self.update_submenu_cache(menu_id=menu_id, submenu_id=submenu_id))
        return update

    async def create_submenu(self, submenu_schemas: schemas.SubmenuCreate, menu_id: int) -> Any:
        create = await self.submenu_repository.create_submenu(submenu_schemas=submenu_schemas, menu_id=menu_id)
        self.background_task.add_task(await self.update_submenu_cache(menu_id=menu_id))
        self.background_task.add_task(await self.menu_service.update_menu_cache(menu_id=menu_id))
        self.background_task.add_task(await self.menu_service.update_menu_cache())
        return create
