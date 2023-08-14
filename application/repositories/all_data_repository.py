from typing import Any, Sequence

from fastapi import Depends
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from application.db_app.database import connect_db

from application.db_app.models import Menu, Submenu, Dish


class AllDataRepository:
    def __init__(self, session: Session = Depends(connect_db)):
        self.db: AsyncSession = session
        self.menu = Menu
        self.submenu = Submenu
        self.dish = Dish

    async def get_all(self) -> Any | Sequence[Row | RowMapping]:
        menu = await self.db.execute(
            select(
                self.menu,
                self.submenu,
                self.dish
            ).outerjoin(
                self.menu.submenu_rel
            ).outerjoin(
                self.submenu.dish
            ).options(joinedload(self.menu.submenu_rel).joinedload(self.submenu.dish))
        )
        return menu.unique().scalars().all()
