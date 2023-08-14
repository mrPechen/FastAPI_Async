from typing import Any

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Row, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from application.db_app import schemas
from application.db_app.database import connect_db
from application.db_app.models import Dish, Menu, Submenu
from application.repositories.submenu_repository import SubmenuRepository


class DishRepository:

    def __init__(self, session: Session = Depends(connect_db)):
        self.db: AsyncSession = session
        self.menu = Menu
        self.submenu = Submenu
        self.dish = Dish
        self.submenu_repository = SubmenuRepository(session=session)

    async def get_dishes(self, menu_id: int, submenu_id: int) -> Any | None:
        result = await self.db.execute(
            select(
                self.dish.id,
                self.dish.submenu_id,
                self.dish.title,
                self.dish.description,
                self.dish.price
            ).filter(self.dish.menu_id == menu_id, self.dish.submenu_id == submenu_id)
            .group_by(self.dish.id)
        )
        return result.all()

    async def get_dish(self, menu_id: int, submenu_id: int, dish_id: int) -> HTTPException | Row[tuple] | None:
        result = await self.db.execute(
            select(
                self.dish.id,
                self.dish.submenu_id,
                self.dish.title,
                self.dish.description,
                self.dish.price
            ).filter(self.dish.menu_id == menu_id, self.dish.submenu_id == submenu_id, self.dish.id == dish_id)
        )
        item = result.first()
        if not item:
            raise HTTPException(status_code=404, detail='dish not found')
        return item

    async def create_dish(self, dish_schema: schemas.DishCreate, menu_id: int,
                          submenu_id: int) -> HTTPException | Row[tuple[Any]]:
        # await self.submenu_repository.get_submenu(menu_id=menu_id, submenu_id=submenu_id)
        db_dish = self.dish(**dish_schema.model_dump(), menu_id=menu_id, submenu_id=submenu_id)
        self.db.add(db_dish)
        await self.db.commit()
        await self.db.refresh(db_dish)
        dish_id = jsonable_encoder(db_dish)['id']
        return await self.get_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

    async def update_dish(self, dish_schemas: schemas.DishUpdate, menu_id: int,
                          submenu_id: int, dish_id: int) -> HTTPException | Row[tuple[Any]]:
        new_data = dish_schemas.model_dump(exclude_unset=True)
        await self.db.execute(update(self.dish).
                              where(self.dish.menu_id == menu_id,
                                    self.dish.submenu_id == submenu_id,
                                    self.dish.id == dish_id).values(new_data).returning(self.dish))
        await self.db.commit()
        return await self.get_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

    async def delete_dish(self, menu_id: int, submenu_id: int, dish_id: int) -> HTTPException | dict[str, str | bool]:
        result = await self.db.execute(select(self.dish).filter(self.dish.menu_id == menu_id,
                                                                self.dish.submenu_id == submenu_id,
                                                                self.dish.id == dish_id))
        item = result.scalars().first()
        if not item:
            raise HTTPException(status_code=404, detail='menu id, submenu id or dish id not found')
        await self.db.delete(item)
        await self.db.commit()
        return {'status': True, 'message': 'The dish has been deleted'}
