from typing import Any, Sequence

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Row, distinct, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from application.db_app import schemas
from application.db_app.database import connect_db
from application.db_app.models import Dish, Menu, Submenu


class MenuRepository:

    def __init__(self, session: Session = Depends(connect_db)):
        self.db: AsyncSession = session
        self.menu = Menu
        self.submenu = Submenu
        self.dish = Dish

    async def get_menus(self) -> Sequence[Row[tuple]]:
        result = await self.db.execute(
            select(
                self.menu.id,
                self.menu.title,
                self.menu.description,
                func.count(distinct(self.submenu.id)).label('submenus_count'),
                func.count(distinct(self.dish.id)).label('dishes_count'),
            )
            .outerjoin(self.submenu, self.menu.id == self.submenu.menu_id)
            .outerjoin(self.dish, self.submenu.id == self.dish.submenu_id)
            .group_by(self.menu.id)
        )
        return result.all()

    async def get_menu(self, menu_id: int) -> HTTPException | Row[tuple] | None:
        result = await self.db.execute(
            select(
                self.menu.id,
                self.menu.title,
                self.menu.description,
                func.count(distinct(self.submenu.id)).label('submenus_count'),
                func.count(distinct(self.dish.id)).label('dishes_count'),
            ).filter(self.menu.id == menu_id)
            .outerjoin(self.submenu, self.menu.id == self.submenu.menu_id)
            .outerjoin(self.dish, self.submenu.id == self.dish.submenu_id)
            .group_by(self.menu.id)
        )
        item = result.first()
        if not item:
            raise HTTPException(status_code=404, detail='menu not found')
        return item

    async def delete_menu(self, menu_id: int) -> HTTPException | dict[str, str | bool]:
        delete = await self.db.execute(select(self.menu).filter(self.menu.id == menu_id))
        item = delete.scalars().first()
        if not item:
            raise HTTPException(status_code=404, detail='menu not found')
        await self.db.delete(item)
        await self.db.commit()
        return {'status': True, 'message': 'The menu has been deleted'}

    async def update_menu(self, menu_schemas: schemas.MenuUpdate, menu_id: int) -> HTTPException | Row[tuple[Any]]:
        new_data = menu_schemas.model_dump(exclude_unset=True)
        await self.db.execute(update(self.menu).where(self.menu.id == menu_id).values(new_data).returning(self.menu))
        await self.db.commit()
        return await self.get_menu(menu_id=menu_id)

    async def create_menu(self, menu_schemas: schemas.MenuCreate) -> Row[tuple[Any]]:
        db_menu = self.menu(**menu_schemas.model_dump())
        self.db.add(db_menu)
        await self.db.commit()
        await self.db.refresh(db_menu)
        menu_id = jsonable_encoder(db_menu)['id']
        return await self.get_menu(menu_id)
