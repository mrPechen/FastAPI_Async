from typing import Any

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base: Any = declarative_base()


class Menu(Base):
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    submenu_rel = relationship('Submenu', cascade='all,delete', back_populates='menu_rel')
    dish_rel = relationship('Dish', cascade='all,delete', back_populates='menu_rel2')


class Submenu(Base):
    __tablename__ = 'submenu'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    description = Column(String)
    menu_id = Column(Integer, ForeignKey('menu.id'))
    menu_rel = relationship('Menu', back_populates='submenu_rel')
    dish = relationship('Dish', cascade='all, delete', back_populates='submenu_rel')


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    description = Column(String)
    price = Column(String)
    submenu_id = Column(Integer, ForeignKey('submenu.id'))
    submenu_rel = relationship('Submenu', back_populates='dish')
    menu_rel2 = relationship('Menu', back_populates='dish_rel')
    menu_id = Column(Integer, ForeignKey('menu.id'))
