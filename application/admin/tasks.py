from typing import Any

from asgiref.sync import async_to_sync

from application.admin.AdminService import EntityMerger
from application.admin.DataSource import XlsxDataSource
from application.celery.task_for_file import task
from application.db_app.models import Dish, Menu, Submenu


async def run() -> Any:
    url = 'https://docs.google.com/spreadsheets/d/1XPapODkrVhDUzbiR9vSmH7_-cZvjn3HcclbMGlEkbp4/export?format=csv'
    file = XlsxDataSource('application/admin/Menu.xlsx')
    menu = file.menus_file_data
    submenu = file.submenus_file_data
    dish = file.dishes_file_data
    print(menu)
    await EntityMerger(entity_array=menu, model=Menu).run()
    await EntityMerger(entity_array=submenu, model=Submenu).run()
    await EntityMerger(entity_array=dish, model=Dish).run()


@task.task
def sync_run() -> Any:
    async_to_sync(run)()
