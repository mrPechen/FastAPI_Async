from typing import Any, Sequence

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Row, distinct, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from application.db_app import schemas
from application.db_app.database import connect_db
from application.db_app.models import Dish, Menu, Submenu
from application.repositories.menu_repository import MenuRepository


class SubmenuRepository:

    def __init__(self, session: Session = Depends(connect_db)):
        self.db: AsyncSession = session
        self.menu = Menu
        self.submenu = Submenu
        self.dish = Dish
        self.menu_repository = MenuRepository(session=session)

    async def get_submenus(self, menu_id: int) -> HTTPException | Sequence[Row[tuple[Any]]] | None:
        menu = await self.menu_repository.get_menu(menu_id=menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='submenu not found')
        result = await self.db.execute(
            select(
                self.submenu.id,
                self.submenu.menu_id,
                self.submenu.title,
                self.submenu.description,
                func.count(distinct(self.dish.id)).label('dishes_count'),
            ).filter(self.submenu.menu_id == menu_id)
            .outerjoin(self.dish, self.submenu.id == self.dish.submenu_id)
            .group_by(self.submenu.id)
        )
        return result.all()

    async def get_submenu(self, menu_id: int, submenu_id: int) -> HTTPException | Row[tuple[Any]] | None:
        result = await self.db.execute(
            select(
                self.submenu.id,
                self.submenu.menu_id,
                self.submenu.title,
                self.submenu.description,
                func.count(distinct(self.dish.id)).label('dishes_count'),
            ).filter(self.submenu.menu_id == menu_id, self.submenu.id == submenu_id)
            .outerjoin(self.dish, self.submenu.id == self.dish.submenu_id)
            .group_by(self.submenu.id)
        )
        item = result.first()
        if not item:
            raise HTTPException(status_code=404, detail='submenu not found')
        return item

    async def create_submenu(self, submenu_schemas: schemas.SubmenuCreate,
                             menu_id: int) -> HTTPException | Row[tuple[Any]]:
        menu = await self.menu_repository.get_menu(menu_id=menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail='menu not found')
        db_submenu = self.submenu(**submenu_schemas.model_dump(), menu_id=menu_id)
        self.db.add(db_submenu)
        await self.db.commit()
        await self.db.refresh(db_submenu)
        submenu_id = jsonable_encoder(db_submenu)['id']
        return await self.get_submenu(menu_id=menu_id, submenu_id=submenu_id)

    async def update_submenu(self, submenu_schemas: schemas.SubmenuUpdate, menu_id: int,
                             submenu_id: int) -> HTTPException | Row[tuple[Any]]:
        new_data = submenu_schemas.model_dump(exclude_unset=True)
        await self.db.execute(update(self.submenu).
                              where(self.submenu.menu_id == menu_id,
                                    self.submenu.id == submenu_id).values(new_data).returning(self.submenu))
        await self.db.commit()
        return await self.get_submenu(menu_id=menu_id, submenu_id=submenu_id)

    async def delete_submenu(self, menu_id: int, submenu_id: int) -> HTTPException | dict[str, str | bool]:
        result = await self.db.execute(select(self.submenu).filter(self.submenu.menu_id == menu_id,
                                                                   self.submenu.id == submenu_id))
        item = result.scalars().first()
        if not item:
            raise HTTPException(status_code=404, detail='menu id or submenu id not found')
        await self.db.delete(item)
        await self.db.commit()
        return {'status': True, 'message': 'The submenu has been deleted'}
