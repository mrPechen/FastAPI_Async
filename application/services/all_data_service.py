import json
from typing import Any, Sequence

from fastapi import Depends
from sqlalchemy import Row, RowMapping
from fastapi.background import BackgroundTasks

from application.repositories.all_data_repository import AllDataRepository
from fastapi.encoders import jsonable_encoder

from application.cache.cache import RedisRepository


class AllDataService:
    def __init__(self, all_data_repository: AllDataRepository = Depends()):
        self.repository = all_data_repository
        self.redis = RedisRepository()
        self.background_task = BackgroundTasks()

    async def set_cache(self, value: any) -> Any:
        data = jsonable_encoder(value)
        serialized_data = json.dumps(data)
        return await self.redis.redis.set(name='all_data', value=serialized_data, ex=120)

    async def get_cache(self) -> Any:
        return await self.redis.get_cache(name='all_data')

    async def get_all_data(self) -> Any | Sequence[Row | RowMapping]:
        data = await self.repository.get_all()
        cache = await self.get_cache()
        if cache:
            return cache
        self.background_task.add_task(await self.set_cache(value=data))
        return data
