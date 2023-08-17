from typing import Any

from fastapi import Depends
from fastapi.background import BackgroundTasks

from application.cache.cache import RedisRepository
from application.db_app import schemas
from application.repositories.dish_repository import DishRepository
from application.services.menu_service import MenuService
from application.services.submenu_service import SubmenuService


class DishService:
    def __init__(self, dish_repository: DishRepository = Depends()):
        self.dish_repository = dish_repository
        self.redis = RedisRepository()
        self.cache_name = 'dish_cache'
        self.menu_service = MenuService(self.dish_repository.submenu_repository.menu_repository)
        self.submenu_service = SubmenuService(self.dish_repository.submenu_repository)
        self.background_task = BackgroundTasks()

    async def set_cache(self, value: Any, dish_id: int | None = None, if_list: bool = False) -> Any:
        name = self.cache_name
        if if_list is True:
            return await self.redis.set_cache(name=f'{name}', value=value, if_list=True)
        if dish_id:
            return await self.redis.set_cache(name=f'{name}_{dish_id}', value=value)
        return await self.redis.set_cache(name=name, value=value)

    async def get_cache(self, dish_id: int | None = None) -> Any:
        name = self.cache_name
        if dish_id:
            return await self.redis.get_cache(name=f'{name}_{dish_id}')
        return await self.redis.get_cache(name=name)

    async def delete_cache(self, dish_id: int | None = None) -> Any:
        name = self.cache_name
        if dish_id:
            await self.redis.delete_cache(name=f'{name}_{dish_id}')
        await self.redis.delete_cache('menu_cache')
        await self.redis.delete_cache('submenu_cache')
        return await self.redis.delete_cache(name=f'{name}')

    async def update_dish_cache(self, menu_id: int, submenu_id: int, dish_id: int | None = None) -> Any:
        if dish_id:
            dish = await self.dish_repository.get_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
            return await self.set_cache(value=dish, dish_id=dish_id)
        dishes = await self.dish_repository.get_dishes(menu_id=menu_id, submenu_id=submenu_id)
        return await self.set_cache(value=dishes, if_list=True)

    async def get_dishes(self, menu_id: int, submenu_id: int) -> Any:
        dishes = await self.dish_repository.get_dishes(menu_id=menu_id, submenu_id=submenu_id)
        get_cache = await self.get_cache()
        if get_cache:
            return get_cache
        self.background_task.add_task(await self.set_cache(value=dishes, if_list=True))
        return dishes

    async def get_dish(self, menu_id: int, submenu_id: int, dish_id: int) -> Any:
        dish = await self.dish_repository.get_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        get_cache = await self.get_cache(dish_id=dish_id)
        if get_cache:
            return get_cache
        self.background_task.add_task(await self.set_cache(value=dish, dish_id=dish_id))
        return dish

    async def delete_dish(self, menu_id: int, submenu_id: int, dish_id: int) -> Any:
        delete = await self.dish_repository.delete_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        self.background_task.add_task(await self.delete_cache())
        self.background_task.add_task(await self.delete_cache(dish_id=dish_id))
        self.background_task.add_task(await self.submenu_service.delete_cache(submenu_id=submenu_id))
        self.background_task.add_task(await self.menu_service.delete_cache(menu_id=menu_id))
        self.background_task.add_task(await self.menu_service.update_menu_cache())
        return delete

    async def update_dish(self, dish_schemas: schemas.DishUpdate, menu_id: int,
                          submenu_id: int, dish_id: int) -> Any:
        update = await self.dish_repository.update_dish(dish_schemas=dish_schemas,
                                                        menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        self.background_task.add_task(await self.update_dish_cache(menu_id=menu_id, submenu_id=submenu_id))
        self.background_task.add_task(
            await self.update_dish_cache(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id))
        self.background_task.add_task(await self.menu_service.update_menu_cache())
        return update

    async def create_dish(self, dish_schemas: schemas.DishCreate, menu_id: int, submenu_id: int) -> Any:
        create = await self.dish_repository.create_dish(dish_schema=dish_schemas, menu_id=menu_id,
                                                        submenu_id=submenu_id)
        self.background_task.add_task(await self.update_dish_cache(menu_id=menu_id, submenu_id=submenu_id))
        self.background_task.add_task(await self.submenu_service.update_submenu_cache(menu_id=menu_id))
        self.background_task.add_task(
            await self.submenu_service.update_submenu_cache(menu_id=menu_id, submenu_id=submenu_id))
        self.background_task.add_task(await self.menu_service.update_menu_cache(menu_id=menu_id))
        self.background_task.add_task(await self.menu_service.update_menu_cache())
        return create
