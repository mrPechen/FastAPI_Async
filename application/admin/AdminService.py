from typing import Any

from application.db_app.database import SessionLocal
from sqlalchemy import select


class EntityMerger:
    def __init__(self, entity_array, model):
        self.repository = SessionLocal()
        self.entity_array = entity_array
        self.model = model

    async def run(self) -> Any:

        model = self.model
        arr = self.entity_array
        model_id = await self.repository.execute(select(model.id))
        ids_set_from_file = {i.id for i in arr}
        ids_set_from_bd = {i for i in model_id.scalars().all()}
        ids_set_for_update = ids_set_from_bd.intersection(ids_set_from_file)
        ids_set_for_delete = ids_set_from_bd.difference(ids_set_from_file)
        ids_set_for_create = ids_set_from_file.difference(ids_set_from_bd)
        for item in arr:
            result = model(**item.model_dump())
            if item.id in ids_set_for_create:
                self.repository.add(result)
            elif item.id in ids_set_for_update:
                await self.repository.merge(result)  # TODO обновляет все записи
        for item in ids_set_for_delete:
            model_item = await self.repository.execute(select(model).filter_by(id=item))
            delete = model_item.scalars().first()
            await self.repository.delete(delete)

        await self.repository.commit()
